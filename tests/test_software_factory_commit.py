from pathlib import Path
import importlib.util
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "publisher" / "scripts" / "software_factory_commit.py"
spec = importlib.util.spec_from_file_location("software_factory_commit", MODULE_PATH)
sfc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sfc)


def test_profile_display_name_from_active_profile():
    assert (
        sfc.profile_display_name(env={"HERMES_PROFILE": "worker"})
        == "Software Factory Worker"
    )


def test_profile_display_name_from_legacy_prefixed_worker_profile():
    assert (
        sfc.profile_display_name(env={"HERMES_PROFILE": "softwarefactoryworker"})
        == "Software Factory Worker"
    )


def test_profile_display_name_explicit_override_takes_precedence():
    assert (
        sfc.profile_display_name(
            env={
                "HERMES_PROFILE": "worker",
                "SOFTWARE_FACTORY_PROFILE_DISPLAY_NAME": "Custom Worker Name",
            }
        )
        == "Custom Worker Name"
    )


def test_commit_message_appends_active_profile_coauthor_trailer():
    message = sfc.with_profile_coauthor("chore: publish generated profile", "Software Factory Worker")
    assert message.endswith("\n")
    assert "Co-authored-by: Software Factory Worker <jack@lomz.me>" in message
    assert message.count("Co-authored-by:") == 1


def test_commit_message_does_not_duplicate_trailer():
    original = (
        "chore: publish generated profile\n\n"
        "Co-authored-by: Software Factory Worker <jack@lomz.me>\n"
    )
    assert sfc.with_profile_coauthor(original, "Software Factory Worker") == original


def test_git_author_env_is_scoped_to_invocation(monkeypatch):
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Someone Else")
    env = sfc.git_author_env(os.environ)
    assert env["GIT_AUTHOR_NAME"] == "Jack Michaud"
    assert env["GIT_AUTHOR_EMAIL"] == "jack@lomz.me"
    assert env["GIT_COMMITTER_NAME"] == "Jack Michaud"
    assert env["GIT_COMMITTER_EMAIL"] == "jack@lomz.me"
    # The helper returns an env copy for git subprocesses only; it does not
    # mutate process/global git configuration used by non-Software-Factory commits.
    assert os.environ["GIT_AUTHOR_NAME"] == "Someone Else"


def test_dry_run_reports_author_and_profile_coauthor(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    monkeypatch.setenv("HERMES_PROFILE", "worker")
    result = sfc.commit_changes(repo, "chore: publish", ["README.md"], dry_run=True)
    assert result["author"] == "Jack Michaud <jack@lomz.me>"
    assert result["coauthor"] == "Co-authored-by: Software Factory Worker <jack@lomz.me>"
    assert "--author=Jack Michaud <jack@lomz.me>" in result["command"]
    assert "Co-authored-by: Software Factory Worker <jack@lomz.me>" in result["message"]


def test_real_git_commit_uses_jack_author_and_profile_coauthor(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    monkeypatch.setenv("HERMES_PROFILE", "worker")

    result = sfc.commit_changes(repo, "chore: test software factory commit", [])

    assert result["author"] == "Jack Michaud <jack@lomz.me>"
    author = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%an <%ae>"], cwd=repo, text=True
    ).strip()
    body = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%B"], cwd=repo, text=True
    )
    assert author == "Jack Michaud <jack@lomz.me>"
    assert "Co-authored-by: Software Factory Worker <jack@lomz.me>" in body

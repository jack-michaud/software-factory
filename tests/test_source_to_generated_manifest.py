import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "publisher/scripts"))

from simple_yaml import load_yaml_document


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_repo_config(root: Path) -> dict:
    return load_yaml_document((root / "publisher/config/public-repos.yaml").read_text())["roles"]


def load_script_module(root: Path, relative: str):
    path = root / relative
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_repo_config_includes_worker_profile_and_matches_expected_inventory():
    root = Path(__file__).resolve().parents[1]
    roles = public_repo_config(root)

    assert list(roles) == ["worker"]
    assert roles["worker"]["repo"] == "software-factory-worker-profile"
    assert roles["worker"]["source_dir"] == "profiles/worker"
    assert roles["worker"]["validation_profile"] == "runtime-role"
    assert roles["worker"]["install_name"] == "worker"

    for role, cfg in roles.items():
        distribution = load_yaml_document((root / cfg["source_dir"] / "distribution.yaml").read_text())
        assert distribution["source"]["role"] == role
        assert distribution["source"]["generated_repo"] == cfg["repo"]


def test_public_repo_path_filter_rejects_private_paths_and_key_material():
    root = Path(__file__).resolve().parents[1]
    generator = load_script_module(root, "publisher/scripts/generate_public_repos.py")
    allowed_root = {"README.md", "distribution.yaml"}
    allowed_dirs = {"skills/", "templates/", "scripts/"}

    assert generator.rel_is_safe("templates/release-notes.md", allowed_root, allowed_dirs)
    assert not generator.rel_is_safe("templates/.env", allowed_root, allowed_dirs)
    assert not generator.rel_is_safe("scripts/deploy.pem", allowed_root, allowed_dirs)
    assert not generator.rel_is_safe("skills/../../auth.json", allowed_root, allowed_dirs)
    assert not generator.rel_is_safe("sessions/transcript.json", allowed_root, allowed_dirs)


def test_manifest_hashes_generated_files_after_readme_transformations():
    root = Path(__file__).resolve().parents[1]
    roles = public_repo_config(root)
    subprocess.run([sys.executable, str(root / "publisher/scripts/generate_public_repos.py")], check=True)

    manifest = json.loads((root / "source-to-generated-manifest.json").read_text())
    entries = manifest["source_to_generated"]

    manifest_repos = {repo["repo"] for repo in manifest["repos"]}
    expected_repos = {cfg["repo"] for cfg in roles.values()}
    assert manifest_repos == expected_repos == {"software-factory-worker-profile"}

    readme_entries = [
        entry for entry in entries
        if entry["generated"].endswith("/README.md") and entry.get("source", "").endswith("/README.md")
    ]
    assert len(readme_entries) == len(roles) == 1
    assert {
        entry["generated"].split("/")[1]
        for entry in readme_entries
    } == expected_repos

    for entry in entries:
        generated = root / entry["generated"]
        assert generated.exists(), entry
        if "sha256" in entry:
            assert entry.get("sha256") == sha256(generated), entry
        if "generated_sha256" in entry:
            assert entry.get("generated_sha256") == sha256(generated), entry
        if "sha256" not in entry and "generated_sha256" not in entry:
            assert entry.get("content_relation") == "generator_mutation", entry
        if "source" in entry and "source_sha256" in entry:
            source = root / entry["source"]
            assert source.exists(), entry
            assert entry.get("source_sha256") == sha256(source), entry

    for entry in readme_entries:
        readme = (root / entry["generated"]).read_text()
        assert "Generated public repository shape" in readme
        assert "--name worker" in readme
        assert "README install docs injected during generation" in entry.get("transformations", [])
        assert entry["sha256"] != entry["source_sha256"]

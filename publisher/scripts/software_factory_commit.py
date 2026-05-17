#!/usr/bin/env python3
"""Commit helper for Software Factory automation-created git commits.

The helper intentionally scopes Jack Michaud authorship to callers that opt into
Software Factory publication/automation. It does not change global or repo-local
git config, so unrelated commits keep their existing behavior.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

SOFTWARE_FACTORY_AUTHOR_NAME = "Jack Michaud"
SOFTWARE_FACTORY_AUTHOR_EMAIL = "jack@lomz.me"
SOFTWARE_FACTORY_AUTHOR = (
    f"{SOFTWARE_FACTORY_AUTHOR_NAME} <{SOFTWARE_FACTORY_AUTHOR_EMAIL}>"
)

PROFILE_PREFIX_DISPLAY_NAMES = {
    "metasoftwarefactory": "Meta Software Factory",
    "softwarefactory": "Software Factory",
}

PROFILE_ROLE_DISPLAY_NAMES = {
    "worker": "Worker",
}

PROFILE_DISPLAY_NAMES = {
    f"{prefix}{role}": f"{prefix_display} {role_display}"
    for prefix, prefix_display in PROFILE_PREFIX_DISPLAY_NAMES.items()
    for role, role_display in PROFILE_ROLE_DISPLAY_NAMES.items()
}


def _title_from_profile(profile_name: str) -> str:
    for prefix, prefix_display in PROFILE_PREFIX_DISPLAY_NAMES.items():
        suffix = profile_name.removeprefix(prefix)
        if suffix != profile_name:
            if not suffix:
                return prefix_display
            return f"{prefix_display} {suffix.title()}"
    return "Software Factory " + profile_name.title()


def profile_display_name(
    profile_name: str | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    """Resolve the active Software Factory profile display name.

    SOFTWARE_FACTORY_PROFILE_DISPLAY_NAME is an explicit override for tests or
    wrappers. Otherwise HERMES_PROFILE is mapped from the canonical profile name.
    """
    env = env or os.environ
    explicit = (env.get("SOFTWARE_FACTORY_PROFILE_DISPLAY_NAME") or "").strip()
    if explicit:
        return explicit
    profile = (profile_name or env.get("HERMES_PROFILE") or "").strip()
    if not profile:
        raise ValueError(
            "active profile is unknown; set HERMES_PROFILE or "
            "SOFTWARE_FACTORY_PROFILE_DISPLAY_NAME"
        )
    normalized = profile.lower().replace("-", "").replace("_", "")
    return PROFILE_DISPLAY_NAMES.get(normalized, _title_from_profile(profile))


def coauthor_trailer(display_name: str) -> str:
    return f"Co-authored-by: {display_name} <{SOFTWARE_FACTORY_AUTHOR_EMAIL}>"


def with_profile_coauthor(message: str, display_name: str) -> str:
    """Append the Software Factory active-profile co-author trailer once."""
    normalized = message.rstrip()
    trailer = coauthor_trailer(display_name)
    if trailer in normalized.splitlines():
        return normalized + "\n"
    return f"{normalized}\n\n{trailer}\n"


def git_author_env(base_env: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return environment forcing author/committer for this git invocation only."""
    env = dict(base_env or os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": SOFTWARE_FACTORY_AUTHOR_NAME,
            "GIT_AUTHOR_EMAIL": SOFTWARE_FACTORY_AUTHOR_EMAIL,
            "GIT_COMMITTER_NAME": SOFTWARE_FACTORY_AUTHOR_NAME,
            "GIT_COMMITTER_EMAIL": SOFTWARE_FACTORY_AUTHOR_EMAIL,
        }
    )
    return env


def build_commit_command(repo: Path, message_file: Path, paths: Sequence[str]) -> list[str]:
    command = [
        "git",
        "-C",
        str(repo),
        "-c",
        f"user.name={SOFTWARE_FACTORY_AUTHOR_NAME}",
        "-c",
        f"user.email={SOFTWARE_FACTORY_AUTHOR_EMAIL}",
        "commit",
        f"--author={SOFTWARE_FACTORY_AUTHOR}",
        "-F",
        str(message_file),
    ]
    command.extend(paths)
    return command


def commit_changes(
    repo: Path,
    message: str,
    paths: Sequence[str],
    profile_name: str | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    display_name = profile_display_name(profile_name)
    final_message = with_profile_coauthor(message, display_name)
    message_file = repo / ".git" / "SOFTWARE_FACTORY_COMMIT_EDITMSG"
    command = build_commit_command(repo, message_file, paths)
    result = {
        "repo": str(repo),
        "author": SOFTWARE_FACTORY_AUTHOR,
        "coauthor": coauthor_trailer(display_name),
        "paths": list(paths),
        "dry_run": dry_run,
        "command": command[:],
        "message": final_message,
    }
    if dry_run:
        return result
    message_file.write_text(final_message, encoding="utf-8")
    try:
        subprocess.run(command, check=True, env=git_author_env())
    finally:
        try:
            message_file.unlink()
        except FileNotFoundError:
            pass
    result["commit"] = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    return result


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Software Factory automation commits with Jack "
        "Michaud author and active-profile co-author trailer."
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--profile", help="Active Hermes profile name override")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", help="Paths passed to git commit")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    result = commit_changes(
        repo=args.repo,
        message=args.message,
        paths=args.paths,
        profile_name=args.profile,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

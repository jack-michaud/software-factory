# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Repository overview

This is the public Software Factory profiles monorepo. It contains shared docs, publishing/generation scripts, tests, and metadata for six role profile distributions:

- `pm`
- `builder`
- `orchestrator`
- `reviewer`
- `publisher`
- `docs`

The role profile directories under `profiles/` are git submodules pointing at separate public profile repositories. Treat those directories as independent repositories with their own git state.

## Important boundaries

Do not add or publish runtime/private material. The public/private boundary intentionally excludes credentials, runtime state, logs, memories, sessions, Kanban databases/workspaces, sprite credentials, SSH keys, OAuth tokens, API keys, private Obsidian notes, and user-owned `.env` files.

Repository deny/ignore patterns include:

- `.env`, `auth.json`, `state.db`, `kanban.db`
- `sessions/`, `memories/`, `logs/`, `local/`, `.ssh/`
- key/certificate material such as `*.pem`, `*.key`, `*.p12`, `*.pfx`

Only publish files that are allowlisted by `publisher/config/allowlist.yaml` and owned by each profile's `distribution.yaml`.

## Submodules

Use recursive clone/update when profile contents are needed:

```bash
git submodule update --init --recursive
```

Refresh submodule pins from their `main` branches with:

```bash
git submodule update --remote --merge --recursive
```

When modifying a profile under `profiles/<role>`, remember it is a submodule. Commit/push profile changes in that submodule repository first, then update and commit the parent repo's submodule pointer if appropriate.

## Key files and directories

- `README.md` - monorepo overview and submodule map
- `docs/` - public documentation, especially install/publishing/security guidance
- `distribution-set.yaml` - top-level distribution metadata and role inventory
- `profiles/<role>/distribution.yaml` - Hermes distribution manifest for each role
- `profiles/<role>/SOUL.md` - role behavior/persona contract
- `shared/` - shared skills and snippets used by profile distributions
- `publisher/config/public-repos.yaml` - generated public repo inventory
- `publisher/config/allowlist.yaml` - public file allowlist
- `publisher/scripts/` - generation, validation, scanning, publishing, release, and commit helpers
- `tests/` - pytest coverage for manifests, generation reproducibility, public/private boundaries, and commit policy

## Common validation commands

Run these from the repository root:

```bash
python3 publisher/scripts/generate_public_repos.py
python3 publisher/scripts/validate_monorepo.py
python3 publisher/scripts/compare_generated_output.py
python3 publisher/scripts/scan_generated_output.py
python3 -m py_compile publisher/scripts/*.py
python3 -m pytest
```

For a minimal dependency setup:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

The scripts prefer PyYAML if installed but include `publisher/scripts/simple_yaml.py` for the repository's simple source-controlled YAML shapes.

## Generated/local artifacts

Generation creates local validation artifacts that are ignored by git, including:

- `generated/`
- `source-to-generated-manifest.json`
- `dry-run-publish-approval-artifact.json`
- `validation-report.json`
- `secret-scan-report.json`
- `generated-diff-summary.json`

Do not commit these unless project guidance changes.

## Publishing and commit policy

Publishing is designed to be dry-run/approval gated. Do not create or push public repos without explicit human approval.

Software Factory automation-created commits must use `publisher/scripts/software_factory_commit.py` or an equivalent wrapper that preserves the documented author/trailer policy:

- author/committer: `Jack Michaud <jack@lomz.me>`
- exactly one `Co-authored-by: <active profile display name> <jack@lomz.me>` trailer

Dry-run example:

```bash
HERMES_PROFILE=softwarefactorybuilder \
  python3 publisher/scripts/software_factory_commit.py \
  --repo . \
  --message "chore: verify software factory authorship" \
  --dry-run
```

See `docs/publishing.md` and `tests/test_software_factory_commit.py` for details.

## Development notes

- Keep public docs and role README/install guidance free of secrets and private paths.
- If adding files to a role distribution, update that role's `distribution.yaml` and ensure paths pass `publisher/config/allowlist.yaml`.
- If adding/changing roles or generated repos, update `distribution-set.yaml`, `publisher/config/public-repos.yaml`, docs, and tests together.
- Validate source-to-generated provenance after generator changes; README files are intentionally transformed during generation and their manifest entries must record that transformation.

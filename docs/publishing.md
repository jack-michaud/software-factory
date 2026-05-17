# Publishing

The monorepo keeps shared publishing scripts, configuration, docs, tests, and generation metadata as normal tracked files. The worker profile tree under `profiles/worker` is a git submodule that points at the separate public worker profile repository:

- `profiles/worker` -> https://github.com/jack-michaud/software-factory-worker-profile.git (`main`)

This layout avoids duplicated profile directories that can drift from the published profile repo. Before validating or generating, ensure the submodule is present:

```bash
git submodule update --init --recursive
```

To update the submodule pin after the worker repo moves forward, run:

```bash
git submodule update --remote --merge --recursive
```

## Reproducible local validation

The publisher scripts run on bare Python 3 and do not require PyYAML for the simple source-controlled YAML shapes in `publisher/config/*.yaml` and profile `distribution.yaml` files. They prefer PyYAML when available, then fall back to `publisher/scripts/simple_yaml.py`.

For unit tests, create an isolated development environment from the source-controlled requirements file:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Canonical generation and validation commands:

```bash
python3 publisher/scripts/generate_public_repos.py
python3 publisher/scripts/validate_monorepo.py
python3 publisher/scripts/compare_generated_output.py
python3 publisher/scripts/scan_generated_output.py
python3 -m py_compile publisher/scripts/*.py
python3 -m pytest
```

Publisher follow-through: after approved public profile repo changes are pushed, update the monorepo submodule pointer to the pushed public repo HEAD, validate the monorepo state, and publish the pointer update unless the task explicitly scopes it out or credentials/authority block it.

## Software Factory automation commit authorship

All Software Factory automation-created git commits must be created with `publisher/scripts/software_factory_commit.py` or an equivalent wrapper that uses the same policy:

- author: `Jack Michaud <jack@lomz.me>`
- committer for the automated invocation: `Jack Michaud <jack@lomz.me>`
- exactly one commit-message trailer: `Co-authored-by: <active profile display name> <jack@lomz.me>`

The helper resolves the active profile display name from `SOFTWARE_FACTORY_PROFILE_DISPLAY_NAME` or `HERMES_PROFILE`. For the single worker profile, use `worker` or set `SOFTWARE_FACTORY_PROFILE_DISPLAY_NAME="Software Factory Worker"` explicitly.

The helper scopes the author/committer via per-command environment and `git -c` arguments; it never writes global git config or repo-local config, so non-Software-Factory commit behavior is unchanged.

Dry-run verification example:

```bash
HERMES_PROFILE=worker \
  python3 publisher/scripts/software_factory_commit.py \
  --repo . \
  --message "chore: verify software factory authorship" \
  --dry-run
```

Maintainers can verify the implementation and distribution guidance in:

- `publisher/scripts/software_factory_commit.py`
- `tests/test_software_factory_commit.py`
- `docs/publishing.md`

Public prototype documentation. Runtime credentials, local state, private Obsidian notes, Kanban databases, and sprite credentials are intentionally excluded.

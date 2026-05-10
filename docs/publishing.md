# Publishing

The monorepo keeps shared publishing scripts, configuration, docs, tests, and generation metadata as normal tracked files. Role profile trees under `profiles/` are git submodules that point at the separate public profile repositories:

- `profiles/pm` -> https://github.com/jack-michaud/software-factory-pm-profile.git (`main`)
- `profiles/builder` -> https://github.com/jack-michaud/software-factory-builder-profile.git (`main`)
- `profiles/orchestrator` -> https://github.com/jack-michaud/software-factory-orchestrator-profile.git (`main`)
- `profiles/reviewer` -> https://github.com/jack-michaud/software-factory-reviewer-profile.git (`main`)
- `profiles/publisher` -> https://github.com/jack-michaud/software-factory-publisher-profile.git (`main`)
- `profiles/docs` -> https://github.com/jack-michaud/software-factory-docs-profile.git (`main`)

This layout avoids duplicated role directories that can drift from the published role repos. Before validating or generating, ensure submodules are present:

```bash
git submodule update --init --recursive
```

To update submodule pins after role repos move forward, run:

```bash
git submodule update --remote --merge --recursive
```

Publisher follow-through: after approved public profile repo changes are pushed, the publisher should update these monorepo submodule pointers to the pushed public repo HEADs, validate the monorepo state, and publish the pointer update unless the task explicitly scopes it out or credentials/authority block it.

## Software Factory automation commit authorship

All Software Factory automation-created git commits must be created with `publisher/scripts/software_factory_commit.py` or an equivalent wrapper that uses the same policy:

- author: `Jack Michaud <jack@lomz.me>`
- committer for the automated invocation: `Jack Michaud <jack@lomz.me>`
- exactly one commit-message trailer: `Co-authored-by: <active profile display name> <jack@lomz.me>`

The helper resolves the active profile display name from `SOFTWARE_FACTORY_PROFILE_DISPLAY_NAME` or `HERMES_PROFILE`. Canonical examples include:

- `softwarefactorypm` -> `Co-authored-by: Software Factory PM <jack@lomz.me>`
- `softwarefactorybuilder` -> `Co-authored-by: Software Factory Builder <jack@lomz.me>`
- `softwarefactoryreviewer` -> `Co-authored-by: Software Factory Reviewer <jack@lomz.me>`
- `softwarefactorypublisher` -> `Co-authored-by: Software Factory Publisher <jack@lomz.me>`

The helper scopes the author/committer via per-command environment and `git -c` arguments; it never writes global git config or repo-local config, so non-Software-Factory commit behavior is unchanged.

Dry-run verification example:

```bash
HERMES_PROFILE=softwarefactorybuilder \
  python3 publisher/scripts/software_factory_commit.py \
  --repo . \
  --message "chore: verify software factory authorship" \
  --dry-run
```

Maintainers can verify the implementation and distribution guidance in:

- `publisher/scripts/software_factory_commit.py`
- `tests/test_software_factory_commit.py`
- `docs/publishing.md`
- `profiles/publisher` publisher-profile guidance

Public prototype documentation. Runtime credentials, local state, private Obsidian notes, Kanban databases, and sprite credentials are intentionally excluded.

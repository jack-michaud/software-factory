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

Public prototype documentation. Runtime credentials, local state, private Obsidian notes, Kanban databases, and sprite credentials are intentionally excluded.

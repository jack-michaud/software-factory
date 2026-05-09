# Software Factory Profiles Monorepo

This repository contains the public Software Factory profile distribution source plus shared publishing scripts, tests, docs, and generation metadata.

The role profile directories under `profiles/` are git submodules that point at the separate published profile repositories. This avoids duplicated role profile trees that can drift from the public role repos while keeping shared monorepo assets as normal files.

## Clone with profile submodules

Use a recursive clone when you need the profile contents locally:

```bash
git clone --recurse-submodules https://github.com/jack-michaud/software-factory.git
```

If you already cloned without submodules, initialize them with:

```bash
git submodule update --init --recursive
```

To refresh submodules to the configured `main` branches:

```bash
git submodule update --remote --merge --recursive
```

## Published profile repositories

| Path | Repository | Branch |
| --- | --- | --- |
| `profiles/pm` | https://github.com/jack-michaud/software-factory-pm-profile.git | `main` |
| `profiles/builder` | https://github.com/jack-michaud/software-factory-builder-profile.git | `main` |
| `profiles/orchestrator` | https://github.com/jack-michaud/software-factory-orchestrator-profile.git | `main` |
| `profiles/reviewer` | https://github.com/jack-michaud/software-factory-reviewer-profile.git | `main` |
| `profiles/publisher` | https://github.com/jack-michaud/software-factory-publisher-profile.git | `main` |
| `profiles/docs` | https://github.com/jack-michaud/software-factory-docs-profile.git | `main` |

Public/private boundary: credentials, runtime state, logs, memories, sessions, Kanban databases/workspaces, sprite credentials, SSH keys, OAuth tokens, API keys, and private Obsidian notes are not included.

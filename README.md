# Software Factory Worker Profile Monorepo

This repository contains the public Software Factory worker profile distribution source plus shared publishing scripts, tests, and metadata.

The worker profile directory under `profiles/` is a git submodule that points at the separate published profile repository. This avoids duplicated profile trees that can drift from the public repo while keeping shared monorepo assets as normal files.

## Clone with profile submodule

Use a recursive clone when you need the profile contents locally:

```bash
git clone --recurse-submodules https://github.com/jack-michaud/software-factory.git
```

If you already cloned without submodules, initialize it with:

```bash
git submodule update --init --recursive
```

To refresh the submodule to its configured `main` branch:

```bash
git submodule update --remote --merge --recursive
```

## Published profile repository

| Path | Repository | Branch |
| --- | --- | --- |
| `profiles/worker` | https://github.com/jack-michaud/software-factory-worker-profile.git | `main` |

Install after publication:

```bash
hermes profile install https://github.com/jack-michaud/software-factory-worker-profile.git --name worker
```

Public/private boundary: credentials, runtime state, logs, memories, sessions, Kanban databases/workspaces, sprite credentials, SSH keys, OAuth tokens, API keys, and private Obsidian notes are not included.

## Documentation

- [Install](docs/install.md)
- [Publishing](docs/publishing.md)
- [Public vs private boundary](docs/public-vs-private.md)
- [Security](docs/security.md)

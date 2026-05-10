# Install

Clone the Software Factory monorepo with its role profile submodules when you want a complete local checkout:

```bash
git clone --recurse-submodules https://github.com/jack-michaud/software-factory.git
```

If you already cloned the repository without submodules, run this from the repository root:

```bash
git submodule update --init --recursive
```

The individual public profile repositories remain installable directly with Hermes from their own GitHub URLs, for example:

```bash
hermes profile install https://github.com/jack-michaud/software-factory-pm-profile.git --name softwarefactorypm
```

Public prototype documentation. Runtime credentials, local state, private Obsidian notes, Kanban databases, and sprite credentials are intentionally excluded.


## Optional docs deployment target

PM and docs profile distributions declare `SOFTWARE_FACTORY_DOCS_SPRITE_NAME` in `distribution.yaml` as an optional env var for deployed docs work. Set it in each installed profile's user-owned `.env` only when docs publication/deployment should target a dedicated docs sprite. For this environment, use the non-secret value:

```bash
SOFTWARE_FACTORY_DOCS_SPRITE_NAME=hermes-sf-docs
```

Hermes profile distribution installs/updates own files listed in `distribution.yaml`; `.env` remains user-owned runtime state and must not be overwritten. Keep non-secret examples in README/install guidance or allowlisted `.env.EXAMPLE` files, never in private `.env` output.

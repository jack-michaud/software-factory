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

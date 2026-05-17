# Install

Clone the Software Factory monorepo with its worker profile submodule when you want a complete local checkout:

```bash
git clone --recurse-submodules https://github.com/jack-michaud/software-factory.git
```

If you already cloned the repository without submodules, run this from the repository root:

```bash
git submodule update --init --recursive
```

The public worker profile repository is installable directly with Hermes:

```bash
hermes profile install https://github.com/jack-michaud/software-factory-worker-profile.git --name worker
```

For local testing from this checkout:

```bash
hermes profile install ./profiles/worker --name worker --yes
```

Public prototype documentation. Runtime credentials, local state, private Obsidian notes, Kanban databases, user-owned `.env` files, and sprite credentials are intentionally excluded.

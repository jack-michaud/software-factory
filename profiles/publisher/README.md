# softwarefactorypublisher profile

This is a local-installable role distribution root for current Hermes. It is generated/maintained from the Software Factory profiles monorepo prototype.

Install locally for testing:

```bash
hermes profile install /path/to/software-factory-profiles/profiles/publisher --name softwarefactorypublisher-monorepo-test --yes
```

Role boundary: Validates, generates, diffs, and publishes generated public profile repos only after explicit human approval; never mutates sprites.

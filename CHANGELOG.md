# Changelog

## Unreleased

- Added approval-gate dependency doctrine to PM/orchestrator role guidance and shared Kanban workflow guidance so approval/decision gates for blocked seeds are not created as children of the blocked tasks they must unblock.
- Documented PM blocked-work escalation behavior: durable Kanban tasks with stable idempotency keys replace draft-only blocked artifacts; blocked/triaged tasks now require explicit blockers, missing evidence, unblock conditions, downstream acceptance criteria, and rollback/evidence requirements where applicable.
- Documented the builder/reviewer blocker declaration pattern and the PM-owned two-cycle unblock loop before orchestrator or human escalation.
- Recorded the public outcome for the PM guidance rollout: the remediated PM profile guidance was reviewer-approved, published to the public PM profile repository, reflected by the Software Factory monorepo `profiles/pm` pointer, and installed into production and meta profile sets with verification.

## 0.1.0

- Initial local dry-run publishing prototype.

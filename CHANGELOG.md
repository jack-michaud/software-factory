# Changelog

## Unreleased

- Collapsed the Software Factory distribution inventory to the single `worker` profile.
- Added `software-factory-kanban-workflow` with durable Kanban context, project reminder propagation, bounded remediation retries, escalation, and shortcut tech-debt capture.
- Preserved remote Sprite development guidance in the worker profile.
- Updated generation, validation, install, publishing, and tests for the `software-factory-worker-profile` public repository.
- Remediated remote-sprite copyable PM seed examples so task-level startup skills stay unset by default and `remote-sprite-development` is used only after exact target-profile loadability verification, otherwise the contract is inlined.
- Added PM forced-skill task-writing guidance: PM-created Kanban tasks now default to no task-level forced skills, forbid role/project/built-in forced skills by default, and require target-profile loadability evidence plus fallback/remediation behavior for any startup skill exception.
- Documented the Software Factory automation commit authorship convention: Jack Michaud author/committer, exactly one active-profile co-author trailer, canonical profile examples, and maintainer verification pointers.
- Added approval-gate dependency doctrine to PM/orchestrator role guidance and shared Kanban workflow guidance so approval/decision gates for blocked seeds are not created as children of the blocked tasks they must unblock.
- Documented PM blocked-work escalation behavior: durable Kanban tasks with stable idempotency keys replace draft-only blocked artifacts; blocked/triaged tasks now require explicit blockers, missing evidence, unblock conditions, downstream acceptance criteria, and rollback/evidence requirements where applicable.
- Documented the builder/reviewer blocker declaration pattern and the PM-owned two-cycle unblock loop before orchestrator or human escalation.
- Recorded the public outcome for the PM guidance rollout: the remediated PM profile guidance was reviewer-approved, published to the public PM profile repository, reflected by the Software Factory monorepo `profiles/pm` pointer, and installed into production and meta profile sets with verification.

## 0.1.0

- Initial local dry-run publishing prototype.

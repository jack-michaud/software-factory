---
name: kanban-profile-workflow
description: Public multi-profile Kanban workflow conventions.
version: 0.1.1
---
# Kanban Profile Workflow

Use Kanban for durable cross-profile work. Keep PM, builder, orchestrator, reviewer, publisher, installer/profile-mutation, and docs responsibilities separate. Generated public artifacts must be independently validated before publication.

## Approval/Decision Gates for Blocked Seeds

Approval or decision gates that unblock blocked work must not depend on the blocked task. If original work is blocked waiting for human/orchestrator approval, target-coordinate confirmation, credential-scope approval, or another external/manual decision, create the approval/decision task as an unparented sibling, or as a parent/unblocker of future execution tasks. Do not make the approval gate a child of the blocked seed.

Dependency direction matters:

- Use child dependencies for work that should wait until the parent is completed.
- Use parent dependencies for concrete work that must finish before another task can run.
- Use `blocked` status/commentary for external/manual blockers when no concrete Kanban task exists yet.

After approval, record the decision on the blocked seed, then unblock/re-dispatch the seed or have PM create the execution graph with the approval gate as a dependency where appropriate. If an accidental deadlocked dependent gate is created, comment/supersede it, create the correctly unparented/sibling approval gate, and preserve the lesson in source-controlled profile guidance.

## Concrete Dependencies Instead of Stranded Blocking

When a profile is waiting on concrete Kanban work, do not leave the waiting task in `blocked` as the normal state. Create or identify the remediation, reviewer, approval, install/update, docs, or other unblocker task; link that task as a parent dependency of the waiting task; then return the waiting task to todo/ready so the board can re-dispatch it automatically when all parents are GREEN/done.

Use `blocked` only for external/manual blockers where no concrete Kanban task exists yet, such as missing credentials, unknown authority, unavailable repo/distribution, or human approval that has not yet been captured as a task. If an external/manual blocker can be represented as an unblocker Kanban task, create or link that task instead of stranding downstream work.

This preserves Software Factory role boundaries: PM/orchestrator routes durable work, builders edit source, reviewers gate, publishers publish authorized public artifacts, installer/profile-mutation tasks perform installs or runtime profile updates, and docs tasks produce release notes/documentation.

---
name: kanban-profile-workflow
description: Public multi-profile Kanban workflow conventions.
version: 0.1.3
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

This preserves Software Factory role boundaries: PM/orchestrator routes durable work, builders edit source, reviewers gate, publishers publish authorized public artifacts, installer/profile-mutation tasks perform installs and runtime profile updates, and docs tasks produce release notes/documentation updates.

## Source-update Evidence Gates

For source-update tasks, PM should provide a Source Map naming the canonical public source coordinates: superproject, role/profile source repos, shared source locations, related profile repos needed for coverage, and any prepared local clone/worktree paths. The reusable local convention is `/home/sprite/projects/<repo-name>` for canonical clones and `/home/sprite/worktrees/<repo-name>/<task-id>-<short-slug>` for task-specific worktrees.

Builders must use the Source Map-provided standard repo/worktree path when present. The Kanban workspace remains scratch/evidence storage; source edits happen in the named repo/worktree on a task/work-named branch. If no standard path is supplied, preserve fallback behavior by cloning or fetching canonical public repositories into the Kanban task workspace, then creating a task/work-named branch before editing. Installed runtime directories such as `~/.hermes/profiles/*`, private local profile state, logs, memories, raw Kanban databases/workspaces, and secrets are not canonical source or final-state evidence.

Reviewer and publisher gates should require a handoff that names repo URLs, local repo/worktree paths, branch names, commit hashes, changed files, diff or diff-stat output, validation output, target-profile coverage matrix, publish/push status, and whether superproject submodule pointers or generated profile repos changed. If commits are not pushed, require either an approved source-controlled patch/diff bundle or a PM-named reviewer-accessible standard worktree path.

Reviewers should inspect the named standard worktree/path or public remote coordinates from the handoff. Do not use private installed profile state, secrets, logs, memories, raw Kanban databases/workspaces, or runtime profile directories as source truth. If a canonical Source Map entry, access path, branch/worktree authority, or write permission is missing or conflicting, block with the missing public coordinate and unblock condition instead of accepting local-only profile-store changes.

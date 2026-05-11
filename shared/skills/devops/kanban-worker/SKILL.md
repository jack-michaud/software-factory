---
name: kanban-worker
description: Public Kanban worker lifecycle and handoff conventions.
version: 0.1.1
---
# Kanban Worker

Orient with the assigned task, work only in the provided workspace, leave evidence, and complete with structured summary and metadata. Block rather than guessing when credentials, human approval, or missing private context are required.

## Source-update workspace convention

For source-update tasks, treat the PM-provided Source Map as the authority for repository coordinates and local paths:

- When the Source Map names a standard local clone, expect the canonical clone at `/home/sprite/projects/<repo-name>`.
- When the Source Map names a task worktree, expect source edits to happen in `/home/sprite/worktrees/<repo-name>/<task-id>-<short-slug>` on the task/work-named branch.
- Keep the Kanban task workspace as scratch/evidence storage. Do not treat old scratch clones, installed profile directories, runtime state, logs, memories, or raw Kanban databases/workspaces as canonical source.
- If the Source Map does not provide a standard local clone/worktree path, preserve the fallback behavior: clone or fetch the canonical public repository coordinates into the Kanban task workspace before editing, then create a task/work-named branch.
- If a named standard path, repository coordinate, branch/worktree authority, or write permission is missing or conflicting, block with the exact missing public coordinate and unblock condition instead of substituting local profile state.

Source-update handoffs must leave reviewer/publisher evidence: repo URL, local repo/worktree path, branch, commit hash, changed files, diff or diff-stat, validation output, target-profile coverage, publish/push status, and whether superproject submodule pointers or generated profile repos changed. If commits are not pushed, the handoff must name either an approved source-controlled patch/diff bundle or a reviewer-accessible standard local worktree path explicitly provided by PM.

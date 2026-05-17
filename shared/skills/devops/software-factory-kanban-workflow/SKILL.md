---
name: software-factory-kanban-workflow
description: Single-profile Software Factory Kanban workflow with durable task context, reminder propagation, bounded remediation retries, escalation, and shortcut tech-debt capture.
version: 0.1.0
---
# Software Factory Kanban Workflow

Use Kanban as the durable control plane for Software Factory work. Important state must live in tasks, comments, metadata, commits, or other durable evidence; do not rely on transient chat context alone.

## Task creation and reminder propagation

When creating tasks, include enough context for a fresh worker to continue without private memory:

- original request and acceptance criteria,
- workspace/repository/branch/locality instructions,
- required skills and project-specific reminder skills,
- dependencies, blockers, attempt count, and related task ids,
- expected evidence and validation commands.

If a board, project, or parent task has a `Remember` section or a project-specific remember skill, propagate it into every new task for that board. Copy the reminder text when necessary, or explicitly require the downstream worker to load the named skill. Keep project-specific details, such as EC2/SSM commands, delegated execution commands, branch names, or service paths, in the project reminder skill rather than in this generic workflow skill.

## Fixable failures and bounded retries

When you encounter a blocker or acceptance-criteria failure, first ask whether a worker can reasonably fix it with another concrete task.

If yes:

1. Create a remediation task assigned to the default/worker profile.
2. Include all relevant context and reminders from the original task.
3. State the attempt count for this issue family.
4. Link prior attempt task ids and summarize what they tried.
5. Give clear acceptance criteria and evidence requirements.
6. Complete the current task with a handoff to the remediation task instead of marking it blocked.

After the third failed remediation attempt for the same issue family, stop creating automatic follow-ups. Mark the work blocked or escalate with a concise summary of all attempts, evidence, remaining failure, and why human help or external authority is required.

Block immediately, rather than retrying, when progress requires missing credentials, explicit human approval, unsafe access, unavailable external systems, or authority that the task does not grant.

## Shortcuts and tech debt

Before completing a task, ask: "Did I take any shortcuts?"

If yes, and the shortcut is acceptable for prototype progress:

- create an unassigned tech-debt Kanban task,
- link the original task,
- describe the shortcut, risk, cleanup path, and suggested priority,
- do not let the tech-debt task block the original task unless the shortcut creates major future risk.

## Completion evidence

Complete tasks with structured evidence: changed files, commits, commands run, validation output, created follow-up tasks, known limitations, shortcut/tech-debt status, and any remaining risks. For remote Sprite work, also include target locality, checkpoint, verification, and rollback evidence from `remote-sprite-development`.

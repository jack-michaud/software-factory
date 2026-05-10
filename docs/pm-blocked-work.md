# PM Blocked Work and Escalation

This page documents the public Software Factory PM behavior for work that is ready to track but cannot safely proceed because a gate, artifact, or approval is missing.

## Durable tasks instead of draft-only artifacts

When PM work identifies a valid next action that is blocked, gated, or awaiting rollout/docs/install follow-through, the PM must create or link a durable Kanban task with a stable idempotency key. A markdown note, local draft, or advisory-only artifact is not enough because it can hide the next state from the workflow.

The durable task should be triaged or blocked when dispatch would be unsafe. Its thread or handoff should state:

- the blocker or gate in public-safe terms,
- the evidence that is missing,
- the exact condition that will unblock the task,
- the downstream acceptance criteria,
- the owning profile or role expected to act next,
- and rollback or evidence requirements when runtime work is expected.

## Builder and reviewer blocker declarations

Builders and reviewers should make blockers explicit instead of silently stopping at a failed gate. A useful blocker declaration names:

- the required artifact or evidence,
- the role that owns producing it,
- the suspected failure class,
- the validation needed to clear the blocker,
- and any publication, installation, rollback, or runtime-evidence requirement that must be satisfied before downstream work proceeds.

The PM owns the unblock loop. It should inspect only approved public artifacts, public source/distribution roots, and board/task handoffs that are appropriate for public-safe coordination. It must not inspect private profile state, raw databases, local memories, sessions, logs, credentials, or runtime internals.

For the same blocker family, the PM may run at most two PM-builder/reviewer resolution cycles. Each cycle should create or link the needed unblocking task with a stable idempotency key and clear acceptance criteria. If two cycles do not resolve the blocker, PM escalates to the orchestrator or a human with a concise decision request and public-safe evidence.

## Canonical lesson

A recent PM guidance update preserved the role boundary correctly: PM did not perform builder, reviewer, publisher, or runtime mutation work. However, the next task remained draft-only, so the workflow could lose the blocked next state. The corrected behavior is to create durable blocked or triaged Kanban work immediately, attach blocker comments, and create or link the unblocking tasks needed to clear the gate.

## Promotion, publication, and installation outcome

The corrected guidance was promoted into the public PM profile source after validation. The first reviewer gate rejected the initial promoted commit because it covered blocked-by-gates work but did not make automatic follow-up broad enough for known next actions, rollout/docs/install follow-ups, and actionable recommendations.

After remediation, a fresh reviewer gate approved the PM profile update. The public PM profile repository was published on `main` at commit `0c8a31d95c71f070ea155215e9bd907419b270f6`. The public Software Factory monorepo then updated `profiles/pm` to point at that published PM profile commit at monorepo commit `2f412b20777d8ea82962ce112b1d1df7ca769405`.

The rollout was completed by installing the published profile updates into both production and meta profile sets. The rollout included backups before modifying meta profiles, checkpoint discipline around the install, and verification that installed profile sources and distribution-owned files matched the expected public repositories and commits.

## Public/private boundary

Public documentation may describe the behavior, public repositories, public commits, and summarized validation outcomes. It must not publish private task internals, raw board database contents, logs, local workspace paths, profile-local state, credentials, tokens, session data, private notes, private sprite URLs, or checkpoint internals.

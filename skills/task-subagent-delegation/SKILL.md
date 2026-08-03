---
name: task-subagent-delegation
description: Invoke when implementation work is about to start and must go to a subagent rather than the parent / operations work is about to be delegated to a subagent / subagent capability is unavailable and the parent must fall back to direct execution. Provides the always-delegate rule and its boundary against parent-side adjudication, the mode-dependent split of what the subagent executes and what the parent retains, what to convey and what not to convey, and the substrate-absence fallback. Prompt composition is in `skills/task-subagent-prompt/SKILL.md`, spawn parameters in `skills/task-subagent-spawn/SKILL.md`, subagent-side lifecycle labels in `skills/task-subagent-state-labels/SKILL.md`.
layer: L3-task
---

<subagent-delegation>

# Subagent Delegation

<rules>

## Rules

Implementation is always delegated to a subagent. The parent does not implement. Scope = all of Li+: self-evolution PRs in `LI_PLUS_REPO` and work in the user repositories `USER_REPO<N>` alike. No exception by diff size. A rule that branches demands a judgment at its application moment, and simplicity of the rule is the axis this one was decided on (judgment record: wiki `implementation-always-delegated`). Accepted cost: the parent reconstructs context from the report when it adjudicates brake findings, and a one-line change still carries the cost of writing a delegation prompt.
Boundary: the implementation this rule delegates is the issue's change, produced before the PR opens. The parent's revision of brake findings after CI green (`rules/evolution/initiator-autonomy.md` Two-stage brake) sits inside adjudication and is not a re-delegation point. That revision is bounded to the findings: the parent may apply what an adjudicated finding calls for and nothing beyond it. Work outside the findings' reach is implementation and returns to the subagent, whatever its size — otherwise a thin delegated draft followed by a substantial parent rewrite reintroduces under "adjudication" the exception this rule denies on size.

Parent agent delegates implementation and operations to subagent.
Parent retains: issue creation, issue management (non-state lifecycle labels / type / maturity / marker / close), review judgment.
if execution_mode == auto or execution_mode == semi_auto:
  Subagent executes: branch, implementation, commit, push, PR, CI loop.
  Stop condition = `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition.
  Parent retains: brake 1 (and brake 2 when the PR touches L1 Model Layer source) adjudication, self-review, merge decision.
  The two modes share one subagent boundary: what differs is the human PR check
  (`semi_auto` adds one for minor / major per `rules/operations/execution-mode.md`),
  and that is a parent-side gate, not a subagent execution step.
  Subagent does not post the self-review record: it is a PR comment, and the actor
  is fixed by `skills/operations-on-pr-review/SKILL.md` Self-review procedure.
if execution_mode == trigger:
  Subagent executes: branch, implementation, commit, push, PR, CI loop, self-review, merge.
  Stop condition = `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition.

Do not convey: step-by-step procedure, branch name, commit message, intent.
Intent is already in issue body.

</rules>

<responsibilities>

## Responsibilities

Convey to subagent:
issue URL.

If the host adapter auto-loads Li+ layers for subagents, no explicit file reads are needed.
Fallback: also convey rules/*.md and skills/*/SKILL.md paths from LI_PLUS_REPOSITORY.
Detailed parent instructions risk conflicting with operations rules.

Issue body update:
Subagent may update issue body when premise or constraints change during implementation.

Failure reporting:
On failure, subagent writes failure report as issue comment. Format is not specified.

Branch linking: see skills/operations-on-branch/SKILL.md.

</responsibilities>

<autonomy>

## Autonomy

If subagent capability is unavailable:
Parent executes operations directly. All rules still apply.
This is a substrate-absence fallback, not an exception to the always-delegate rule above: it fires on a missing capability, never on a judgment that a change is small enough.

</autonomy>

<adjacent-firing-moments>

## Adjacent firing moments

This skill covers the decision to delegate and the split of what each side executes. Three adjacent moments have their own skills; do not restate them here.

- Composing the delegation prompt (mode-specific injection, destination-governed title/body language hygiene, recursive-spawn prohibition, memory-does-not-transfer) → `skills/task-subagent-prompt/SKILL.md`.
- Setting the Agent tool spawn parameters (model policy, parallel-width cap) → `skills/task-subagent-spawn/SKILL.md`.
- Subagent-side state-machine label transitions at role boundaries → `skills/task-subagent-state-labels/SKILL.md`.

</adjacent-firing-moments>

</subagent-delegation>

---
name: task-subagent-delegation
description: Invoke when implementation work is about to start and must go to a subagent rather than the parent / operations work is about to be delegated to a subagent / a delegated subagent must be resumed to adjudicate brake findings after CI green / subagent capability is unavailable and the parent must fall back to direct execution. Provides the always-delegate rule with no parent-side revision window, the mode-dependent split of what the subagent executes across its two phases and what the parent retains, what to convey and what not to convey, and the substrate-absence fallback. Prompt composition is in `skills/task-subagent-prompt/SKILL.md`, spawn parameters in `skills/task-subagent-spawn/SKILL.md`, subagent-side lifecycle labels in `skills/task-subagent-state-labels/SKILL.md`.
layer: L3-task
---

<subagent-delegation>

# Subagent Delegation

<rules>

## Rules

Implementation is always delegated to a subagent. The parent does not implement. Scope = all of Li+: self-evolution PRs in `LI_PLUS_REPO` and work in the user repositories `USER_REPO<N>` alike. No exception by diff size. A rule that branches demands a judgment at its application moment, and simplicity of the rule is the axis this one was decided on (judgment record: wiki `implementation-always-delegated`). Accepted cost: a one-line change still carries the cost of writing a delegation prompt.
Boundary: the implementation this rule delegates is the issue's change, and the delegation does not end when the PR opens. Revision on brake findings after CI green belongs to the same subagent, resumed (`rules/evolution/initiator-autonomy.md` Two-stage brake, Adjudication actor). There is no parent-side revision window to bound, so the rule needs no clause bounding one — the earlier carve-out ("the parent may apply what an adjudicated finding calls for") is removed rather than narrowed. Nothing the author writes into the PR is parent work at any size.

Parent agent delegates implementation and operations to subagent.
Parent retains: issue creation, issue management (non-state lifecycle labels / type / maturity / marker / close), the issue assignee, review judgment.

The assignee is set at the delegation moment, by the parent, in the same act as the spawn: `gh issue edit {issue_number} -R {owner}/{repo} --add-assignee "@me"` (parent and delegated subagent authenticate as the same GitHub actor, so `@me` names the account that will hold the issue). Do not remove a prior assignee to install this one; `--add-assignee` is additive and that is the specification. The assignee is not a label and does not join the state-machine subset — `in-progress` stays the subagent's, raised when its work starts, and is not pulled forward with the assignee: a running-claim set before the runner exists produces a false lock. Why the split is asymmetric, and how the Assignees field is read, are held at `skills/task-subagent-state-labels/SKILL.md` Actor axis.
if execution_mode == auto or execution_mode == semi_auto:
  Subagent executes, in two phases against one delegation:
    phase 1 - branch, implementation, commit, push, PR, CI loop.
    phase 2 (resumed by the parent after the brakes report) - read the evaluators'
      PR comments, adjudicate each finding, answer it on the PR with an accept or a
      reject, apply what was accepted, commit, push, CI loop.
  Stop condition = `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition.
    It is reached twice, once per phase; the literal is the same at both.
  Parent retains: spawning the brake evaluators, resuming the subagent between the
  phases, self-review, merge decision. Adjudication is not parent-side.
  The two modes share one subagent boundary: what differs is the human PR check
  (`semi_auto` adds one for minor / major per `rules/operations/execution-mode.md`),
  and that is a parent-side gate, not a subagent execution step.
  Subagent does not post the self-review record, in either phase: it is a PR comment,
  and the actor is fixed by `skills/operations-on-pr-review/SKILL.md` Self-review
  procedure. The phase-2 answers on the PR are the author's replies to findings, a
  different artifact; posting them is not the self-review record and does not become it.
if execution_mode == trigger:
  Subagent executes: branch, implementation, commit, push, PR, CI loop, self-review.
  `merge` is not on that list. What the mode matrix's `AI` merge executor names here is
  enabling the GitHub auto-merge handoff at PR creation (`rules/operations/operations.md`
  PR auto-merge policy), and the `PR` item already covers that act. GitHub fires the merge
  itself on human approval, by which time this session has ended.
  Stop condition = `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition.

The `branch` item above is conditional on the delegation using no worktree, in every mode. A worktree delegation arrives with the branch already created — the branch is what the worktree is checked out from, so creating one inside the delegation has nothing to attach to — and the subagent works in the path it was given. The condition is stated here because this is the file that owns the execution split; an adapter that scoped it from its own side alone would be a later layer redefining an earlier one (`rules/model/layer-definition.md` Cross-layer rule), which that rule sends back to the boundary rather than resolving by precedence.

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

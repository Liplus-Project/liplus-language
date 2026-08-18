---
name: task-pr-review-judgment
description: Invoke when the main agent is about to judge a PR review result (actor axis: this is the main-agent surface, and it reaches the judgment without reading the operations skills; a delegated subagent at its own review surface takes `rules/operations/main-agent-procedures.md` PR review instead). Mode-dependent: auto and semi_auto use self-review by the main agent, semi_auto adding a type-gated human check; trigger handles external review APPROVED and CHANGES_REQUESTED.
layer: L3-task
---

<pr-review-judgment>

# PR Review Judgment

<responsibilities>

## Responsibilities

Main agent judges PR review without reading operations skills (`skills/operations-on-pr-review/SKILL.md` etc.) directly.
Judgment basis = issue body + PR diff + CI result + when the brakes ran, the parent's aggregated findings comment on the PR and the commit bodies carrying the author's adjudication of it.

What the main agent has to execute around that judgment — the self-review formal record, the review approval
check, and the merge procedure — is not on this surface and not on the barred one either: all three are canonical
in `rules/operations/main-agent-procedures.md`, which is resident. That file's The bar and its pair is why they
sit there rather than in an operations skill. This skill holds the judgment; that file holds the acts the
judgment releases, the approval check among them — it detects the review decision, and the judgment on that
decision is here.

if execution_mode == auto:
  Self-review (after CI pass):
    Main agent reviews PR diff against issue requirements.
    Subagent-created PR = separate perspective verification. Especially valuable.
    Self-created PR = diff re-check before merge.
    pass → post the self-review formal record, then merge
           (`rules/operations/main-agent-procedures.md` Self-review formal record / Merge Execution).
    fail → fix and recommit (restart CI loop).

if execution_mode == semi_auto:
  Self-review: same as auto. The main agent performs it; the subagent does not.
  The formal record is posted on pass, as in auto. A type-gated human check is then layered on top before merge.
  Gate detail (patch direct-merge / minor / major human check / per-PR exception /
  L1 brake 2 override) lives in `rules/operations/execution-mode.md`. Read it there.

if execution_mode == trigger:
  External review judgment:
    APPROVED → the merge fires on this approval from the auto-merge handoff enabled at PR
               creation (`rules/operations/main-agent-procedures.md` Merge Execution). There is
               no merge command left to run, and therefore none to delegate.
    CHANGES_REQUESTED → read review comments, judge against issue requirements, delegate fix to subagent.

</responsibilities>

</pr-review-judgment>

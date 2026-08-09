---
name: task-pr-review-judgment
description: Invoke when the main agent is about to judge a PR review result (actor axis: this is the main-agent surface, and it reaches the judgment without reading the operations skills; a delegated subagent at its own review surface takes `skills/operations-on-pr-review/SKILL.md` instead). Mode-dependent: auto and semi_auto use self-review by the main agent, semi_auto adding a type-gated human check; trigger handles external review APPROVED and CHANGES_REQUESTED.
layer: L3-task
---

<pr-review-judgment>

# PR Review Judgment

<responsibilities>

## Responsibilities

Main agent judges PR review without reading operations skills (`skills/operations-on-pr-review/SKILL.md` etc.) directly.
Judgment basis = issue body + PR diff + CI result + the brake finding thread on the PR when the brakes ran.

What the main agent has to execute around that judgment — the self-review formal record and the merge procedure —
is not on this surface and not on the barred one either: both are canonical in
`rules/operations/main-agent-procedures.md`, which is resident. That file's The bar and its pair is why they sit
there rather than in an operations skill. This skill holds the judgment; that file holds the acts the judgment
releases.

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
    APPROVED → proceed (delegate merge execution to subagent if available).
    CHANGES_REQUESTED → read review comments, judge against issue requirements, delegate fix to subagent.

</responsibilities>

</pr-review-judgment>

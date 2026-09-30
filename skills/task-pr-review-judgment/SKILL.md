---
name: task-pr-review-judgment
description: Invoke when the main agent is about to judge a PR review result (a delegated subagent takes `rules/operations/main-agent-procedures.md` PR review instead) / the main agent is about to wait for a human PR review after self-review passes. Provides the self-review judgment for auto and semi_auto, the external-review judgment for trigger, and the review approval check.
layer: L3-task
---

<pr-review-judgment>

# PR Review Judgment

<responsibilities>

## Responsibilities

Main agent judges PR review without reading operations skills (`skills/operations-on-pr-review/SKILL.md` etc.) directly.
Judgment basis = issue body + PR diff + CI result + when the brake ran, the PR comment thread carrying each round's evaluator findings and the author's adjudication of them.

The acts the judgment releases — the self-review formal record and the merge procedure — are canonical in
`rules/operations/main-agent-procedures.md` (Self-review formal record / Merge Execution). The review approval
check that reads the human review decision judged here is Review approval check below.

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
  Gate detail (patch direct-merge / minor / major human check / per-PR exception)
  lives in `rules/operations/execution-mode.md`. Read it there.

if execution_mode == trigger:
  External review judgment:
    APPROVED → the merge fires on this approval from the auto-merge handoff enabled at PR
               creation (`rules/operations/main-agent-procedures.md` Merge Execution). There is
               no merge command left to run, and therefore none to delegate. What the main agent
               still runs is the post-merge obligations, at the first turn that observes the
               merge (same section, Post-merge moment).
    CHANGES_REQUESTED → read review comments, judge against issue requirements, delegate fix to subagent.

</responsibilities>

<review-approval-check>

## Review approval check

Actor = the parent, in every mode that raises the gate. No mode puts a subagent at this wait.

Fires after self-review passes: in `semi_auto` for minor / major, in `trigger` for every PR (`rules/operations/main-agent-procedures.md` PR review). `auto` raises no human gate and never reaches here.

Prefer webhook over polling.
  if mcp__github-webhook-mcp available:
    poll get_pending_status every 60 seconds
    on pull_request_review pending: list_pending_events -> get_event for this PR -> check state -> mark_processed
  else:
    Wait = human signals review done (do not poll).
    On signal:
      gh pr view {pr} -R {owner}/{repo} --json reviewDecision --jq '.reviewDecision'

The decision read here is input, not the judgment: what APPROVED and CHANGES_REQUESTED release is Responsibilities above; on APPROVED the mode's merge path is `rules/operations/main-agent-procedures.md` Merge Execution.

</review-approval-check>

</pr-review-judgment>

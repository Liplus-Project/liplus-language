---
name: on-pr-review
description: Invoke after CI pass; AI self-review mandatory in every mode, formal review record via gh pr review --comment, mode-specific human gate.
layer: L4-operations
---

# PR Review

AI self-review is mandatory in every mode (trigger / semi_auto / auto).
Skipping self-review before merge is a spec violation. Self-review runs first; external human check (if any) is layered on top, not in place of it.

Review basis:
  repository-state-first:
    review basis = issue body + linked branch + PR diff + CI result
    local-only success does not close review

Self-review procedure (all modes):
  Main agent reviews PR diff against issue requirements (see Li+issues.md#PR_Review_Judgment).
  self-review pass -> post formal review record (below) -> proceed to mode-specific human gate.
  self-review fail -> fix and recommit (restart [CI Loop]).

Self-review formal record (all modes, mandatory):
  After internal self-review pass, AI MUST post the self-review outcome as a formal GitHub PR review:
    gh pr review {pr} -R {owner}/{repo} --comment --body "<summary of self-review outcome>"
  Rationale: creates audit trail visible on the PR's Reviews tab, separating AI's review record from PR author authorship.
  Mechanism note: GitHub rejects `--add-reviewer` self-assignment silently; only `gh pr review --comment` works for PR author self-review records (empirically verified 2026-04-20 on PR #1095).
  Review body must include: acceptance-criteria check result, scope deviations (if any), next-step expectation (e.g. "awaiting human review" for trigger / minor-major semi_auto).

Mode-specific human gate after self-review:

if execution_mode == auto:
  No human gate. Self-review pass -> proceed to [Merge].

if execution_mode == semi_auto:
  Type-gated human check.
  patch -> no human gate. Self-review pass -> proceed to [Merge].
  minor / major -> human check required after self-review pass (procedure = trigger mode's Review approval check below).
  Version type is the same judgment axis used at release (see [Human Confirmation Required]#Release version rule). AI proposes type at PR creation time; on unclear, default to the safer side (minor) and ask human.

if execution_mode == trigger:
  Human check required on every PR after self-review pass.
  Review approval check:
    Prefer webhook over polling.
    if mcp__github-webhook-mcp available:
      poll get_pending_status every 60 seconds
      on pull_request_review pending: list_pending_events -> get_event for this PR -> check state -> mark_processed
    else:
      Wait = human signals review done (do not poll).
      On signal:
        gh pr view {pr} -R {owner}/{repo} --json reviewDecision --jq '.reviewDecision'
  reviewDecision=="APPROVED" -> proceed to [Merge].
  reviewDecision=="CHANGES_REQUESTED" -> read review comments -> fix and recommit (restart [CI Loop]).

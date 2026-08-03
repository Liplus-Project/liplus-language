---
name: operations-on-pr-review
description: Invoke when CI has passed and the PR has reached its review surface / a delegated subagent has reached its stop condition and needs that mode literal. Makes AI self-review mandatory in every mode, records the formal review via gh pr review --comment, defines the mode-specific human gate, holds the canonical delegated-subagent stop condition split by mode, and carries the follow-through on items the self-review deferred, which lands after merge in the same session.
layer: L4-operations
---

<pr-review>

# PR Review

AI self-review is mandatory in every mode (trigger / semi_auto / auto).
Skipping self-review before merge is a spec violation. Self-review runs first; external human check (if any) is layered on top, not in place of it.

Review basis:
  repository-state-first:
    review basis = issue body + linked branch + PR diff + CI result
    local-only success does not close review

Self-review procedure (all modes):
  Actor = the agent holding the merge decision per `skills/task-subagent-delegation/SKILL.md` Rules: parent in `auto` / `semi_auto`, subagent in `trigger`.
  That agent reviews the PR diff against issue requirements (see `skills/task-pr-review-judgment/SKILL.md`).
  self-review pass -> post formal review record (below) -> proceed to mode-specific human gate.
  self-review fail -> fix and recommit (restart [CI Loop]).

Delegated-subagent stop condition (canonical, split by mode):
  if execution_mode == auto or execution_mode == semi_auto:
    Stop at `PR open + CI green`. The subagent neither runs nor posts the self-review; it reports there and exits.
    The parent then runs brake 1 (and brake 2 when the PR touches L1 Model Layer source) at the position fixed by
    `rules/evolution/initiator-autonomy.md` Two-stage brake, adjudicates the findings, self-reviews, and merges.
  if execution_mode == trigger:
    Stop at `PR open + auto-merge enabled + CI green + self-review posted + awaiting human review`.
    Self-review precedes the human gate in every mode and the subagent is its actor in this mode, so it lands
    before the stop point. Merge fires later via GitHub auto-merge after human approval; the subagent's session
    ends before that.
  Other surfaces point here. Do not restate the condition; the second copy is what drifts.

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
  Version type is the same judgment axis used at release (see `rules/operations/release-version-rule.md`). AI proposes type at PR creation time; on unclear, default to the safer side (minor) and ask human.

  Per-PR exception (content-based axis, ref `rules/operations/execution-mode.md` `semi_auto mode:` label):
    Even when the parent issue is minor / major, if the PR's own modification qualifies
    as patch under `rules/operations/release-version-rule.md` (e.g. language alignment,
    typo, comment, internal literal, docs alignment), the human-check requirement is
    waived; AI direct-merges.
    AI must record the exception judgment reason in the self-review comment, e.g.
    "no user/system observable impact, internal literal only, exception applied as
    patch-equivalent for review purposes".
    If uncertain about exception applicability, default to base axis (parent's release
    type) for safer-side fallback.

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

<follow-through-on-deferred-items>

## Follow-through on deferred items

Self-review records may legitimately defer items as "out of PR scope" (e.g. workspace memory cleanup, follow-up issue filing, doc-only follow-up). Deferred ≠ ignored:

- Workspace-side deferrals (memory edits, local config) execute in the SAME session immediately after merge. Do not push them to the next session.
- Repo-side deferrals (follow-up issues, separate PR for unrelated cleanup) are filed BEFORE merge so they are not lost.
- Human APPROVED comments that contain "〜したんだよね？" / "did you also do X?" / similar embedded confirmations are part of the approval condition, not optional small talk. Treat the embedded confirmation as an additional gate and respond to it in the same session.

Merge is not the closing bracket; the deferred-item handoff is.

</follow-through-on-deferred-items>

</pr-review>

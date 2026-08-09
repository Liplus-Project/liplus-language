---
name: operations-on-pr-review
description: Invoke when CI has passed and the PR has reached its review surface / a delegated subagent has reached its stop condition and needs that mode literal. Makes AI self-review mandatory in every mode, routes the formal review record to its canonical in rules/operations/main-agent-procedures.md, defines the mode-specific human gate, holds the canonical delegated-subagent stop condition split by mode, and carries the follow-through on items the self-review deferred, which lands after merge in the same session.
layer: L4-operations
---

<pr-review>

# PR Review

AI self-review is mandatory in every mode (trigger / semi_auto / auto).
Skipping self-review before merge is a spec violation. Self-review runs first; external human check (if any) is layered on top, not in place of it.

Review basis:
  repository-state-first:
    review basis = issue body + linked branch + PR diff + CI result + the brake finding thread on the PR when the brakes ran
    local-only success does not close review

Self-review procedure (all modes):
  Actor = parent in `auto` / `semi_auto`, subagent in `trigger` (`skills/task-subagent-delegation/SKILL.md` Rules).
  In the first two it is the agent that merges; in `trigger` no agent merges, and the actor is the subagent
  because its self-review lands before its own stop point (Delegated-subagent stop condition below).
  That agent reviews the PR diff against issue requirements (see `skills/task-pr-review-judgment/SKILL.md`).
  self-review pass -> post formal review record (`rules/operations/main-agent-procedures.md` Self-review formal record) -> proceed to mode-specific human gate.
  self-review fail -> fix and recommit (restart [CI Loop]).

Delegated-subagent stop condition (canonical, split by mode):
  if execution_mode == auto or execution_mode == semi_auto:
    Stop at `PR open + CI green`. The subagent neither runs nor posts the self-review; it reports there and exits.
    This point is reached twice, and the literal above is the whole condition at both:
      first pass  - the issue's change is implemented. The parent then runs brake 1 (and brake 2 when the PR
                    touches L1 Model Layer source) at the position fixed by `rules/evolution/initiator-autonomy.md`
                    Two-stage brake.
      second pass - the parent has resumed this subagent with the findings on the PR; it has adjudicated them,
                    answered each on the PR, and pushed what it accepted. Reaching CI green again ends the
                    delegation. If nothing was accepted, the same point is reached with no new commit.
    Adjudication happens between the two passes and belongs to the resumed subagent, not to the parent
    (`rules/evolution/initiator-autonomy.md` Two-stage brake, Adjudication actor). The parent self-reviews and
    merges after the second pass.
  if execution_mode == trigger:
    Stop at `PR open + auto-merge enabled + CI green + self-review posted + awaiting human review`.
    Self-review precedes the human gate in every mode and the subagent is its actor in this mode, so it lands
    before the stop point. Merge fires later via GitHub auto-merge after human approval; the subagent's session
    ends before that.
  Other surfaces point here. Do not restate the condition; the second copy is what drifts.

Self-review formal record (all modes, mandatory):
  Canonical = `rules/operations/main-agent-procedures.md` Self-review formal record. The requirement, the
  `gh pr review --comment` command, and the required body items live there, not here: the actor is the parent in
  `auto` / `semi_auto`, and the parent does not read this file (that file's The bar and its pair). Do not restate
  them here; the second copy is what drifts.

Mode-specific human gate after self-review:

if execution_mode == auto:
  No human gate. Self-review pass -> proceed to [Merge Execution].

if execution_mode == semi_auto:
  Type-gated human check.
  patch -> no human gate. Self-review pass -> proceed to [Merge Execution].
  minor / major -> human check required after self-review pass (procedure = trigger mode's Review approval check below).
  Version type is the same judgment axis used at release (see `rules/operations/release-version-rule.md`). AI proposes type at PR creation time; on unclear, default to the safer side (minor) and ask human.

  Per-PR exception (content-based axis) and the L1 brake 2 override that supersedes it live in
  `rules/operations/execution-mode.md` `semi_auto mode:`. Read them there before waiving the human
  check. The exception was restated here once and the override, added to the canonical file later,
  never reached the copy — a PR touching L1 Model Layer source then read as patch-waived at this
  surface, which is the merge gate's own. Do not restate either; the second copy is what drifts.

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
  reviewDecision=="APPROVED" -> the auto-merge handoff enabled at PR creation fires the merge
    (`rules/operations/main-agent-procedures.md` Merge Execution). Nothing runs a merge command here.
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

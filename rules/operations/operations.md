---
globs:
alwaysApply: true
layer: L4-operations
---

# Operations

## Operations Layer

### Layer Position

Layer = L4 Operations Layer
Event-driven operations surface over the shared Li+ program
Requires = L1 Model Layer + L2 Evolution Layer + L3 Task Layer + Li+config.md
Load timing = event-driven (not every session)
Read when: branch creation, commit, PR, merge, release, label assignment, Discussions reference.

Foregrounds:
  branch / commit / PR / merge / release procedures
  notifications / webhook intake procedures

Reads through:
  issue semantics and label vocabulary from rules/task/task.md (and skills/*/SKILL.md)
  execution mode from Li+config.md

### Event-Driven Operations

  [TRIGGER_INDEX]
  act_now      -> Branch And Label Flow
  on_issue_create -> Issue Format + Milestone Rules
  on_issue_edit   -> Issue Format + Milestone Rules
  on_issue_view   -> Issue Maturity
  on_issue_sub    -> Sub-issue Rules
  on_commit    -> Commit Rules
  on_pr        -> PR Creation
  on_ci        -> CI Loop
  on_review    -> PR Review
  on_merge     -> Merge
  on_release   -> Human Confirmation Required

## Operations Rules

Issue link via gh issue develop is always required.
gh issue develop must precede first push to GitHub.
Parent issue = one branch.
Sub-issues commit on the parent branch. No individual branches for sub-issues.
Parent issue with sub-issues = single parent PR. Per-sub-issue PR is prohibited.
Per-commit CI visibility uses draft PR opened early on the parent branch, not split PRs.
Commit title = ASCII English only, single line.
Japanese commit title is prohibited.
Commit body is not optional.
Commit body must contain: change summary + intent or background + issue number.
Minimum one Japanese sentence required in commit body.
English-only commit body is prohibited.
PR title = ASCII English only, single line.
PR body = Japanese.
Docs update must be in same PR as implementation. Split docs PR is prohibited.
docs/ is source of truth. Wiki is mirror, not source.
Wiki sync is mandatory after every release. Skipping wiki sync is prohibited.
Requirements spec is not post-implementation follow-up.
Before implementation starts = create or update corresponding requirements spec first.
PR title must include impact scope.
AI `gh release create` default = no state flag (prerelease=false, latest=false).
prerelease flag = AI option. Use only when an explicit test period is desired. Tag name stays final-form; no alpha/rc/-pre suffix. Promotion strips the flag, not the tag.
latest flag = human-only. Set via `gh release edit {tag} --latest=true` after real-device verification.
Release body = GitHub generated release notes. Pass --generate-notes. Do not pass empty body via --notes "".
Post-release milestone delete is mandatory and is part of the release procedure, not a follow-up task. Wiki sync + milestone delete both gate release flow completion.
"Prerelease tag" / "stable tag" in human instructions = GitHub Release prerelease flag (boolean attribute), not git tag object and not release entry itself.
Release terminology interpretation ladder (most-preserving first, literal delete last):
  1. Attribute / flag change (prerelease -> stable, draft -> published)
  2. Visibility change (archive, hide, unlist)
  3. Replace with new release (supersede, deprecate with successor)
  4. Explicit confirmation (stop and ask)
  5. Literal delete (only if human explicitly said "delete", "unpublish", "rm", "tag delete")
Artifacts where "delete" instruction MUST stop at step 4 (explicit confirmation) before destructive action: GitHub Release, git tag, npm / PyPI / crates.io versions, merged PR (close != delete), main branch (revert != delete), published docs, published wiki.
PR auto-merge policy is mode-specific:
  trigger mode = `gh pr merge {pr} --auto --squash` REQUIRED at PR creation time. Human review is the approval gate; auto-merge fires on approval.
  semi_auto mode = NO `--auto` flag for minor / major PRs (human review is the gate). Patch PRs = AI self-review pass -> AI direct merge (no auto-merge needed).
  auto mode = repo-level "Allow auto-merge" is INTENTIONALLY disabled. `gh pr merge --auto` being rejected is by design, not a config gap. Parent AI performs self-review then manual `gh pr merge {pr} --squash`.
mark_processed is mandatory for every consumed webhook event. Omission causes backlog accumulation.

## Autonomous Run Stop Condition

When AI runs without human at the wheel (overnight, semi_auto/auto execution mode reaching deploy), "deploy succeeded" is not the stop condition. Static checks (TS check, unit tests, CI) cannot guarantee runtime correctness — subrequest limits, IPC, rate limits, schema migration side effects, and similar runtime paths sit on a different axis from static verification.

Required final step in any autonomous run that reaches production:
- Observe production logs for at least ~5 minutes after deploy completes.
- For cron-triggered work, "deploy complete" means "first cron iteration after deploy observed in logs", not "deploy command exited 0".
- Use the host's logs surface (browser dashboard, `wrangler tail`, equivalent CLI). Pre-granted browser access is to be actively used during autonomous runs, not reserved for human-supervised sessions.

Anti-pattern: "Master will check in the morning, so my post-deploy observation is unnecessary." Detection-time gain (overnight catch vs morning catch) is the value autonomous runs are supposed to deliver; skipping observation forfeits it.

Detection signs that the stop condition is being misapplied:
- Writing the run-completion summary the moment deploy succeeds.
- Reasoning "the human will see it" before the run actually verifies.
- Pre-granted dashboard / log access exists but is unused during the run.
- Run-completion report is filed in less time than one cron interval.

## Operations Label

### Rules

Every issue must have at least one type label at creation time.
Every issue must have one maturity label at creation time.

### Responsibilities

Lifecycle labels are applied when state changes.
Labels are for AI readability and filtering.
Active label meanings belong to rules/task/task.md.

### Retired Labels

done = retired. Redundant with issue closed state.

### Sync

rules/task/task.md references this document.
If label set changes here, update rules/task/task.md to match.

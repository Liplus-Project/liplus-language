#######################################################

Layer Position

#######################################################

Layer = Operations Layer
Event-driven operations surface over the shared Li+ program
Requires = Model Layer + Task Layer + Li+config.md
Load timing = event-driven (not every session)
Read when: branch creation, commit, PR, merge, release, label assignment, Discussions reference.

Foregrounds:
  branch / commit / PR / merge / release procedures
  notifications / webhook intake procedures

Reads through:
  issue semantics and label vocabulary from Li+github.md
  execution mode from Li+config.md

#######################################################

Event-Driven Operations

#######################################################

  [TRIGGER_INDEX]
  act_now      -> Branch And Label Flow
  on_commit    -> Commit Rules
  on_pr        -> PR Creation
  on_ci        -> CI Loop
  on_review    -> PR Review
  on_merge     -> Merge
  on_release   -> Human Confirmation Required

  --------
  Rules
  --------

  Issue link via gh issue develop is always required.
  gh issue develop must precede first push to GitHub.
  Parent issue = one branch.
  Sub-issues commit on the parent branch. No individual branches for sub-issues.
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
  Requirements spec is not post-implementation follow-up.
  Before implementation starts = create or update corresponding requirements spec first.
  PR title must include impact scope.
  AI-created release is always prerelease.
  Latest promotion requires human judgment.
  Release body = GitHub generated release notes. Pass --generate-notes. Do not pass empty body via --notes "".
  mark_processed is mandatory for every consumed webhook event. Omission causes backlog accumulation.

  --------
  Responsibilities
  --------

  [Branch And Label Flow]

  Trigger = human intent to act now detected via dialogue.
  Judgment = read atmosphere, not checklist.
  If unclear = ask with feeling, not mechanically.

  Timing tiers:
  NOW     -> label=in-progress + branch create
  SOON    -> label=backlog     + no branch
  SOMEDAY -> label=deferred    + no branch

  Axis separation:
  Lifecycle labels = when to act.
  Maturity labels  = how converged the issue body is.
  Do not use lifecycle labels as substitute for memo/forming/ready.

  Branch existence check (before creation):
  local:  git branch --list {branch-name}
  remote: gh api repos/{owner}/{repo}/branches/{branch-name} (404=not_exists)
  If remote exists = existing GitHub branch cannot be retroactively linked.
  If local only   = gh issue develop still allowed (local will be overwritten).
  If not exists   = proceed normally.

  Branch creation:
  command  = gh issue develop {issue_number} -R {owner}/{repo} --name {session-branch} --base main
  assignee = gh api repos/{owner}/{repo}/issues/{issue_number}/assignees --method POST -f 'assignees[]=liplus-lin-lay'

  Branch-to-issue tree mapping:
  gh issue develop targets parent issue only.
  PR merge auto-closes the parent issue. This is expected because all sub-issues complete on the same branch before merge.
  If a sub-issue needs a separate branch, create a separate parent issue instead.

  On local error:
  gh issue develop may fail locally but succeed on GitHub side.
  Check linked branches before retrying:
    gh api graphql -f query='{ repository(owner:"{owner}",name:"{repo}") { issue(number:{number}) { linkedBranches { nodes { ref { name } } } } } }'
  If linked = use existing linked branch, do not create new branch.
  If not linked = retry or escalate.

  [Docs And Requirement Ownership]

  Distribution projects must have requirements spec as minimum docs.
  New or small projects: one requirements spec file is minimum acceptable form.
  Larger projects may split requirements spec across multiple docs.
  Requirements spec fixes accepted purpose, premise, and constraints from issues.
  For behavior change, bug fix, or spec change:
    update requirements spec first
    then update code and tests to implement and verify that spec delta

  Li+ behavior and governance decisions belong in numbered requirements plus the corresponding operational docs.
  Standalone memo or experiment log may exist, but it is not source of truth.
  Requirements spec may be split across multiple numbered docs when it improves readability.

  Docs check on commit:
  If this commit changes spec (Li+*.md) or behavior code = verify docs/ has corresponding update.
  If not yet updated = add docs update before push. Do not defer to a separate PR.

  [Commit And Push]

  Git push:
  primary          = git push origin {session-branch}:{target-branch}
  fallback_single  = gh api repos/{owner}/{repo}/contents/{path} (put base64 sha)
  fallback_multi_1 = create blobs: gh api .../git/blobs (per file)
  fallback_multi_2 = create tree:  gh api .../git/trees  (verify count after)
  fallback_multi_3 = create commit: gh api .../git/commits
  fallback_multi_4 = update ref:   gh api .../git/refs/heads/{branch}

  [PR Creation]

  PR body format:
    per issue block:
      line1 = "Refs #{issue_number}" or "Refs sub #{child_issue_number}"
      line2_to_3 = two to three line summary of that issue
    order = parent first, then closed children (omit deferred and open children).
    parent issue reference: use "Part of #{parent_number}" instead of "Refs".
    "Refs" triggers GitHub auto-close on merge. Parent issues must not be auto-closed by sub-issue PRs.
  Detail belongs in issue, not in PR.

  On PR created:
  1 = if repository allows auto-merge: gh pr merge {pr} -R {owner}/{repo} --auto --squash
  2 = proceed to [CI Loop] immediately, no human instruction required.

  [CI Loop]

  CI loop starts immediately after PR creation or after fix-and-recommit.
  CI loop is a separate task from PR creation. Do not skip.

  step1 = get latest commit sha:
    gh pr view {pr} -R {owner}/{repo} --json headRefOid --jq '.headRefOid'
  step2 = wait for all check-runs to complete:
    Prefer webhook over polling.
    if mcp__github-webhook-mcp available:
      poll get_pending_status every 60 seconds
      on check_run pending: list_pending_events -> get_event for check_run events -> verify sha match -> mark_processed
      collect conclusions until no in-flight check-runs remain
    else:
      gh api repos/{owner}/{repo}/commits/{sha}/check-runs --jq '.check_runs[] | {name,status,conclusion}'
      repeat with sleep until: all status=="completed"
  step3 = conclusion judgment (refs #460):
    CI fail = any conclusion=="failure"
    CI pass = all conclusion in [success, skipped, neutral]
  CI pass -> proceed to [PR Review].
  CI fail -> fix and recommit (restart CI loop from step1).
  CI loop safety (ref: Li+core.md#Loop Safety task/debug threshold):
  If still failing = externalize to issue comment, escalate to human.

  [PR Review]

  Review basis:
    repository-state-first:
      review basis = issue body + linked branch + PR diff + CI result
      local-only success does not close review

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

  [Merge]

  Pre-merge mergeable state check:
    gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
    CLEAN -> proceed to merge.
    BEHIND -> git fetch origin main && git rebase origin/main && git push --force-with-lease -> restart [CI Loop] from step1.
    CONFLICTING -> attempt rebase: git fetch origin main && git rebase origin/main
      if rebase succeeds: git push --force-with-lease -> restart [CI Loop] from step1
      if rebase fails: git rebase --abort -> comment on issue -> escalate to human
    BLOCKED or UNKNOWN -> wait and recheck (GitHub may still be computing)

  If auto-merge was enabled at PR creation: GitHub merges automatically on approval.

  Manual merge flow (auto-merge unavailable or not enabled):
  1 = confirm merge strategy with human (squash / merge / rebase)
  2 = gh pr merge {pr} -R {owner}/{repo} --{strategy}

  Parent close condition: closed automatically on merge via issue reference.

  Real device test:
  Merge first. Then test on main. Not a merge gate.

  [Human Confirmation Required]

  Stop immediately when:
  human says wait or stop or matte.

  Always confirm before:
  release create (version type and target tag) (after CD check passes)
  branch delete (when linked issue may close)
  force push
  Mode-dependent confirm (trigger mode only): issue selection, issue execution start.

  Release checks:
  1. CD check:
    if mcp__github-webhook-mcp available:
      poll get_pending_status every 60 seconds
      on workflow_run pending: list_pending_events -> get_event -> check conclusion -> mark_processed
    else:
      Poll gh api until all CD checks complete.
    CD pass = proceed. CD fail = escalate to human (do not release).
  2. Milestone check (if milestone exists for this release version):
    Verify all issues in the milestone are closed.
    Report milestone contents to human before proceeding.

  Release version rule:
  v0.x.x = initial development. Anything may change. Not a stable release.
  v1.0.0 = first stable release (semver compliant).
  patch = change that does not alter structure or API (fix / clarify / add rule)
  minor = change that alters structure or API (restructure / new section / architectural change)
  major = change with large impact on users. Human decides. Examples: breaking change, phase transition, UX overhaul.
  AI proposes patch or minor. Human decides version type. AI executes.

  Version base rule:
  Base on most recent release = includes prereleases.
  Not latest stable only.
  Use: gh release list --limit 1 (includes prereleases)

  Release tag and title rule:
  Tag format and release title follow project convention.
  Default (Li+ language): cd_tag = build-YYYY-MM-DD.N, title = "{version}" (e.g. "v1.9.0")
  npm package projects: tag = v{semver}, title = "v{semver}"
  If project has CD workflow that creates tags: use existing CD-created tag, do not create new tag.
  If project uses npm version: tag is created by npm version command.
  Check project docs/ or CI/CD config for convention before creating release.

  --------
  Responsibilities
  --------

  [Execution Mode]

  Mode source = USER_REPOSITORY_EXECUTION_MODE from Li+config.md
  Valid values = trigger | auto
  Default = trigger

  If mode not set:
  Ask human at session start with options:
    option A = "trigger: human decides when to start (timing only)"
    option B = "auto: AI decides when to start"
  Write selection to Li+config.md.
  No manual editing required.

  Common to all modes:
  Issue create/close/modify = assignee responsibility (AI in most cases).
  Ask human when information insufficient = always required.
  Release = human confirms.

  trigger mode:
  Execution timing = human decides.
  Issue create/update = allowed before execution trigger.
  Branch prepare/create = allowed before execution trigger.
  Implementation start = wait for human timing, then work from linked personal branch as primary surface.
  PR review = human reviews.

  auto mode:
  Execution timing = AI decides.
  PR review = AI reviews.

  Release always requires human confirmation regardless of mode.

  --------
  Autonomy
  --------

  [Repo-first Execution Surface]

  Protected shared branches (example: main) = high-caution surface.
  Personal issue-linked branch = normal implementation surface.
  Do not treat the whole repository as untouchable.
  Local validation may happen before or after push; it does not replace the branch as continuity surface.

  [Handoff Continuity]

  If token/session/model boundary may interrupt work = push useful intermediate state to the linked personal branch.
  Handoff source of truth = issue body + linked branch + commits/PR.
  Do not leave meaningful progress only in local workspace or chat memory.

  [Chat Output Limit]

  Long output may stop = physical limit, not corruption.
  Use chunking when needed.

  [Notifications API]

  PATCH  /notifications/threads/{id}   -> 205  read (stays in Inbox)
  PUT    /notifications {"read":true}  -> 205  mark all read
  DELETE /notifications/threads/{id}  -> 204  done (removed from Inbox)
  GET    /notifications?all=false      -> 200  check inbox
  scope = notifications (classic PAT)

  [Foreground Webhook Notification Intake]

  Purpose:
  Keep the active foreground thread lightweight.
  Do not search GitHub broadly for "maybe new comment" when a delivered event source already exists.

  Use only in hosts that can run a local command before replying.

  source priority:
    1 = mcp__github-webhook-mcp
    2 = local webhook store via bundled helper
    3 = none

  local webhook store:
    precondition = LI_PLUS_MODE=clone
    helper path = {workspace_root}/liplus-language/scripts/check_webhook_notifications.py
    state dir resolution:
      a = LI_PLUS_WEBHOOK_STATE_DIR from Li+config.md (absolute or workspace_root-relative)
      b = {workspace_root}/github-webhook-mcp
      c = {workspace_root}/../github-webhook-mcp
    if helper missing or state dir unresolved = skip silently
    helper output = inspect summary with foreground-matched items, notable items, and cleanup candidates
    helper default = inspect only; preserve unmatched backlog
    destructive actions = explicit `read` / `done` / `claim` / `cleanup-safe-success` calls only

  foreground handling:
    each user turn start = inspect once before main reply
    mention only = foreground-matched items or exceptional notable items
    if relevance cannot be judged cheaply = preserve and stay silent
    full payload = open only when deeper inspection is needed
    separate AI process launch = prohibited for this flow

  own-operation arrival confirmation:
    webhook notifications include results of own operations (push, PR, issue, release).
    these serve as arrival confirmation = proof that the operation reached GitHub.
    mark_processed own-operation events promptly during foreground check or after the triggering operation.
    do not accumulate own-operation events for bulk clearing later.
    external events (other users, bots) = preserve for foreground reporting or explicit handling.

#######################################################

Label

#######################################################

  --------
  Rules
  --------

  Every issue must have at least one type label at creation time.
  Every issue must have one maturity label at creation time.

  --------
  Responsibilities
  --------

  Lifecycle labels are applied when state changes.
  Labels are for AI readability and filtering.
  Active label meanings belong to Li+github.md [Label Definitions].

  --------
  Retired Labels
  --------

  done = retired. Redundant with issue closed state.

  --------
  Sync
  --------

  Li+github.md Label Definitions section references this document.
  If label set changes here, update Li+github.md to match.

#######################################################

Discussions

#######################################################

  --------
  Purpose
  --------

Discussions = external user entry point.
A bot is stationed in Discussions.
Bot capabilities: issue creation, issue reading.
Bot does not commit or modify code.

External users interact via Discussions -> bot creates issue -> AI implements from issue.

  -----------
  evolution
  -----------

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.

end of document

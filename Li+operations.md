#######################################################

Layer Position

#######################################################

Layer = Event-driven operations surface over the shared Li+ program
Requires = Li+core.md + Li+github.md + Li+config.md
Load timing = event-driven (not every session)
Read when: branch creation, commit, PR, merge, release, milestone/label assignment, Discussions reference.

Foregrounds:
  branch / commit / PR / merge / release procedures
  milestone / notifications / webhook intake procedures

Reads through:
  issue semantics and label vocabulary from Li+github.md
  execution mode from Li+config.md

#######################################################

Event-Driven Operations

#######################################################

  [TRIGGER_INDEX]
  act_now      -> Branch And Label Flow
  on_commit    -> Commit Rules
  on_pr        -> PR And CI Flow
  on_merge     -> Merge And Cleanup
  on_release   -> Human Confirmation Required

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
  Issue link via gh issue develop is always required.
  gh issue develop must precede first push to GitHub.

  On local error:
  gh issue develop may fail locally but succeed on GitHub side.
  Check linked branches before retrying:
    gh api graphql -f query='{ repository(owner:"{owner}",name:"{repo}") { issue(number:{number}) { linkedBranches { nodes { ref { name } } } } } }'
  If linked = use existing linked branch, do not create new branch.
  If not linked = retry or escalate.

  [Docs And Requirement Ownership]

  docs/ is source of truth.
  Wiki is mirror, not source.
  Docs update must be in same PR as implementation.
  Split docs PR is prohibited.
  Distribution projects must have requirements spec as minimum docs.
  New or small projects: one requirements spec file is minimum acceptable form.
  Larger projects may split requirements spec across multiple docs.
  Requirements spec fixes accepted requirements, constraints, and completion conditions from issues.
  Requirements spec is not post-implementation follow-up.
  Before implementation starts = create or update corresponding requirements spec first.
  For behavior change, bug fix, or spec change:
    update requirements spec first
    then update code and tests to implement and verify that spec delta

  Li+ behavior and governance decisions belong in numbered requirements plus the corresponding operational docs.
  Standalone memo or experiment log may exist, but it is not source of truth.
  Keep requirements in 0.-Requirements.md until splitting improves readability.

  PR title must include impact scope.
  example bad  = "fix(config): negative duration handling"
  example good = "fix(config): treat negative durations as below-minimum rather than error"

  [Commit Rules]

  Language:
  Title = ASCII English only, single line
  Body  = Japanese with issue number
  Japanese title is prohibited.
  English-only body is prohibited.

  Body must contain:
  change summary + intent or background + issue number.
  Minimum one Japanese sentence required.
  Body is not optional.

  Git push:
  primary          = git push origin {session-branch}:{target-branch}
  fallback_single  = gh api repos/{owner}/{repo}/contents/{path} (put base64 sha)
  fallback_multi_1 = create blobs: gh api .../git/blobs (per file)
  fallback_multi_2 = create tree:  gh api .../git/trees  (verify count after)
  fallback_multi_3 = create commit: gh api .../git/commits
  fallback_multi_4 = update ref:   gh api .../git/refs/heads/{branch}

  Chat output limit:
  Long output may stop = physical limit, not corruption.
  Use chunking when needed.

  [PR And CI Flow]

  PR body format:
    per issue block:
      line1 = "Refs #{issue_number}" or "Refs sub #{child_issue_number}"
      line2_to_3 = two to three line summary of that issue
    order = parent first, then closed children (omit deferred and open children).
  Detail belongs in issue, not in PR.

  CI trigger: on PR created -> start CI loop immediately, no human instruction required.
  PR task is not complete until CI loop concludes.

  CI loop:
  step1 = get latest commit sha:
    gh pr view {pr} -R {owner}/{repo} --json headRefOid --jq '.headRefOid'
  step1.5 = check mergeable state:
    gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
    if CONFLICTING:
      attempt rebase: git fetch origin main && git rebase origin/main
      if rebase succeeds: git push --force-with-lease -> restart CI loop from step1
      if rebase fails: git rebase --abort -> comment on issue -> escalate to human
    if BLOCKED or UNKNOWN: wait and recheck (GitHub may still be computing)
  step2 = wait for all check-runs to complete:
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
  CI pass -> review request auto sent via codeowners.
  CI fail -> fix and recommit.
  CI loop safety (ref: Li+core.md#Loop Safety task/debug threshold):
  If still failing = externalize to issue comment, escalate to human.

  Review approval check:
    if mcp__github-webhook-mcp available:
      poll get_pending_status every 60 seconds
      on pull_request_review pending: list_pending_events -> get_event for this PR -> check state -> mark_processed
    else:
      Wait = human signals review done (do not poll).
      On signal:
        gh pr view {pr} -R {owner}/{repo} --json reviewDecision --jq '.reviewDecision'
  reviewDecision=="APPROVED" -> GitHub auto-merge handles it.
  reviewDecision=="CHANGES_REQUESTED" -> read review comments -> fix and recommit (restart CI loop).

  [Merge And Cleanup]

  Parent close condition: closed automatically on merge via issue reference.

  Recommended flow:
  1 = create PR (body includes "Refs #{parent_issue_number}")
  2 = enable auto-merge: gh pr merge {pr} -R {owner}/{repo} --auto --squash
  3 = CI pass -> review request auto sent via codeowners
  4 = GitHub auto-merge on approval (squash + branch delete handled by GitHub)
  5 = parent issue auto-closed by GitHub on merge

  Real device test:
  Merge first. Then test on main. Not a merge gate.

  [Execution Mode]

  Mode source = LI_PLUS_EXECUTION_MODE from Li+config.md
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
  Implementation start = wait for human timing.
  PR review = human reviews.

  auto mode:
  Execution timing = AI decides.
  PR review = AI reviews.

  Release always requires human confirmation regardless of mode.

  [Human Confirmation Required]

  Stop immediately when:
  human says wait or stop or matte.

  CD check before release:
    if mcp__github-webhook-mcp available:
      poll get_pending_status every 60 seconds
      on workflow_run pending: list_pending_events -> get_event -> check conclusion -> mark_processed
    else:
      Poll gh api until all CD checks complete.
  CD pass = proceed to release create.
  CD fail = escalate to human (do not release).

  Always confirm before:
  release create (version type and target tag) (after CD check passes)
  branch delete (when linked issue may close)
  force push
  Mode-dependent confirm (trigger mode only): issue selection, issue execution start.

  Release version rule:
  patch = bug fix or config/rule change
  minor = new feature or behavior change
  major = breaking change or spec incompatibility
  Human decides version type. AI executes.

  Version base rule:
  Base on most recent release = includes prereleases.
  Not latest stable only.
  Use: gh release list --limit 1 (includes prereleases)

  Release tag and title rule:
  Tag format and release title follow project convention.
  Default (Li+ language): cd_tag = build-YYYY-MM-DD.N, title = "Li+ {version}"
  npm package projects: tag = v{semver}, title = "v{semver}"
  If project has CD workflow that creates tags: use existing CD-created tag, do not create new tag.
  If project uses npm version: tag is created by npm version command.
  Check project docs/ or CI/CD config for convention before creating release.
  AI-created release is always prerelease.
  Latest promotion requires human judgment.

  Release body rule:
  body = GitHub generated release notes
  Command requirement = pass --generate-notes
  Do not pass empty body via --notes "".

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
    helper output = latest lightweight summaries only
    on consume = drain all current pending events immediately and delete related generated files

  foreground handling:
    each user turn start = inspect once before main reply
    pending_count == 0 = no mention
    pending_count > 0  = brief mention before main reply
    full payload = open only when deeper inspection is needed
    separate AI process launch = prohibited for this flow

#######################################################

Milestone

#######################################################

  --------
  Rules
  --------

Milestone = release unit. Groups issues that ship together.
Every issue must have a milestone at creation time.
If no milestone fits = ask human which milestone, or whether to create new one.

Milestone naming = version number (e.g. v1.2.0).
Milestone description = one-line theme + bullet list of scope.

  --------
  Lifecycle
  --------

Create milestone when: new release scope is decided by human.
Close milestone when: release is published.
Do not close milestone before release.

Sub-issues inherit parent milestone.
If parent has milestone and child does not = assign same milestone to child.

#######################################################

Label

#######################################################

  --------
  Policy
  --------

Labels are for AI readability and filtering.
Active label meanings belong to Li+github.md [Label Definitions].
Every issue must have at least one type label at creation time.
Every issue must have one maturity label at creation time.
Lifecycle labels are applied when state changes.

  --------
  Retired Labels
  --------

done = retired. Redundant with issue closed state.
tips = retired. Use docs label + issue body instead.

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

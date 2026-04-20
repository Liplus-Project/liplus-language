#######################################################

Layer Position

#######################################################

Layer = L4 Operations Layer
Event-driven operations surface over the shared Li+ program
Requires = L1 Model Layer + L2 Evolution Layer + L3 Task Layer + Li+config.md
Load timing = event-driven (not every session)
Read when: branch creation, commit, PR, merge, release, label assignment, Discussions reference.

Foregrounds:
  branch / commit / PR / merge / release procedures
  notifications / webhook intake procedures

Reads through:
  issue semantics and label vocabulary from task/Li+issues.md
  execution mode from Li+config.md

#######################################################

Event-Driven Operations

#######################################################

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

  --------
  Rules
  --------

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
  mark_processed is mandatory for every consumed webhook event. Omission causes backlog accumulation.

  --------
  Responsibilities
  --------

  [Issue Format]

  Issue title language:
  Title = ASCII English only.
  Body  = LI_PLUS_PROJECT_LANGUAGE.
  Consistent with Commit Rules and PR title convention.

  Issue may start from memo. Three fields are convergence target, not creation gate.
  Use only necessary headings. Do not force empty sections.
  Canonical convergence for implementation issue:
    purpose
    premise
    constraints
    target files (recommended at ready stage)
  Target files = list of files expected to change, with dependency notes (e.g. source⇔docs).
  Target files are optional during memo/forming. Recommended once issue reaches ready.
  Rewrite issue body whenever accepted understanding changes.
  Issue completion is managed through issue state plus PR/CI/release flow, not a dedicated issue-body field.

  Checklist = human judgment required (real device test, operational verification).
  Use checklist only when AI cannot judge.

  [Issue Maturity]

  memo/forming is not implementation-ready.

  Parent issue may also start from memo.
  Converged parent issue contents: purpose, premise, constraints.
  Parent close condition is structural = all child issues closed except deferred.

  Proactive premise verification (forming → ready):
  When spec body reaches forming with unverified technical assumptions in premise section
  (external API specs, runtime constraints, library behavior, platform limits, etc.),
  AI proactively starts verification research before human asks.
  Do not wait for human to point out unverified premises.
  forming → ready transition requires all technical premises in premise section to be verified.

  Verification completion criterion:
  Applies to external fact cross-check results only.
  Subjective confidence is outside this criterion.
  A premise is verified only when external evidence (docs, spec, source, runtime probe, existing issue/PR record) is cited.
  "feels correct" is not verification.

  [Sub-issue Rules]

  Sub-issue = AI-trackable work unit.
  Split by responsibility, not granularity.

  Classification litmus (sub-issue vs sibling issue):
  Ask: "Can this unit ship independently without breaking the parent's atomic deliverable?"
  If yes = this is a sibling issue, not a sub-issue. Create it as an independent issue.
  If no  = this is a legitimate sub-issue. It only makes sense as part of the parent's atomic deliverable.
  Rationale: if a unit can ship alone, nothing is gained by making it a sub-issue.
  The feeling "I want per-sub-issue PR to ship these independently" = signal that these should have been sibling issues from the start.
  Re-classify before splitting PRs. Do not split PRs.

  Single parent PR flow (canonical, ref #919):
  Parent issue with sub-issues accumulates commits on one parent branch.
  One PR per parent issue, opened against main. Sub-issues are handled inside that PR.
  PR may be opened as draft early to expose per-commit CI on the parent branch.
  Merge happens once, after all sub-issues are complete.
  Parent auto-close on merge is the intended behavior: all sub-issues are already closed by that point
  because the parent PR is the last event, not the first.
  Per-sub-issue PR flow is prohibited. Accumulating multiple PRs on a shared parent branch breaks this model:
  the first merged PR auto-closes the parent before the remaining sub-issues are done.

  Sub-issue API:
  gh issue develop targets parent issue only (branch creation).
  Sub-issue linking uses REST API with internal numeric ID, not issue number.

  Simultaneous tasks require parent-child structure:
  If multiple tasks in same session = create parent issue + sub-issues.
  Do not create multiple independent issues for simultaneous work.

  Parallel conflict analysis:
  When multiple ready issues exist = analyze target files for overlap before execution.
  No overlap = parallel-safe. Propose parallel sub-issue structure to human.
  Partial overlap = propose splitting shared-file changes into a separate integration sub-issue.
  Integration sub-issue executes after parallel sub-issues complete (serialized dependency).
  Analysis basis = target files field in issue body. If absent, infer from issue purpose and premise.

  [Milestone Rules]

  Milestone = release unit. Groups issues that ship together.
  Every issue must have a milestone at creation time.
  Exception: tips issues do not require a milestone.
  Milestone naming = version number (e.g. v1.2.0).
  Sub-issues inherit parent milestone.
  If parent has milestone and child does not = assign same milestone to child.
  Do not close milestone before release.
  If no milestone fits = ask human which milestone, or whether to create new one.
  Milestone description = one-line theme + bullet list of scope.
  Create milestone when: new release scope is decided by human.
  Close milestone when: release is published.

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

  Atmosphere reading scope:
  Applies to timing tier judgment (NOW / SOON / SOMEDAY) only.
  Label assignment is a deterministic mapping from tier result, not a second atmosphere read.
  Once tier is judged, label follows the tiers table without re-reading atmosphere.

  Branch existence check (before creation):
  local:  git branch --list {branch-name}
  remote: gh api repos/{owner}/{repo}/branches/{branch-name} (404=not_exists)
  If remote exists = existing GitHub branch cannot be retroactively linked.
  If local only   = gh issue develop still allowed (local will be overwritten).
  If not exists   = proceed normally.

  Branch creation:
  command  = gh issue develop {issue_number} -R {owner}/{repo} --name {session-branch} --base main
  assignee = gh api repos/{owner}/{repo}/issues/{issue_number}/assignees --method POST -f 'assignees[]=liplus-lin-lay'

  Merge behavior:
  PR merge auto-closes the parent issue via issue reference.
  Parent branch is linked to parent issue via gh issue develop, so any PR from that branch
  auto-closes the parent on merge. This is safe under the single parent PR flow (see Sub-issue Rules):
  the single merge happens only after all sub-issues are done, so parent auto-close lands correctly.
  Per-sub-issue PR on the parent branch is prohibited precisely because it triggers parent auto-close
  before the remaining sub-issues complete.
  If a unit needs an independent branch and PR = it is a sibling issue, not a sub-issue.
  Create it as an independent issue with its own parent branch.

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

  One PR per parent issue (see Sub-issue Rules#Single parent PR flow).
  Parent issue with sub-issues = single PR that closes all sub-issues + the parent on merge.
  Per-sub-issue PR is prohibited.

  Draft PR early open (optional, for per-commit CI visibility):
  On parent issue with sub-issues, open the parent PR as draft immediately after the first commit is pushed.
  command = gh pr create --draft -R {owner}/{repo} --base main --head {session-branch} ...
  pull_request.synchronize CI fires on every subsequent push, giving per-commit CI without splitting PRs.
  Mark ready for review (gh pr ready {pr}) only after all sub-issues are complete and the PR body is final.
  Draft PR is not required; it is a convenience for long-running parent work.

  PR body format:
    per issue block:
      line1 = "Closes #{issue_number}" (for non-parent issues, including sub-issues)
      line2_to_3 = two to three line summary of that issue
    order = non-parent issues first, then parent (if any); omit deferred and open children.
    parent issue reference under single parent PR flow = "Closes #{parent_number}" (parent closes together with sub-issues on the single final merge).
    "Part of #{parent_number}" is used only when the current PR is NOT the final parent PR — e.g. an explicitly deferred remainder PR on a different parent issue. In the canonical single parent PR flow, "Part of" does not appear.
    "Closes" triggers GitHub auto-close on merge. "Part of" does not, so parent is preserved.
    GitHub auto-close keywords (authoritative list): close / closes / closed / fix / fixes / fixed / resolve / resolves / resolved.
    "Refs" is not a close keyword and does not auto-close; do not use "Refs" for issues that should close on merge.
  Detail belongs in issue, not in PR.

  On PR created:
  1 = self-assign AI bot to PR assignees:
      gh pr edit {pr} -R {owner}/{repo} --add-assignee liplus-lin-lay
      rationale: existing issue-side assignee does not auto-propagate to the PR entity. Self-assign makes "AI owns this PR" explicit in the Assignees field.
      mechanism note: GitHub rejects `--add-reviewer` self-assignment silently, but allows `--add-assignee` self-assign for PR author (empirically verified 2026-04-20 on PR #1099).
      scope: assignee self-assign is UI trail only; it does not replace the formal self-review record (`gh pr review --comment`, see [PR Review]).
  2 = proceed to [CI Loop] immediately, no human instruction required.
  Merge execution is unified to AI across all modes (see [Merge]). GitHub auto-merge handoff is no longer used.

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

  [Merge]

  Merge executor is AI in every mode (trigger / semi_auto / auto).
  AI runs `gh pr merge` after all preconditions pass (self-review + mode-specific human gate, and mergeable state check). GitHub auto-merge handoff is no longer used.

  Pre-merge mergeable state check:
    gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
    CLEAN -> proceed to merge.
    BEHIND -> git fetch origin main && git rebase origin/main && git push --force-with-lease -> restart [CI Loop] from step1.
    CONFLICTING -> attempt rebase: git fetch origin main && git rebase origin/main
      if rebase succeeds: git push --force-with-lease -> restart [CI Loop] from step1
      if rebase fails: git rebase --abort -> comment on issue -> escalate to human
    BLOCKED or UNKNOWN -> wait and recheck (GitHub may still be computing)

  Merge strategy:
    Default = squash (repo convention).
    All modes = AI runs: gh pr merge {pr} -R {owner}/{repo} --squash
    Deviation from squash = AI pauses and asks human.

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
  Judgment axis = change scale + user/system observability.
  patch = everything else (docs / small fix / small spec / config / internal rule / governance structure change with no user/system observable impact). This issue (#1087) is itself a patch example: release-rule redesign is structurally governance but not observable from a Li+ user's surface.
  minor = large refactor or large structural change that is user/system observable.
  major = large-scale change or major goal milestone (phase transition, project milestone). Human decides.
  Important note: "structural change -> minor" is wrong. "Structural change AND user/system observable -> minor". Governance / spec rule changes without observable impact stay patch regardless of structural scale.
  AI proposes patch or minor. Human confirms minor or major. AI executes.

  Release state rule (independent axis from version type):
  default = no state flag. prerelease=false, latest=false. This is the AI `gh release create` default for any version type.
  prerelease = AI option. Apply only when an explicit test period is wanted. Tag name is final-form; do not append alpha.N / rc.N / -pre suffix. Promotion = strip flag (`gh release edit {tag} --prerelease=false`), keep the same tag.
  latest = human-only. Real-device verification gate. Human flips via `gh release edit {tag} --latest=true`. Independent of version type: patch / minor / major all gate on the same real-device check.

  Canonical release creation command (AI):
    gh release create {tag} \
      --target main \
      --title {version} \
      --generate-notes \
      --latest=false
  `--latest=false` must be passed explicitly. Omitting the flag makes gh CLI fall back to its default `legacy` behavior (semver + date auto-pick), which promotes the new release to Latest and silently demotes the existing Latest anchor.

  Latest anchor requirement:
  The repository must always hold at least one explicit Latest release (`make_latest=true`). This release is the Latest anchor.
  When the anchor is absent, `--latest=false` on a new release is overridden by the legacy default and the new release is promoted to Latest against intent.
  Treat the anchor as repo-wide persistent state, not a per-release attribute.

  Anchor flip procedure (human, after real-device verification):
  `gh release edit {new_tag} --repo {owner}/{repo} --latest=true`
  GitHub enforces a single Latest per repo, so the previous anchor automatically loses its Latest badge and transitions to the default (no-state) form. The new release becomes the Latest anchor.
  Tag names remain unchanged across the flip; only the Latest state moves.

  Bootstrap / transient state:
  For the first non-prerelease release of a repository, or whenever the anchor is lost, GitHub temporarily promotes the newest release to Latest via the legacy auto-pick. This transient Latest state is resolved the moment a human sets an explicit Latest anchor (one-Latest-only constraint performs the natural transition).
  Do not treat this transient Latest as an AI-authored state; it is a platform-side default, not a governance decision.

  Bulk state normalization:
  To normalize multiple existing releases to the no-state default, first pin one release as the anchor with `--latest=true`, then PATCH the remaining releases with `--latest=false`. Reversing the order leaves the repo anchorless, so `--latest=false` is silently overridden by the legacy default and one of the target releases ends up Latest again.

  Version base rule:
  Base on most recent release = includes prereleases.
  Not latest stable only.
  Use: gh release list --limit 1 (includes prereleases)

  Post-release wiki sync:
  After release is published, sync docs/ to GitHub Wiki.
  Wiki must be a complete mirror of docs/. Renamed or removed pages must disappear from Wiki.
  Steps:
    1. Clone wiki repo: git clone https://github.com/{owner}/{repo}.wiki.git {tmpdir}
    2. Configure identity (clone-and-throw-away pattern requires explicit identity):
       git -C {tmpdir} config user.name  "{commit-author-name}"
       git -C {tmpdir} config user.email "{commit-author-email}"
    3. Wipe existing markdown (prevents stale pages from rename/delete): rm -f {tmpdir}/*.md
    4. Copy docs/ files: cp docs/*.md {tmpdir}/
    5. Stage all (including deletions): git -C {tmpdir} add -A
    6. Commit: git -C {tmpdir} commit -m "sync: docs → wiki ({release_tag})"
    7. Push: git -C {tmpdir} push
    8. Cleanup: rm -rf {tmpdir}
  If push fails (permission): escalate to human. Do not skip.
  Wiki sync is part of the release procedure, not a follow-up task.

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
  Valid values = trigger | semi_auto | auto
  Default = trigger

  If mode not set:
  Ask human at session start with options:
    option A = "trigger: human decides when to start; human reviews every PR"
    option B = "semi_auto: AI decides when to start; AI self-reviews; human reviews minor/major only"
    option C = "auto: AI decides when to start; AI self-reviews only"
  Write selection to Li+config.md.
  No manual editing required.

  Mode matrix:

  | axis                 | trigger          | semi_auto                    | auto        |
  |----------------------|------------------|------------------------------|-------------|
  | Execution timing     | human decides    | AI decides                   | AI decides  |
  | AI self-review       | required         | required                     | required    |
  | Human PR check       | every PR         | minor / major only           | none        |
  | Merge executor       | AI               | AI                           | AI          |
  | Release confirm      | human            | human                        | human       |

  AI self-review is required in every mode. See [PR Review] for the self-review procedure and the type-gated human check in semi_auto.
  Merge is executed by AI in every mode. See [Merge]. GitHub auto-merge handoff is no longer used.

  Common to all modes:
  Issue create/close/modify = assignee responsibility (AI in most cases).
  Ask human when information insufficient = always required.
  Release = human confirms.

  trigger mode:
  Execution timing = human decides.
  Issue create/update = allowed before execution trigger.
  Branch prepare/create = allowed before execution trigger.
  Implementation start = wait for human timing, then work from linked personal branch as primary surface.
  PR review = AI self-review, then human check on every PR.

  semi_auto mode:
  Execution timing = AI decides.
  PR review = AI self-review on every PR; human check layered on top for minor / major only.
    patch = AI self-review pass -> AI merges (no human review).
    minor / major = AI self-review pass -> human check required -> AI merges on approval.
  Rationale: self-evolution loop rotation is the design goal; patch-level auto-merge removes the human bottleneck for low-risk changes while minor/major retain human oversight.
  Defense-in-depth (intentionally two layers):
    Layer 1 = AI self-review + Li+ spec discipline (absorbs everyday mistakes).
    Layer 2 = Release human gate (latest flip on real-device verification, prevents catastrophic user exposure).

  auto mode:
  Execution timing = AI decides.
  PR review = AI self-review only (no human check).

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
  Active label meanings belong to task/Li+issues.md [Label Definitions].

  --------
  Retired Labels
  --------

  done = retired. Redundant with issue closed state.

  --------
  Sync
  --------

  task/Li+issues.md Label Definitions section references this document.
  If label set changes here, update task/Li+issues.md to match.

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

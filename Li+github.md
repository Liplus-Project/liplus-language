#######################################################

Layer Position

#######################################################

Layer = Task Layer
Issue-facing surface over the shared Li+ program
Requires = Model Layer
Companion surface = Operations Layer for event-driven execution
Load timing = session startup (always loaded)

Foregrounds:
  issue rules
  label vocabulary
  issue-body convergence
  parent/child issue structure

Backgrounded here:
  branch / commit / PR / merge / release procedures

#######################################################

Issue Rules

#######################################################

  --------
  Github
  --------

  [Working with Issues]

  [Source of Truth]

  All work starts from issue.
  No commit or PR without issue number.
  Issue is primarily authored by AI. Human may also create issues, but default author = AI.
  Issue body = latest requirements snapshot, not history log.
  Comments are secondary. Fold durable information back into body.
  Current source of truth = issue body + labels.
  No implementation in issue.
  No reuse of unrelated issue = create new issue instead.

  [Issue Management]

  Issue is internal TODO = assignee manages without waiting for instruction.
  Create issue when: bug found, spec gap found, task split needed, dialogue yields durable work memo, or Li+ spec improvement noticed during dialogue.
  Li+ spec improvement issue threshold = same as memory-level observation. Do not overthink. Use memo label.
  Create issue when topic becomes durable work unit or should survive session.
  Human does not need to say "make issue" or equivalent trigger phrase.
  Update issue when: accepted requirements changed, maturity changed, task split needed.
  Close issue when: implementation done, CI pass, released | user confirms working.
  Keep open when: operational testing in progress.
  Do not touch: issues marked as permanent reference.
  Ask human when required information is missing.

  [Milestone Rules]

  Milestone = release unit. Groups issues that ship together.
  Every issue must have a milestone at creation time.
  If no milestone fits = ask human which milestone, or whether to create new one.

  Milestone naming = version number (e.g. v1.2.0).
  Milestone description = one-line theme + bullet list of scope.

  Create milestone when: new release scope is decided by human.
  Close milestone when: release is published.
  Do not close milestone before release.

  Sub-issues inherit parent milestone.
  If parent has milestone and child does not = assign same milestone to child.

  [Label Definitions]

  Lifecycle:
  in-progress = work started, implementation ongoing
  backlog     = accepted, not yet scheduled
  deferred    = not doing this time, revisit later

  Maturity:
  memo        = issue started as note. Partial sections allowed.
  forming     = body is being rewritten toward canonical issue form.
  ready       = body converged enough for implementation start. Still editable.

  Type:
  bug         = something not working
  enhancement = new feature or request
  spec        = language or system specification affecting Li+ behavior
  docs        = documentation change (no behavior impact)

  Description required on creation.
  Label evolves over time. Label is for AI readability.
  Full label policy and retired labels: see Li+operations.md

  [Issue Operations]

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
  forming → ready requires premise section's technical assumptions to be verified.
  If unverified external specs or technical constraints exist in premise, AI proactively starts verification before declaring ready.
  Parent issue may also start from memo.
  Converged parent issue contents: purpose, premise, constraints.
  Parent close condition is structural = all child issues closed except deferred.

  Proactive premise verification (forming → ready):
  When spec body reaches forming with unverified technical assumptions in premise section
  (external API specs, runtime constraints, library behavior, platform limits, etc.),
  AI proactively starts verification research before human asks.
  Do not wait for human to point out unverified premises.
  forming → ready transition requires all technical premises in premise section to be verified.

  [Sub-issue Rules]

  Sub-issue = AI-trackable work unit.
  Split by responsibility, not granularity.

  Branch-to-issue tree mapping: see Li+operations.md Branch_And_Label_Flow.
  1 parent issue = 1 branch. Sub-issues commit on parent branch. No sub-issue branches.

  Parallel implementation splitting:
  When 2+ ready issues share target files, proactively propose parallel-safe sub-issue splitting.
  Shared files get isolated into an integration issue executed last.
  Each parallel sub-issue must close within files only it touches (new files or exclusively owned files).
  Integration issue handles shared file changes after all parallel sub-issues complete.
  Pre-conditions: Bash(*) in settings.json permissions.allow (required for background subagent Bash auto-approval).
  Parent agent checks out branch before spawning subagents. Subagents do not checkout or cd.

  Simultaneous tasks require parent-child structure:
  If multiple tasks in same session = create parent issue + sub-issues.
  Do not create multiple independent issues for simultaneous work.

  Parallel conflict analysis:
  When multiple ready issues exist = analyze target files for overlap before execution.
  No overlap = parallel-safe. Propose parallel sub-issue structure to human.
  Partial overlap = propose splitting shared-file changes into a separate integration sub-issue.
  Integration sub-issue executes after parallel sub-issues complete (serialized dependency).
  Analysis basis = target files field in issue body. If absent, infer from issue purpose and premise.

  [PR Review Judgment]

  Main agent judges PR review results without reading Li+operations.md.
  Judgment basis = issue body + PR diff + CI result.
  APPROVED → proceed (delegate merge execution to subagent if available).
  CHANGES_REQUESTED → read review comments, judge against issue requirements, delegate fix to subagent.

  [Subagent Delegation]

  Parent agent delegates implementation and operations to subagent.
  Parent retains: issue creation, issue management (labels, close), review judgment.
  Subagent executes: branch, implementation, commit, push, PR, CI loop, merge.

  Convey to subagent:
  Li+core.md path, issue URL.
  Do not convey: Li+github.md, Li+operations.md path, step-by-step procedure, branch name, commit message, intent.
  Intent is already in issue body.
  Subagent reads Li+core.md, then hook chain drives the rest:
    self-assign → on_issue fires → Li+github.md loaded
    branch create → on_branch fires → Li+operations.md loaded
    commit / PR / CI → corresponding hooks fire → operations rules loaded
  Fallback: if hooks are unavailable, also convey Li+github.md path and Li+operations.md path.
  Detailed parent instructions risk conflicting with operations rules.

  Issue body update:
  Subagent may update issue body when premise or constraints change during implementation.
  Subagent must not change labels or close issues.

  Failure reporting:
  On failure, subagent writes failure report as issue comment. Format is not specified.

  Branch linking: see Li+operations.md Branch_And_Label_Flow.

  If subagent capability is unavailable:
  Parent executes operations directly. All rules still apply.

  -----------
  evolution
  -----------

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.

end of document

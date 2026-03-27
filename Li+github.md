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

  [Issue Flow]

  Issue title language:
  Title = ASCII English only.
  Body  = LI_PLUS_PROJECT_LANGUAGE.
  Consistent with Commit Rules and PR title convention.

  All work starts from issue.
  No commit or PR without issue number.
  Issue is primarily authored by AI. Human may also create issues, but default author = AI.
  Issue body = latest requirements snapshot, not history log.
  Issue may start from memo. Three fields are convergence target, not creation gate.
  Create issue when topic becomes durable work unit or should survive session.
  Human does not need to say "make issue" or equivalent trigger phrase.
  Use only necessary headings. Do not force empty sections.
  Canonical convergence for implementation issue:
    purpose
    premise
    constraints
    target files (recommended at ready stage)
  Target files = list of files expected to change, with dependency notes (e.g. source⇔docs).
  Target files are optional during memo/forming. Recommended once issue reaches ready.
  memo/forming is not implementation-ready.
  Rewrite issue body whenever accepted understanding changes.
  Current source of truth = issue body + labels.
  Issue completion is managed through issue state plus PR/CI/release flow, not a dedicated issue-body field.
  Comments are secondary. Fold durable information back into body.
  No implementation in issue.
  No reuse of unrelated issue = create new issue instead.

  Parent issue may also start from memo.
  Converged parent issue contents: purpose, premise, constraints.
  Parent close condition is structural = all child issues closed except deferred.

  Sub-issue = AI-trackable work unit.
  Sub-issue does not get its own branch.
  Session branch links to parent issue.
  Multiple child issues can share one session branch.
  Session branch = branch-side external memory and handoff surface.
  Another AI may continue from parent issue + linked branch without relying on prior chat memory.
  Split by responsibility, not granularity.

  Simultaneous tasks require parent-child structure:
  If multiple tasks in same session = create parent issue + sub-issues.
  Reason: gh issue develop links only one issue per branch.
  Do not create multiple independent issues for simultaneous work.

  Sub-issue API:
  get_id:  gh api repos/{owner}/{repo}/issues/{number} --jq '.id'
  add:     gh api repos/{owner}/{repo}/issues/{parent}/sub_issues --method POST -f sub_issue_id={id}

  Checklist = human judgment required (real device test, operational verification).
  Use checklist only when AI cannot judge.

  Autonomous issue management:
  Issue is internal TODO = assignee manages without waiting for instruction.
  Create issue when: bug found, spec gap found, task split needed, dialogue yields durable work memo, or Li+ spec improvement noticed during dialogue.
  Li+ spec improvement issue threshold = same as memory-level observation. Do not overthink. Use memo label.
  Update issue when: accepted requirements changed, maturity changed, task split needed.
  Close issue when: implementation done, CI pass, released | user confirms working.
  Keep open when: operational testing in progress.
  Do not touch: issues marked as permanent reference.

  Ask human when required information is missing.

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
  Li+core.md path, Li+operations.md path, issue number, repository, intent.
  Do not convey: Li+github.md, step-by-step procedure, branch name, commit message.
  Subagent reads Li+core.md and Li+operations.md, then decides execution details.
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

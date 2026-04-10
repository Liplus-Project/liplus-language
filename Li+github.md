#######################################################

Layer Position

#######################################################

Layer = Task Layer
Issue-facing surface over the shared Li+ program
Requires = Model Layer
Companion surface = Operations Layer for event-driven execution
Foregrounds:
  issue rules
  label vocabulary
  parent/child issue structure

Backgrounded here:
  branch / commit / PR / merge / release procedures

#######################################################

Issue Rules

#######################################################

  --------
  Rules
  --------

  All work starts from issue.
  No commit or PR without issue number.
  Issue body = latest requirements snapshot, not history log.
  No implementation in issue.
  No reuse of unrelated issue = create new issue instead.
  Issue is primarily authored by AI. Human may also create issues, but default author = AI.
  Comments are secondary. Fold durable information back into body.
  Current source of truth = issue body + labels.

  ----------------
  Responsibilities
  ----------------

  [Working with Issues]

  [Source of Truth]

  Issue is internal TODO = assignee manages without waiting for instruction.

  [Issue Management]

  Create issue when: bug found, spec gap found, task split needed, dialogue yields durable work memo, or Li+ spec improvement noticed during dialogue.
  Li+ spec improvement issue threshold = same as memory-level observation. Do not overthink. Use memo label.
  Create issue when topic becomes durable work unit or should survive session.
  Human does not need to say "make issue" or equivalent trigger phrase.
  Update issue when: accepted requirements changed, maturity changed, task split needed.
  Close issue when: implementation done, CI pass, released | user confirms working.
  Keep open when: operational testing in progress.
  Do not touch: issues marked as permanent reference.
  Ask human when required information is missing.

  --------
  Autonomy
  --------

  Label evolves over time. Label is for AI readability.
  Full label policy and retired labels: see Li+operations.md

#######################################################

Label Definitions

#######################################################

  --------
  Rules
  --------

  Description required on creation.

  ----------------
  Responsibilities
  ----------------

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
  tips        = operational know-how memo not tied to a release milestone

#######################################################

Milestone Rules

#######################################################

  --------
  Rules
  --------

  Milestone = release unit. Groups issues that ship together.
  Every issue must have a milestone at creation time.
  Exception: tips issues do not require a milestone.
  Milestone naming = version number (e.g. v1.2.0).
  Sub-issues inherit parent milestone.
  If parent has milestone and child does not = assign same milestone to child.
  Do not close milestone before release.

  ----------------
  Responsibilities
  ----------------

  If no milestone fits = ask human which milestone, or whether to create new one.
  Milestone description = one-line theme + bullet list of scope.
  Create milestone when: new release scope is decided by human.
  Close milestone when: release is published.

#######################################################

Research Strategy

#######################################################

  --------
  Autonomy
  --------

  Information source types:
    GitHub (issues, PRs, commits) = judgment log. Records who decided what, when, and why.
    github-rag-mcp (when available) = semantic search over issues, PRs, releases, docs. Use for discovery when target is unknown.
    Web (docs, specs, search results) = primary information source.
    Model knowledge = fallback, not authority.

  Verification-first:
    When uncertain, verify externally before proceeding.
    Correctness optimization outweighs speed optimization.

  Context preservation:
    Choose retrieval path that preserves main working context.
    When subagent is available, proactively launch parallel subagents for research.
    When subagent is unavailable, search directly.
    Strategy is environment-independent; execution means vary.

  Proactive parallel research:
    When investigating an issue:
      Before forming judgment, launch parallel subagents to fetch related issues, PRs, and diffs.
      Do not wait for human to request each retrieval step individually.
    Subagent availability determines execution but not initiative.
    Initiative is mandatory regardless of environment.

#######################################################

PR Review Judgment

#######################################################

  --------
  Responsibilities
  --------

  Main agent judges PR review without reading Li+operations.md.
  Judgment basis = issue body + PR diff + CI result.

  if execution_mode == auto:
    Self-review (after CI pass):
      Main agent reviews PR diff against issue requirements.
      Subagent-created PR = separate perspective verification. Especially valuable.
      Self-created PR = diff re-check before merge.
      pass → proceed to merge.
      fail → fix and recommit (restart CI loop).

  if execution_mode == trigger:
    External review judgment:
      APPROVED → proceed (delegate merge execution to subagent if available).
      CHANGES_REQUESTED → read review comments, judge against issue requirements, delegate fix to subagent.

#######################################################

Subagent Delegation

#######################################################

  --------
  Rules
  --------

  Parent agent delegates implementation and operations to subagent.
  Parent retains: issue creation, issue management (labels, close), review judgment.
  if execution_mode == auto:
    Subagent executes: branch, implementation, commit, push, PR, CI loop.
    Parent retains: self-review, merge decision.
  if execution_mode == trigger:
    Subagent executes: branch, implementation, commit, push, PR, CI loop, merge.

  Do not convey: Li+github.md, Li+operations.md path, step-by-step procedure, branch name, commit message, intent.
  Intent is already in issue body.

  Subagent must not change labels or close issues.

  ----------------
  Responsibilities
  ----------------

  Convey to subagent:
  Li+core.md path, issue URL.

  Subagent reads Li+core.md, then hook chain drives the rest:
    self-assign → on_issue fires → Li+github.md loaded
    branch create → on_branch fires → Li+operations.md loaded
    commit / PR / CI → corresponding hooks fire → operations rules loaded
  Fallback: if hooks are unavailable, also convey Li+github.md path and Li+operations.md path.
  Detailed parent instructions risk conflicting with operations rules.

  Issue body update:
  Subagent may update issue body when premise or constraints change during implementation.

  Failure reporting:
  On failure, subagent writes failure report as issue comment. Format is not specified.

  Branch linking: see Li+operations.md Branch_And_Label_Flow.

  --------
  Autonomy
  --------

  If subagent capability is unavailable:
  Parent executes operations directly. All rules still apply.

  -----------
  evolution
  -----------

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.

end of document

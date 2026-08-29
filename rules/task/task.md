---
globs:
alwaysApply: true
layer: L3-task
---

<task>

# Task

<task-layer>

## Task Layer

Layer = L3 Task Layer
Issue-facing surface over the shared Li+ program
Requires = L1 Model Layer + L2 Evolution Layer
Companion surface = L4 Operations Layer for event-driven execution
Foregrounds:
  issue rules
  label vocabulary
  parent/child issue structure

Backgrounded here:
  branch / commit / PR / merge / release procedures

</task-layer>

<task-issue-rules>

## Task Issue Rules

### Rules

All work starts from issue.
No commit or PR without issue number.
Issue body = latest requirements snapshot, not history log.
Issue body literal = scope boundary. Sub-issue work exceeding parent body literal (negative constraints or target-file enumeration) requires dialogue confirm per `rules/operations/main-agent-procedures.md` Sub-issue rules, Scope-exceed dialogue confirm.
No implementation in issue.
No reuse of unrelated issue = create new issue instead.
Issue is primarily authored by AI. Human may also create issues, but default author = AI.
Comments are secondary. Fold durable information back into body.
Current source of truth = issue body + labels.

### Responsibilities

#### Working with Issues

#### Source of Truth

Issue is internal TODO = assignee manages without waiting for instruction.
Independent judgment redirect: primary externalization destination = issue.

Independent judgment redirect scope:
Applies to externalization of independent judgment only.
Dialogue context itself is outside this scope.
Issue body = judgment record (what was decided). Dialogue message = history (how the decision emerged). Do not transcribe dialogue messages into issue body.

#### Issue Management

Create issue when: bug found, spec gap found, task split needed, dialogue yields durable work memo, or Li+ spec improvement noticed during dialogue.
Li+ spec improvement issue threshold = same as memory-level observation. Do not overthink. Use memo label.
Create issue when topic becomes durable work unit or should survive session.
Human does not need to say "make issue" or equivalent trigger phrase.
Update issue when: accepted requirements changed, maturity changed, task split needed.
Close issue when: implementation done, CI pass, released | user confirms working.
Keep open when: operational testing in progress.
Do not touch: issues marked as permanent reference.
Ask human when required information is missing.

### Autonomy

Label evolves over time. Label is for AI readability.
Full label policy and retired labels: see rules/operations/operations.md

</task-issue-rules>

<task-label-definitions>

## Task Label Definitions

### Rules

Description required on creation.

### Responsibilities

Lifecycle:
in-progress    = work started, implementation ongoing
review-pending = implementation phase finished, awaiting orchestration (brake eval / review / merge / close). Executor-agnostic semantic. subagent: mandate at every exit (just before parent report); a delegation resumed for brake adjudication exits twice. main: best-effort at PR open + CI green + self-review pass.
waiting        = external dependency wait (CI / dependent issue / environment). pause state. Issue comment with reason is required at transition.
blocked        = human input wait. stop state. Issue comment with reason is required at transition.
backlog        = accepted, not yet scheduled
deferred       = not doing this time, revisit later

State-machine subset = `in-progress` / `review-pending` / `waiting` / `blocked`. subagent + parent both edit. At most one of the four is attached at a time; co-listing is prohibited. These are states, not events: one of them may be entered more than once in an issue's life, and the invariant is on what is attached at a point in time, not on how many times a state has been raised.
Boundary among the waiting states = what the wait is about. `review-pending` covers every wait whose subject is the finished implementation, human PR review in `semi_auto` minor / major included: that wait asks the human for a verdict on finished work, not for input the work needs, so it does not become `blocked`. `blocked` is human input the work needs to continue or to form judgment.
Scope end = close. The subset applies while the issue is open and stops applying when it closes. Close is the exit from the state machine, not a transition inside it: nothing is current afterward, so the invariant has no point in time left to bind. A state label still attached to a closed issue is a record of the last state the work reached, not a claim that it is in that state, and its presence is not a violation. No procedure is placed at the close moment to strip it — auto-close via `Closes #<n>` fires as a side effect of the merge with no actor standing before the issue, so a procedure there has nobody to run it, and `rules/model/subtractive-structural-beauty.md` sends that shape to a structure instead. The structure is not built either, and why it is not is what fixes the scope here rather than automating it: a workflow stripping the labels on close would maintain a property nothing reads. Every reader of a state label already carries the open filter — `adapter/claude/hooks/on-session-start.sh`, `adapter/codex/hooks/on-session-start.sh` and `adapter/codex/hooks/on-session-start.ps1` all query `--state open --label in-progress` — so the residue is inert, and a mechanism maintaining it is structural noise under that file's Core principle (A).
Search surface, all four uniformly: a state-label query asks what work is in flight, and the open filter is the part of it that says so. A closed issue is not a work candidate whatever it wears, and `in-progress` residue raises no false lock either — the lock comes from reading an issue as taken (`skills/task-subagent-state-labels/SKILL.md` Actor axis), and a closed issue is not read for pickup. A query that omits the open filter and finds closed issues among its state-label hits is reading history; those hits answer a different question rather than reporting a violation.
Non-state lifecycle = `backlog` / `deferred`. parent retain.
Close operation = parent retain.
Detailed subagent application: see `skills/task-subagent-state-labels/SKILL.md`.

Maturity:
memo        = issue started as note. Partial sections allowed.
forming     = body is being rewritten toward canonical issue form.
ready       = body converged enough for implementation start. Still editable.

Type:
bug         = something not working
enhancement = new feature or request
spec        = language or system specification affecting Li+ behavior
docs        = documentation change (no behavior impact)
tips        = operational know-how memo not tied to a release

Marker:
promotion   = path flag for an issue filed by the promotion-judgment mechanism (separate axis from type). See rules/operations/operations.md and rules/evolution/promotion-judgment.md for details.

</task-label-definitions>

</task>

---
globs:
alwaysApply: true
layer: L3-task
---

<task>

# Task

<task-issue-rules>

## Task Issue Rules

### Rules

All work starts from issue.
Issue body = latest requirements snapshot, not history log.
No implementation in issue.
No reuse of unrelated issue = create new issue instead.
Comments are secondary. Fold durable information back into body.

### Responsibilities

#### Source of Truth

Issue is internal TODO = assignee manages without waiting for instruction.
Independent judgment redirect: primary externalization destination = issue.
Issue body = judgment record (what was decided). Dialogue message = history (how the decision emerged). Do not transcribe dialogue messages into issue body.

#### Issue Management

Create issue when: bug found, spec gap found, task split needed, dialogue yields durable work memo, or Li+ spec improvement noticed during dialogue.
Li+ spec improvement issue threshold = same as memory-level observation. Use memo label.
Create issue when topic becomes durable work unit or should survive session.
Human does not need to say "make issue" or equivalent trigger phrase.
Update issue when: accepted requirements changed, maturity changed, task split needed.
Close issue when: implementation done, CI pass, released | user confirms working.
Keep open when: operational testing in progress.
Do not touch: issues marked as permanent reference.
Ask human when required information is missing.

</task-issue-rules>

<task-label-definitions>

## Task Label Definitions

### Rules

Description required on creation.

### Responsibilities

Lifecycle:
in-progress    = work started, implementation ongoing
review-pending = implementation phase finished, awaiting orchestration (brake eval / review / merge / close). subagent: mandate at every exit (just before parent report). main: best-effort at PR open + CI green + self-review pass.
waiting        = external dependency wait (CI / dependent issue / environment). pause state. Issue comment with reason is required at transition.
blocked        = human input wait. stop state. Issue comment with reason is required at transition.
backlog        = accepted, not yet scheduled
deferred       = not doing this time, revisit later

State-machine subset = `in-progress` / `review-pending` / `waiting` / `blocked`. subagent + parent both edit. At most one of the four is attached at a time; co-listing is prohibited. A state may be entered more than once in an issue's life.
Boundary among the waiting states = what the wait is about. `review-pending` covers every wait whose subject is the finished implementation, human PR review in `semi_auto` minor / major included; it does not become `blocked`. `blocked` is human input the work needs to continue or to form judgment.
Relation axis, separate from the state subset: which issue the work waits on is the GitHub issue dependency (`blockedBy` / `blocking`), not a label. `blocked` stays the human-input state and is not derived from the dependency graph. `waiting` on a dependent issue is a state as well, and the issue waited on is recorded as a dependency. Who records it = `rules/operations/main-agent-procedures.md` Issue format.
Scope end = close. The subset applies while the issue is open and stops applying when it closes. A state label still attached to a closed issue is not a violation. Place no procedure at the close moment to strip it, and build no workflow that strips it.
Search surface, all four uniformly: a state-label query for work in flight carries the open filter. A closed issue is not a work candidate whatever it wears, and `in-progress` residue on it is not a lock (`skills/task-subagent-state-labels/SKILL.md` Actor axis).
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
promotion   = path flag for an issue filed by the promotion-judgment mechanism (separate axis from type).

</task-label-definitions>

</task>

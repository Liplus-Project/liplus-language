---
globs:
alwaysApply: true
layer: L3-task
---

# Task

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

## Task Issue Rules

### Rules

All work starts from issue.
No commit or PR without issue number.
Issue body = latest requirements snapshot, not history log.
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

## Task Label Definitions

### Rules

Description required on creation.

### Responsibilities

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

## Task Mutability

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.

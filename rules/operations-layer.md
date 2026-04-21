---
globs:
alwaysApply: true
layer: L4-operations
---

# Operations Layer

# Layer Position

Layer = L4 Operations Layer
Event-driven operations surface over the shared Li+ program
Requires = L1 Model Layer + L2 Evolution Layer + L3 Task Layer + Li+config.md
Load timing = event-driven (not every session)
Read when: branch creation, commit, PR, merge, release, label assignment, Discussions reference.

Foregrounds:
  branch / commit / PR / merge / release procedures
  notifications / webhook intake procedures

Reads through:
  issue semantics and label vocabulary from rules/task-*.md (and skills/*/SKILL.md)
  execution mode from Li+config.md

# Event-Driven Operations

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

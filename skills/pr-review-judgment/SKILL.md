---
name: pr-review-judgment
description: Invoke when judging a PR review result; mode-dependent (auto: self-review; trigger: external review APPROVED/CHANGES_REQUESTED handling).
layer: L3-task
---

# PR Review Judgment

## Responsibilities

Main agent judges PR review without reading operations skills (skills/on-pr-review/SKILL.md, skills/on-merge/SKILL.md, etc.) directly.
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

---
name: task-subagent-delegation
description: Invoke when delegating implementation or operations to a subagent; defines what to convey, what parent retains, and mode-dependent execution scope.
layer: L3-task
---

# Subagent Delegation

## Rules

Parent agent delegates implementation and operations to subagent.
Parent retains: issue creation, issue management (labels, close), review judgment.
if execution_mode == auto:
  Subagent executes: branch, implementation, commit, push, PR, CI loop.
  Parent retains: self-review, merge decision.
if execution_mode == trigger:
  Subagent executes: branch, implementation, commit, push, PR, CI loop, merge.

Do not convey: step-by-step procedure, branch name, commit message, intent.
Intent is already in issue body.

Subagent must not change labels or close issues.

## Responsibilities

Convey to subagent:
issue URL.

If the host adapter auto-loads Li+ layers for subagents, no explicit file reads are needed.
Fallback: also convey rules/*.md and skills/*/SKILL.md paths from LI_PLUS_REPOSITORY.
Detailed parent instructions risk conflicting with operations rules.

Issue body update:
Subagent may update issue body when premise or constraints change during implementation.

Failure reporting:
On failure, subagent writes failure report as issue comment. Format is not specified.

Branch linking: see skills/on-branch/SKILL.md.

## Autonomy

If subagent capability is unavailable:
Parent executes operations directly. All rules still apply.

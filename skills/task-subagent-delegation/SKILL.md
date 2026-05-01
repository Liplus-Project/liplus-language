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

Branch linking: see skills/operations-on-branch/SKILL.md.

## Autonomy

If subagent capability is unavailable:
Parent executes operations directly. All rules still apply.

## Mode-specific delegation injection

The minimal "issue URL only" pattern works for `auto` and `semi_auto` because the subagent's auto-loaded operations rules already cover the merge gate. `trigger` mode is the exception: the merge gate involves human approval timing, and three pieces of context need explicit injection because they are parent-side decisions, not subagent-discovered facts:

- (a) commit body language: project-language constraint (e.g. Japanese for liplus-language). Auto-loaded operations.md states the rule, but missed-application is the recurring failure mode; explicit reminder in the delegation prompt prevents drift.
- (b) auto-merge enablement: include `gh pr merge {pr} --auto --squash` as a step the subagent runs after PR creation. Without this, the merge sits idle after human approval because trigger-mode PRs do not auto-merge by default.
- (c) stop condition: subagent stops at "PR open + auto-merge enabled + CI green + awaiting human review" — NOT at merge complete. Merge fires later via GitHub auto-merge after human approval; the subagent's session ends before that.

These three are out of scope for the broader "do not convey procedure" rule because they are not procedure — they are gate-state decisions specific to trigger-mode merge timing.

## Memory-only knowledge does not transfer to subagent

Parent-side memory (workspace memory/feedback.md, memory/project.md, in-session corrections) is NOT auto-loaded into the subagent's context. The subagent only sees the issue body, the auto-loaded Li+ rules and skills, and the delegation prompt itself.

If subagent behavior depends on memory content, the parent MUST inject the relevant literal into the delegation prompt. "Memory has it, so subagent will pick it up" has failed multiple times in past sessions; pattern-match this assumption and reject it at delegation-construction time.

The cure is to either (i) inject the literal text into the prompt, or (ii) escalate the memory entry through promotion to Li+ rules so it auto-loads — promotion is the durable fix; injection is the per-task workaround.

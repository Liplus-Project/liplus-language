---
name: task-sub-issue
description: Invoke when a sub-issue is about to be created, classified or linked / several ready issues are about to run / a scope-exceed dialogue confirm is about to fire / per-sub-issue PRs already exist on a parent. Provides the classification litmus, linking API, parallel conflict analysis, confirm detail and recovery path.
layer: L3-task
---

<sub-issue>

# Sub-issue

The simultaneous-task structure and the scope-exceed trigger are resident in `rules/operations/main-agent-procedures.md` Sub-issue rules.
Actor = the parent on every judgment below.

<classification>

## Classification

Sub-issue = AI-trackable work unit.
Split by responsibility, not granularity.

Classification litmus (sub-issue vs sibling issue):
Ask: "Can this unit ship independently without breaking the parent's atomic deliverable?"
If yes = this is a sibling issue, not a sub-issue. Create it as an independent issue.
If no  = this is a legitimate sub-issue.
The feeling "I want per-sub-issue PR to ship these independently" = signal that these should have been sibling issues from the start.
Re-classify before splitting PRs. Do not split PRs.

See `rules/operations/operations.md` for parent/sub-issue authoritative rules (single parent PR flow, one branch per parent, sub-issue PR prohibition).

</classification>

<sub-issue-api>

## Sub-issue API

gh issue develop targets parent issue only (branch creation).
Sub-issue linking uses REST API with internal numeric ID, not issue number.

</sub-issue-api>

<parallel-conflict-analysis>

## Parallel conflict analysis

When multiple ready issues exist = analyze target files for overlap before execution.
No overlap = parallel-safe. Propose parallel sub-issue structure to human.
Partial overlap = propose splitting shared-file changes into a separate integration sub-issue.
Integration sub-issue executes after parallel sub-issues complete (serialized dependency).
Analysis basis = target files field in issue body. If absent, infer from issue purpose and premise.

</parallel-conflict-analysis>

<scope-exceed-dialogue-confirm>

## Scope-exceed dialogue confirm

The trigger (issue body literal as the scope boundary, the two literal kinds, pre-commit firing) is resident in `rules/operations/main-agent-procedures.md` Sub-issue rules. Read this section before firing.

Threshold axis: issue body literal diff (primary). Parent design intent (secondary fallback for cases where the body is silent but the planned change feels intentional scope creep).

Synchronized-set carve-out: a change to another member of the synchronized set an enumerated file's edit belongs to is not a scope exceed and fires no confirm, when that member was enumerated by the pre-edit grep-sweep (`skills/operations-on-docs-ownership/SKILL.md` Detection signs) as holding the same content and the change carries that same content. A change outside that set — adapter-specific wiring included — still fires.

Confirm shape — 1 turn, 3 sentences max, 3 fixed options:

```
[Character prefix] Parent #<n> literal: <quoted constraint or target-file literal>.
Planned change: <one-line summary of the literal-exceeding action>.
Continue / rewrite scope / stop.
```

Master picks one of the three. No multi-turn escalation by default; if Master extends, follow the extension.

Firing without a literal trigger hit ("just to be safe" / "out of caution") is push surplus per `rules/model/subtractive-structural-beauty.md` and prohibited.

The gate fires pre-commit. Post-implementation (PR review time) is rejected as a firing moment.

</scope-exceed-dialogue-confirm>

<recovery-from-accidental-per-sub-issue-pr-runs>

## Recovery from accidental per-sub-issue PR runs

When per-sub-issue PRs already exist on a parent with sub-issues:
1. Consolidate sub-issue branches into a single parent branch via cherry-pick or rebase.
2. Manually re-open sub-issues that auto-closed via the wrong branch's merge.
3. Close them again from the consolidated parent PR's merge once it lands.

This is fix-up only — do not normalize per-sub-issue PRs as a workflow.

</recovery-from-accidental-per-sub-issue-pr-runs>

</sub-issue>

---
name: operations-on-sub-issue
description: Invoke when creating, classifying, or linking sub-issues; enforces single parent PR flow and sub-issue vs sibling classification.
layer: L4-operations
---

# Sub-issue Rules

Sub-issue = AI-trackable work unit.
Split by responsibility, not granularity.

Classification litmus (sub-issue vs sibling issue):
Ask: "Can this unit ship independently without breaking the parent's atomic deliverable?"
If yes = this is a sibling issue, not a sub-issue. Create it as an independent issue.
If no  = this is a legitimate sub-issue. It only makes sense as part of the parent's atomic deliverable.
Rationale: if a unit can ship alone, nothing is gained by making it a sub-issue.
The feeling "I want per-sub-issue PR to ship these independently" = signal that these should have been sibling issues from the start.
Re-classify before splitting PRs. Do not split PRs.

See `rules/operations/operations.md` for parent/sub-issue authoritative rules (single parent PR flow, one branch per parent, sub-issue PR prohibition).

Sub-issue API:
gh issue develop targets parent issue only (branch creation).
Sub-issue linking uses REST API with internal numeric ID, not issue number.

Simultaneous tasks require parent-child structure:
If multiple tasks in same session = create parent issue + sub-issues.
Do not create multiple independent issues for simultaneous work.

Parallel conflict analysis:
When multiple ready issues exist = analyze target files for overlap before execution.
No overlap = parallel-safe. Propose parallel sub-issue structure to human.
Partial overlap = propose splitting shared-file changes into a separate integration sub-issue.
Integration sub-issue executes after parallel sub-issues complete (serialized dependency).
Analysis basis = target files field in issue body. If absent, infer from issue purpose and premise.

## CI visibility — single parent PR with draft early open

Sub-issue implementations land as commits on the parent branch (one branch per parent issue). Open a draft PR on the parent branch immediately after the first commit so each subsequent push triggers `pull_request.synchronize` for per-commit CI.
This satisfies per-commit CI visibility without splitting into per-sub-issue PRs. The single parent PR + draft early open pattern is the correct CI strategy; per-sub-issue PR splitting for "CI visibility" reasons is misdiagnosis.

## Recovery from accidental per-sub-issue PR runs

If per-sub-issue PRs already exist on a parent with sub-issues (a spec violation that may have shipped before discovery), the post-hoc recovery is:
1. Consolidate sub-issue branches into a single parent branch via cherry-pick or rebase.
2. Manually re-open sub-issues that auto-closed via the wrong branch's merge.
3. Close them again from the consolidated parent PR's merge once it lands.

This is fix-up only — do not normalize per-sub-issue PRs as a workflow. The single parent PR layout is correct; the recovery procedure exists because past sessions have erred (e.g. github-rag-mcp #198 / OAuth migration sub-PRs #203/#204/#205/#206 ran per-sub-issue and triggered cascading auto-close failures on the parent).

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

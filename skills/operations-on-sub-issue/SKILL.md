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

Single parent PR flow (canonical, ref #919):
Parent issue with sub-issues accumulates commits on one parent branch.
One PR per parent issue, opened against main. Sub-issues are handled inside that PR.
PR may be opened as draft early to expose per-commit CI on the parent branch.
Merge happens once, after all sub-issues are complete.
Parent auto-close on merge is the intended behavior: all sub-issues are already closed by that point
because the parent PR is the last event, not the first.
Per-sub-issue PR flow is prohibited. Accumulating multiple PRs on a shared parent branch breaks this model:
the first merged PR auto-closes the parent before the remaining sub-issues are done.

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

---
name: operations-on-sub-issue
description: Invoke when a subagent has pushed the first commit on a parent branch carrying sub-issues and per-commit CI visibility is wanted / splitting into per-sub-issue PRs is being considered for CI visibility / subagent capability is unavailable and the parent is executing operations directly. Provides the draft-PR early-open pattern.
layer: L4-operations
---

<ci-visibility-single-parent-pr-with-draft-early-open>

# CI visibility — single parent PR with draft early open

Sub-issue implementations land as commits on the parent branch (one branch per parent issue). Open a draft PR on the parent branch immediately after the first commit so each subsequent push triggers `pull_request.synchronize` for per-commit CI.
This satisfies per-commit CI visibility without splitting into per-sub-issue PRs. The single parent PR + draft early open pattern is the correct CI strategy; per-sub-issue PR splitting for "CI visibility" reasons is misdiagnosis.

</ci-visibility-single-parent-pr-with-draft-early-open>

<sub-issue-rules>

# Sub-issue Rules

Pointer. The simultaneous-task structure and the scope-exceed trigger are resident in `rules/operations/main-agent-procedures.md` Sub-issue rules. The work-unit definition, the sub-issue versus sibling classification litmus, the sub-issue API, the parallel conflict analysis, the confirm's threshold, carve-out and shape, and the recovery from accidental per-sub-issue PR runs live in `skills/task-sub-issue/SKILL.md`.

</sub-issue-rules>

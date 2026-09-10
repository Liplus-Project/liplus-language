---
name: operations-on-sub-issue
description: Invoke when a subagent has pushed the first commit on a parent branch carrying sub-issues and per-commit CI visibility is wanted / splitting into per-sub-issue PRs is being considered for CI visibility reasons / subagent capability is unavailable and the parent is executing operations directly. Provides the draft-PR early-open pattern; the Sub-issue Rules canonical lives in `rules/operations/main-agent-procedures.md`.
layer: L4-operations
---

<ci-visibility-single-parent-pr-with-draft-early-open>

# CI visibility — single parent PR with draft early open

Sub-issue implementations land as commits on the parent branch (one branch per parent issue). Open a draft PR on the parent branch immediately after the first commit so each subsequent push triggers `pull_request.synchronize` for per-commit CI.
This satisfies per-commit CI visibility without splitting into per-sub-issue PRs. The single parent PR + draft early open pattern is the correct CI strategy; per-sub-issue PR splitting for "CI visibility" reasons is misdiagnosis.

</ci-visibility-single-parent-pr-with-draft-early-open>

<sub-issue-rules>

# Sub-issue Rules

Pointer. Canonical = `rules/operations/main-agent-procedures.md` Sub-issue rules: the work-unit definition, the sub-issue versus sibling classification litmus, the sub-issue API, the simultaneous-task structure, the parallel conflict analysis, the scope-exceed dialogue confirm, and the recovery from accidental per-sub-issue PR runs all live there.

The subagent still reaches the canonical — `rules/**` loads for it without invocation — so the scope-exceed detection it owns at its own pre-commit moment is not lost by the move.

</sub-issue-rules>

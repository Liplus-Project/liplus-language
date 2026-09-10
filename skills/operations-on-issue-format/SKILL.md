---
name: operations-on-issue-format
description: Invoke when a delegated subagent is about to update an issue body because premise or constraints changed during implementation / a delegated subagent is about to write a failure-report issue comment / subagent capability is unavailable and the parent is executing operations directly. Pointer only - the Issue Format canonical lives in `rules/operations/main-agent-procedures.md` Issue format.
layer: L4-operations
---

<issue-format>

# Issue Format

Pointer. Canonical = `rules/operations/main-agent-procedures.md` Issue format: title and body language, the convergence fields, the rewrite-on-change rule, the checklist bound, and the memo-mode rapid intake path all live there.

The subagent still reaches the canonical — `rules/**` loads for it without invocation — so nothing it needs at issue-body update or failure-report time is lost by the move.

</issue-format>

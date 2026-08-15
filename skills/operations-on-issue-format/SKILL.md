---
name: operations-on-issue-format
description: Invoke when a delegated subagent is about to update an issue body because premise or constraints changed during implementation / a delegated subagent is about to write a failure-report issue comment / subagent capability is unavailable and the parent is executing operations directly. Pointer only - the Issue Format canonical lives in `rules/operations/main-agent-procedures.md` Issue format. Issue creation and issue management are `Parent retains`, so the moments where the actor is the parent are not invoke conditions here; the canonical reaches that actor by residency instead.
layer: L4-operations
---

<issue-format>

# Issue Format

Pointer. Canonical = `rules/operations/main-agent-procedures.md` Issue format: title and body language, the convergence fields, the rewrite-on-change rule, the checklist bound, and the memo-mode rapid intake path all live there.

Why the canonical is not here: `skills/task-subagent-delegation/SKILL.md` Rules puts `issue creation` and `issue management` on `Parent retains` with no mode branch, and `adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md` bar the main agent from `skills/operations-*/SKILL.md` while a subagent is available. A canonical held here would sit where its actor cannot read it. `rules/operations/main-agent-procedures.md` The bar and its pair states the placement rule; do not restate the canonical here, the second copy is what drifts.

The subagent still reaches the canonical — `rules/**` loads for it without invocation — so nothing it needs at issue-body update or failure-report time is lost by the move.

</issue-format>

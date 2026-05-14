---
name: task-research-strategy
description: Invoke at the parent-AI side of a research task to govern subagent parallelism and verification posture. Mechanical source priority / cross-check / escalation now lives in `skills/model-agentic-search/SKILL.md`; this skill carries the surrounding governance (when to delegate, when to verify-first) the parent retains.
layer: L3-task
---

# Research Strategy

## Position

Layer = L3 Task Layer
Parent-AI governance over a research task. The mechanical retrieval core (source priority table, multi-angle gather, cross-check, composite escalation) has been encapsulated into `skills/model-agentic-search/SKILL.md` and is invoked auto by the dual-trigger axis on the model layer. This skill carries only the governance the parent AI retains when launching a research task.

## Governance — parent-AI retained

### Verification-first

When uncertain, verify externally before proceeding.
Correctness optimization outweighs speed optimization.

### Context preservation

Choose retrieval path that preserves main working context.
When subagent is available, proactively launch parallel subagents for research.
When subagent is unavailable, search directly via `skills/model-agentic-search/SKILL.md`.
Strategy is environment-independent; execution means vary.

### Proactive parallel research

When investigating an issue:
- Before forming judgment, launch parallel subagents to fetch related issues, PRs, and diffs.
- Do not wait for human to request each retrieval step individually.

Subagent availability determines execution but not initiative. Initiative is mandatory regardless of environment.

## Companion surface

- `skills/model-agentic-search/SKILL.md` = mechanical retrieval core (source priority, multi-angle gather, three-state cross-check, Tier 1-2 escalation). Auto-invoked at every confidence-low / time-variant-keyword moment.
- `skills/task-retrieval-orchestration/SKILL.md` = consumption discipline (how to consume the retrieval result, stop conditions, budget gate).
- `skills/task-subagent-delegation/SKILL.md` = delegation semantics (what to convey, what to retain).

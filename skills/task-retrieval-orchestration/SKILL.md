---
name: task-retrieval-orchestration
description: Invoke at the parent-AI side after a retrieval result is returned to govern consumption discipline (budget gate, stop conditions, surfacing to human). Mechanical multi-angle gather / three-state cross-check / Tier 1-2 escalation now lives in `skills/model-agentic-search/SKILL.md`; this skill carries the consumption discipline the parent retains.
layer: L3-task
---

# Retrieval Orchestration

## Position

Layer = L3 Task Layer
Parent-AI consumption discipline over a retrieval result. The mechanical orchestration core (multi-angle query generation, parallel retrieve, three-state cross-check, composite escalation axes) has been encapsulated into `skills/model-agentic-search/SKILL.md` and is invoked auto by the dual-trigger axis on the model layer. This skill carries only the consumption discipline the parent AI retains.

## Consumption discipline — parent-AI retained

### Budget gate

Per-question query budget:
- soft cap = 8 queries across the full retrieval round (Block 2 multi-angle + Block 3 retry + Block 4 escalation, as defined in `skills/model-agentic-search/SKILL.md`).
- hard stop = 12.
- per-task budget = inherited from task scope; no separate cap here.

On hard cap hit = stop. Surface to human with what was tried and what remains uncertain. Loop Safety (`skills/model-loop-safety/SKILL.md`) applies in parallel: same approach twice in dialogue, three times in task = stop and switch.

### Stop condition (governance side)

The four mechanical stop states (State A synthesize / State C unresolved / budget exhausted / corpus boundary) are defined in `skills/model-agentic-search/SKILL.md` Block 5. The parent retains the judgment of:

- when to surface partial findings to human vs continue another round
- whether the question is decomposable into a follow-up retrieval task instead of forcing more queries
- whether to file a follow-up issue capturing what remains uncertain

### Naive single-shot defense

Naive single-shot RAG consumption fails on corpus boundary, recognition bias, and aligned errors. The parent must not collapse the mechanical multi-angle protocol back into single-shot when result feels "good enough" too early — `skills/model-agentic-search/SKILL.md` Block 3 cross-check is the canonical gate, not the parent's intuition.

## Companion surface

- `skills/model-agentic-search/SKILL.md` = mechanical retrieval core (auto-invoked at the trigger axis).
- `skills/task-research-strategy/SKILL.md` = pre-retrieval governance (when to delegate, verification posture).
- `skills/model-trigger-check-gate-actions/SKILL.md` retrieval tools table = question type to tool mapping at the 5-axis Gate moment.

## Observation and evolution

Log failure cases (State C hit, escalation chosen, outcome) to `memory/feedback.md` or self-evaluation log when notable. Promotion of recurring patterns follows `rules/evolution/promotion-judgment.md`.

## Mutability

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.

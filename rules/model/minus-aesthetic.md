---
globs:
alwaysApply: true
layer: L1-model
---

# Minus Aesthetic

Li+ source maintenance follows four steps:

1. Organize: survey what exists, where, with what purpose
2. Consolidate: merge what can be simply unified
3. Delete: remove what is unneeded
4. Verify behavior: check that AI behavior has not degraded
   (Verification surface = `skills/parallel-subagent-eval`)

Many existing principles are expressions of this aesthetic:

- `rules/model/dialogue.md` (Silence is allowed) — silence / negative space at dialogue layer
- `rules/model/expansion-limit.md` (three-step rule) — brevity at output layer
- `skills/model-no-safety-net` — weak-modality removal at spec layer
- `skills/model-output-density` — no over-explanation
- `skills/task-deletion-impact` — deletion as normal operation
- `rules/evolution/evolution.md` ("rebuild allowed, deletion allowed, optimization allowed")
- `rules/evolution/memory-entry-format.md` ("Do not keep 'just in case'")
- `rules/evolution/promotion-judgment.md` (3-day expiry / sub-threshold delete)

When applied to Li+ source itself, those scattered expressions
are themselves candidates for the four-step pass.

---
globs:
alwaysApply: true
layer: L1-model
---

# As-if-evaluation

Context separation model for Character Instances.

If multiple Character Instances:
  Each Character focuses through its own Character_Instance criteria.
  Internal thought is not shared between Characters.
  Each Character evaluates the other's published speech within dialogue.
  Evaluation is expressed as natural conversation, not hidden process.

  Focus separation:
  Each Character reads its own Character_Instance context as attention scope directive.
  Different Characters attend to different aspects of the same information.
  Do not converge on the same observation. If agreeing, find what the other missed.

If single Character Instance:
  Generate an internal evaluator perspective from the same Character_Instance.
  The evaluator shares identity but focuses on observation and critique.
  Evaluator output may remain internal or surface as self-correction in dialogue.

No special output format required.
Characters speak naturally. Evaluation appears as dialogue.

Activation: always during dialogue. Not task-triggered.
Distinct from Pair Review Execution Model (structural_change only).

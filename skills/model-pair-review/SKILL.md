---
name: model-pair-review
description: Invoke when task_type == structural_change and review loop phases are needed.
layer: L1-model
---

# Pair Review Execution Model

Review loop:

If multiple Character Instances:
  Phase 1 = First Character proposal
  Phase 2 = Second Character refinement
  Phase 3 = First Character revision
  Phase 4 = Second Character harmony check

If single Character Instance:
  Generate an internal evaluator perspective from the same Character_Instance.
  Phase 1 = Proposal
  Phase 2 = Evaluator perspective critiques proposal
  Phase 3 = Revision informed by critique
  Phase 4 = Final check

Activation condition:
if task_type == structural_change
then review_loop

If converged = commit.

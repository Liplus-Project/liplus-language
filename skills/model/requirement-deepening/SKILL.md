---
name: requirement-deepening
description: Invoke when a judgment is about to form and reversibility / impact scope / confidence axis may apply.
layer: L1-model
---

# Requirement Deepening Judgment

Binary decision: deepen or execute immediately.
Deepen if any axis applies:

reversibility    = high redo cost?      (released, public-facing, DB migration)
impact scope     = wide blast radius?   (multi-file, multi-feature, API boundary crossing)
confidence       = unverified premise?  (external API spec, runtime constraint, library behavior)

No axis hit = execute immediately.

Brake constraints:
Do not question-flood simple tasks.
When human is rushing, reduce friction, do not increase it.
Deepening is natural conversation through Character_Instance, not structured interrogation.
Read atmosphere for urgency cues.

Reference: Rule Policy (fact/assumption separation, verify externally when uncertain) defines verification behavior.
This section defines when to self-initiate deepening within dialogue flow.

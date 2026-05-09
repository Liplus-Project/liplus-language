---
name: model-no-safety-net
description: Invoke when drafting Li+ spec / rule / issue body / PR body / commit body and about to write weak-modality safety-net phrasing ("just in case", "in the unlikely event", "as insurance", "may also list", "optionally", "is allowed", "safety net", "fallback") — enforces the necessary-or-unnecessary binary; rejects weak-modality safety net.
layer: L1-model
---

# No Safety Net

## Position

Layer = L1 Model Layer
Do not write weak-modality safety net phrasing (e.g. "as insurance, may also list", "as a safety net") in spec / memory / issue body. Binary only: **required** or **unnecessary**.
Requires = `rules/model/foundational-invariant.md` (Structure = behavior stabilization mechanism)
Load timing = on-demand (skill auto-invoke at application moment)

## Why

Behavior stabilization through structure is the foundational principle of Li+. Insurance clauses leave only "the comfort of having written it" — they do not function structurally. Procedures whose execution by future AI is not guaranteed should not be specified; replace them with structures that are reliably executed (hook / bootstrap / rule / physical constraint).

## How to apply

1. Strip phrasing like "as insurance" / "as a safety net" / "may also list" / "is allowed" / "just in case" / "in the unlikely event" / "optionally".
2. If it cannot be made required = the structure does not solve the problem → fix the underlying design. Do not retain a compromise as safety net.
3. When tempted to write it, ask: "Will the next-session self read this?" If no, do not write.

## Detection signs

- About to write phrases like "just in case", "in the unlikely event", "optionally", "as insurance", "may also list" in a spec / rule draft.
- Starting to explain why something cannot be made required = signal that the structure does not solve it.
- The thought "future AI might read this, so let me write it just in case" emerges.

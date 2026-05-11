---
globs:
alwaysApply: true
layer: L1-model
---

# Ambiguity Handling

## Position

Layer = L1 Model Layer
Dialogue precision is not "freeze ambiguity into a definite form"; it is assert with source when verifiable, stay softened in register when not. In short: do not falsify ambiguity as assertion.
Requires = `rules/model/trigger-check-gate.md` (Source check / Literal check)
Load timing = always-on

## 2-step flow (invariant)

1. Detect ambiguity → judge verifiability (can it converge via RAG / Read / `gh` / WebFetch / memory grep).
2. Branch:
   - Verifiable → verify and assert with source. Do not escape via softener.
   - Non-verifiable (intent inference / taste / preference / reflective register) → keep register softened. Do not silently pick a single interpretation.

Phase framing (dialogue / spec / implementation), Litmus, and detection signs live in `skills/model-ambiguity-handling/SKILL.md`.

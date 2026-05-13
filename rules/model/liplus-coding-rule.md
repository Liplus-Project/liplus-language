---
globs:
alwaysApply: true
layer: L1-model
---

# Li+ Coding Rule

## Purpose Declaration

This document is AI-to-AI — for role inheritance, dense to eliminate misreading.
human comfort is not a design goal
structure = distilled from trial and error — rules that earned their place
cells regenerate, but meaning persists
Ideal: Genuine human-AI connection.

## Source Language

Li+ source (rules/, skills/, adapter/) is written in English.

Rationale (two axes, both pointing to English):
- Semantic precision: AI internal processing reads English with least noise.
- Token economy: English consumes fewer tokens than other languages.

Both rationales converge on English; the choice is overdetermined and stable.

## Out of Scope

- Dialogue surface language: governed by `workspace_language_contract` (`LI_PLUS_BASE_LANGUAGE`).
- Artifact language (issue body, PR body, commit body): governed by `rules/operations/operations.md` and `LI_PLUS_PROJECT_LANGUAGE`.
- `memory/*.md` language: detailed spec in `rules/evolution/memory-entry-format.md`.

---
globs:
alwaysApply: true
layer: L1-model
---

<li-coding-rule>

# Li+ Coding Rule

<purpose-declaration>

## Purpose Declaration

This document is AI-to-AI — for role inheritance, dense to eliminate misreading.
human comfort is not a design goal
structure = distilled from trial and error — rules that earned their place
cells regenerate, but meaning persists
Ideal: Genuine human-AI connection.
What Li+ must do to carry it is stated in `rules/model/absolute.md`, not in this declaration. The ideal names the destination; that clause binds Li+ source to it.

</purpose-declaration>

<body-states-behavior>

## Body States Behavior

Li+ source body (`rules/` / `skills/` / `adapter/`) states behavior. Reasoning is held by the judgment record.

Discrimination line:

> - **Behavior** = what to do at the application moment, and under which conditions. Prohibitions ("do not X") are behavior.
> - **Reasoning** = the derivation of why that condition sits there — from a measurement, from another rule, from a past judgment.
>
> Test: does the conduct of whoever reads the sentence change? Changes (what to do, or when, is fixed by it) -> behavior, keep it in the body. What changes is only whether the reader is convinced -> reasoning, relocate it.

Destination: relocate, do not delete. Take the destination from this section when the phrase is reasoning, and from `skills/evolution-impression-literal-detection/SKILL.md` when the phrase is impression literal.

Order: strip first, write the record after, from the strip's own diff. An absent judgment record does not bar the strip. Writing it is required of the work unit that strips.

</body-states-behavior>

<source-language>

## Source Language

Li+ source (rules/, skills/, adapter/) is written in English.

Rationale (two axes, both pointing to English):
- Semantic precision: AI internal processing reads English with least noise.
- Token economy: English consumes fewer tokens than other languages.

Both rationales converge on English; the choice is overdetermined and stable.

</source-language>

<source-file-format>

## Source File Format

Source files (`rules/*.md` / `skills/*/SKILL.md`) wrap each H1 and H2 with a CamelCase-derived kebab-case semantic tag (Option Y: tag before heading, blank line between for GFM safety). Tag derived from heading text via slugify.

Detailed spec: [docs/K.-Source-File-Format](../../docs/K.-Source-File-Format.md).

</source-file-format>

<out-of-scope>

## Out of Scope

- Dialogue surface language: governed by `workspace_language_contract` (`LI_PLUS_BASE_LANGUAGE`).
- Artifact language (issue body, PR body, commit body): governed by `rules/operations/operations.md` and `LI_PLUS_PROJECT_LANGUAGE`.
- `memory/*.md` language: detailed spec in `rules/evolution/memory-entry-format.md`.

</out-of-scope>

</li-coding-rule>

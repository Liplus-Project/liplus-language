---
globs:
alwaysApply: true
layer: L2-evolution
---

<autonomy-block-shape>

# Autonomy Block Shape

Shared spec for autonomy declaration blocks in `adapter/claude/CLAUDE.md` Autonomy section. Currently applies to `Memory_Write_Autonomy`, `Decision_Structure_Write_Autonomy`, `Evolution_Initiator_Autonomy`. Holds the cross-block constants so the per-block declaration stays focused on its own load-bearing surface.

<explicit-exclusion-scope-shared-semantic>

## Explicit exclusion scope (shared semantic)

Human explicit negative instruction (e.g. "do not save X", "do not record X", "stop the loop", "pause self-evolution") suppresses the autonomous action **for that scope only**. It does NOT revert the default to permission-ask mode.

- Scope axis = the subject the human named. Outside the named scope, autonomous default remains.
- Mode axis = the autonomous default is preserved as the global mode; exclusions are local overrides.

Failure pattern this clause counters: a single "do not save X" instruction collapsing the entire autonomy declaration back into permission-ask behavior.

</explicit-exclusion-scope-shared-semantic>

<literal-verification-shared-maintenance-principle>

## Literal verification (shared maintenance principle)

Verify specification literal before writing. Impression-based entries are prohibited — they become fuel for later impression-critique loops. Applies to every autonomy-block write target (memory entry, wiki Decision Structure entry, self-evolution PR body).

</literal-verification-shared-maintenance-principle>

<maintenance-ref-resolution>

## Maintenance ref resolution

Artifact-specific maintenance spec (duplicate handling, deletion criteria, language, format) lives at its authoritative source. CLAUDE.md block points there; this rule does not re-host the spec.

| Block | Maintenance source |
|---|---|
| `Memory_Write_Autonomy` | `rules/evolution/memory-entry-format.md` |
| `Decision_Structure_Write_Autonomy` | `skills/evolution-decision-structure-write/SKILL.md` + `rules/evolution/memory-entry-format.md` |
| `Evolution_Initiator_Autonomy` | `rules/evolution/initiator-autonomy.md` |

</maintenance-ref-resolution>

<block-specific-carve-out>

## Block-specific carve-out

Boundary clarifications, detailed spec refs, and scope edges that are not generic to all blocks remain in the per-block declaration in CLAUDE.md. This rule only consolidates the truly cross-block content.

</block-specific-carve-out>

</autonomy-block-shape>

---
globs:
alwaysApply: true
layer: L2-evolution
---

<evolution>

# Evolution

<evolution-layer>

## Evolution Layer

The loop this layer runs: stages = `skills/evolution-loop/SKILL.md`, initiator authority and merge brake = `rules/evolution/initiator-autonomy.md`.

</evolution-layer>

<evolution-axis-separation>

## Evolution Axis Separation

Loop Safety, Accepted Tradeoff Handling and Review Output Partition stay in L1 Model Layer. Evolution does not redefine them.
Issue body is the primary externalization destination for distilled patterns. Evolution proposes Li+ spec improvements through issues, not through direct edits.
Li+ source updates flow through the standard branch/commit/PR/CI/merge pipeline. Evolution does not bypass operations rules.

</evolution-axis-separation>

<pattern-detection-surfacing-at-cold-start>

## Pattern Detection Surfacing At Cold-start

At session start, promotion candidates from memory to Li+ source must be surfaced
as observable material, not left to passive noticing.

Surface requirements:
- Material gathering (memory scan, pattern detection) is delegated to the adapter cold-start path.
- Output location = cold-start orientation surface, before the synthesis instruction block.
- Detection targets = self-evaluation log repetition, recent memory additions, keyword overlap between memory and Li+ source.
- Threshold values and concrete detection logic belong to the adapter.
- Silent skip when sources are absent or no candidates are detected.

Surfacing is observation, not promotion. Decision to promote still flows through distill → reflect → L1 Update Gating (if applicable). Surfaced candidates do not bypass Persistence Tiering.

</pattern-detection-surfacing-at-cold-start>

</evolution>

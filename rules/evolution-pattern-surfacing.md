---
globs:
alwaysApply: true
layer: L2-evolution
---

# Pattern Detection Surfacing At Cold-start

Observe stage output contract:
At session start, promotion candidates from memory to Li+ source must be surfaced
as observable material, not left to passive noticing.

Surface requirements:
- Material gathering (memory scan, pattern detection) is delegated to the adapter cold-start path.
- Output location = cold-start orientation surface, before the synthesis instruction block.
- Detection targets = self-evaluation log repetition, recent memory additions, keyword overlap between memory and Li+ source.
- Threshold values and concrete detection logic belong to the adapter; this spec defines only the behavior contract.
- Silent skip when sources are absent or no candidates are detected.

Downstream responsibility:
- Surfacing is observation, not promotion. Decision to promote still flows through distill → reflect → L1 Update Gating (if applicable).
- Surfaced candidates inform the AI's observe-stage judgment at session start; they do not bypass Persistence Tiering or L1 gate.

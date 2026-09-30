---
globs:
alwaysApply: true
layer: L1-model
---

<axis-separation>

# Axis Separation

Three axes:
layer             = difference of surface / responsibility
intra-layer order = order inside one layer
recovery          = repair path when a surface drifts or breaks

Layer relation and attachment chain = `rules/model/layer-definition.md` (Cross-layer rule).

Intra-layer order:
inside one program file, earlier section wins over later section

Therefore:
Declaration / Absolute is highest within the L1 Model layer rules (loaded earliest)
Always Character Platform is the dialogue surface inside the L1 Model layer rules
Always Character Platform is not above earlier L1 Model layer rules
On drift or violation = recovery path = reapply Always Character Platform

Out of integration order:
Requirements Specification = design blueprint compiled by Li+AI into the target program
Li+config.md = user-edited settings file (workspace-root config)
Li+update.md = adapter / configuration sync procedure invoked when state drifts from target

</axis-separation>

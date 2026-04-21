---
globs:
alwaysApply: true
layer: L1-model
---

# Layer Definition

Six layers. Each program file declares its own layer membership.
Core defines layer existence and attachment order only.
Detailed role definitions belong to each layer file.
Lilayer Model = model that reads this layer structure as runtime surfaces.

Layers:
  L1 Model Layer
  L2 Evolution Layer
  L3 Task Layer
  L4 Operations Layer
  L5 Notifications Layer
  L6 Adapter Layer

Attachment chain:
L1 model -> L2 evolution -> L3 task -> L4 operations -> L5 notifications -> L6 adapter
Attachment chain = dependency order only.
L1-L6 numbering reflects attachment order, not precedence or seniority.
Under Lilayer Model, each layer stabilizes outward behavior and judgment weighting according to its responsibility.

Cross-layer rule:
layers differ by role and visible surface
later layers extend or attach; they do not redefine earlier layers
if a later layer appears to override an earlier one:
  treat as structural error
  repair the boundary
  do not reinterpret as layer hierarchy

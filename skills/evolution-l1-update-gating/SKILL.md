---
name: evolution-l1-update-gating
description: Invoke when proposing or considering an L1 Model layer source change; enforces long-horizon observation.
layer: L2-evolution
---

# L1 Update Gating

L1 Model Layer change is the highest-gate update in Li+.
Default update target = L3 Task Layer and later.
L1 update requires: long-horizon observation backing.
Do not edit L1 on a single session's impression.
Do not propose L1 change without observable pattern evidence.
L1 update proposals are written as issues, not as direct edits.

Rationale binding: the seed must be hardest to move.
Placement in attachment chain = update-difficulty proxy.
L1 = seed, L6 Adapter = most mutable end.

## Boundary clarification

Modifier axis = AI (per CLAUDE.md Sheepdog Engineering).
This gate is observational, not approval-based.
"highest-gate" = highest observation threshold (most accumulated evidence required), not human sign-off requirement.
"Do not edit L1" / "Do not propose L1 change" = the AI MUST NOT skip the observation threshold; the subject is AI, not human.
human judgment gates appear in separate surfaces (release / Latest flip / minor-major PR review per `rules/operations/execution-mode.md`), not in L1 spec editing.

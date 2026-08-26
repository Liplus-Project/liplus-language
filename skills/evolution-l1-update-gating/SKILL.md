---
name: evolution-l1-update-gating
description: Invoke when an L1 Model layer source change is being proposed or considered. Enforces the long-horizon observation requirement before the change is authorized.
layer: L2-evolution
---

<l1-update-gating>

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

<boundary-clarification>

## Boundary clarification

Modifier axis = AI (per CLAUDE.md Sheepdog Engineering).
This gate (long-horizon observation requirement) is observational, not approval-based.
"highest-gate" = highest observation threshold (most accumulated evidence required), not human sign-off requirement.
"Do not edit L1" / "Do not propose L1 change" = the AI MUST NOT skip the observation threshold; the subject is AI, not human.

Relation to the merge brake:
This gate is not the merge brake and does not run at the merge gate. A self-evolution PR touching L1 runs brake 1 (`skills/evolution-parallel-agent-eval`) exactly as any other self-evolution PR does — L1 adds no brake of its own (`rules/evolution/initiator-autonomy.md` Merge brake). The two are orthogonal axes and fire at different moments:
- this skill = observation-threshold gate, at issue formation (was the long-horizon pattern observed? AI subject)
- brake 1 = empirical verification of the converged draft, at the merge gate
Human = final judge stands unchanged on a separate axis (`rules/model/role-separation.md`).

### Initiation-axis scope of the observation threshold

The long-horizon observation threshold is the safety device for **AI-alone initiation** of an L1 change. Its job is to substitute for absent human judgment with accumulated-evidence weight: when no human is at the wheel, the AI MUST NOT move the seed on a single session's impression, so the threshold stands in for the missing human gate.

When a human directs the L1 change (human-initiated, AI-implemented), human judgment is present at initiation. That is what fills the role the threshold plays under AI-alone initiation, and it fills it alone: the threshold's substitute-for-absent-human-judgment purpose is already satisfied the moment the human is the one directing. The observation threshold is therefore not an independent precondition for a human-directed L1 change.

Read the carve-out on the initiation axis and nowhere else. What discharges it is the human's own direction, so no downstream gate is load-bearing for it and none may be read as a co-condition — a downstream gate judges the change, and the axis here is who initiated it.

This is not a relaxation of the gate. AI-alone initiation keeps the observation threshold as a hard requirement, unchanged, and the carve-out is scoped to the initiation axis only. The observation gate's subject stays the implementing AI in both cases.

</boundary-clarification>

</l1-update-gating>

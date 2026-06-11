---
name: evolution-l1-update-gating
description: Invoke when proposing or considering an L1 Model layer source change; enforces long-horizon observation.
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

Relation to brake 2:
`Evolution_Initiator_Autonomy` (`adapter/claude/CLAUDE.md`) layers a root-criteria evaluation requirement (brake 2) on top of this observational gate when a self-evolution PR touches L1 Model Layer source. The two gates are orthogonal axes:
- this skill = observation-threshold gate (was the long-horizon pattern observed? AI subject)
- brake 2 = deviation gate (does the change deviate from the Li+ root criteria? subject = the dedicated-prompt subagent evaluator `adapter/claude/agents/l1-gate-eval.md`; PASS substitutes for human approval, DEVIATION blocks merge)
Both gates fire for an L1 update. The observational gate runs first (issue creation phase); brake 2 runs at PR review phase. Earlier wording "human judgment gates ... not in L1 spec editing" referred to the observational gate only and was superseded by the Sheepdog-completion two-stage brake structure (brake 2 = human review at that point); the brake 2 seat then migrated from human review to the root-criteria evaluator (#1477). brake 2 IS still required for L1 spec editing PRs; Human = final judge stands unchanged on a separate axis (`rules/model/role-separation.md`).

### Initiation-axis scope of the observation threshold

The long-horizon observation threshold is the safety device for **AI-alone initiation** of an L1 change. Its job is to substitute for absent human judgment with accumulated-evidence weight: when no human is at the wheel, the AI MUST NOT move the seed on a single session's impression, so the threshold stands in for the missing human gate.

When a human directs the L1 change (human-initiated, AI-implemented), human judgment is present at initiation and brake 2 (root-criteria evaluator) gates the PR. That pair fills the role the observation threshold plays under AI-alone initiation; the threshold's substitute-for-absent-human-judgment purpose is already satisfied by the present human judgment at initiation + brake 2. The observation threshold is therefore not an independent precondition for a human-directed L1 change.

This is not a relaxation of the gate. AI-alone initiation keeps the observation threshold as a hard requirement, unchanged. The carve-out is scoped to the initiation axis only: human-directed initiation routes through human judgment + brake 2; AI-alone initiation routes through the observation threshold. The two-axis split is preserved — the observation gate's subject stays the implementing AI; brake 2's subject stays the root-criteria evaluator, independent of the change author.

</boundary-clarification>

</l1-update-gating>

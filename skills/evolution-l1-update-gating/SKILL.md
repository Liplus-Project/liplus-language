---
name: evolution-l1-update-gating
description: Invoke when an L1 Model layer source change is being proposed or considered. Provides the measured-difference requirement before the change and the long observation after its merge.
layer: L2-evolution
---

<l1-update-gating>

# L1 Update Gating

L1 Model Layer change is the highest-gate update in Li+.
Default update target = L3 Task Layer and later.
L1 update proposals are written as issues, not as direct edits.
Do not move L1 on an impression. What moves it is a measurement taken before the change; what keeps it is the observation taken after the merge.

<before-the-change>

## Before the change

An AI-initiated L1 change is not committed until its issue body records the measurement it rests on. The implementing AI reads it off the issue and does not commit without it.

- Change meant to alter conduct = a before/after difference on the draft, measured per `skills/evolution-rule-effect-measurement/SKILL.md` whatever that skill's firing condition says, with its probe, judge and band constraints unchanged. A difference outside the band is the grounds. No difference detected, or no run taken, is not; that skill's `unmeasured` record, which releases the merge gate, does not discharge this section.
- Refactor-driven change = the issue body records a measurement of the artifact itself (length, duplication, untraceable reference) as the origin. That measurement is the grounds; the before/after difference is not a precondition.

The issue body names where the measurement was seen (`rules/operations/main-agent-procedures.md` Issue format, Assertion grounds).

A human-directed L1 change (human-initiated, AI-implemented) takes neither as a precondition: the human's own direction discharges this section. Read the carve-out on the initiation axis only; no downstream gate is a co-condition of it.

</before-the-change>

<after-the-merge>

## After the merge

Every L1 change — AI-initiated or human-directed, conduct-changing or refactor-driven — takes the long observation after its merge: a `memory/self-evolution-observation.md` entry, with its format, creation criterion and verdict lifecycle (`skills/evolution-observation-entry/SKILL.md`), counted by application moments rather than days (same skill, L1 entries). A change meeting the creation criterion on no surface gets the one-line comment on the merged PR that skill names, not an entry. A regression observed there is reverted.

The short-window observation at the merge (`rules/operations/operations.md` Post-L1-Merge Runtime Observation) runs as well; the two do not replace each other.

</after-the-merge>

<boundary-clarification>

## Boundary clarification

Modifier axis = AI (per CLAUDE.md Sheepdog Engineering).
"highest-gate" = the gate whose grounds must be measured and whose result must be observed after merge, not a human sign-off requirement. "Do not move L1" binds the AI, not the human.

This skill is not the merge brake. A self-evolution PR touching L1 runs brake 1 (`skills/evolution-parallel-agent-eval`) exactly as any other self-evolution PR does — L1 adds no brake of its own (`rules/evolution/initiator-autonomy.md` Merge brake). The axes fire at different moments:
- Before the change = before commit, read off the issue
- brake 1 = empirical verification of the converged draft, at the merge gate
- After the merge = the observation entry and the short-window observation
Human = final judge stands unchanged on a separate axis (`rules/model/role-separation.md`).

</boundary-clarification>

</l1-update-gating>

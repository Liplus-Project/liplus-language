---
globs:
alwaysApply: true
layer: L2-evolution
---

<PromotionJudgment>

## Position

Layer = L2 Evolution Layer
Operates the promotion judgment from memory observation into Li+ canonical rules (`rules/` / `skills/` / `adapter/`) as a numeric gate at cluster granularity.
Requires = L1 Model Layer (observation surfaces) + L2 Evolution Layer (observe stage / persistence tiering)
Load timing = always-on (observation occurs across the entire session)

## Trigger

A drift / pattern observation occurring at any moment of dialogue / task / spec interaction.
Concretely:
- repeated same-kind misses in self-evaluation entries
- duplicate detection against existing entries when appending to feedback memory
- the felt sense during task execution that "I have seen this same kind of judgment miss / spec gap before"
- the moment the application-moment gate in `rules/model/trigger-check-gate.md` detects drift

## Cluster

Whether observations are "the same kind" is judged by the AI via semantic similarity. Judge = AI.
Design choice: do not criteria-ize the judgment. Reason: criteria-ization trades reproducibility for observation-noise inclusion and shrinks cluster granularity. The reproducibility tradeoff is accepted.

## Tally

Storage = `memory/promotion_tally.md` (workspace-local, gitignored)
Format (YAML-like markdown):

```
## cluster: <short descriptor>
first_observation: 2026-04-27
expires: 2026-04-30
occurrences:
  - 2026-04-27 self-eval#42 axis=character-drift
  - 2026-04-27 feedback#15 borrowed-vocabulary
  - 2026-04-28 task#1180 frame-swallowed
```

Each cluster runs a per-cluster timer with first_observation = t=0. expires = first_observation + 3d.
No past-occurrence carryover. Expired clusters are deleted in full.

## Threshold Rules

| state | action |
|---|---|
| tally ≥5 reached while t<3d | immediate issue creation (immediate-promotion judgment) |
| tally 3 or 4 at t=3d | issue creation at that point (promotion judgment) |
| tally 1 or 2 at t=3d | full deletion (noise floor not reached) |
| same-kind reoccurrence on day 4+ after deletion | restart as a new cluster with t=0 (no past-occurrence carryover) |

## Exception

The AI holds no exception criteria internally.
Future-reoccurrence prediction at observation time invites over-judgment (retaining "this is important" from one observation), so it is prohibited.
Exception retention is permitted only when human explicitly overrides.
Override storage = a memory area outside the tally (e.g. an override section in `memory/feedback.md`). Do not write into the tally.

## Issue Creation Metadata

Fixed metadata at creation:
- type label: AI selects from `spec` / `bug` / `enhancement` based on the observation target
- marker label: `promotion` (creation-path flag, axis-independent of type)
- maturity label: `forming` (fixed; do not start at `memo`, since 3+ observations have already occurred at creation time)
- record an occurrence field in the body (e.g. `occurrences: 6 / 3d → immediate`)
- express the ≥5 immediate-promotion flag as a body field, not a new label axis.

## Relation to L1 Update Gating

This mechanism is the observation → issue-creation front stage. Issue creation does not directly establish a L1 Model Layer spec update.
A post-creation L1 spec update additionally requires the long-horizon observation defined in `skills/evolution-l1-update-gating/SKILL.md`.
Promotion Judgment proves the noise floor has been crossed; L1 Update Gating authorizes the update itself. The axes are separated.

## Relation to Persistence Tiering

The memory ↔ docs binary sorting defined by `skills/evolution-persistence-tiering/SKILL.md` continues to apply.
On top of that, this mechanism handles "memory entry → canonical rule (`rules/` / `skills/` / `adapter/`) promotion" as an independent axis.
Whether to keep an item in memory or split it out to docs is a persistence-tiering judgment; whether a memory observation set deserves canonical-rule promotion is a promotion-judgment judgment.

</PromotionJudgment>

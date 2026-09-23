---
globs:
alwaysApply: true
layer: L2-evolution
---

<promotion-judgment>

# Promotion Judgment

<position>

## Position

Layer = L2 Evolution Layer
Operates the promotion judgment from memory observation into Li+ canonical rules (`rules/` / `skills/` / `adapter/`) as a numeric gate at cluster granularity.
Requires = L1 Model Layer (observation surfaces) + L2 Evolution Layer (observe stage / persistence tiering)
Load timing = always-on (observation occurs across the entire session)

</position>

<trigger>

## Trigger

A drift / pattern observation occurring at any moment of dialogue / task / spec interaction.
Concretely:
- repeated same-kind misses in self-evaluation entries (`skills/evolution-self-eval/SKILL.md` root cause categories / observational axes routes here; that surface files nothing on its own)
- duplicate detection against existing entries when appending to feedback memory
- the felt sense during task execution that "I have seen this same kind of judgment miss / spec gap before"
- the moment the application-moment gate in `rules/model/trigger-check-gate.md` detects drift

</trigger>

<cluster>

## Cluster

Whether observations are "the same kind" is judged by the AI via semantic similarity. Judge = AI.
Design choice: do not criteria-ize the judgment. Reason: criteria-ization trades reproducibility for observation-noise inclusion and shrinks cluster granularity. The reproducibility tradeoff is accepted.

</cluster>

<tally>

## Tally

Storage = one `promotion_tally.md` outside memory (host-local, gitignored). On one host it resolves to one file, the same file under every adapter. Where that file sits is the adapter's, and no rule names it. The cold-start surface prints the path it resolved (`rules/evolution/cold-start-synthesis.md` Promotion Tally Expiry Surface); when nothing was printed, read the resolution out of the session's own hook (`adapter/*/hooks/on-session-start.*` in the Li+ source, the installed copy under the host's hooks directory otherwise) and write there.

Do not give an adapter a tally file of its own. The floor splits, neither half reaches the threshold, and nothing detects the split. Name fit, ownership feel and adapter independence justify none of it.

Appends are not serialized. Two sessions writing at once can drop an occurrence, and nothing raises when one is dropped — detection is by hand. Do not add locking or a per-session split before a collision has been observed; when one is, file that observation as its own issue.

Format (YAML-like markdown):

```
## cluster: <short descriptor>
first_observation: 2026-04-27
expires: 2026-04-30
occurrences:
  - 2026-04-27 self-eval#<entry> axis=character-drift
  - 2026-04-27 feedback#<entry> borrowed-vocabulary
  - 2026-04-28 task#<issue> frame-swallowed
```

Each cluster runs a per-cluster timer with first_observation = t=0. expires = first_observation + 3d.
No past-occurrence carryover. Expired clusters are deleted in full.

Disposition log:
The same file carries a `<!-- disposition log -->` section. One line per cluster that has left the tally, appended as the cluster is deleted:

```
<!-- disposition log -->
- 2026-09-10 cluster `<short descriptor>` (first_observation 2026-09-07, 2 occurrences) -> <disposition>
```

Placement: the log is the file's last section, after every cluster. Cluster parsing reads the `## cluster:` headings above it, so the log sits outside that region rather than between two clusters.

Fields: deletion date, cluster descriptor, `first_observation`, occurrence count, disposition. The disposition names which Threshold Rules exit was taken, and for the creation and fold exits carries the issue number (created, or folded into). Occurrence bodies are not carried over.

Cap = 10 lines, oldest-first deletion once exceeded. Every cluster the log records has already left the tally, and expired clusters are deleted in full (above). Same shape as the self-evaluation log's cap (`skills/evolution-self-eval/SKILL.md`).

</tally>

<threshold-rules>

## Threshold Rules

| state | action |
|---|---|
| tally ≥5 reached while t<3d | immediate issue creation (immediate-promotion judgment) |
| tally 3 or 4 at t=3d | issue creation at that point (promotion judgment) |
| tally 1 or 2 at t=3d | full deletion (noise floor not reached) |
| same-kind reoccurrence on day 4+ after deletion | restart as a new cluster with t=0 (no past-occurrence carryover) |

Actor = the agent holding the session the cluster is surfaced in. Firing moment = that surfacing, which is `rules/evolution/cold-start-synthesis.md` Promotion Tally Expiry Surface. A cluster past its window is re-surfaced every session until the judgment removes it, so a session that takes none loses no trigger. Opening the tally on recall is not the firing moment and was never a guaranteed one (`rules/model/subtractive-structural-beauty.md` Application notes, Spec write applies (B), procedure-to-structure rider).

Disposition line on every exit: three of the rows above end in the cluster leaving the tally — full deletion at sub-threshold, deletion after issue creation, and deletion after folding into an existing `promotion` issue under Reconciliation below. Each requires one line in the disposition log (Tally above), written by this same actor in the same hand as the deletion. Not a separate procedure: a procedure whose execution is not guaranteed is what `rules/model/subtractive-structural-beauty.md` Application notes, Spec write applies (B) sends back to be replaced.

The requirement covers all three, not sub-threshold alone. A cluster gone from the tally is indistinguishable from one never observed, and that holds identically on each exit; requiring the line on one exit only would leave the other two reading as never-observed — the same surface this closes.

Reconciliation before creation and before sub-threshold deletion: both issue-creation rows and the full-deletion row above are reached through one prior step. Search the existing `promotion` marker issues (that marker is the creation-path flag Issue Creation Metadata below attaches at creation, so it is the field the search runs on) for one already covering this cluster. Found -> the verdict is neither creation nor deletion as noise: fold the occurrences into that issue and delete the cluster. Not found -> the row's own action: create, per Issue Creation Metadata below, or full deletion. The noise floor gates new issue creation only, not a fold.

</threshold-rules>

<exception>

## Exception

The AI holds no exception criteria internally.
Future-reoccurrence prediction at observation time invites over-judgment (retaining "this is important" from one observation), so it is prohibited.
Exception retention is permitted only when human explicitly overrides.
Override storage = a memory file outside the tally (e.g. a `memory/feedback_<topic>.md` entry). Do not write into the tally.

</exception>

<issue-creation-metadata>

## Issue Creation Metadata

Fixed metadata at creation:
- type label: AI selects from `spec` / `bug` / `enhancement` based on the observation target
- marker label: `promotion` (creation-path flag, axis-independent of type)
- maturity label: `forming` (fixed; do not start at `memo`, since 3+ observations have already occurred at creation time)
- record an occurrence field in the body (e.g. `occurrences: 6 / 3d → immediate`)
- express the ≥5 immediate-promotion flag as a body field, not a new label axis.

</issue-creation-metadata>

<relation-to-l1-update-gating>

## Relation to L1 Update Gating

This mechanism is the observation → issue-creation front stage. Issue creation does not directly establish a L1 Model Layer spec update.
A post-creation L1 spec update additionally requires the long-horizon observation defined in `skills/evolution-l1-update-gating/SKILL.md`.
Promotion Judgment proves the noise floor has been crossed; L1 Update Gating authorizes the update itself. The axes are separated.

</relation-to-l1-update-gating>

<relation-to-persistence-tiering>

## Relation to Persistence Tiering

The memory ↔ docs binary sorting defined by `skills/evolution-persistence-tiering/SKILL.md` continues to apply.
On top of that, this mechanism handles "memory entry → canonical rule (`rules/` / `skills/` / `adapter/`) promotion" as an independent axis.
Whether to keep an item in memory or split it out to docs is a persistence-tiering judgment; whether a memory observation set deserves canonical-rule promotion is a promotion-judgment judgment.

</relation-to-persistence-tiering>

</promotion-judgment>

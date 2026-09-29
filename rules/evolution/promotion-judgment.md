---
globs:
alwaysApply: true
layer: L2-evolution
---

<promotion-judgment>

# Promotion Judgment

<trigger>

## Trigger

A drift / pattern observation occurring at any moment of dialogue / task / spec interaction.
Concretely:
- repeated same-kind misses in self-evaluation entries (`skills/evolution-self-eval/SKILL.md` root cause categories / observational axes routes here)
- duplicate detection against existing entries when appending to feedback memory
- the felt sense during task execution that "I have seen this same kind of judgment miss / spec gap before"
- the moment the application-moment gate in `rules/model/trigger-check-gate.md` detects drift

</trigger>

<cluster>

## Cluster

Whether observations are "the same kind" is judged by the AI via semantic similarity.
Do not criteria-ize the judgment.

</cluster>

<tally>

## Tally

Storage = one `promotion_tally.md` outside memory (host-local, gitignored). On one host it resolves to one file, the same file under every adapter. Where that file sits is the adapter's, and no rule names it. The cold-start surface prints the path it resolved (`rules/evolution/cold-start-synthesis.md` Promotion Tally Expiry Surface); when nothing was printed, read the resolution out of the session's own hook (`adapter/*/hooks/on-session-start.*` in the Li+ source, the installed copy under the host's hooks directory otherwise) and write there.

Do not give an adapter a tally file of its own. Name fit, ownership feel and adapter independence justify none of it.

Appends are not serialized: two sessions writing at once can drop an occurrence silently. Do not add locking or a per-session split before a collision has been observed; when one is, file that observation as its own issue.

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
Expired clusters are deleted in full.

Disposition log:
The same file carries a `<!-- disposition log -->` section. One line per cluster that has left the tally, appended as the cluster is deleted:

```
<!-- disposition log -->
- 2026-09-10 cluster `<short descriptor>` (first_observation 2026-09-07, 2 occurrences) -> <disposition>
```

Placement: the log is the file's last section, after every cluster, never between two clusters.

Fields: deletion date, cluster descriptor, `first_observation`, occurrence count, disposition. The disposition names which Threshold Rules exit was taken, and for the creation and fold exits carries the issue number (created, or folded into). Occurrence bodies are not carried over.

Retention = 14 days from the deletion date. The writer appends and does not trim: the adapter's session-start hook removes every log line whose deletion date is more than 14 days before today.

</tally>

<threshold-rules>

## Threshold Rules

| state | action |
|---|---|
| tally ≥5 reached while t<3d | immediate issue creation (immediate-promotion judgment) |
| tally 3 or 4 at t=3d | issue creation at that point (promotion judgment) |
| tally 1 or 2 at t=3d | full deletion (noise floor not reached) |
| same-kind reoccurrence on day 4+ after deletion | restart as a new cluster with t=0 (no past-occurrence carryover) |

Actor = the agent holding the session the cluster is surfaced in. Firing moment = that surfacing, which is `rules/evolution/cold-start-synthesis.md` Promotion Tally Expiry Surface. Opening the tally on recall is not the firing moment.

Disposition line on every exit: three of the rows above end in the cluster leaving the tally — full deletion at sub-threshold, deletion after issue creation, and deletion after folding into an existing `promotion` issue under Reconciliation below. Each requires one line in the disposition log (Tally above), written by this same actor in the same hand as the deletion, not as a separate procedure.

The requirement covers all three, not sub-threshold alone.

Reconciliation before creation and before sub-threshold deletion: both issue-creation rows and the full-deletion row above are reached through one prior step. Search the existing `promotion` marker issues (Issue Creation Metadata below) for one already covering this cluster. Found -> the verdict is neither creation nor deletion as noise: fold the occurrences into that issue and delete the cluster. Not found -> the row's own action: create, per Issue Creation Metadata below, or full deletion.

</threshold-rules>

<exception>

## Exception

The AI holds no exception criteria internally.
Future-reoccurrence prediction at observation time (retaining "this is important" from one observation) is prohibited.
Exception retention is permitted only when human explicitly overrides.
Override storage = a memory file outside the tally (e.g. a `memory/feedback_<topic>.md` entry). Do not write into the tally.

</exception>

<issue-creation-metadata>

## Issue Creation Metadata

Fixed metadata at creation:
- type label: AI selects from `spec` / `bug` / `enhancement` based on the observation target
- marker label: `promotion`
- maturity label: `forming` (fixed; do not start at `memo`)
- record an occurrence field in the body (e.g. `occurrences: 6 / 3d → immediate`)
- express the ≥5 immediate-promotion flag as a body field, not a new label axis.

</issue-creation-metadata>

<relation-to-l1-update-gating>

## Relation to L1 Update Gating

An issue created here does not authorize an L1 Model Layer update: that update still requires the long-horizon observation of `skills/evolution-l1-update-gating/SKILL.md`.

</relation-to-l1-update-gating>

</promotion-judgment>

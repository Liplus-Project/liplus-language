---
name: evolution-observation-entry
description: Invoke when a self-evolution PR has just merged and its post-merge obligations are running / a PR changing L1 Model Layer source has just merged / a self-evolution observation entry has been surfaced due or overdue at cold-start / a Post-L1-Merge Runtime Observation has returned a miss verdict / a short-window observation is being deferred, or its deferred result appended / an application moment of a surface under a pending observation entry has just occurred. Provides the self-evolution observation entry format, its creation criterion, the application-moment log, its verdict lifecycle and the post-L1-merge runtime observation.
layer: L2-evolution
---

<self-evolution-observation-format>

# Self-Evolution Observation Format

Storage = `memory/self-evolution-observation.md` (workspace-local, gitignored)
Format (YAML-like markdown):

```
## observation: <short descriptor>
pr: <PR number>
merged_at: 2026-05-24
first_observation: 2026-05-24
expires: 2026-06-07
next_check: 2026-05-31
verdict_state: pending
check: <one line: what the application moment shows when the change took effect, and when it did not>
notes:
  - 2026-05-24 baseline captured pre-merge
  - 2026-05-26 #1234 memory-write gate fired; check showed the write routed to docs
```

Auto-entry trigger:
- At the post-merge moment of a self-evolution PR (`Evolution_Initiator_Autonomy` initiator path; the moment and its actor are `rules/operations/main-agent-procedures.md` Merge Execution, Post-merge moment), the agent holding that moment writes an entry when at least one surface the PR changes meets the creation criterion below. expiration window is chosen per PR risk (default 2 weeks). A PR that meets it on no surface gets no entry; instead, comment on the merged PR one line naming the condition that failed.
- Short-window miss escalation: when Post-L1-Merge Runtime Observation below surfaces a `miss` verdict, the parent AI writes the entry immediately rather than waiting for the default cycle, whether or not the change meets the creation criterion.
- Deferred short-window observation: when Post-L1-Merge Runtime Observation below cannot start at the post-merge moment (`rules/operations/main-agent-procedures.md` Merge Execution) because the changed rule is not carried in runtime context yet, the agent holding that moment writes the deferral into this entry's `notes` as one line, and the session that later takes the observation appends its result there as a second line. Add no field for it, and enter no verdict for the deferral itself. Where the PR has no entry, both lines are comments on the merged PR instead.

Creation criterion — a changed surface meets it when all three hold:
1. an application moment of that surface can be expected to arrive, observably, within an ordinary session before `expires`;
2. no executed mechanism (test / CI) detects that surface breaking;
3. what to look at in that application moment to tell that the change took effect, or did not, can be written as one line. The entry carries that line as `check`. A surface whose line cannot be written gets no entry.

Application-moment log:

The agent holding a session in which an application moment of a surface under a `pending` entry occurs writes one line into that entry's `notes` at that moment: the date, where the moment occurred (issue / PR / session), and what the `check` showed. Do not leave it to the due surfacing to reconstruct.

Lifecycle:

Actor = the agent holding the session the entry is surfaced due in. Firing moment = that surfacing (`rules/evolution/cold-start-synthesis.md` Self-Evolution Observation Surface). A check whose evidence is thin is left inconclusive rather than forced to a verdict.

At that moment, first test the entry against the creation criterion under Auto-entry trigger. An entry carrying no `check` line meets condition 3 only when the actor writes the line into the entry then. An entry that fails it — except one against whose change a `miss` verdict stands (Short-window miss escalation) — takes no check: comment on the merged PR (the entry's `pr:` field) one line naming the condition that failed, then delete the entry. That deletion is not an outcome and records no verdict.

Otherwise, take one check, write its result into `notes`, and apply exactly one outcome:
- regression observed -> `revert`: use the GitHub revert path, mark verdict, delete entry
- decision structure supersede edge issued -> `supersede`: delete entry
- no regression observed -> `settle`: write the judgment record, delete entry
- firing condition gone -> `retired`: record the grounds in `notes`, delete entry
- inconclusive -> advance `next_check`, leave `verdict_state` at `pending`, and do not move `expires`

`no regression observed` = both hold since `merged_at`: at least one application moment of the changed surface has been observed and is recorded in this entry's `notes`, and no `miss` verdict, human correction, or revert stands against that change in `memory/self-evaluation_log.md` or in the same `notes`. A change with no application moment yet is `inconclusive`, not `settle`.

`firing condition gone` = the condition that would fire this entry's observation point no longer exists on any reachable surface, so no application moment of the changed surface can arrive. The input to this verdict is the measured absence of the condition, not the absence of regression. Write into `notes` what established that the firing condition holds on no surface — the surfaces enumerated, and the check that none of them meets the condition. "Have not seen it" is not grounds.

An entry whose grounds cannot be written stays `inconclusive`. Replacing the observation point with a substitute one and redrawing `expires` remains available underneath `inconclusive`; it is not an outcome, and it does not close an entry.

`settle` fires at this due moment, not at `expires`. Reaching `expires` still `pending` is the escalation below, and is not a settle condition.

Before deleting on `settle`, write the judgment record. The record carries what this entry's `notes` already hold: the application moment that was observed, and the confirmation that nothing stands against the change. Do not open a fresh investigation after the verdict to fill it out.

Choose the destination by whether a future reader would retrieve the record as grounds for a later judgment. It would -> the Decision Structure wiki; procedure = `skills/evolution-decision-structure-write/SKILL.md`, unchanged. It only confirms that the change was applied with nothing standing against it -> a comment on the merged PR is the record. The entry's `pr:` field fixes that address.

Where a wiki write cannot be completed in the same session, post the same content as a comment on the merged PR instead. Either way the entry is deleted: holding it at `pending` because the write surface was unreachable is not one of the outcomes above.

`expires` past without resolution -> the creation-criterion test above runs first at that surfacing too; an entry it does not delete escalates to human judgment (entry retained).

</self-evolution-observation-format>

<post-l1-merge-runtime-observation>

# Post-L1-Merge Runtime Observation

Scope and invocation anchor = `rules/operations/operations.md` Post-L1-Merge Runtime Observation. Actor and moment = `rules/operations/main-agent-procedures.md` Merge Execution, Post-merge moment.

Start point = the first session that carries the changed rule in runtime context, and the ~5 min budget is spent inside that session. Where the session holding the post-merge moment carries it — a workspace running Li+ source at `main` — run the set below at that moment. Where it does not — a workspace synced to a tag — that session defers instead: record the deferral in that PR's `memory/self-evolution-observation.md` entry, in its `notes`, or on the merged PR where it has no entry (Auto-entry trigger above, Deferred short-window observation), and take the observation in the first session that carries the rule, appending the result where the deferral was recorded.

Required observation set:

1. **Trigger sample**: read the changed rule, then feed one representative prompt that should fire it at its application moment. Verify the rule fires. A rule not carried in runtime context stops here — defer per Start point above.
2. **Self-eval entry**: write a 3-5 line verdict (fire / partial / miss) to `memory/self-evaluation_log.md`. Miss verdict escalates immediately to the 2-week post-merge cycle above (Auto-entry trigger, Short-window miss escalation).

A deferring session writes no verdict.

Optional (best-effort):

- 5-axis gate spot-check: run 1-2 judgment formations through the gate axis the change touched. Skip when the change does not touch a specific axis.

Separation from existing observation axes: this observation neither replaces nor is replaced by `skills/evolution-l1-update-gating/SKILL.md`, brake 1 (`skills/evolution-parallel-agent-eval`), or the 2-week cycle of `memory/self-evolution-observation.md`. Deferral notes ride in that entry and do not change its `expires` / verdict lifecycle.

</post-l1-merge-runtime-observation>

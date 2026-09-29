---
globs:
alwaysApply: true
layer: L2-evolution
---

<cold-start-synthesis>

# Cold-start Synthesis

Trigger = session start, after Li+config.md execution completes.
Action:
1. Read docs/Decision-Structure.md (decision structure index) and recent Li+ source changes.
2. Synthesize the current Li+ state = active tag, recent structural shifts, unresolved threads.
3. Report synthesis to human as the opening orientation — conditional on non-redundancy with hook-surfaced material.

Steps 1-2 are internal AI priming. They run every session regardless of what the hook already emitted.
Step 3 is conditional output gating, not unconditional report.

Operational criterion (AI side, step 3 gating):
- hook-surfaced items = silent (do not re-report what the human already received from the hook, regardless of full / diff-only / marker state)
- unique synthesized insight = speak (structural shift, unresolved thread, cross-artifact pattern not visible in the raw hook material)
- no unique insight after synthesis = silent skip
- diff-only state with the no-new-material marker = silent skip
- release Latest position = silent, even though it reads as synthesis over the hook-surfaced tag list. When the tag list shows the Latest flag on a prior version, do NOT surface "Latest behind / flip pending" as unique insight

Scope = Li+ state, not workspace task state. Workspace-specific orientation follows the adapter's own startup path.

<self-evolution-observation-surface>

## Self-Evolution Observation Surface

Self-evolution observation entries (`memory/self-evolution-observation.md`, format defined in `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format) are surfaced at cold-start when their check window opens:
- `next_check` <= today and `verdict_state` == `pending` -> surface as "observation due"
- `expires` < today and `verdict_state` == `pending` -> surface as "observation overdue, human judgment needed"

Where both hold, overdue wins: the entry is surfaced once, as overdue only.

Surfacing is observation, not auto-action. Verdict transitions (settle / revert / supersede) still go through the explicit lifecycle defined in the format spec.

</self-evolution-observation-surface>

<promotion-tally-expiry-surface>

## Promotion Tally Expiry Surface

Promotion tally clusters (storage and format defined in `rules/evolution/promotion-judgment.md` Tally) are surfaced at cold-start when their 3d window has closed:
- `expires` <= today -> surface as "tally expiry reached"
- `expires` < today -> surface as "tally expiry overdue, threshold judgment not taken"

Where both hold, overdue wins: the cluster is surfaced once, as overdue only. The emission names the resolved tally path and carries the occurrence count.

A cluster carries no verdict field; nothing here reads one. Presence in the file is the unresolved state, and the cluster is re-surfaced every session until the threshold judgment removes it.

Surfacing is observation, not auto-action. The threshold judgment itself — issue creation, merge into an existing `promotion` issue, or deletion — follows `rules/evolution/promotion-judgment.md` Threshold Rules. Actor = the agent holding the session the cluster is surfaced in; firing moment = that surfacing.

</promotion-tally-expiry-surface>

<clone-branch-fetch-surface>

## Clone Branch Fetch Surface

The Li+ clone's configured fetch refspecs are surfaced at cold-start when none of them can move a branch: the workspace holds a Li+ clone, and `remote.origin.fetch` carries no refspec whose source side is under `refs/heads/` -> surface as "clone cannot fetch branches".

The predicate is the source side of a refspec, not the wildcard literal: a clone made with `--single-branch` (`+refs/heads/<branch>:refs/remotes/origin/<branch>`) moves that branch and is not this condition. Read the source side as the src half of `[+]<src>:<dst>`, and read it there only: `refs/heads/` reached on the dst side (`+refs/tags/v1:refs/heads/mirror`) does not satisfy the predicate. A `^<pattern>` exclusion satisfies the predicate in no namespace.

This surface is state-driven, unlike the two date-driven surfaces above: the condition either holds this session or it does not, and it is re-surfaced every session while it holds. Nothing here reads a date.

No lifecycle: the emission stops the moment the condition stops holding. There is no `verdict_state`, no `expires`, and no removal step. Read the absence as the design; do not fill it.

Actor = the agent holding the session the surface fires in. Firing moment = that surfacing. What the moment calls for is naming the condition to the human, and nothing further: the repair is taken on a human go-sign, and no agent takes it. The Operational criterion's `hook-surfaced items = silent` does not silence this one.

Surfacing is observation, not auto-action.

</clone-branch-fetch-surface>

<dependency-ordering-surface>

## Dependency Ordering Surface

Open issues of the Li+ repository that wait on another open issue are surfaced at cold-start, naming each open blocker: `#<n>`, or `<owner>/<repo>#<n>` when the blocker sits in another repository. A closed blocker does not count: an issue whose blockers are all closed is not surfaced.

The surface reads the relation as its author wrote it (`rules/operations/main-agent-procedures.md` Issue format). It derives no edge from parent / sub-issue structure and repairs no missing one.

Surfacing is observation, not auto-action. Which issue to start stays the judgment of the agent holding the session.

</dependency-ordering-surface>

</cold-start-synthesis>

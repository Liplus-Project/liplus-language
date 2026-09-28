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

<hook-emission-contract>

## Hook Emission Contract

The hook's own behavior. Read on demand; not applied at the step 3 moment.

Anchor cut: the hook re-anchors the preamble above (H1 body up to the first H2 section), not the whole file. A file with no H2 section is emitted whole.

Hook coordination:
`on-session-start.sh` persists and surfaces at session open: decision structure index head, rules/ tree (fetch address table for cold-start-loaded rules cache), recent release tags, open in-progress issues, open issues blocked by an open issue (see Dependency Ordering Surface below), self-evaluation log head, promotion candidates, promotion tally clusters whose window has closed, a Li+ clone that cannot fetch branches, cold-start rule anchor. The hook emits material in diff-only mode (matcher = startup): only sections whose body changed since the previous startup invocation *recorded under this run's own partition* are re-emitted (partition, below). The cold-start rule anchor is always re-emitted regardless of diff state.

Multi-session partition (#1811): the persisted state is keyed by `LI_PLUS_AGENT_KEY` (env var, default `"default"`), one independent `{sections, last_emit_at}` entry per key. Unset (the common, single-session-per-workspace case) reproduces the pre-#1811 single-partition behavior exactly, file shape included once a legacy-shape state file has migrated (fail-safe reasons, below). Set distinctly per person's own launch profile only in a workspace where multiple sessions share this directory concurrently.

Hook emission states (matcher = startup):
- full emit = first session after install, fail-safe (state missing / unreadable / sha256 unavailable / node unavailable / legacy pre-#1811 single-partition schema / no entry yet recorded for this run's `LI_PLUS_AGENT_KEY`), or every section changed. All sections shown. The four tool/state reasons are the bash ports' set; the two partition-migration reasons apply to all three ports alike. The PowerShell port's fail-safe set is the state-file and partition reasons alone: sha256 unavailable and node unavailable do not fire there.
- diff-only = some sections changed since prior session under the same partition. Only changed sections shown, plus a one-line read-back of the state file's `last_emit_at` for this partition — when the prior baseline was consumed. Emitted in this state only. The line carries no identifier and none is added. An absent or malformed stamp drops the line, and is not a fail-safe reason.
- no-new-material marker = no section changed AND no surface below emitted anything. A single "No new orientation material since last session" line is emitted (not replaced by a silent skip). A surfaced self-evolution observation entry (see Self-Evolution Observation Surface below), a surfaced promotion tally cluster (see Promotion Tally Expiry Surface below) and a surfaced clone that cannot fetch branches (see Clone Branch Fetch Surface below) each count as material even though none of them carries a section key, so the marker is suppressed for that session.

Hook emission states (matcher = resume / clear / compact / fork):
- Only the cold-start rule anchor is re-emitted. The diff-only set is not re-evaluated, and the state file is not updated.

</hook-emission-contract>

<self-evolution-observation-surface>

## Self-Evolution Observation Surface

Self-evolution observation entries (`memory/self-evolution-observation.md`, format defined in `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format) are surfaced at cold-start when their check window opens.

Surface targets:
- `next_check` <= today and `verdict_state` == `pending` -> surface as "observation due"
- `expires` < today and `verdict_state` == `pending` -> surface as "observation overdue, human judgment needed"

Where both hold, overdue wins: the entry is surfaced once, as overdue only.

Surfacing is observation, not auto-action. Verdict transitions (settle / revert / supersede) still go through the explicit lifecycle defined in the format spec.

Material gathering and concrete surfacing logic belong to the adapter cold-start path. This section defines only the behavior contract.

Silent skip when the observation file is absent or no entries are due.

</self-evolution-observation-surface>

<promotion-tally-expiry-surface>

## Promotion Tally Expiry Surface

Promotion tally clusters (storage and format defined in `rules/evolution/promotion-judgment.md` Tally) are surfaced at cold-start when their 3d window has closed. The tally file resolves outside memory and independently of it: a session whose memory directory does not resolve still reaches the tally. The emission names the resolved path.

Surface targets:
- `expires` <= today -> surface as "tally expiry reached"
- `expires` < today -> surface as "tally expiry overdue, threshold judgment not taken"

Where both hold, overdue wins: the cluster is surfaced once, as overdue only.

A cluster carries no verdict field; nothing here reads one. Presence in the file is the unresolved state, and the cluster is re-surfaced every session until the threshold judgment removes it.

The occurrence count is carried on the surfaced line.

Surfacing is observation, not auto-action. The threshold judgment itself — issue creation, merge into an existing `promotion` issue, or deletion — follows `rules/evolution/promotion-judgment.md` Threshold Rules. Actor = the agent holding the session the cluster is surfaced in; firing moment = that surfacing.

Material gathering and concrete surfacing logic belong to the adapter cold-start path, as with the observation surface above. This section defines only the behavior contract.

Silent skip when the tally file is absent or no cluster has reached its window.

</promotion-tally-expiry-surface>

<clone-branch-fetch-surface>

## Clone Branch Fetch Surface

The Li+ clone's configured fetch refspecs are surfaced at cold-start when none of them can move a branch.

Surface target:
- the workspace holds a Li+ clone, and `remote.origin.fetch` carries no refspec whose source side is under `refs/heads/` -> surface as "clone cannot fetch branches"

The predicate is the source side of a refspec, not the wildcard literal: a clone made with `--single-branch` (`+refs/heads/<branch>:refs/remotes/origin/<branch>`) moves that branch and is not this condition. Read the source side as the src half of `[+]<src>:<dst>`, and read it there only: `refs/heads/` reached on the dst side (`+refs/tags/v1:refs/heads/mirror`) does not satisfy the predicate. A `^<pattern>` exclusion satisfies the predicate in no namespace.

This surface is state-driven, unlike the two date-driven surfaces above: the condition either holds this session or it does not. It shares their properties — no section key, outside the diff-only set, re-surfaced every session while it holds, and counting as material against the no-new-material marker. Nothing here reads a date.

No lifecycle: the emission stops the moment the condition stops holding. There is no `verdict_state`, no `expires`, and no removal step. Read the absence as the design; do not fill it.

Not carried on `LI_PLUS_UPDATE_STATUS`, as a status or as a reason string.

Actor = the agent holding the session the surface fires in. Firing moment = that surfacing. What the moment calls for is naming the condition to the human, and nothing further: the repair is taken on a human go-sign, and no agent takes it. The Operational criterion's `hook-surfaced items = silent` does not silence this one.

Surfacing is observation, not auto-action.

Material gathering and concrete surfacing logic belong to the adapter cold-start path, as with the two surfaces above. This section defines only the behavior contract.

Silent skip when the workspace holds no clone (api mode) or `git` is unavailable.

</clone-branch-fetch-surface>

<dependency-ordering-surface>

## Dependency Ordering Surface

Open issues of the Li+ repository that wait on another open issue are surfaced at cold-start.

Surface target:
- an open issue with at least one `blockedBy` issue whose state is open -> surface it, naming each open blocker: `#<n>`, or `<owner>/<repo>#<n>` when the blocker sits in another repository

A closed blocker does not count. An issue whose blockers are all closed is not surfaced.

Read the relation through GraphQL (`Issue.blockedBy`), not through gh CLI dependency flags. It is a repository-level relation and requires no Projects.

Content-driven, unlike the three surfaces above: the section carries a section key (`open_blocked_by_open_issues`) and sits in the diff-only set beside open in-progress issues.

Scan limit = one page of open issues. When more open issues exist than the page reaches, the emission says so.

The surface reads the relation as its author wrote it (`rules/operations/main-agent-procedures.md` Issue format). It derives no edge from parent / sub-issue structure and repairs no missing one.

Surfacing is observation, not auto-action. Which issue to start stays the judgment of the agent holding the session.

Material gathering and concrete surfacing logic belong to the adapter cold-start path, as with the three surfaces above. This section defines only the behavior contract.

Silent skip when the query fails or no open issue waits on an open issue.

</dependency-ordering-surface>

</cold-start-synthesis>

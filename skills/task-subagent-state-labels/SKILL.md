---
name: task-subagent-state-labels
description: Invoke when a subagent starts work on an issue / a subagent has finished its implementation phase and is about to report to the parent and exit / a subagent has just been resumed by the parent to adjudicate brake findings / a subagent pauses on an external dependency such as CI or a dependent issue or the environment / a subagent pauses waiting on human input / a subagent reverts from review-pending to in-progress after a CI failure. Provides the subagent-side state-machine label mandate and its authority boundary.
layer: L3-task
---

<state-machine-label-discipline-subagent-side-mandate>

# State-machine label discipline (subagent side, mandate)

Subagent MUST fire state-machine labels at role boundaries:

- Work start → add `in-progress` (remove any prior `review-pending` / `waiting` / `blocked`). The label is the whole of this transition. The assignee is not part of it and is not the subagent's to set — the parent sets it when it delegates. Detail = Actor axis below.
- Role completion (the phase's work is finished, orchestration awaited) → switch `in-progress` → `review-pending` immediately before reporting to parent and exiting. In `auto` / `semi_auto` what the parent does next after phase 1 is the brake, not the review; the brake evaluates the finished implementation, so the wait's subject is the one `rules/task/task.md` Boundary assigns to `review-pending`, and phase 1 needs no state of its own.
- Resumed for brake adjudication (`auto` / `semi_auto` phase 2) → switch `review-pending` → `in-progress` before starting. Reading the findings, adjudicating them and pushing what was accepted is work running. A resume opening a later brake round fires the same transition, for the same reason.
- Pause on external dependency (CI / dependent issue / environment) → switch to `waiting` + write issue comment with reason. The reason comment is mandatory cross-session handoff context.
- Pause on human input requirement → switch to `blocked` + write issue comment with reason. Comment is mandatory. Human review of the finished implementation is not this state; it stays `review-pending` per `rules/task/task.md` Boundary.
- CI fail → fix recovery → before retry, revert `review-pending` → `in-progress` (same subagent in-session is allowed; the label reflects the actual work state).

These are transitions, not one-shot events: an item fires every time its own trigger occurs. Under the two-phase stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition) role completion is reached at the end of phase 1 and again at the end of each brake round the parent opens, which is capped (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure, Round trips). The cycle a resumed delegation traces is `in-progress` → `review-pending` repeating, which holds the one-at-a-time invariant at every point along it.

Label authority canonical spec is in `rules/task/task.md` Task Label Definitions section (`Lifecycle:` field); this skill defines the application-moment behavior.

</state-machine-label-discipline-subagent-side-mandate>

<actor-axis-issue-assignee>

# Actor axis (issue assignee)

The state axis (`in-progress`) reads whether work is running. The actor axis (assignee) reads who is running it. A single-actor setup is complete on the state axis alone; the moment two or more actors can touch one issue, "running" without "who is running it" is incomplete, and the actor axis becomes load-bearing.

Two axes, two actors, two moments. The subagent raises `in-progress` when its work starts. The parent sets the assignee when it delegates, and that act is held on its own surface (`skills/task-subagent-delegation/SKILL.md` Rules). Do not self-assign. Arriving at an issue that already names you in the Assignees field is the ordinary shape of a delegation, not a state to reconcile.

The split is asymmetric, and only the assignee moves forward. Pulling both halves to the parent to have one site is the simplification this refuses. `in-progress` is a claim that work is running, and only the actor actually running it can make that claim correctly. Set before the delegation, it outlives a subagent that dies during pre-implementation investigation: the issue then reads "work running" with nobody running it, other agents and later sessions read it as taken and leave it alone, and nothing clears it — a false lock. The assignee makes no such claim. It says who the issue was handed to, not that work is underway; it is additive; and current ownership is read from the handoff record and never from the field alone (below), so a stale assignee shuts nobody out. That asymmetry is what the split rests on, not a division of labour that could be tidied up.

What moving the assignee forward buys: `Work start` is a moment the executor has to read, and that read lands behind the implementation read — minutes can pass after spawn with neither the label nor the assignee fired. The delegation moment is not read at all; the parent is already standing on it, so the interpretation is removed rather than checked. `in-progress` keeps the executor-read moment, which is the right one for a label that names when work actually began, and its lateness is the label being accurate rather than a defect to repair.

Assignment is additive and stays additive. `--add-assignee` does not displace a prior assignee, and that is the specification, not a defect: a takeover mid-issue is itself information, and the record of who has held the issue is kept rather than overwritten. Do not remove a previous assignee to install the incoming one.

Handoff record on takeover (both, they carry different content):
- issue body = who the current owner is — a snapshot of state, per `rules/task/task.md` `Issue body = latest requirements snapshot, not history log`.
- issue comment = the takeover event and how it came about, per the same file's `Comments are secondary`.

Consequence of additivity: your own account appearing in the Assignees field does not establish that you are the current owner. Current ownership is read from the handoff record, never from the assignee field alone.

A new session finding an issue `in-progress` with no memory of starting is a normal detection signal, not an anomaly. Read the handoff record, determine whether the current owner is you or another actor, and only then judge whether to resume. The Assignees field carries no part of that signal: the parent assigns at delegation, so your own account standing there is the expected state of work that has just been handed to you.

</actor-axis-issue-assignee>

<authority-boundary>

# Authority Boundary

Subagent label authority is partial: the state-machine lifecycle subset (`in-progress` / `review-pending` / `waiting` / `blocked`) is editable by subagent. All other label axes (non-state lifecycle / type / maturity / marker) and close operations remain parent retain (`skills/task-subagent-delegation/SKILL.md` Rules).

</authority-boundary>

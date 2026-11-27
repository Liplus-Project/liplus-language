---
name: task-subagent-state-labels
description: Invoke when a subagent starts work on an issue / a subagent has finished its implementation phase and is about to report to the parent and exit / a subagent is entering brake adjudication (phase 2), resumed by the parent or spawned cold / a subagent pauses on an external dependency such as CI, a dependent issue or the environment / a subagent pauses waiting on human input / a subagent reverts from In review to In progress after a CI failure. Provides the subagent-side work-state mandate (issue status and pause labels).
layer: L3-task
---

<work-state-discipline-subagent-side-mandate>

# Work-state discipline (subagent side, mandate)

Subagent MUST fire the work state at role boundaries. Status writes use the Write command of `rules/task/task.md` Task Label Definitions (`Status`).

- Work start → write status `In progress` (remove any `waiting` / `blocked`). The status write is the whole of this transition. The assignee and the `Todo` status are not part of it and are not the subagent's to set — the parent sets them when it delegates. Detail = Actor axis below.
- Role completion (the phase's work is finished, orchestration awaited) → write status `In review` immediately before reporting to parent and exiting, with no `waiting` / `blocked` attached. In `auto` / `semi_auto` what the parent does next after phase 1 is the brake, not the review; the brake evaluates the finished implementation, so the wait's subject is the one `rules/task/task.md` Boundary assigns to `In review`, and phase 1 needs no state of its own.
- Entering brake adjudication (`auto` / `semi_auto` phase 2) → write status `In progress` before starting. Reading the findings, adjudicating them and pushing what was accepted is work running. The trigger is the phase, not the mechanism that put you in it: a true resume and a cold spawn under the reconstruction fallback (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary) both enter phase 2 and both fire this transition. Entering a later brake round fires it again, on either path, for the same reason.
- Pause on external dependency (CI / dependent issue / environment) → add `waiting` + write issue comment with reason; the status stays `In progress`. The reason comment is mandatory cross-session handoff context.
- Pause on human input requirement → add `blocked` + write issue comment with reason; the status stays `In progress`. Comment is mandatory. Human review of the finished implementation is not this state; it stays `In review` per `rules/task/task.md` Boundary.
- CI fail → fix recovery → before retry, write status `In progress` back from `In review` (same subagent in-session is allowed; the status reflects the actual work state).

These are transitions, not one-shot events: an item fires every time its own trigger occurs. Under the two-phase stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition) role completion is reached at the end of phase 1 and again at the end of each brake round the parent opens (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure step 8, Round boundary). The cycle a resumed delegation traces is `In progress` → `In review` repeating.

Work-state canonical spec is in `rules/task/task.md` Task Label Definitions section (`Status` and `Lifecycle labels` fields); this skill defines the application-moment behavior.

</work-state-discipline-subagent-side-mandate>

<actor-axis-issue-assignee>

# Actor axis (issue assignee)

The state axis (status `In progress`) reads whether work is running. The actor axis (assignee) reads who is running it. A single-actor setup is complete on the state axis alone; the moment two or more actors can touch one issue, "running" without "who is running it" is incomplete, and the actor axis becomes load-bearing.

Two axes, two actors, two moments. The subagent writes `In progress` when its work starts. The parent sets the assignee, with the status `Todo`, when it delegates, and that act is held on its own surface (`skills/task-subagent-delegation/SKILL.md` Rules). Do not self-assign. Arriving at an issue that already names you in the Assignees field is the ordinary shape of a delegation, not a state to reconcile.

The split is asymmetric, and only the assignee and `Todo` move forward. Pulling `In progress` to the parent as well to have one site is the simplification this refuses. `In progress` is a claim that work is running, and only the actor actually running it can make that claim correctly. Set before the delegation, it outlives a subagent that dies during pre-implementation investigation: the issue then reads "work running" with nobody running it, other agents and later sessions read it as taken and leave it alone, and nothing clears it — a false lock. The assignee and `Todo` make no such claim. They say who the issue was handed to, not that work is underway; the assignee is additive; and current ownership is read from the handoff record and never from the field alone (below), so a stale assignee costs the next reader one confirmation with the named actor or the human, not a lock nobody can clear. That asymmetry is what the split rests on, not a division of labour that could be tidied up.

What moving the assignee forward buys: `Work start` is a moment the executor has to read, and that read lands behind the implementation read — minutes can pass after spawn with neither the status nor the assignee fired. The delegation moment is not read at all; the parent is already standing on it, so the interpretation is removed rather than checked. `In progress` keeps the executor-read moment, which is the right one for a status that names when work actually began, and its lateness is the status being accurate rather than a defect to repair.

Assignment is additive and stays additive. `--add-assignee` does not displace a prior assignee, and that is the specification, not a defect: a takeover mid-issue is itself information, and the record of who has held the issue is kept rather than overwritten. Do not remove a previous assignee to install the incoming one.

Handoff record on takeover (both, they carry different content):
- issue body = who the current owner is — a snapshot of state, per `rules/task/task.md` `Issue body = latest requirements snapshot, not history log`.
- issue comment = the takeover event and how it came about, per the same file's `Comments are secondary`.

Consequence of additivity: your own account appearing in the Assignees field does not establish that you are the current owner. Current ownership is read from the handoff record, never from the assignee field alone.

Reading the field before an issue is taken — when another account there stops the start, and what lifts that stop — is `rules/operations/main-agent-procedures.md` Branch and label flow, Assignee read.

A new session finding an issue at status `In progress` with no memory of starting is a normal detection signal, not an anomaly. Read the handoff record, determine whether the current owner is you or another actor, and only then judge whether to resume. The Assignees field carries no part of that signal: the parent assigns at delegation, so your own account standing there is the expected state of work that has just been handed to you.

</actor-axis-issue-assignee>

<authority-boundary>

# Authority Boundary

Subagent authority is partial: the work state (status `In progress` / `In review`, labels `waiting` / `blocked`) is editable by subagent. The `Todo` status write, all other label axes (non-state lifecycle / type / maturity / marker) and close operations remain parent retain (`skills/task-subagent-delegation/SKILL.md` Rules).

</authority-boundary>

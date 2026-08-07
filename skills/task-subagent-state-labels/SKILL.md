---
name: task-subagent-state-labels
description: Invoke when a subagent starts work on an issue / a subagent has finished its implementation phase and is about to report to the parent and exit / a subagent has just been resumed by the parent to adjudicate brake findings / a subagent pauses on an external dependency such as CI or a dependent issue or the environment / a subagent pauses waiting on human input / a subagent reverts from review-pending to in-progress after a CI failure. Provides the subagent-side state-machine label mandate (in-progress, review-pending, waiting, blocked), the transitions that fire twice under the two-phase stop condition, the mandatory issue-comment requirement on waiting and blocked transitions, and the authority boundary against parent-retained label axes.
layer: L3-task
---

<state-machine-label-discipline-subagent-side-mandate>

# State-machine label discipline (subagent side, mandate)

Subagent MUST fire state-machine labels at role boundaries:

- Work start → add `in-progress` (remove any prior `review-pending` / `waiting` / `blocked`) **and self-assign the issue** with `gh issue edit {issue_number} -R {owner}/{repo} --add-assignee "@me"`. The pair is the transition; firing one without the other leaves it half-executed. Detail = Actor axis below.
- Role completion (the phase's work is finished, orchestration awaited) → switch `in-progress` → `review-pending` immediately before reporting to parent and exiting. In `auto` / `semi_auto` what the parent does next after phase 1 is the brakes, not the review; the brakes evaluate the finished implementation, so the wait's subject is the one `rules/task/task.md` Boundary assigns to `review-pending`, and phase 1 needs no state of its own.
- Resumed for brake adjudication (`auto` / `semi_auto` phase 2) → switch `review-pending` → `in-progress` before touching the PR. Reading the findings, answering them on the PR and pushing what was accepted is work running.
- Pause on external dependency (CI / dependent issue / environment) → switch to `waiting` + write issue comment with reason. The reason comment is mandatory cross-session handoff context.
- Pause on human input requirement → switch to `blocked` + write issue comment with reason. Comment is mandatory. Human review of the finished implementation is not this state; it stays `review-pending` per `rules/task/task.md` Boundary.
- CI fail → fix recovery → before retry, revert `review-pending` → `in-progress` (same subagent in-session is allowed; the label reflects the actual work state).

These are transitions, not one-shot events: an item fires every time its own trigger occurs. Under the two-phase stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition) role completion is reached twice, so `review-pending` is raised at the end of phase 1 and again at the end of phase 2. The cycle a resumed delegation traces is `in-progress` → `review-pending` → `in-progress` → `review-pending`, which holds the one-at-a-time invariant at every point along it.

Label authority canonical spec is in `rules/task/task.md` Task Label Definitions section (`Lifecycle:` field); this skill defines the application-moment behavior.

</state-machine-label-discipline-subagent-side-mandate>

<actor-axis-issue-assignee>

# Actor axis (issue assignee)

The state axis (`in-progress`) reads whether work is running. The actor axis (assignee) reads who is running it. A single-actor setup is complete on the state axis alone; the moment two or more actors can touch one issue, "running" without "who is running it" is incomplete, and the actor axis becomes load-bearing.

Assignment is additive and stays additive. `--add-assignee` does not displace a prior assignee, and that is the specification, not a defect: a takeover mid-issue is itself information, and the record of who has held the issue is kept rather than overwritten. Do not remove a previous assignee to install yourself.

Handoff record on takeover (both, they carry different content):
- issue body = who the current owner is — a snapshot of state, per `rules/task/task.md` `Issue body = latest requirements snapshot, not history log`.
- issue comment = the takeover event and how it came about, per the same file's `Comments are secondary`.

Consequence of additivity: your own account appearing in the Assignees field does not establish that you are the current owner. Current ownership is read from the handoff record, never from the assignee field alone.

A new session finding itself assigned and `in-progress` with no memory of starting is a normal detection signal, not an anomaly. Read the handoff record, determine whether the current owner is you or another actor, and only then judge whether to resume.

</actor-axis-issue-assignee>

<authority-boundary>

# Authority Boundary

Subagent label authority is partial: the state-machine lifecycle subset (`in-progress` / `review-pending` / `waiting` / `blocked`) is editable by subagent. All other label axes (non-state lifecycle / type / maturity / marker) and close operations remain parent retain (`skills/task-subagent-delegation/SKILL.md` Rules).

</authority-boundary>

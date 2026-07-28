---
name: task-subagent-state-labels
description: Invoke when a subagent starts work on an issue / a subagent has finished its implementation phase and is about to report to the parent and exit / a subagent pauses on an external dependency such as CI or a dependent issue or the environment / a subagent pauses waiting on human input / a subagent reverts from done to in-progress after a CI failure. Provides the subagent-side state-machine label mandate (in-progress, done, waiting, blocked), the mandatory issue-comment requirement on waiting and blocked transitions, and the authority boundary against parent-retained label axes.
layer: L3-task
---

<state-machine-label-discipline-subagent-side-mandate>

# State-machine label discipline (subagent side, mandate)

Subagent MUST fire state-machine labels at role boundaries:

- Work start → add `in-progress` (remove any prior `done` / `waiting` / `blocked`).
- Role completion (implementation phase finished, orchestration awaited) → switch `in-progress` → `done` immediately before reporting to parent and exiting.
- Pause on external dependency (CI / dependent issue / environment) → switch to `waiting` + write issue comment with reason. The reason comment is mandatory cross-session handoff context.
- Pause on human input requirement → switch to `blocked` + write issue comment with reason. Comment is mandatory.
- CI fail → fix recovery → before retry, revert `done` → `in-progress` (same subagent in-session is allowed; the label reflects the actual work state).

Label authority canonical spec is in `rules/task/task.md` Task Label Definitions section (`Lifecycle:` field); this skill defines the application-moment behavior.

</state-machine-label-discipline-subagent-side-mandate>

<authority-boundary>

# Authority Boundary

Subagent label authority is partial: the state-machine lifecycle subset (`in-progress` / `done` / `waiting` / `blocked`) is editable by subagent. All other label axes (non-state lifecycle / type / maturity / marker) and close operations remain parent retain (`skills/task-subagent-delegation/SKILL.md` Rules).

</authority-boundary>

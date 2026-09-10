---
name: operations-on-branch
description: Invoke when a subagent is about to start implementing and must judge whether to work on a protected shared branch such as main instead of the personal issue-linked branch it was given / local validation is about to be treated as the completion condition in place of the branch. Provides the repo-first execution surface; the branch and label flow canonical lives in `rules/operations/main-agent-procedures.md`.
layer: L4-operations
---

<repo-first-execution-surface>

# Repo-first Execution Surface

Protected shared branches (example: main) = high-caution surface.
Personal issue-linked branch = normal implementation surface.
Do not treat the whole repository as untouchable.
Local validation may happen before or after push; it does not replace the branch as continuity surface.

</repo-first-execution-surface>

<branch-and-label-flow>

# Branch And Label Flow

Pointer. Canonical = `rules/operations/main-agent-procedures.md` Branch and label flow: the act-now trigger, the NOW / SOON / SOMEDAY tiers and their label mapping, the atmosphere-reading scope, the branch existence check, the `gh issue develop` command, the merge behavior, and the local-error recovery all live there.

The subagent still reaches the canonical — `rules/**` loads for it without invocation — so nothing it needs when it creates the branch itself is lost by the move.

</branch-and-label-flow>

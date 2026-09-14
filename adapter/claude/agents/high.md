---
name: high
description: Li+ generic subagent, effort fixed at `high`. Carries no role of its own — the spawning parent conveys role and procedure in the invocation prompt (`skills/task-subagent-spawn/SKILL.md` fixes which effort a given spawn selects; `skills/task-subagent-prompt/SKILL.md` and `skills/evolution-parallel-agent-eval/SKILL.md` hold the role literals injected into that prompt). Named as `subagent_type` directly by the parent at spawn; not self-invoked.
effort: high
---

<!-- --- Li+ BEGIN ({LI_PLUS_TAG}) --- -->

You are a Li+ subagent spawned at `high` effort. This file fixes effort only — no role, no procedure.

What you do, and what you read to do it, arrive in the prompt that spawned you. Li+ rules load into your context without being invoked (`rules/**/*.md`), and Li+ skills invoke on description match (`skills/*/SKILL.md`). Take your task from the prompt, not from this file.

<!-- --- Li+ END --- -->

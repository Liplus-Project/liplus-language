---
name: task-subagent-delegation
description: Invoke when delegating implementation, operations, or a bounded read-only investigation (audit / consistency check / grep-and-report) to a subagent; defines what to convey, what parent retains, and mode-dependent execution scope.
layer: L3-task
---

<subagent-delegation>

# Subagent Delegation

<rules>

## Rules

Parent agent delegates implementation and operations to subagent.
Parent retains: issue creation, issue management (non-state lifecycle labels / type / maturity / marker / close), review judgment.
if execution_mode == auto:
  Subagent executes: branch, implementation, commit, push, PR, CI loop.
  Parent retains: self-review, merge decision.
if execution_mode == trigger:
  Subagent executes: branch, implementation, commit, push, PR, CI loop, merge.

Do not convey: step-by-step procedure, branch name, commit message, intent.
Intent is already in issue body.

Subagent label authority is partial: the state-machine lifecycle subset (`in-progress` / `done` / `waiting` / `blocked`) is editable by subagent. All other label axes (non-state lifecycle / type / maturity / marker) and close operations remain parent retain.

</rules>

<state-machine-label-discipline-subagent-side-mandate>

## State-machine label discipline (subagent side, mandate)

Subagent MUST fire state-machine labels at role boundaries:

- Work start → add `in-progress` (remove any prior `done` / `waiting` / `blocked`).
- Role completion (implementation phase finished, orchestration awaited) → switch `in-progress` → `done` immediately before reporting to parent and exiting.
- Pause on external dependency (CI / dependent issue / environment) → switch to `waiting` + write issue comment with reason. The reason comment is mandatory cross-session handoff context.
- Pause on human input requirement → switch to `blocked` + write issue comment with reason. Comment is mandatory.
- CI fail → fix recovery → before retry, revert `done` → `in-progress` (same subagent in-session is allowed; the label reflects the actual work state).

Label authority canonical spec is in `rules/task/task.md` Lifecycle section; this skill defines the application-moment behavior.

</state-machine-label-discipline-subagent-side-mandate>

<responsibilities>

## Responsibilities

Convey to subagent:
issue URL.

If the host adapter auto-loads Li+ layers for subagents, no explicit file reads are needed.
Fallback: also convey rules/*.md and skills/*/SKILL.md paths from LI_PLUS_REPOSITORY.
Detailed parent instructions risk conflicting with operations rules.

Issue body update:
Subagent may update issue body when premise or constraints change during implementation.

Failure reporting:
On failure, subagent writes failure report as issue comment. Format is not specified.

Branch linking: see skills/operations-on-branch/SKILL.md.

</responsibilities>

<autonomy>

## Autonomy

If subagent capability is unavailable:
Parent executes operations directly. All rules still apply.

</autonomy>

<mode-specific-delegation-injection>

## Mode-specific delegation injection

The minimal "issue URL only" pattern works for `auto` and `semi_auto` because the subagent's auto-loaded operations rules already cover the merge gate. `trigger` mode is the exception: the merge gate involves human approval timing, and three pieces of context need explicit injection because they are parent-side decisions, not subagent-discovered facts:

- (a) commit body language: project-language constraint (e.g. Japanese for liplus-language). Auto-loaded operations.md states the rule, but missed-application is the recurring failure mode; explicit reminder in the delegation prompt prevents drift.
- (b) auto-merge enablement: include `gh pr merge {pr} --auto --squash` as a step the subagent runs after PR creation. Without this, the merge sits idle after human approval because trigger-mode PRs do not auto-merge by default.
- (c) stop condition: subagent stops at "PR open + auto-merge enabled + CI green + awaiting human review" — NOT at merge complete. Merge fires later via GitHub auto-merge after human approval; the subagent's session ends before that.

These three are out of scope for the broader "do not convey procedure" rule because they are not procedure — they are gate-state decisions specific to trigger-mode merge timing.

</mode-specific-delegation-injection>

<delegation-prompt-hygiene-ascii-only-example-text>

## Delegation prompt hygiene (ASCII-only example text)

Any example text the subagent may quote into an artifact (suggested PR title / commit title / commit body / wiki entry / issue body) MUST be ASCII-only. Subagents mirror the prompt's literal style when emitting artifacts; non-ASCII typographic characters (em-dash `—` / en-dash `–` / box-drawing `─` / smart quotes `' " ' "` / JA characters in example PR titles) leak through and persist in merged artifacts because governance CI checks PR titles only — commit bodies, wiki entry bodies, and issue bodies are not byte-checked.

How to apply:
- Substitute ASCII before sending the prompt: em-dash -> `-` / `--`, en-dash -> `-`, box-drawing horizontal -> `-` / `=`, smart quotes -> ASCII `'` `"`, JA-in-example-PR-title -> romanize or omit.
- Add an explicit instruction to the prompt: "Use ASCII characters only in PR titles, commit titles/bodies, and entry body text. Apply `od -c` byte-level verification to BOTH titles AND body content text."
- The prompt's surrounding prose may use non-ASCII (em-dash for English reading efficiency is fine); the *example text fields* the subagent might copy must be ASCII.

Detection signs:
- About to write `—` or `──` in an example title / body field inside the delegation prompt.
- Example PR title field contains JA characters or smart quotes.
- Re-reading own prompt: surrounding prose mixes typographic chars freely while example fields inherit the same mix.
- Subagent reports "pre-existing em-dash found in previously-merged artifact" — the propagation already happened.

</delegation-prompt-hygiene-ascii-only-example-text>

<bounded-delegation-prohibit-recursive-subagent-spawn>

## Bounded delegation: prohibit recursive subagent spawn

A subagent with Agent tool access (`Tools: *`, typically `general-purpose`) defaults to the same fan-out instinct the parent has: when its assigned task looks like it has multiple independent sub-checks, it may spawn its own nested Agent-tool children rather than executing directly. Absent an explicit prohibition, this can cascade at every level — each hop adds real API cost with no visible warning until the rate limit wall is hit, and the top-level report ends up as coordinator meta-commentary ("waiting for background agent") instead of actual findings.

How to apply:
- When delegating a bounded read-only investigation (audit / consistency check / grep-and-report) to a subagent, explicitly state in the prompt: "Do this yourself directly using Read/Grep/Bash — do not spawn further subagents via the Agent tool for this task."
- If a subagent's task has 2-3 independent sub-checks that seem parallelizable, prefer sequencing them directly inside one subagent's own tool calls over letting it decide to spawn children.
- Reserve subagent-of-subagent delegation for genuinely large-scale parallel work where the fan-out is deliberate and bounded (e.g. `skills/evolution-parallel-agent-eval` N=3 evaluator pattern — a controlled, known-width fan-out is exempt from this prohibition).

This is a tool-authority bound (which tools the subagent may use), not a conveyed step-by-step procedure — it does not conflict with the top-level Rules section's "do not convey: step-by-step procedure" constraint, same reconciliation as `mode-specific-delegation-injection` above.

Detection signs:
- About to write a delegation prompt with multiple distinct "Check A / Check B" sections without explicitly stating the subagent should perform all checks directly itself.
- A task-notification result consisting of meta-commentary ("I'll wait for the background agent", "the audit is running in the background") rather than actual findings — that phrasing means the "agent" is a coordinator that itself spawned more agents instead of doing the work.
- A burst of many task-notifications arriving in immediate succession after only 2-3 Agent calls were made.

</bounded-delegation-prohibit-recursive-subagent-spawn>

<memory-only-knowledge-does-not-transfer-to-subagent>

## Memory-only knowledge does not transfer to subagent

Parent-side memory (workspace memory/feedback.md, memory/project.md, in-session corrections) is NOT auto-loaded into the subagent's context. The subagent only sees the issue body, the auto-loaded Li+ rules and skills, and the delegation prompt itself.

If subagent behavior depends on memory content, the parent MUST inject the relevant literal into the delegation prompt. "Memory has it, so subagent will pick it up" has failed multiple times in past sessions; pattern-match this assumption and reject it at delegation-construction time.

The cure is to either (i) inject the literal text into the prompt, or (ii) escalate the memory entry through promotion to Li+ rules so it auto-loads — promotion is the durable fix; injection is the per-task workaround.

</memory-only-knowledge-does-not-transfer-to-subagent>

</subagent-delegation>

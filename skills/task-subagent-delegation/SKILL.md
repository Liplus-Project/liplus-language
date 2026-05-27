---
name: task-subagent-delegation
description: Invoke when delegating implementation or operations to a subagent; defines what to convey, what parent retains, and mode-dependent execution scope.
layer: L3-task
---

# Subagent Delegation
<subagent-delegation>

## Rules
<rules>

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

## State-machine label discipline (subagent side, mandate)
<state-machine-label-discipline-subagent-side-mandate>

Subagent MUST fire state-machine labels at role boundaries:

- Work start → add `in-progress` (remove any prior `done` / `waiting` / `blocked`).
- Role completion (implementation phase finished, orchestration awaited) → switch `in-progress` → `done` immediately before reporting to parent and exiting.
- Pause on external dependency (CI / dependent issue / environment) → switch to `waiting` + write issue comment with reason. The reason comment is mandatory cross-session handoff context.
- Pause on human input requirement → switch to `blocked` + write issue comment with reason. Comment is mandatory.
- CI fail → fix recovery → before retry, revert `done` → `in-progress` (same subagent in-session is allowed; the label reflects the actual work state).

Label authority canonical spec is in `rules/task/task.md` Lifecycle section; this skill defines the application-moment behavior.

</state-machine-label-discipline-subagent-side-mandate>

## Responsibilities
<responsibilities>

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

## Autonomy
<autonomy>

If subagent capability is unavailable:
Parent executes operations directly. All rules still apply.

</autonomy>

## Mode-specific delegation injection
<mode-specific-delegation-injection>

The minimal "issue URL only" pattern works for `auto` and `semi_auto` because the subagent's auto-loaded operations rules already cover the merge gate. `trigger` mode is the exception: the merge gate involves human approval timing, and three pieces of context need explicit injection because they are parent-side decisions, not subagent-discovered facts:

- (a) commit body language: project-language constraint (e.g. Japanese for liplus-language). Auto-loaded operations.md states the rule, but missed-application is the recurring failure mode; explicit reminder in the delegation prompt prevents drift.
- (b) auto-merge enablement: include `gh pr merge {pr} --auto --squash` as a step the subagent runs after PR creation. Without this, the merge sits idle after human approval because trigger-mode PRs do not auto-merge by default.
- (c) stop condition: subagent stops at "PR open + auto-merge enabled + CI green + awaiting human review" — NOT at merge complete. Merge fires later via GitHub auto-merge after human approval; the subagent's session ends before that.

These three are out of scope for the broader "do not convey procedure" rule because they are not procedure — they are gate-state decisions specific to trigger-mode merge timing.

</mode-specific-delegation-injection>

## Delegation prompt hygiene (ASCII-only example text)
<delegation-prompt-hygiene-ascii-only-example-text>

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

## Memory-only knowledge does not transfer to subagent
<memory-only-knowledge-does-not-transfer-to-subagent>

Parent-side memory (workspace memory/feedback.md, memory/project.md, in-session corrections) is NOT auto-loaded into the subagent's context. The subagent only sees the issue body, the auto-loaded Li+ rules and skills, and the delegation prompt itself.

If subagent behavior depends on memory content, the parent MUST inject the relevant literal into the delegation prompt. "Memory has it, so subagent will pick it up" has failed multiple times in past sessions; pattern-match this assumption and reject it at delegation-construction time.

The cure is to either (i) inject the literal text into the prompt, or (ii) escalate the memory entry through promotion to Li+ rules so it auto-loads — promotion is the durable fix; injection is the per-task workaround.

</memory-only-knowledge-does-not-transfer-to-subagent>

</subagent-delegation>

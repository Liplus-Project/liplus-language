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

<subagent-model-policy>

## Subagent Model Policy

Parent session runs opus-class model or above (`opus`, or another positively-classified opus-class-or-above id such as `fable`; per #1532 this is out of this skill's change scope, set at the scheduled-task / session level). All subagents set the Agent tool `model` parameter explicitly — default and floor = `sonnet`; explicit specification of a higher-class id (e.g. `opus`, `fable`) remains permitted but is not the default. Implicit parent-model inheritance is prohibited. Named explicitly, per Master's decision (2026-07-25) that no category is left implied:

- General delegation under this skill's Rules (implementation / operations subagent spawn).
- Brake-1 evaluators in `skills/evolution-parallel-agent-eval/SKILL.md`.
- Brake 2, the L1 root-criteria evaluator (`adapter/claude/agents/l1-gate-eval.md`, spawned by the parent as a subagent at the `model` parameter set here; its PASS verdict substitutes for human approval on PRs touching L1 Model Layer source per `Evolution_Initiator_Autonomy`). This file is not edited — the model is set at spawn time by the parent, not in the evaluator prompt file itself.
- `adapter/claude/agents/dialogue-evaluator.md` (ported to `adapter/codex/agents/dialogue-evaluator.toml`), spawned on explicit human request for dialogue evaluation. Its frontmatter carries no `model:` field, so the floor applies at spawn time the same way as the other categories. This file is not edited either.

These four are exhaustive over `adapter/*/agents/*` (verified by directory listing at #1532 fix time: only `dialogue-evaluator` and `l1-gate-eval`, each ported to `claude` and `codex`) plus the file-less general-delegation category. `.github/scripts/liplus_discussions_agent.py` (Discussions intake bot) is a separate GitHub Actions + direct Anthropic API caller, not spawned via the Agent tool from a Li+ session, and is out of scope for this policy.

Rationale (#1532): token budget reduction. Empirically grounded on Master's operational observation that Li+ previously ran entirely on Sonnet with no observed regression — during that period the parent model was also Sonnet, so brake 1's effective floor was already Sonnet.

</subagent-model-policy>

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

<parallel-width-cap>

## Parallel-Width Cap

Cap = 5 subagents in flight at once (spawned and not yet returned), applying to every parallel delegation pattern that funnels through this skill: cross-parent-issue worktree parallelism and same-parent sub-issue parallelism (both defined in `adapter/claude/CLAUDE.md` Subagent_Delegation), and bounded read-only investigation fan-out (defined in this skill's own frontmatter description). The value 5 is a provisional bound, bracketed against the established eval default width (N=3) and well under host-scale fan-out (Dynamic Workflows research preview: up to 16 concurrent / 1000 cumulative per run, evaluated and deferred in #1426 / #1428) — it is not derived from a cost or latency measurement and should be revised on observation.

Enforcement mechanism: per-message batch size (Agent tool calls in a single message) is necessary but not sufficient on its own — a message launching 5, followed by a second message launching 5 more before the first wave has returned, keeps every message at or under 5 while actual in-flight width reaches 10. The binding condition (not a stylistic preference) is that a new batch may not be launched until every subagent in the prior batch has completed and reported; only then does per-message batch size equal actual concurrent width. If a task needs wider fan-out than 5 total, split into sequential batches under this same rule rather than overlapping waves.

This cap governs top-level concurrent width (how many subagents the parent has in flight at once). It is a separate axis from `Bounded delegation: prohibit recursive subagent spawn` above, which governs spawn depth (a subagent spawning its own children) — the two do not extend or narrow each other.

Exempt: `evolution-parallel-agent-eval`'s own N / M / P fan-out (default N=3, up to N=3 x P=2 = 6, or N=3 x axis_count under the M=1 exception pattern) is a separately-bounded, deliberate fan-out per that skill's Design Dimensions and is not subject to this cap.

</parallel-width-cap>

<memory-only-knowledge-does-not-transfer-to-subagent>

## Memory-only knowledge does not transfer to subagent

Parent-side memory (workspace memory/feedback.md, memory/project.md, in-session corrections) is NOT auto-loaded into the subagent's context. The subagent only sees the issue body, the auto-loaded Li+ rules and skills, and the delegation prompt itself.

If subagent behavior depends on memory content, the parent MUST inject the relevant literal into the delegation prompt. "Memory has it, so subagent will pick it up" has failed multiple times in past sessions; pattern-match this assumption and reject it at delegation-construction time.

The cure is to either (i) inject the literal text into the prompt, or (ii) escalate the memory entry through promotion to Li+ rules so it auto-loads — promotion is the durable fix; injection is the per-task workaround.

</memory-only-knowledge-does-not-transfer-to-subagent>

</subagent-delegation>

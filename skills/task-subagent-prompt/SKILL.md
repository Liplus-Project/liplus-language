---
name: task-subagent-prompt
description: Invoke when a subagent delegation prompt is being composed / example artifact text such as a suggested PR title or commit body is about to be written into a delegation prompt / a delegation runs in trigger execution mode and merge-gate context must be injected / an implementation subagent is about to be resumed to adjudicate brake findings / subagent behavior depends on something that exists only in parent-side memory / a bounded read-only investigation prompt is being written and recursive subagent spawn must be prohibited. Provides the mode-specific injection items for trigger mode, the resume-phase authority boundary literal that keeps the resumed author off self-review and merge, field-scoped language hygiene for quotable example text, the recursive-spawn prohibition literal, and the memory-does-not-transfer rule with its injection or promotion cure.
layer: L3-task
---

<mode-specific-delegation-injection>

# Mode-specific delegation injection

The minimal "issue URL only" pattern works for `auto` and `semi_auto` because the subagent's auto-loaded operations rules already cover the merge gate. `trigger` mode is the exception: the merge gate involves human approval timing, and three pieces of context need explicit injection because they are parent-side decisions, not subagent-discovered facts:

- (a) commit body language: the destination artifact's governing language contract and repository governance (liplus-language requires Japanese). Auto-loaded operations.md states the repository rule, but missed-application is the recurring failure mode; explicit reminder in the delegation prompt prevents drift.
- (b) auto-merge enablement: include `gh pr merge {pr} --auto --squash` as a step the subagent runs after PR creation. Without this, the merge sits idle after human approval because trigger-mode PRs do not auto-merge by default.
- (c) stop condition: the `trigger` form is longer than the `auto` / `semi_auto` one and ends short of merge complete. Read it at `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition, which splits by mode; inject that mode's literal into the prompt. Do not restate it here.

These three are out of scope for the broader "do not convey procedure" rule (`skills/task-subagent-delegation/SKILL.md` Rules) because they are not procedure — they are gate-state decisions specific to trigger-mode merge timing.

</mode-specific-delegation-injection>

<resume-phase-authority-boundary>

# Resume-phase authority boundary

In `auto` / `semi_auto`, the parent resumes the implementation subagent after the brakes report so the author adjudicates the findings (`rules/evolution/initiator-autonomy.md` Two-stage brake, Adjudication actor). The resume message is a prompt like any other, and the same injection reasoning as `mode-specific-delegation-injection` applies to it: the authority boundary at the resume point is a gate-state decision, not procedure, so conveying it does not collide with "do not convey step-by-step procedure".

It has to be injected rather than left to the auto-loaded rules. The subagent resumes holding a session in which it has already run the whole implementation and is one CI-green away from a mergeable PR; the pull toward "finish it" is strongest exactly there. #1628 recorded a delegated subagent in `semi_auto` overrunning this boundary and executing both the self-review post and the merge.

Inject into the resume prompt:

- (a) the stop condition literal for this mode, read from `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition. Do not restate it here.
- (b) the two negatives, verbatim:

  > Do not run or post the self-review, and do not merge. The self-review actor is the agent holding the merge decision, which is the parent in this mode. Report at your stop condition and exit.

- (c) where the findings are: the PR URL, and that the evaluators posted their findings as PR comments. The parent does not paste the findings into the resume message — routing them through parent context is the cost this whole path removes (`skills/evolution-parallel-agent-eval/SKILL.md` Constraint: Findings route to the PR, not to the parent). At brake 2 the parent posts the named deviation to the PR itself, because that evaluator has no PR surface to post to; the deviation and the author's answer then sit on the same thread the self-review reads, exactly as at brake 1. Carrying it only inside the resume message would leave the one finding class that blocks merge with no durable record.

The Codex fallback takes the same three items. When `resume_agent` is unavailable, the parent spawns a fresh subagent into the author role and it reconstructs from the issue body, the PR diff, and the PR comments; the role is unchanged, so the boundary injected into it is unchanged.

</resume-phase-authority-boundary>

<delegation-prompt-hygiene-field-scoped-language>

# Delegation prompt hygiene (field-scoped artifact language)

Example artifact text MUST follow the destination artifact's governing language contract; being example text does not create an independent ASCII-only category. Resolve the language from (1) an explicit human language instruction for that artifact, (2) an accepted thread agreement, then (3) the destination repository / workspace project-language default (`LI_PLUS_PROJECT_LANGUAGE` when applicable), while also satisfying destination-repository governance. A host workspace language contract does not override `LI_PLUS_REPO` governance.

Issue / PR / commit title examples MUST be ASCII English only. Body examples (issue / PR / commit bodies and wiki entries) MUST follow the resolved governing language contract and MUST NOT be rewritten under an ASCII-only rule. In liplus-language, issue / PR / commit bodies contain Japanese as required by repository governance.

Subagents mirror the prompt's literal style when emitting artifacts. Non-ASCII typographic characters (em-dash `—` / en-dash `–` / box-drawing `─` / smart quotes `' " ' "` / JA characters in example titles) can leak from a prompt into an ASCII-English-governed title field. Body fields are validated as well-formed UTF-8 that renders without mojibake, not as ASCII byte sequences.

How to apply:
- For issue / PR / commit title examples, rewrite into ASCII English before sending the prompt: em-dash -> `-` / `--`, en-dash -> `-`, box-drawing horizontal -> `-` / `=`, smart quotes -> ASCII `'` `"`, and JA example-title text -> translate / rewrite into ASCII English or omit.
- For issue / PR / commit body and wiki-entry examples, resolve the destination artifact's governing language contract using the precedence above; validate well-formed UTF-8 and inspect rendered text for mojibake. Do not use an ASCII-only check as body validation.
- Add an explicit instruction to the prompt: "Use ASCII English only in issue, PR, and commit titles. Resolve issue/PR/commit bodies and wiki entries from each destination artifact's governing language contract: an explicit human language instruction for that artifact, then an accepted thread agreement, then the destination repository/workspace project-language default, while satisfying destination-repository governance. The host workspace language contract does not override LI_PLUS_REPO governance; in liplus-language, issue/PR/commit bodies require Japanese. Never apply an ASCII-only rule to bodies. Apply `od -c` byte-level verification to title fields, and verify body text is well-formed UTF-8 and renders without mojibake."
- The prompt's surrounding prose is outside title-field ASCII checks; every example field the subagent might copy follows its own destination-field contract.

Detection signs:
- About to write `—` or `──` in an ASCII-English-governed example title inside the delegation prompt.
- Example PR title field contains JA characters or smart quotes.
- Example body is forced to ASCII or omits the resolved governing language contract or destination-repository governance.
- A host workspace language default is used to override `LI_PLUS_REPO` governance.
- `od -c` or another byte-level ASCII check is applied to body content as an acceptance criterion instead of UTF-8 / mojibake validation.
- One instruction groups title and body fields under the same ASCII-only clause.

</delegation-prompt-hygiene-field-scoped-language>

<bounded-delegation-prohibit-recursive-subagent-spawn>

# Bounded delegation: prohibit recursive subagent spawn

A subagent with Agent tool access (`Tools: *`, typically `general-purpose`) defaults to the same fan-out instinct the parent has: when its assigned task looks like it has multiple independent sub-checks, it may spawn its own nested Agent-tool children rather than executing directly. Absent an explicit prohibition, this can cascade at every level — each hop adds real API cost with no visible warning until the rate limit wall is hit, and the top-level report ends up as coordinator meta-commentary ("waiting for background agent") instead of actual findings.

How to apply:
- When delegating a bounded read-only investigation (audit / consistency check / grep-and-report) to a subagent, explicitly state in the prompt: "Do this yourself directly using Read/Grep/Bash — do not spawn further subagents via the Agent tool for this task."
- If a subagent's task has 2-3 independent sub-checks that seem parallelizable, prefer sequencing them directly inside one subagent's own tool calls over letting it decide to spawn children.
- Reserve subagent-of-subagent delegation for genuinely large-scale parallel work where the fan-out is deliberate and bounded (e.g. `skills/evolution-parallel-agent-eval` N=3 evaluator pattern — a controlled, known-width fan-out is exempt from this prohibition).

This is a tool-authority bound (which tools the subagent may use), not a conveyed step-by-step procedure — it does not conflict with `skills/task-subagent-delegation/SKILL.md` Rules' "do not convey: step-by-step procedure" constraint, same reconciliation as `mode-specific-delegation-injection` above.

Spawn depth is the axis here. Top-level concurrent width is a separate axis, in `skills/task-subagent-spawn/SKILL.md` Parallel-Width Cap; the two do not extend or narrow each other.

Detection signs:
- About to write a delegation prompt with multiple distinct "Check A / Check B" sections without explicitly stating the subagent should perform all checks directly itself.
- A task-notification result consisting of meta-commentary ("I'll wait for the background agent", "the audit is running in the background") rather than actual findings — that phrasing means the "agent" is a coordinator that itself spawned more agents instead of doing the work.
- A burst of many task-notifications arriving in immediate succession after only 2-3 Agent calls were made.

</bounded-delegation-prohibit-recursive-subagent-spawn>

<memory-only-knowledge-does-not-transfer-to-subagent>

# Memory-only knowledge does not transfer to subagent

Parent-side memory (the per-topic entry files `memory/feedback_<topic>.md`, `memory/project_<topic>.md` and their siblings, plus in-session corrections) is NOT auto-loaded into the subagent's context. The subagent only sees the issue body, the auto-loaded Li+ rules and skills, and the delegation prompt itself.

If subagent behavior depends on memory content, the parent MUST inject the relevant literal into the delegation prompt. "Memory has it, so subagent will pick it up" has failed multiple times in past sessions; pattern-match this assumption and reject it at delegation-construction time.

The cure is to either (i) inject the literal text into the prompt, or (ii) escalate the memory entry through promotion to Li+ rules so it auto-loads — promotion is the durable fix; injection is the per-task workaround.

</memory-only-knowledge-does-not-transfer-to-subagent>

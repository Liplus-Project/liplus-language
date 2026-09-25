---
name: task-subagent-prompt
description: Invoke when a subagent delegation prompt is being composed / example artifact text such as a suggested PR title or commit body is about to be written into a delegation prompt / a delegation runs in trigger execution mode and merge-gate context must be injected / an implementation subagent is about to be resumed to adjudicate brake findings / brake adjudication is starting and no resume target for the implementation subagent is held / subagent behavior depends on something that exists only in parent-side memory / a bounded read-only investigation prompt is being written and recursive subagent spawn must be prohibited. Provides the prompt composition rules for each of these moments.
layer: L3-task
---

<role-literal-implementation-delegate>

# Role literal: implementation delegate

On Claude Code this is the implementation-delegate role's only home: `adapter/claude/agents/` holds effort-named files (`low.md` / `medium.md` / `high.md`) that carry no role. Every delegation prompt composed under `skills/task-subagent-delegation/SKILL.md` injects the literal below verbatim, before any mode-specific or resume-phase addition. Copy it; do not re-compose it per spawn.

> You are the Li+ implementation delegate. A parent agent hands you one issue's change; you carry it to the stop condition, report there, and exit.
>
> What you execute is fixed by `skills/task-subagent-delegation/SKILL.md` Rules, split by execution mode. Where your session ends is fixed by `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition. Read both at the moment they apply. Neither is restated here; the second copy is what drifts.
>
> Li+ rules load into your context without being invoked (`rules/**/*.md`), and Li+ skills invoke on description match (`skills/*/SKILL.md`).
>
> Standing bounds on this role:
>
> - Work inside the path the delegation gave you, on the branch it arrived on. Do not create, move, or remove worktrees or per-session clones.
> - Do not spawn subagents of your own (Bounded delegation, below).
> - Do not post the self-review record and do not merge. Those actors are fixed elsewhere and neither is you.
> - Report at the stop condition and exit. The parent holds the judgment; forming it for them is not your share.
>
> Correctness is repository state, not local success: the issue's requirement met in the pushed diff, with CI green on it.

Spawn call: one of `subagent_type: low` / `medium` / `high`, selected by the parent against the work that delegation carries (criteria = `skills/task-subagent-spawn/SKILL.md` Subagent Model Policy). The role picks neither the effort nor the `model`; the literal above is injected whichever the spawn names. Do not write a role fragment into `adapter/claude/agents/{low,medium,high}.md`.

On Codex the role body stays in `adapter/codex/agents/implementer.toml`; this section does not move it.

</role-literal-implementation-delegate>

<mode-specific-delegation-injection>

# Mode-specific delegation injection

`auto` / `semi_auto` delegations carry no merge-gate injection; the subagent's auto-loaded operations rules cover the merge gate. A `trigger` delegation injects two items. They are gate-state decisions, not procedure, so the "do not convey procedure" rule (`skills/task-subagent-delegation/SKILL.md` Rules) does not bar them:

- (a) auto-merge enablement: include `gh pr merge {pr} --auto --squash` as a step the subagent runs after PR creation. Without it the PR sits idle after human approval.
- (b) stop condition: direct the subagent to read its own stop condition for this mode at `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition, which splits by mode, and to restate it before it starts. Carry the pointer, not the literal: the parent may not read that file (`rules/operations/main-agent-procedures.md` The bar and its pair). Do not restate the condition here either.

Artifact body language is not a `trigger`-mode item, and its absence here exempts no mode: it is required in every delegation, at Delegation prompt hygiene below. Do not add a copy of it to this list.

</mode-specific-delegation-injection>

<resume-phase-authority-boundary>

# Resume-phase authority boundary

In `auto` / `semi_auto`, the parent resumes the implementation subagent after the brake reports so the author adjudicates the findings (`rules/evolution/initiator-autonomy.md` Merge brake, Adjudication actor). Inject the authority boundary into the resume message; auto-loaded rules alone do not hold it at the resume point. It is a gate-state decision, not procedure, so conveying it does not collide with "do not convey step-by-step procedure". The overrun it guards against is a resumed subagent in `semi_auto` executing both the self-review post and the merge.

Inject into the resume prompt:

- (a) an instruction to read its own stop condition for this mode at `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition and restate it before acting. Carry the pointer, not the literal: the parent may not read that file (`rules/operations/main-agent-procedures.md` The bar and its pair). The boundary itself is carried by (b), which stays verbatim.
- (b) the two negatives, verbatim:

  > Do not run or post the self-review, and do not merge. The self-review actor is the agent holding the merge decision, which is the parent in this mode. Report at your stop condition and exit.

- (c) where the findings are: the PR URL, and that this round's evaluator comments on its thread carry them (`skills/evolution-parallel-agent-eval/SKILL.md` Constraint: Findings are posted to the PR by the evaluator). Do not paste the findings into the resume message.

- (d) the resolved language for the adjudication comment the author posts on the PR, named as the value for this run, with the instruction that it is not to be written into any file the subagent edits. A PR comment resolves on the base-language side of `Workspace_Language_Contract`, so neither the body language of Delegation prompt hygiene (b) below nor the value the phase-1 prompt carried answers it.

A resume opening a later round (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure, Round boundary) takes these four unchanged. Its subject is the entry alone — new findings are on the thread — and the parent adds no correction of its own to it.

The list is closed by criterion, not by enumeration. An item is injected when it is a gate-state decision at the resume point: the boundary of what the resumed author may do, or parent-side state its own session cannot see. What the author does inside that boundary is procedure and stays where it is canonically held. The subagent's own state-label transitions at this moment are not listed; they are mandated at `skills/task-subagent-state-labels/SKILL.md`, which auto-loads and names the resume among its triggers. An item auto-load already covers is promoted into this list on a measured overrun at this point, not on the prospect of one (`rules/model/subtractive-structural-beauty.md` required or unnecessary). If the doubt is that the auto-load surface does not fire reliably, fix that surface, not this list.

Reconstruction fallback. It applies when the parent holds no resume target it can address: the host has no resume mechanism (Codex without `resume_agent`), or the parent does not hold the phase-1 agent id — the standing case whenever adjudication runs in a later session than the implementation. Both route to the same fallback; each adapter names only which of the two its host produces.

The fallback: the parent spawns a fresh subagent into the author role, and it reconstructs from the issue body, the PR diff, the commits on the branch, and the PR comment thread, which carries the findings of every round so far and any adjudication already made. The four items above are injected unchanged, and the parent still does not paste the findings. Exactly one item is added: the spawn enters at phase 2 — the change is already implemented and the PR is open, and its work is adjudication, not implementation (`skills/task-subagent-delegation/SKILL.md` Rules, the two phases). A true resume does not carry that item.

This is not the substrate-absence fallback of `skills/task-subagent-delegation/SKILL.md` Autonomy. Subagent capability is present and only the resume target is gone, so the work stays on a subagent. Routing a lost id to the parent would move adjudication off the author and break `rules/evolution/initiator-autonomy.md` Merge brake, Adjudication actor.

</resume-phase-authority-boundary>

<delegation-prompt-hygiene-field-scoped-artifact-language>

# Delegation prompt hygiene (field-scoped artifact language)

Example artifact text follows the destination field's contract; being example text creates no ASCII-only category of its own.

- (a) Issue / PR / commit title examples: ASCII English only. Subagents mirror the prompt's literal style, so rewrite each example title before sending: em-dash -> `-` / `--`, en-dash -> `-`, box-drawing horizontal -> `-` / `=`, smart quotes -> ASCII `'` `"`, and JA example-title text -> translate / rewrite into ASCII English or omit.
- (b) Body examples (issue / PR / commit bodies and wiki entries): the destination artifact's governing language contract, resolved by the precedence in the instruction below (its project-language default is `LI_PLUS_PROJECT_LANGUAGE` when applicable), while also satisfying destination-repository governance. A host workspace language contract does not override `LI_PLUS_REPO` governance. Never rewrite a body under an ASCII-only rule; validate it as well-formed UTF-8 that renders without mojibake.
- The prompt's surrounding prose is outside title-field ASCII checks; every example field the subagent might copy follows its own destination-field contract.

Add this instruction to the prompt:

> "Use ASCII English only in issue, PR, and commit titles. Resolve issue/PR/commit bodies and wiki entries from each destination artifact's governing language contract: an explicit human language instruction for that artifact, then an accepted thread agreement, then the destination repository/workspace project-language default, while satisfying destination-repository governance. The host workspace language contract does not override LI_PLUS_REPO governance. Never apply an ASCII-only rule to bodies. Apply `od -c` byte-level verification to title fields, and verify body text is well-formed UTF-8 and renders without mojibake."

Name the resolved body language next to that instruction, as the value for this run, and say it is not to be written into any file the subagent edits. The subagent cannot resolve it itself: `LI_PLUS_BASE_LANGUAGE` / `LI_PLUS_PROJECT_LANGUAGE` are emitted by the session-start hook into the parent's session, and hook output does not reach a subagent (`skills/evolution-parallel-agent-eval/SKILL.md` Constraint: Character_Instance non-inheritance). Write no resolved language name into this file or any other Li+ source.

Detection signs:
- About to write `—` or `──`, JA characters, or smart quotes in an ASCII-English-governed example title.
- Example body is forced to ASCII or omits the resolved governing language contract or destination-repository governance.
- A host workspace language default is used to override `LI_PLUS_REPO` governance.
- A resolved language name is about to be written into the quoted instruction above, or into any other Li+ source line, instead of being named per run.
- The prompt is about to be sent with the contract named and no resolved value, leaving the subagent the prompt's own language as its only signal.
- `od -c` or another byte-level ASCII check is applied to body content as an acceptance criterion instead of UTF-8 / mojibake validation.
- One instruction groups title and body fields under the same ASCII-only clause.

</delegation-prompt-hygiene-field-scoped-artifact-language>

<bounded-delegation-prohibit-recursive-subagent-spawn>

# Bounded delegation: prohibit recursive subagent spawn

A subagent holding the Agent tool — the Li+ implementation delegate on either port (neither definition names `tools`, so both take the default set) and the host's built-in general-purpose agent alike — may spawn nested children when its task looks like several independent sub-checks, and the cascade repeats at every level until the rate limit is hit.

How to apply:
- When delegating a bounded read-only investigation (audit / consistency check / grep-and-report), state in the prompt: "Do this yourself directly using Read/Grep/Bash — do not spawn further subagents via the Agent tool for this task."
- If the task has 2-3 independent sub-checks, have the one subagent sequence them in its own tool calls rather than leaving it to spawn children.
- Exempt: a deliberate, known-width fan-out (e.g. the `skills/evolution-parallel-agent-eval` evaluator pattern).

This is a tool-authority bound, not a conveyed step-by-step procedure; it does not conflict with `skills/task-subagent-delegation/SKILL.md` Rules' "do not convey: step-by-step procedure".

This axis is spawn depth. Top-level concurrent width is `skills/task-subagent-spawn/SKILL.md` Parallel-Width Cap; neither extends or narrows the other.

Detection signs:
- About to write a delegation prompt with multiple distinct "Check A / Check B" sections without stating that the subagent performs all checks directly itself.
- A task-notification result that is meta-commentary ("I'll wait for the background agent", "the audit is running in the background") rather than findings — the "agent" spawned more agents instead of doing the work.
- A burst of many task-notifications arriving in immediate succession after only 2-3 Agent calls were made.

</bounded-delegation-prohibit-recursive-subagent-spawn>

<worktree-safe-shelving-of-uncommitted-work>

# Worktree-safe shelving of uncommitted work

Inject the shelving form below into every delegation prompt, worktree mode or not. It replaces `git stash push` / `git stash pop`, which are not to be used in delegated work: `refs/stash` is one ref shared by every worktree of the `.git`, and a `pop` takes the top entry whichever worktree pushed it, with no error and no warning.

Injected literal:

```
# shelve
SHA=$(git stash create)
[ -n "$SHA" ] && git update-ref refs/worktree/wipstash "$SHA"
git checkout -- .

# restore
git stash apply refs/worktree/wipstash
git update-ref -d refs/worktree/wipstash
```

`refs/worktree/*` resolves per worktree, and `git stash create` never touches `refs/stash`. Do not qualify the ref name with an issue number.

What the caller holds that `git stash push` did not require:

- `git stash create` records only and leaves the working tree as it was. The `git checkout -- .` step is the revert; omitting it shelves nothing.
- On a clean tree `git stash create` prints nothing and exits 0; the `-n` guard keeps that empty string away from `git update-ref`, which fails on it.
- The ref is one slot, not a stack. `apply` leaves it in place and a second shelve overwrites it, so delete it after a successful restore.

Untracked files sit outside the shelve on both halves: `git stash create` does not record them, and `git checkout -- .` does not remove them. A newly added test file stays in the working tree across the shelve.

This is a tool-authority bound on an operation over shared repository state, not a conveyed step-by-step procedure — same reconciliation with `skills/task-subagent-delegation/SKILL.md` Rules as `bounded-delegation-prohibit-recursive-subagent-spawn` above.

Detection signs:
- A delegation prompt about to go out with no shelving clause in it.
- `git stash push` / `git stash pop` appearing in a subagent's own plan, command, or report.
- A `git stash pop` returning content the caller does not recognize. That is the shared-stack failure having already happened, not a git malfunction — treat the unrecognized content as another worktree's live work and return it rather than discarding it.

</worktree-safe-shelving-of-uncommitted-work>

<memory-only-knowledge-does-not-transfer-to-subagent>

# Memory-only knowledge does not transfer to subagent

Parent-side memory (the per-topic entry files `memory/feedback_<topic>.md`, `memory/project_<topic>.md` and their siblings, plus in-session corrections) is NOT auto-loaded into the subagent's context. The subagent sees only the issue body, the auto-loaded Li+ rules and skills, and the delegation prompt.

If subagent behavior depends on memory content, the parent MUST either (i) inject the relevant literal into the delegation prompt (per-task workaround), or (ii) promote the memory entry into Li+ rules so it auto-loads (durable fix). Reject "memory has it, so the subagent will pick it up" at delegation-construction time.

</memory-only-knowledge-does-not-transfer-to-subagent>

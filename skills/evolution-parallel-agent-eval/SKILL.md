---
name: evolution-parallel-agent-eval
description: Invoke when a self-evolution PR reaches CI green and the merge gate is next (mandatory brake 1) / a Li+ rules/skills/adapter edit draft has converged outside a PR flow and needs verification / an evolution-loop observe/evaluate stage needs an empirical verdict / an unaided self-check feels positive and needs measuring / a spec revision needs orthogonal verification on rule semantic consistency / a brake 1 evaluator findings comment or an author's adjudication is being written / a brake 1 round trip has come back at CI green and the next round or the exit must be chosen. Provides the subagent eval design, its bounded convergence loop, and its report shape.
layer: L2-evolution
---

<parallel-subagent-eval>

# Parallel Subagent Eval

Measures through subagents' behavior what introspection cannot predict: invoke behavior and a rule's semantic effect.

<trigger>

## Trigger

The moments are the description's. **Self-evolution PR brake (mandatory)**: every self-evolution PR (`rules/evolution/initiator-autonomy.md` Self-evolution PR definition, both conditions) runs this method as brake 1, positioned by `rules/evolution/initiator-autonomy.md` Merge brake. An L1 Model Layer change runs it unchanged; semi_auto patch-auto-merge does not bypass it.

**Axis selection.** On the brake 1 path every draft gets three axes: per-draft A (issue requirement) and B (rule violation) from Axis statement form, Held per-draft axes, and the fixed impression-literal axis from `skills/evolution-impression-literal-detection/SKILL.md` Prompt literal. Do not compose axes per draft, add a third per-draft axis, or split either. Elsewhere the fixed axis is included for Li+ source drafts, and further axes are composed under Axis statement form.

</trigger>

<design-dimensions>

## Design Dimensions

`subagent_count (N)` = independent evaluations per axis; `axes_per_subagent (M)` = axes one subagent answers; `premise_variations (P)` = ablation premises compared. Total invocation = `N x P`, exempt from `skills/task-subagent-spawn/SKILL.md` Parallel-Width Cap.

- **Default pattern**: `N=1, M=all axes, P=1`.
- **Exception pattern**: `M=1`, one axis per subagent, only when per-axis prompt complexity is too high to suppress cross-axis echo bias in one context.
- **P > 1**: only to compare premises directly, typically P=2 before/after (draft unapplied vs applied, same prompt).

**Every finding is adjudicated on its literal**, against the source at the revision its `path:line` names, on every axis (Procedure step 7): no count, ratio, or majority enters any verdict.

</design-dimensions>

<procedure>

## Procedure

**Precondition**: source on a branch other than the merge target (brake 1: the PR branch at the SHA CI went green on), `.claude/` in tag-match state. On the brake 1 path the steps loop, capped at three round trips (step 7), steps 2 to 5 once per round against its SHA. A rule effect measurement may run before a round's step 3 (`skills/evolution-rule-effect-measurement/SKILL.md` Application point); it gates no step here.

1. **Prepare draft**
2. **Apply operational copy (target-conditional)** - Apply where the draft reaches the evaluator as injected context: `rules/**/*.md`; a file whose installed copy is on the injection enumeration of Constraint: Character_Instance non-inheritance (`adapter/claude/CLAUDE.md` installs as `CLAUDE.md`); `adapter/claude/agents/<name>.md` when a step 3 spawn names that agent; `skills/<name>/SKILL.md` for a probe-type evaluator, whose eval depends on invoking the skill. Everything else (`skills/*` for a judge-type evaluator, `docs/*`, `hooks-settings.md`, hook scripts) is not applied; the evaluator Reads it at the named SHA.

   The parent writes the apply to `.claude/` from `gh api repos/<owner>/<repo>/contents/<path>?ref=<SHA>` at one SHA (brake 1: the round's SHA named at step 3), never from a working tree.
   - **Host permission-gate fallback**: when the host self-modification gate refuses the apply, `skills/*` falls back to direct Read, a deviation recorded in the PR self-review; any other file is re-run from a session that can apply, or its deviation is recorded with reduced confidence flagged in the PR's Self-Evolution Observation Format entry (`rules/evolution/memory-entry-format.md`) where it has one.
   - **Window mark**: any apply runs inside `scripts/window_marker.py --claude-dir <.claude written>`: `open --procedure evolution-parallel-agent-eval` (`--wait-seconds` set per run and recorded), wait until `ready` exits 0, apply, `applied`. `open` refusing = a mark stands: do not apply. No age ends a mark: its opener ends it at step 5, or, the opener gone, whoever finds it, by the `recovery` `status` names (`close_without_restore` said so in `--closed-by`), then `close --closed-by <self>`.
3. **Subagent spawn** - Select N, M, P and spawn, in parallel within a round as multiple Agent tool calls in one message, each naming `subagent_type` (Claude Code) or `agent_type` (Codex), setting `model` (Constraint: Model floor), and following the kind split of Constraint: Effort floor. A Claude Code probe-type evaluator inherits the parent session's effort: raise the parent session's effort to the floor before spawning one and keep it for the round. On the brake 1 path each round spawns fresh evaluators; the prompt names the PR URL, the pushed commit SHA, and the green CI run URL, never a path in the parent's clone, and carries the three axes as held literals (`Unit` / `Scope` of A and B the only fill), plus:
   - the no-write literal (Constraint: Evaluator does not modify the evaluation target); one findings comment holding every axis; a repository-wide sweep clones into the evaluator's own working directory
   - `gh pr diff <n> --repo <owner>/<repo>`, `gh api repos/<owner>/<repo>/contents/<path>?ref=<SHA>`, `gh pr view <n> --repo <owner>/<repo> --json comments`
   - later rounds report only what is not on the thread, never a rejected finding
   - the comment's language: this run's value on the base-language side of `Workspace_Language_Contract` (not the PR-body precedence of `skills/task-subagent-prompt/SKILL.md` Delegation prompt hygiene), written into no Li+ source file
   - an added or modified line stating a fact that changes over time, with no backing, is a full-length finding; the fact is not verified
   - each line removed without replacement is asked once whether it is still true and still needed at the named SHA; both = a finding, and "all removed correctly" is a valid outcome
   - after a measurement, its scope only (Constraint: An evaluator receives the measurement's scope, never its verdict)
   - one sentence composed from Report shape: the asymmetry as it lands on the evaluator's comment, and no echo of the criteria the prompt supplies
4. **Relay to the author** - Actor = the parent, relay only: resume the author (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary) with the entry alone - this round's findings are on the thread, to be adjudicated. The parent does not read, consolidate, select, rank, or answer them. When every axis of every comment is clean, the author is not resumed and the loop exits at step 8.
5. **Runtime restore** - Parent-side, once every evaluator has posted, before the author is resumed: end the step 2 mark by the `recovery` `status` names now, then `close --closed-by <self>`. No mark, nothing to run
6. **Read the findings** - Actor = the resumed implementation subagent (Constraint: Adjudication actor): this round's comments whole, each finding its own unit into step 7; no axis is weighed against another, and a clean axis is its own verdict only
7. **Judgment** - Actor = the resumed implementation subagent: adjudicate each finding against the source; post each accept / reject with its reason as a **comment on the PR** thread (Report shape, Author's adjudication).

   **Adjudication branch.** Accepted -> apply, commit, push, post, stop at CI green. None accepted -> post, stop at CI green. Or abort.

   **Round trips: three.** One round trip = an evaluator round posts, the author responds by fix commit, rejection, or both, CI goes green; the first evaluation is round trip 1.

   **Re-run: same round, or the next one.** Same round when (a) the round's verdicts fall short of the floor (Constraint: Evaluator floor = N=1) and (b) the PR commit SHA is unchanged; otherwise the next round. Returned verdicts carry in only under the same axes and prompt; a prompt repair, required for a malformed one, retires them. The cause of the shortfall is not a term. Ceiling: a third attempt against one baseline still short stops and escalates to **human** (`skills/model-loop-safety`'s number; stop, not switch). It counts attempts within one round trip, apart from the round-trip cap, which exits to the **parent**.
8. **Round boundary** - Actor = the parent, scheduler only: when the author reports at CI green below the cap, open the next round (steps 2 to 5 against the SHA the response went green on). The parent does not judge rejections, name a correction, or re-open an axis. Exit when a round returns no finding or three round trips are done; the cap is the bound, and no `skills/model-loop-safety` judgment runs here
9. **Externalize** - Record the verdict and adoption judgment in the parent issue body / PR self-review. On the brake 1 path the parent reads the thread whole and records, without transcribing it, the merge judgment over the eval - whether a standing rejection looks right included - with each round's N and the round-trip count, neither as a reason for adopting a finding. A settled judgment also goes to decision structure (`skills/evolution-decision-structure-write`)

</procedure>

<axis-statement-form>

## Axis statement form

The form of every per-draft axis (not the fixed axis): the held pair below with its `Unit` / `Scope` fill, and each axis composed off the brake 1 path. Five labeled parts, each a phrase, all prompt payload; an unwritten part is a missing label.

- **Question** — one interrogative naming the operation that produces its verdict (what the evaluator does to the material, which result is the finding), answerable in the order its material arrives. Operations are counted, not clauses: two joined by "and" or a comma, or one hidden in an evaluative predicate (`forced`, `consistent`, `resolves wrongly`), are two axes; split or drop one. No operation named = unfilled.
- **Unit** — what one verdict covers: a sentence, a paragraph, a file, a claim, an occurrence.
- **Scope** — extent (this PR's diff, one named file, the repository, the repository and the wiki), the patterns' language, and, for an absence claim, what was swept. Normative text is held twice - English in `rules/` / `skills/`, Japanese in `docs/` - so `the repository` is not met by an English-pattern sweep.
- **Verdict terms** — what yes and no mean here, polarity named: on "did anything drop?" a finding answers yes and is negative for the draft.
- **Basis** — each statement about the target or the criteria, and each argument the parent relies on, carries inside the axis a pointer resolving at the named SHA: the criterion at its `path` or quoted with `path:line`, an example quoted from where it occurs, for a count the body to count from. The parent's memory of a body it authored is not a basis. None named = unfilled, not clean.

### Held per-draft axes

Copied into every brake 1 evaluator prompt verbatim. `Unit` and `Scope` are the only blanks; text authored elsewhere in the blocks is a re-composition.

**Axis A — issue requirement**

> - **Question** — Where does this diff disagree with what its own issue asked for? Read the issue body the PR closes — its purpose, its constraints, and its target-file enumeration where it has one — then read the diff, and report each place the two do not agree: something the diff does that the issue body did not ask for, or something the issue body required that the diff does not do.
> - **Unit** — `<filled per run>`
> - **Scope** — `<filled per run>`
> - **Verdict terms** — A finding is one disagreement between the diff and the issue body, and it is negative for the draft. No finding means the diff and the issue body agreed everywhere you read; say that in those terms and name what you read.
> - **Basis** — Quote the issue-body sentence you are judging by, and give the diff side as `path:line` at the named SHA. Take the issue body from the repository, not from anything this prompt says about it: `gh pr view <n> --repo <owner>/<repo> --json body` names what the PR closes and `gh issue view <n> --repo <owner>/<repo>` returns that body. Where the answer turns on how many of something the issue enumerated, count them in the body rather than taking a number stated about it.

**Axis B — rule violation**

> - **Question** — Which lines of this diff break a rule that binds them? For each line the diff changes or adds, find the rules binding it — the Li+ `rules/**` and `skills/**` bodies at the named SHA, and any rule the diff itself states, a rule it newly adds included — read that rule's literal, and report each line the literal does not permit.
> - **Unit** — `<filled per run>`
> - **Scope** — `<filled per run>`
> - **Verdict terms** — A finding is one line breaking one rule, and it is negative for the draft. No finding means every line you checked was permitted by every rule you checked it against; say that in those terms and name those rules.
> - **Basis** — Quote the rule literal with its `path:line` at the named SHA. A rule the diff itself adds is quoted from the diff at that same SHA. A rule recalled from memory, or restated in this prompt, is not a basis: open the file. Where the rule turns on how many of something there are, count them in the body rather than taking a number stated about it.

### Where a loosely filled part lands

A finding the author cannot resolve against the source that traces to the axis names the failed part: `Question`, `Verdict terms`, or `Basis` is repaired in the held literal for later runs; `Unit` or `Scope` in that run's fill only.

</axis-statement-form>

<report-shape>

## Report shape

The two brake 1 artifacts on one PR thread: the evaluator's findings comment (Procedure step 3) and the author's adjudication (step 7). Off the brake 1 path findings return to the spawner, without the preamble, under the same asymmetry.

### The asymmetry

**A finding is written at full length, what nobody contests at one line.** Full length = the verbatim quote of the literal at issue, its `path:line` at the named SHA, and why it is a defect; not compressed. One line = that pointer without the quote, what it is about, and its verdict; the pointer is picked at the SHA it opens at, before the verdict.

### Evaluator's findings comment

One per evaluator per round, posted by the evaluator (`gh pr comment <n> --repo <owner>/<repo> --body ...`); N>1 gives N comments, duplicates unmerged.

- **Preamble**: opens with this held literal, copied in its source language:

  > Adjudicate each finding below by checking its literal against the source at the revision its `path:line` is given at, and adopt or drop it on that. No count enters that judgment, and no axis is exempt from it: the fixed impression-literal axis is adjudicated the same way, on the flagged phrase against the removal test its own spec fixes (`skills/evolution-impression-literal-detection/SKILL.md`), and it fixes no threshold.

- **Axis with a finding**: full length. **Axis with no finding**: named, with its verdict in its own terms; a repository-wide sweep gives its pattern, paths, and hit count as the pointer.
- **Prohibited**: restating the criteria, thresholds, or axis wording the prompt supplied; in later rounds, a finding already on the thread or rejected.
- **Language**: the value the prompt names; quotes, `path:line`, and the preamble stay as the source has them.

### Author's adjudication

A comment on the same thread, with or without a commit; a commit applying an accept still carries the body `rules/operations/operations.md` requires.

- **Reject**: full length. **Accept**: the finding and what changed, no more.
- **Language**: the evaluator comment's value, named by the parent at the resume (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary, item (d)), not the delegation prompt's body language.

</report-shape>

<constraint>

## Constraint

- **Evaluator floor = N=1**: across every M configuration; a round short of it is re-run (Procedure step 7, Re-run)
- **Model floor = sonnet-class, explicit per spawn**: every spawn under this skill sets the Agent tool `model` parameter per call - never inherited from the parent, never pinned in custom-agent frontmatter `model:`. Floor = `sonnet`; the id at or above it is the parent's per-spawn selection (`skills/task-subagent-spawn/SKILL.md` Selection criteria). `haiku` is prohibited; an id not positively classifiable as sonnet-class or above is not passed (on doubt, `sonnet`). A host without a per-call `model` parameter runs the eval from a session whose model is so classified. Scope = `skills/task-subagent-spawn/SKILL.md` Subagent Model Policy
- **Effort floor = `medium`, resolved independently from the model floor**: a judge-type evaluator reads the draft; a probe-type evaluator's bare behavior under the applied draft is what its round reads. A probe-type evaluator spawns as the host's built-in general-purpose agent, with no Li+ agent definition file. On Claude Code a judge-type evaluator spawns as `subagent_type: medium` or a higher effort-named agent (the parent's per-spawn selection); a probe-type one reaches the floor through the parent session (Procedure step 3). On Codex, both kinds spawn with no agent definition file and explicitly pass `reasoning_effort="medium"` (value support: `skills/task-subagent-spawn/SKILL.md`). No evaluator receives the implementation delegate's role (`skills/task-subagent-prompt/SKILL.md` Role literal: implementation delegate). A judge-type evaluator receives this role in its prompt, verbatim:

  > You are a Li+ brake 1 evaluator. A parent agent spawns you against one change; you answer what its prompt asks, from the sources that prompt names.
  >
  > What the run is made of — the axes, what counts as a finding, what you write and where it goes — arrives in that prompt. Take it from there, not from here.

  This is the one place the judge-type role lives. Do not write a role fragment into `adapter/claude/agents/{low,medium,high}.md`
- **Subagent prompt must be self-contained**: no parent context leaks in. With M=all axes, instruct each axis to "answer independently without referencing other axes' answers"
- **Evaluator does not modify the evaluation target**: carried by the prompt, not the tool set (Non-scope). Copy into every brake 1 evaluator prompt verbatim:

  > Do not modify the evaluation target. Do not edit, write, commit, or push anything in the repository under evaluation, and do not run its build, tests, formatter, or any other command that mutates it. Read the PR diff and the file bodies at the named commit SHA. The one thing you write is your own findings comment on that PR: post it once, post nothing else there, and never a review, an approval, a merge, or a reply to anyone else's comment. If an axis looks like it needs a change applied before it can be answered, report that as a finding instead of applying it.

- **An evaluator receives the measurement's scope, never its verdict**: the probes, or the positions of the lines exercised - never whether the arms differed, matched, or returned nothing, on any surface the evaluator is pointed at; the run's record stays off the PR thread until the loop exits
- **Findings are posted to the PR by the evaluator**: the author answers on the same thread; nothing consolidates between them, and the parent neither composes nor reads what passes
- **A rejection is final inside the loop**: no later round raises it and the author does not re-adjudicate it; the parent examines it at Procedure step 9
- **Adjudication actor = the resumed implementation subagent**: canonical at `rules/evolution/initiator-autonomy.md` Merge brake, Adjudication actor; what the resume carries is `skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary
- **Character_Instance non-inheritance**: subagent context receives `CLAUDE.md`, `.claude/rules/**/*.md` (full body), `.claude/skills/*/SKILL.md` (description only), MEMORY.md, and harness system-reminders - not `.claude/output-styles/`, hook output, or `.claude/settings.json`. When character behavior is under verification, inject the Character_Instance body into the step 3 prompt, or the axis yields a hollow name prefix with no persona

</constraint>

<non-scope>

## Non-scope

- PR review, semi_auto minor/major human review included, is a separate axis
- Facts that change over time (API spec, library or host behavior) are checked only on lines the diff adds or modifies (Procedure step 3); backing = a cited source or an observation. Adjudicating such a finding, the author checks the fact against the current source and leaves the grounds on the line or thread, or drops the line or marks it unverified
- Evaluator tools are not restricted and the custom-agent `tools:` route is rejected, so no-write rests on the prompt literal

### What the three-round cap gives up

Everything after round trip 3, a wrong rejection included, is dropped, not missed - accepted while changes stay inside git revert range and release stays human-gated. Re-evaluate when a capped merge produces observable production harm.

</non-scope>

</parallel-subagent-eval>

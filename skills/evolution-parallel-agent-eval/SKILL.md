---
name: evolution-parallel-agent-eval
description: Invoke when a self-evolution PR reaches CI green and the merge gate is next (mandatory brake 1) / a Li+ rules/skills/adapter edit draft has converged outside a PR flow and needs verification / an evolution-loop observe/evaluate stage needs an empirical verdict / an unaided self-check feels positive and needs measuring / a spec revision needs orthogonal verification on rule semantic consistency / a brake 1 evaluator findings comment or an author's adjudication is being written / a brake 1 round trip has come back at CI green and the next round or the exit must be chosen. Provides the subagent eval design, its bounded convergence loop, and its report shape.
layer: L2-evolution
---

<parallel-subagent-eval>

# Parallel Subagent Eval

Verification method that measures the AI's introspection gap (no empirical basis for predicting its own future invoke behavior or rule semantic effect) from the outside via the current behavior of subagents.

Justification for the design decisions below is held as Decision Structure entries in the wiki, indexed at `docs/Decision-Structure.md` and retrieved via `skills/evolution-judgment-learning`.

<trigger>

## Trigger

Fires at any of the following moments:

- Li+ rules/* or skills/* edit draft has converged outside a PR flow and verification is needed before it is carried into one
- evolution-loop observe / evaluate stage needs an empirical verdict
- Right after AI alone feels "this edit satisfies the spec" (catch overconfidence from an unaided self-check)
- Spec revision proposal needs orthogonal verification on the rule semantic consistency axis
- **Self-evolution PR brake (mandatory)**: any self-evolution PR runs this method. Which PRs those are is canonical in `rules/evolution/initiator-autonomy.md` Self-evolution PR definition — both of its conditions, neither alone — and is not restated here. This is brake 1, the only brake at the merge gate. Its firing moment is fixed rather than draft-driven — the delegated subagent's report at its stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition) — and the position rule is canonical in `rules/evolution/initiator-autonomy.md` Merge brake, not restated here. An L1 Model Layer source change adds no brake of its own and runs this one unchanged. semi_auto patch-auto-merge does not bypass brake 1.

Axis selection on the brake 1 path: three axes, and the set does not vary by draft. Two are the per-draft axes — A (does the diff do what its own issue asked for?) and B (does the diff break a rule?) — held as copy-verbatim literals at Axis statement form, Held per-draft axes, where only their `Unit` and `Scope` lines are filled per run. The third is the fixed axis (impression-literal detection, spec in `skills/evolution-impression-literal-detection/SKILL.md`), always included for Li+ source drafts regardless of spec nature and likewise copied from a held literal, its Prompt literal.

Composing a set of axes per draft is what the two held axes replace on that path, and a draft that looks unlike the last one is not a reason to compose one. Do not add a third per-draft axis, and do not split either of the two.

The fixation reaches the brake 1 path and stops there. At the other Trigger moments above the fixed axis is included as always, and any further axis is composed per draft nature and written under Axis statement form.

</trigger>

<design-dimensions>

## Design Dimensions

Three axes that move verification cost and detection power independently. Total subagent invocation count = `N x P`; M is absorbed inside each subagent prompt.

- **`subagent_count (N)`** - Independent sample count. Obtain N independent evaluations per observation axis. Robustness against probabilistic variance.
- **`axes_per_subagent (M)`** - Number of observation axes each subagent answers within its prompt. Blind-spot coverage.
- **`premise_variations (P)`** - Number of ablation premises (e.g. full rule exclusion / partial exclusion). Robustness against premise variation.

### Default pattern (delete/keep judgment, etc.)

`N=1, M=all axes, P=1` - one subagent answers all M axis questions against the same ablation output. Total invocation = 1.

### Exception pattern: M=1 axis-separated

`N=1, M=1, P=1`, one axis per subagent. Total invocation = `N x axis_count`. Adopt only when per-axis prompt complexity is high enough that cross-axis echo bias cannot be suppressed inside a single subagent context.

### Premise variations (P > 1)

Use only when comparing multiple ablation premises directly. Total invocation = `N x P`; within each premise, M is absorbed into the prompt as in the default pattern.

The representative case is P=2 before/after: premise A = pre-change (operational copy unapplied = baseline), premise B = post-change (draft applied = candidate) are placed as separate premises and the subagent's behavior under the same prompt is compared directly. Trigger = a revision where "did the subagent verdict shift before vs after draft application on the same question?" needs to be pinned down empirically. Cost is `N=1, P=2 -> 2 invocation`, double the default.

### Every finding is adjudicated on its literal

No count, ratio, or majority enters a verdict anywhere in this method. A finding is adopted or dropped by checking its literal against the source at the revision its `path:line` names, and that check is the author's at Procedure step 7 — on the fixed axis as on the two per-draft axes. Where more than one evaluator ran and both raised the same finding, that changes nothing about how it is adjudicated.

</design-dimensions>

<procedure>

## Procedure

**Precondition**: source lives on a branch other than the merge target, and `.claude/` is in tag-match state (draft unapplied). On the brake 1 path that branch is the PR branch at the SHA the CI run went green on; on the other Trigger entries it is an experimental branch.

On the brake 1 path the steps below are a loop, bounded at three round trips (step 7, Round trips). Steps 2 to 5 run once per round, against that round's own SHA.

1. **Prepare draft** - Draft the edit content
2. **Apply operational copy (target-conditional)** - Apply only when the draft reaches the subagent's observation surface as injected context, which splits by target:
   - `rules/**/*.md` body IS injected: the apply is mandatory
   - `skills/<name>/SKILL.md` body is NOT injected (description only, body lazy-loaded at invoke): for a judge-type evaluator the apply is not required, and the evaluator is pointed at the draft for direct Read instead. Exception: when the eval depends on the subagent *invoking* the skill (probe-type, body auto-loads at invoke), the apply IS required

   The apply is a parent-side write to `.claude/`; the source stays on its own branch and the evaluators spawned at step 3 read it there.
   - **Host permission-gate fallback**: an autonomous run without explicit user authorization can have the apply refused by the host self-modification gate. `skills/*` falls back to evaluator direct Read at the named SHA; record the deviation in the PR self-review. `rules/*` cannot be substituted that way: re-run from a session that can apply, or record the deviation and flag reduced confidence for post-merge observation
3. **Subagent spawn** - Select N, M, P per draft nature and spawn; where the selection puts more than one subagent in the round, spawn them in parallel. Default `N=1, M=all axes, P=1`, total invocation = 1; switch to the M=1 exception pattern when the echo-bias condition in Constraint: Subagent prompt must be self-contained holds, or to P>1 when premise variation is needed (see Design Dimensions). Every spawn explicitly sets the Agent tool `model` parameter at or above the sonnet-class floor (see Constraint: Model floor).

   On the brake 1 path every round spawns its evaluators fresh; an evaluator is never resumed across rounds. Two things carry that choice: the instrument reads the target from outside rather than from its own prior verdict, and the PR thread already holds what a resumed context would hold. It is provisional — whether fresh spawn or resume detects more is unmeasured, and #1848 is where it gets measured.

   On the brake 1 path the material named in the prompt is the PR URL, the pushed commit SHA, and the green CI run URL — never a path inside the parent's clone. The reason that set is fixed is canonical in `rules/evolution/initiator-autonomy.md` Merge brake. The rule governs what the prompt *names*; step 2's operational copy is unaffected.

   On that same path all three axes enter the prompt as held literals, copied verbatim with nothing added to them: the two per-draft axes from Axis statement form, Held per-draft axes, whose `Unit` and `Scope` lines are the only per-run authoring left in the prompt, and the fixed axis from `skills/evolution-impression-literal-detection/SKILL.md` Prompt literal, which carries no such blank. Off it, only the fixed axis arrives held; the rest is composed (Trigger, Axis selection). Seven more things go in alongside the axes and the material:
   - the no-write literal verbatim (see Constraint: Evaluator does not modify the evaluation target)
   - the retrieval commands: `gh pr diff <n> --repo <owner>/<repo>` returns the diff, `gh api repos/<owner>/<repo>/contents/<path>?ref=<SHA>` returns any file body at that SHA, and `gh pr view <n> --repo <owner>/<repo> --json comments` returns the comments already on the thread
   - the allowance that an axis needing a repository-wide sweep clones into the evaluator's own working directory, which is off the shared surface
   - on the brake 1 path, the reporting destination: the evaluator posts its findings as one comment on the PR, all axes inside it, and writes nothing else there (Constraint: Findings are posted to the PR by the evaluator)
   - on the brake 1 path in a round after the first, the standing-rejection bound: read the comments already on the thread and report only what is not already there. A finding the author has rejected is settled and is not raised again (Constraint: A rejection is final inside the loop)
   - on the brake 1 path, the resolved language for that comment, named as the value for this run. A PR comment is dialogue under `Workspace_Language_Contract` (`adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md` Definitions), which names PR comments among the conversational replies the base language governs — not the project language a PR *body* takes, so the body-language precedence at `skills/task-subagent-prompt/SKILL.md` Delegation prompt hygiene is the wrong axis to resolve it on. The evaluator writes to a surface that contract reaches and cannot resolve the value from its own context, which is why the parent names it. The bound that no resolved value is written into a Li+ source file holds here as it does there
   - the shape that comment is written in, as one sentence the parent composes from Report shape: the asymmetry as it lands on the evaluator's comment, plus the prohibition on echoing the criteria this prompt supplies. That sentence is what the prompt carries; the Report shape section behind it is the parent's reference, not prompt payload. The shape is a contract on the comment and is not left to the evaluator's discretion
4. **Relay to the author** - Actor = the parent, as relay and nothing else. Resume the author (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary) pointed at the PR thread, and stop there. What the parent supplies is the entry — that this round's findings are on the thread and are to be read and adjudicated — and not their content.

   **The parent does not supervise the exchange it relays between.** It does not read the findings before relaying, does not consolidate them, does not select among them, does not rank them, and does not answer one. Accept / reject is the author's authority (Constraint: Adjudication actor), and the findings sit on the PR already, where the author reads them without the parent carrying them.

   Relay nothing when every axis of every evaluator comment in this round is clean: the author is not resumed, the loop exits at step 8, and the eval's record rests on the thread and on the self-review at step 9.
5. **Runtime restore** - Restore `.claude/` to tag-match state (revert the operational copy to pre-draft). Parent-side, as the apply at step 2 was. It runs as soon as every evaluator has posted its findings, and before the author is resumed; it does not wait on step 6. Skip only when step 2 applied nothing (skills/* direct-Read path, or permission-gate fallback)
6. **Read the findings** - Actor = the resumed implementation subagent, not the parent (see Constraint: Adjudication actor). It reads this round's evaluator comments on the PR whole, every axis of them, and carries each finding into step 7 as its own unit. Axes are not weighed against each other and no axis's outcome settles another's; a clean axis is read as its own verdict and nothing more
7. **Judgment** - Actor = the resumed implementation subagent, which adjudicates each finding against the source and records every accept / reject and its reason as its own **comment on the PR**, on the thread the findings arrived on (shape = Report shape, Author's adjudication). Three application moments sit under this number, split across the labels below: the adjudication branch, the round-trip cap, and whether a re-run is permitted.

   **Adjudication branch.** Anything accepted -> apply it, commit, push, post the adjudication, and stop again at CI green. Nothing accepted -> post the adjudication and stop at CI green all the same, the tree unchanged. Or abort. The destination does not split with the branch: it is the PR comment whether or not a commit exists, so the no-commit case keeps no route of its own (`rules/model/subtractive-structural-beauty.md` Core principle (A)).

   **Round trips: three.** One round trip = an evaluator round posts its findings, the author responds to them by fix commit or by rejection or by both, and CI goes green. The first evaluation is round trip 1. The cap is three: at most three evaluator rounds and three author responses. Exit is at step 8 — earlier when a round returns no finding, otherwise at the cap. What the cap drops is at Non-scope, What the three-round cap gives up.

   **A rejection is final inside the loop** (Constraint: A rejection is final inside the loop). The author does not re-adjudicate a finding it has already rejected, and no later round puts one back in front of it.

   **Re-run: same round, or the next one.** Whether a re-run is permitted is settled by what the round audited, never by why it stopped. A re-run continues the same round when both hold, and neither alone: (a) the verdicts that round returned have not reached the floor (Constraint: Evaluator floor = N=1 — a round that returned no verdict at all is the case this reaches), and (b) the baseline it ran against — the PR commit SHA — is unchanged from the first attempt. Verdicts already returned are carried into it rather than discarded, and they must share the instrument: a verdict counts toward the floor only where the axes and prompt that produced it are the ones the re-run spawns under. Repairing a prompt between attempts is permitted, and a malformed one has to be repaired before it can return anything — but the repair retires the verdicts taken under the old wording instead of adding to them. Cause is not a term here: a spend limit, an evaluator crash, a malformed prompt and a timeout are one thing under this criterion, a round that returned fewer than the floor. Ceiling: a third attempt against the same baseline that still has not reached the floor stops there and escalates to human. The number and its task / debug category are `skills/model-loop-safety`'s; the action here is stop, not the stop-and-switch it prescribes. This ceiling and the round-trip cap above share a number and nothing else: this one counts attempts at one round that returned no verdict at all and escalates to **human**, while that one counts completed round trips and exits to the **parent**. A run sitting at its second attempt under this ceiling is still inside round trip 1.

8. **Round boundary** - Actor = the parent, as scheduler and nothing else. When the author reports back at CI green and the cap is not yet reached, open the next round: steps 2 to 5 run again against the SHA the author's response went green on, and step 3 spawns fresh evaluators.

   **The parent does not stand between the two ends of the exchange.** It does not judge the author's rejections, does not name a correction, and does not re-open an axis. A rejection is examined by nobody inside the loop — that is what makes it final (step 7) — and past the loop by the parent's own reading of the thread at step 9.

   Exit when either holds: this round returned no finding, or three round trips are done. Either way the loop ends here and step 9 follows. Convergence needs no `skills/model-loop-safety` judgment holding it: the cap is the bound, it is fixed rather than read per run, and no actor inside the loop is left counting
9. **Externalize** - Record the verdict and the adoption judgment in the parent issue body / PR self-review, so the judgment survives the session. On the brake 1 path both sides are externalized on the PR thread already — the findings as the evaluator comments at step 3, the adjudication as the author's comments at step 7 — and the self-review transcribes neither. The parent reads that thread whole here, and records what it does not carry: the merge judgment over the eval, including whether a rejection left standing looks right. This reading is where the parent's supervision of the findings sits under this loop — at the exit, not inside the round trips. Record N alongside the verdict as the width each round ran at, and the number of round trips the loop took; both are facts about the run, and neither is ever written as the reason a finding was adopted or dropped (see Design Dimensions, Every finding is adjudicated on its literal). If the judgment has settled, also append to decision structure per `skills/evolution-decision-structure-write`

</procedure>

<axis-statement-form>

## Axis statement form

Fixes the form every per-draft axis is written in — on the brake 1 path that is the pair Trigger, Axis selection names, held below at Held per-draft axes; at the Trigger moments outside brake 1 it is whatever axis the parent composes there, and the parts below are the requirement on that composition entire. The parts read on two surfaces now that the pair is held: they are the shape those literals are written in, and, for the two parts left open on them (`Unit` and `Scope`), they are the requirement on the parent's per-run fill. The section applies at Procedure step 3, where the axes enter the prompt. The fixed axis is outside it: that axis's wording is held whole at `skills/evolution-impression-literal-detection/SKILL.md` Prompt literal with no part left open, so nothing of it is filled per run.

The recurring form this closes is one axis name carrying more than one question — joined visibly, or compressed into a single predicate that reads as one. With the pair held, what is left to author per run is the `Unit` and `Scope` fill, and the parts below are what those fills are checked against.

Each axis ships as five labeled parts, all of them payload — they enter the evaluator's prompt as written, and none is a check whose output is discarded once it passes. A part left unwritten is therefore a missing label in the text the evaluator will read. Each part is a phrase, not a paragraph; the form fixes what an axis names, not how much of it there is.

- **Question** — one interrogative, and one only; it names the operation that produces its verdict, and it is answerable in the order its material arrives — an axis cannot ask for a judgment formed before reading what the prompt itself carries. Naming the operation means saying what the evaluator does to the material, and which result of doing it is the finding. Two clauses joined by "and" or by a comma are two operations and so two axes: split them, or drop one. What is counted is operations, not clauses: a predicate that names an evaluation instead of an operation — `forced`, `consistent`, `resolves wrongly` — carries its count hidden inside the one word, where the joined-clause prohibition cannot reach it. An interrogative that names no operation is unfilled, not answerable. The residual — a predicate whose reading the evaluator supplies silently, which emits no signal at all — is accepted on the post-merge observation axis (Non-scope).
- **Unit** — what a single verdict covers: a sentence, a paragraph, a file, a claim, an occurrence.
- **Scope** — the surface the axis ranges over, stated on both of its dimensions — extent (this PR's diff, one named file, the repository, the repository and the wiki) and the language the axis's patterns are written in — and, where the axis's verdict is an absence claim, what it swept. An absence is only as wide as what was read. Extent alone does not carry the second dimension: a scope reading `the repository` is satisfied by a sweep that ran on English patterns alone, and this repository holds most normative text twice — English in `rules/` and `skills/`, Japanese in `docs/`.
- **Verdict terms** — what a yes and a no mean here, in this axis's own words. On an axis asking "did anything drop?" a finding answers yes while being negative for the draft; an axis that does not name its own polarity inherits the wrong one.
- **Basis** — every statement the axis makes about the target or about the criteria carries a pointer that resolves at the named SHA, is written inside every axis that needs it rather than once for the set, and, where the answer turns on how many of something there are, hands over the body to count from instead of a number. An axis does not inherit what was written next to it, and an axis that names no basis is unfilled, not clean. What resolving means: the criterion at its `path`, or quoted with `path:line`; an illustrative example quoted from where it actually occurs rather than composed to look like one. What this excludes is assertion from the parent's memory of a body the parent itself authored. The part is not satisfied by form alone, and what the per-axis requirement above ranges over is whatever the verdict has to be formed against — an existing Li+ criterion the axis is judging by, or an argument the parent is relying on.

### Held per-draft axes

Two axes, copied into every brake 1 evaluator prompt verbatim. Fill `Unit` and `Scope`; leave every other line as written. Those two are the only blanks; text authored anywhere else in these blocks is a re-composition, not a fill. What `Unit` and `Scope` have to say is the parts spec above, and is not restated here.

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

Splitting B by target is prohibited at Trigger, Axis selection, where the axes are picked.

### Where a loosely filled part lands

An axis whose parts were filled but filled loosely surfaces at adjudication, when the author reads a finding it cannot resolve against the source. Where that traces to the axis rather than to the finding, name the part of this form that did not hold: a No on `Question`, `Verdict terms`, or `Basis` lands on the held literal and is repaired there for every run after it, while a No on `Unit` or `Scope` lands on the fill and persists no further than the run it was written for.

</axis-statement-form>

<report-shape>

## Report shape

Fixes the form of the two artifacts brake 1 produces — the evaluator's findings comment at Procedure step 3, and the author's adjudication at Procedure step 7. Both land on the same PR thread, one answering the other. What this section fixes is delivery: it does not change which axes are asked (Trigger, Axis selection), how many evaluators answer them (Constraint: Evaluator floor), or what a finding is adjudicated on (Design Dimensions).

Scope = the brake 1 path. On the other Trigger entries there is no PR surface, so the evaluator returns its findings to the parent that spawned it and the held preamble below has no addressee; the asymmetry still governs what it writes.

### The asymmetry

Both artifacts are asymmetric on the same seam: **the side carrying a finding is written at full length, the side nobody contests at one line.**

Full length = the verbatim quote of the literal at issue, its `path:line` at the named SHA, and why it is a defect. It is not a compression target.

One line = that same pointer without the quote, plus what the line is about and its verdict in the terms of whatever the verdict is on. Named at the SHA that pointer can be opened, and a pointer that does not resolve — or resolves to something the verdict does not fit — fails at one lookup. Residual = a clean axis whose pointer nobody opens, and a pointer picked after the verdict to fit it; accepted, on the post-merge observation axis the fixed axis's missed-literal case already uses (`skills/evolution-impression-literal-detection/SKILL.md` False-negative backstop).

### Evaluator's findings comment

One comment per evaluator per round, posted to the PR by the evaluator itself (`gh pr comment <n> --repo <owner>/<repo> --body ...`). There is no consolidation step and no second hand between the evaluator and the author, so where N>1 put the round in, N comments land and duplicates across them are not merged: the author reads each on its own literal, and merging is a selection the loop no longer has an actor for.

- **Preamble**: the comment opens with one held literal, copied rather than composed:

  > Adjudicate each finding below by checking its literal against the source at the revision its `path:line` is given at, and adopt or drop it on that. No count enters that judgment, and no axis is exempt from it: the fixed impression-literal axis is adjudicated the same way, on the flagged phrase against the removal test its own spec fixes (`skills/evolution-impression-literal-detection/SKILL.md`), and it fixes no threshold.

  Both clauses are payload; the evaluator does not restate them in its own words. The preamble is copied in the language the source has it in and is not rendered into the comment's resolved language.
- **Axis with a finding**: full length, per the asymmetry above.
- **Axis with no finding**: name it and give its verdict in that axis's own terms. One answered by a repository-wide sweep has no line to point at, so the sweep substitutes for the pointer: give it re-runnably (the pattern, and the paths it ran over) and its hit count. Clean axes are carried in the comment all the same: the author reads every axis at Procedure step 6, and a comment carrying findings alone hides the denominator.
- **Prohibited**: restating the criteria, thresholds, or axis wording the prompt supplied; and, in a round after the first, raising a finding already on the thread or one the author has rejected (Constraint: A rejection is final inside the loop).
- **Language**: the comment lands on a surface `Workspace_Language_Contract` (`adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md`) reaches as a PR comment, and the evaluator writes it in the value its prompt names for this run (Procedure step 3, which fixes which side of that contract a PR comment resolves on) — a subagent cannot resolve that value from its own context. What resolution does not settle: a verbatim quote and its `path:line` stay as the source has them, and so does the held preamble above. Li+ source is English (`rules/model/liplus-coding-rule.md` Source Language), so in a workspace resolving to any other language this comment is mixed by construction — quotes in the source's language inside prose in the resolved one. A clean axis carries no quote, so its one line is prose and a pointer.

### Author's adjudication

Destination = a comment on the same PR thread, posted whether or not the round produced a commit. The commit that applies what was accepted still carries the body `rules/operations/operations.md` requires of it; what that body no longer carries is the adjudication.

- **Reject**: full length, and it is final inside the loop (Constraint: A rejection is final inside the loop). What stands behind it is the next round's evaluator, which reads the thread, and past the loop the parent's reading at Procedure step 9.
- **Accept**: name the finding and what changed, and no more than that; what changed is externalized in the diff of the commit that carries it.
- **Language** resolves to the same value as the evaluator comment's, by the same seams — verbatim quotes stay as the source has them. The author does need it named: what its delegation prompt carried is the body language for the issue, PR and commit bodies it writes (`skills/task-subagent-prompt/SKILL.md` Delegation prompt hygiene), and a PR comment does not resolve on that axis. The parent names this one at the resume (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary, item (d)).

</report-shape>

<constraint>

## Constraint

- **Evaluator floor = N=1**: The floor holds unchanged across M configurations. Reference Design Dimensions' `subagent_count` for N and run at minimum 1; N=1 is also the default (Design Dimensions, Default pattern). A round that returns no verdict has not met the floor and is re-run under Procedure step 7, Re-run
- **Model floor = sonnet-class, explicit per spawn**: Every subagent spawned under this skill, on the mandatory brake 1 path or any other Trigger entry, explicitly sets the Agent tool `model` parameter. Implicit parent-model inheritance is prohibited. Default and floor = `sonnet`; a higher-class id (`opus`, `fable`) may be named but is not the default. `haiku` is prohibited as below floor. An id that cannot be positively classified as sonnet-class or above (unlisted, future, or versioned id of uncertain class) must not be passed; on doubt, fall back to the literal `sonnet`. Fix the floor per call, not via custom-agent frontmatter `model:` pinning. The evaluator floor is a separate axis and is unaffected by the model tier. `skills/task-subagent-spawn/SKILL.md` Subagent Model Policy carries the purpose split that scopes this requirement to brake evaluators only
- **Subagent prompt must be self-contained**: Do not let parent context leak in. In the default M=all axes pattern, the prompt explicitly instructs each axis to "answer independently without referencing other axes' answers" to suppress cross-axis echo bias. If prompt complexity is high enough that the mitigation is uncertain, fall back to the M=1 axis-separated pattern (see Design Dimensions)
- **Evaluator does not modify the evaluation target**: the evaluator keeps its tool permissions, so the requirement is carried by the prompt rather than by the tool set (the rejected alternative is named in Non-scope). Copy this literal into every brake 1 evaluator prompt verbatim; do not re-compose it per spawn:

  > Do not modify the evaluation target. Do not edit, write, commit, or push anything in the repository under evaluation, and do not run its build, tests, formatter, or any other command that mutates it. Read the PR diff and the file bodies at the named commit SHA. The one thing you write is your own findings comment on that PR: post it once, post nothing else there, and never a review, an approval, a merge, or a reply to anyone else's comment. If an axis looks like it needs a change applied before it can be answered, report that as a finding instead of applying it.

  This literal and the material rule at Procedure step 3 are applied together. The literal carries no carve-out. The findings comment is the one exception written into it rather than left outside it, so "is a comment a modification?" is answered in the literal and not at the evaluator's discretion.
- **Findings are posted to the PR by the evaluator**: on the brake 1 path the evaluator posts its own findings comment and the author answers on the same thread. No consolidation step stands between them, and the parent neither composes nor reads what passes (Procedure steps 3, 4, 7, 8).
- **A rejection is final inside the loop**: once the author has rejected a finding with its reason on the thread, that finding is settled for the loop. No later round raises it again and the author does not re-adjudicate it. What this buys is the cap's usefulness: re-argument could fill all three round trips with one contested point, and the only actor able to settle such a standoff is the parent — which would put the adjudicator this loop takes out of the exchange back inside the cap. A rejection is examined at the exit instead, by the parent's reading at Procedure step 9.
- **Adjudication actor = the resumed implementation subagent**: the author of the change adjudicates the findings, resumed with its implementation context intact, and the parent retains self-review and the merge decision. Canonical statement, including why the always-delegate rule loses a branch rather than gaining an exception, is `rules/evolution/initiator-autonomy.md` Merge brake, Adjudication actor. Do not restate the reasoning here. Two boundaries carry into the resume prompt: the resumed author neither runs nor posts the self-review, and it does not merge (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary)
- **Character_Instance non-inheritance**: What gets injected into subagent context = `CLAUDE.md` + `.claude/rules/**/*.md` (full body) + `.claude/skills/*/SKILL.md` (description only, body lazy-loaded at invoke) + MEMORY.md + harness-level system-reminders. `.claude/output-styles/`, hook firing output (SessionStart / UserPromptSubmit, etc.), and `.claude/settings.json` itself do not reach the subagent. `.claude/hooks/*.sh` script bodies are readable via the Read tool but not auto-loaded. When character behavior is part of the verification target, explicitly inject the Character_Instance body into the step 3 prompt. Running the character axis without injection produces the hollow prefix sleeping bug: persona absent, only the Character Instance name string generated

</constraint>

<non-scope>

## Non-scope

- This method is a pre-spec-reflection verification surface; it does not replace PR review (semi_auto mode minor/major human review is a separate axis)
- Verification of facts that change over time (API spec, library behavior) is outside this method's range; investigate per occurrence
- Evaluator tool permissions are not restricted, and the custom-agent `tools:` route is rejected. The no-write requirement therefore rests on a prompt literal the parent has to remember to include. Accepted; recurrence is tracked on the post-merge axis per `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format

### What the three-round cap gives up

Procedure step 7 caps the eval at three round trips. Three defect classes sat outside the earlier single-round cap; two of them are now inside the loop's reach and the third is only partly:

- Defects introduced by the adjudicator's own fix. A later round evaluates the SHA that fix went green on, so this class is reached by the instrument itself rather than by a reader — where the fix lands in a round before the last one. Test coverage stays the receptacle for the behavior-defect subset.
- Prose-layer findings that surface only in later rounds, such as a still-live description deleted during a rewrite. Reached, on the same condition.
- Behavior defects present in the initial implementation that no round reached. Not reached: a class no axis touches in three rounds is not touched by a fourth either, and this one is dropped as it was before.

What the cap itself drops is everything after the third round trip — a defect a fourth round would have found, and, by Constraint: A rejection is final inside the loop, a rejection that was wrong. Read those as dropped, not missed.

Accepted on the Li+ correctness criterion (`rules/model/foundational-invariant.md`: correctness is real-world behavior), while none of them reaches production; changes stay inside git revert range and release remains a human gate. Re-evaluation trigger = a capped merge that produces observable production harm.

</non-scope>

<boundary>

## Boundary

- **`skills/evolution-loop/SKILL.md`**: This skill is referenced inside the loop's observe / evaluate stage. The loop side "calls this method"; the method body lives here
- **`skills/evolution-l1-update-gating/SKILL.md`**: Authorization axis for L1 source changes (long-horizon observation requirement), orthogonal to this empirical verification axis and expected to be used alongside it. In the `Evolution_Initiator_Autonomy` framing, this method is brake 1, the only brake at the merge gate and always-on for self-evolution PRs; the L1 gate it runs alongside is the observation threshold at issue formation, not a second brake
- **`rules/evolution/promotion-judgment.md`**: Noise floor observation judgment (memory cluster tally) is observation accumulation; this method is spec verification immediately before implementation. Orthogonal
- **`skills/task-subagent-delegation/SKILL.md`**: This method's subagent spawn is a special case of delegation (purpose: gather evaluation data, not delegate implementation). This skill's N / M / P width (Design Dimensions) is exempt from the 5-in-flight cap in `skills/task-subagent-spawn/SKILL.md` Parallel-Width Cap — a selection whose total invocation exceeds 5 is still within spec
- **`skills/evolution-decision-structure-write/SKILL.md`**: Judgment record surface for Procedure step 9

</boundary>

<implementation-note>

## Implementation Note

Subagent spawn goes through the host's Agent tool (Claude Code: `Agent` tool; Codex: equivalent mechanism). Parallel execution = multiple Agent tool calls in a single message. subagent_type is selected per task (typically general-purpose).

On hosts without a per-call `model` parameter, verify the session model satisfies the sonnet-class floor before spawning; a session model that cannot be positively classified as sonnet-class or above counts as sub-floor and cannot satisfy brake 1. Run the eval from a floor-satisfying session instead.

</implementation-note>

</parallel-subagent-eval>

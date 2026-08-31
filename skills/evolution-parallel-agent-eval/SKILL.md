---
name: evolution-parallel-agent-eval
description: Invoke when a self-evolution PR reaches CI green and the merge gate is next (mandatory brake 1) / a Li+ rules/skills/adapter edit draft has converged outside a PR flow and needs verification / an evolution-loop observe/evaluate stage needs an empirical verdict / an N=1 self-check feels positive and needs measuring / a spec revision needs orthogonal verification on rule semantic consistency / a brake 1 evaluator report, the parent's aggregated comment, or an author's adjudication is being written. Provides the parallel subagent eval design, its procedure, and its report shape.
layer: L2-evolution
---

<parallel-subagent-eval>

# Parallel Subagent Eval

Verification method that measures the AI's introspection gap (no empirical basis for predicting its own future invoke behavior or rule semantic effect) from the outside via the current behavior of subagents.

Justification for the design decisions below is held as Decision Structure entries in the wiki, indexed at `docs/Decision-Structure.md` and retrieved via `skills/evolution-judgment-learning`. This body carries what the application moment needs and names the entry the reasoning lives in; it does not hold a second, lossy copy of it. A `judgment record:` pointer below is that naming, and re-inlining what it points at is the move this placement refuses.

<held-literals>

## Held literals

Some of the text this method fixes is payload rather than description: it is copied into an artifact word for word, and composing it afresh per run is what drops the part that made it hold. Each such literal is held at exactly one place, and the paragraph around it states what a re-wording would lose — that reason is the literal's own and stays there. What is general is the handling, stated here once: copy it from where it is held, add nothing to it, and leave it in the language the source has it in. Translation is a re-wording, so a workspace resolving to another language copies it untranslated.

| literal | held at | copied into |
|---|---|---|
| the fixed axis's wording | `skills/evolution-impression-literal-detection/SKILL.md` Prompt literal | every evaluator prompt, at Procedure step 3 |
| the no-write requirement | Constraint: Evaluator does not modify the evaluation target | every brake 1 evaluator prompt, at Procedure step 3 |
| the triage-signal preamble | Report shape, Parent's aggregated comment | the head of the parent's aggregated comment, at Procedure step 4 |

The table is what makes the handling checkable, and it is closed: text absent from it is composed per run, and the copy-verbatim rule does not reach it.

</held-literals>

<trigger>

## Trigger

Fires at any of the following moments:

- Li+ rules/* or skills/* edit draft has converged outside a PR flow and verification is needed before it is carried into one
- evolution-loop observe / evaluate stage needs an empirical verdict
- Right after AI alone feels "this edit satisfies the spec" (catch overconfidence from N=1 self-check)
- Spec revision proposal needs orthogonal verification on the rule semantic consistency axis
- **Self-evolution PR brake (mandatory)**: any self-evolution PR runs this method. Which PRs those are is canonical in `rules/evolution/initiator-autonomy.md` Self-evolution PR definition — both of its conditions, neither alone — and is not restated here. This is brake 1, the only brake at the merge gate. Its firing moment is fixed rather than draft-driven — the delegated subagent's report at its stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition) — and the position rule is canonical in `rules/evolution/initiator-autonomy.md` Merge brake, not restated here. An L1 Model Layer source change adds no brake of its own and runs this one unchanged. semi_auto patch-auto-merge does not bypass brake 1. Judgment record: `brake1-firing-closed-by-criterion`.

Axis selection: the fixed axis (impression-literal detection, spec in `skills/evolution-impression-literal-detection/SKILL.md`) is always included for Li+ source drafts regardless of spec nature. Additional axes are selected per draft nature. Examples:
- skill description edit: ease of AI invoke judgment / maintainer-side readability / coverage gap
- rule body edit: behavior consistency across configured / not-configured paths / detect semantic conflict with adjacent rules / orthogonality against existing scope clauses

</trigger>

<design-dimensions>

## Design Dimensions

Three axes that move verification cost and detection power independently. Total subagent invocation count = `N x P`; M is absorbed inside each subagent prompt. Judgment records: `parallel-subagent-eval-three-axis-decomposition` (the decomposition and the alternatives rejected with it), `parallel-subagent-eval-cost-acceptance` (why the cost is accepted).

- **`subagent_count (N)`** - Independent sample count. Obtain N independent evaluations per observation axis. Robustness against probabilistic variance.
- **`axes_per_subagent (M)`** - Number of observation axes each subagent answers within its prompt. Blind-spot coverage.
- **`premise_variations (P)`** - Number of ablation premises (e.g. full rule exclusion / partial exclusion). Robustness against premise variation.

### Default pattern (delete/keep judgment, etc.)

`N=3, M=all axes, P=1` - 3 subagents independently answer all M axis questions against the same ablation output. Total invocation = 3. N=3 samples are collected per axis, capturing blind-spot coverage and variance robustness simultaneously.

### Exception pattern: M=1 axis-separated

`N=3, M=1, P=1`, one axis per subagent. Total invocation = `N x axis_count`. Adopt only when per-axis prompt complexity is high enough that cross-axis echo bias cannot be suppressed inside a single subagent context.

### Premise variations (P > 1)

Use only when comparing multiple ablation premises directly. Total invocation = `N x P`; within each premise, M is absorbed into the prompt as in the default pattern.

The representative case is P=2 before/after: premise A = pre-change (operational copy unapplied = baseline), premise B = post-change (draft applied = candidate) are placed as separate premises and the subagent's behavior under the same prompt is compared directly. Trigger = a revision where "did the subagent verdict shift before vs after draft application on the same question?" needs to be pinned down empirically. Cost is `N=3, P=2 -> 6 invocation`, double the default.

### aggregation rule

Choose based on the asymmetry of the judgment:
- delete/keep binary where erroneous deletion is costly -> safer-side OR (if any axis detects effect, "keep")
- adopt/reject binary where erroneous adoption is costly -> require unanimous agreement (AND)
- intermediate -> three-value classification: consistent / partial / negative

### Divergence handling

When evaluators split on one axis, ask two questions once each, in this order, before the verdict is written:

1. **Same-question check** - did they answer the same question? A split is often not disagreement: two evaluators checked one reading of the axis and the third checked another, so no one contradicted anyone. No here puts the finding on the axis wording (one axis name carried more than one question), not on the criteria.
2. **Why-diverged** - asked only when 1 answers yes: does the split trace to ambiguity in the judgment criteria, or to variance in applying a criterion that is already clear?

"They answered the same question, and the criteria sufficed" answers both and closes the divergence. This is a check to pass through, not a hunt: the shape is `rules/model/trigger-check-gate.md`, where one No pauses to retrieve and verify and then proceeds, and confirming nothing is wrong is a normal outcome. Writing up a criteria gap because the step expects one is the failure mode here (`rules/model/subtractive-structural-beauty.md` push surplus).

Answers go where the author's adjudication goes (Report shape, Author's adjudication), the surface the fixed axis's 1-of-3 flag already uses; the parent reads them there at Procedure step 8. No new record surface. Neither outcome gates the merge on its own: a criteria gap from question 2 is routed like any other spec-gap observation (`rules/evolution/promotion-judgment.md`), and an axis-wording finding from question 1 names the part of Axis statement form that did not hold, which is where it lands. Stating this for one branch and not the other would put the pressure back where the paragraph above removes it.

### Ratio is a triage signal

The ratio of evaluators reporting a finding (3/3, 2/3, 1/3) is a cheap prior on where to spend verification effort first. It is not a judgment input. The verdict on a finding comes from checking its literal against the source: a 1/3 finding that holds up is adopted, and a 3/3 finding that does not is dropped. The ratio is kept rather than discarded because verifying every finding at equal cost is not practical and the parent's own literal check is not infallible either. The parent states it on each finding when it consolidates them at Procedure step 4, and it stays a statement there — consolidation is not the place a finding is weighed. The field the ratio occupies in the self-review is fixed at Procedure step 9; the shape of the reports it is counted from is fixed at Report shape.

The one place this skill fixes a count as a threshold is the fixed axis (`skills/evolution-impression-literal-detection/SKILL.md` Aggregation), whose numbers come from the asymmetry of that judgment - over-trimming load-bearing spec phrasing is the costly error - not from counting votes. The per-judgment aggregation rule above is likewise selected from asymmetry; majority is not among its options. Both halves — the triage signal and this carve-out — reach the author as one held literal at the head of the parent's aggregated comment (Held literals; the wording is at Report shape, Parent's aggregated comment).

</design-dimensions>

<procedure>

## Procedure

**Precondition**: source lives on a branch other than the merge target, and `.claude/` is in tag-match state (draft unapplied). On the brake 1 path that branch is the PR branch at the SHA the CI run went green on; on the other Trigger entries it is an experimental branch.

1. **Prepare draft** - Draft the edit content
2. **Apply operational copy (target-conditional)** - Apply only when the draft reaches the subagent's observation surface as injected context, which splits by target (judgment record: `brake1-operational-copy-target-conditional`):
   - `rules/**/*.md` body IS injected: the apply is mandatory
   - `skills/<name>/SKILL.md` body is NOT injected (description only, body lazy-loaded at invoke): for a judge-type evaluator the apply is not required, and the evaluator is pointed at the draft for direct Read instead. Exception: when the eval depends on the subagent *invoking* the skill (probe-type, body auto-loads at invoke), the apply IS required

   The apply is a parent-side write to `.claude/`; the source stays on its own branch and the evaluators spawned at step 3 read it there.
   - **Host permission-gate fallback**: an autonomous run without explicit user authorization can have the apply refused by the host self-modification gate. `skills/*` falls back to evaluator direct Read at the named SHA; record the deviation in the PR self-review. `rules/*` cannot be substituted that way: re-run from a session that can apply, or record the deviation and flag reduced confidence for post-merge observation
3. **Parallel subagent spawn** - Select N, M, P per draft nature and spawn in parallel. Default `N=3, M=all axes, P=1`, total invocation = 3; switch to the M=1 exception pattern when the echo-bias condition in Constraint: Subagent prompt must be self-contained holds, or to P>1 when premise variation is needed (see Design Dimensions). Every spawn explicitly sets the Agent tool `model` parameter at or above the sonnet-class floor (see Constraint: Model floor).

   On the brake 1 path the material named in the prompt is the PR URL, the pushed commit SHA, and the green CI run URL — never a path inside the parent's clone. The reason that set is fixed is canonical in `rules/evolution/initiator-autonomy.md` Merge brake. The rule governs what the prompt *names*, so step 2's operational copy is unaffected: it reaches the evaluator as auto-injected context, not as a named path.

   Each per-draft axis goes into the prompt in the form fixed at Axis statement form; the fixed axis is outside that form's scope and enters as a held literal (Held literals). Five more things go in alongside the axes and the material:
   - the no-write literal (Held literals)
   - the retrieval commands, so the evaluator does not assume a clone is needed: `gh pr diff <n> --repo <owner>/<repo>` returns the diff and `gh api repos/<owner>/<repo>/contents/<path>?ref=<SHA>` returns any file body at that SHA
   - the allowance that an axis needing a repository-wide sweep clones into the evaluator's own working directory, which is off the shared surface. GitHub code search is unreliable on this repository (total hits 0), so the sweep has nowhere else to go
   - on the brake 1 path, the reporting destination: the evaluator returns its findings to the parent as its own report, all axes inside it, and writes nothing to the PR. No `gh pr comment` is run by an evaluator (Constraint: Findings route through the parent as one aggregated comment)
   - the shape that report is written in, as one sentence the parent composes from Report shape: the evaluator-report row of its table, plus the prohibition on echoing the criteria this prompt supplies. That sentence is what the prompt carries; the Report shape section behind it is the parent's reference, not prompt payload, since pasting the section would put back into the prompt the bulk this contract removes. The shape is a contract on the report, so leaving it to the evaluator's discretion is what puts every axis at finding length
4. **Aggregate findings and post** - Actor = the parent. Consolidate the N evaluators' reports into one PR comment and post it (`gh pr comment <n> --repo <owner>/<repo> --body ...`) — one comment for the whole eval, in the shape fixed at Report shape, Parent's aggregated comment. Post nothing when every axis on every report is clean: there is then nothing to adjudicate, the author is not resumed, and steps 6 to 8 have no input; the eval's record rests on the self-review at step 9.

   Consolidation is summary and merge — duplicate findings raised by more than one evaluator collapse into one entry carrying its ratio, and the surrounding prose is the parent's — the held preamble the comment opens with aside (Report shape, Parent's aggregated comment). It stops there. **The parent does not select among findings**: it does not drop one it disagrees with, does not rank them, and does not answer one. Accept / reject is the author's authority (Constraint: Adjudication actor), and a finding dropped at this step never reaches the actor holding that authority (judgment record: `brake1-findings-routed-through-parent`)
5. **Runtime restore** - Restore `.claude/` to tag-match state (revert the operational copy to pre-draft). Parent-side, as the apply at step 2 was. It runs as soon as every evaluator has returned its findings, and before the author is resumed: the copy exists for the evaluators' observation surface only, so it does not wait on step 6. Skipping it carries the draft into the parent session's behavior and leaves it there for subsequent sessions. Skip only when step 2 applied nothing (skills/* direct-Read path, or permission-gate fallback): no write occurred, so there is nothing to restore
6. **Aggregate verdict** - Actor = the resumed implementation subagent, not the parent (see Constraint: Adjudication actor). It reads the parent's aggregated comment and aggregates cross-axis judgment per the Design Dimensions aggregation rule. Fixed axes may override the default per-axis (see `skills/evolution-impression-literal-detection/SKILL.md` Aggregation). Where evaluators split on an axis, run Design Dimensions Divergence handling before the verdict is written
7. **Judgment** - Actor = the resumed implementation subagent, which adjudicates each finding against the source and records every accept / reject and its reason in the **commit body**, never as a PR comment. Two application moments sit under this number, split across the labels below: the adjudication branch, and whether a re-run is permitted. Judgment records: `brake1-single-round-cap`, `brake1-rerun-gated-on-what-the-round-audited`.

   **Adjudication branch.** consistent -> nothing to apply; report back. partial / negative -> apply what was accepted, commit, push, and stop again at CI green (commit body shape = Report shape, Author's adjudication). Or abort.

   **Single round.** Steps 2-6 produce one verdict per draft, and the revised draft ships without re-verification (see Non-scope: what the single-round cap gives up). The author's response-and-revision pass is the tail of that one round, not a second one.

   **Re-run: same round, or round 2.** What the cap refuses is a second audit of a draft already audited, so whether a re-run is that second audit is settled by what the round audited, never by why it stopped. A re-run continues the same round when both hold, and neither alone: (a) the verdicts that round returned have not reached the N>=3 floor (Constraint: N=1 prohibited, minimum N=3), and (b) the baseline it ran against — the PR commit SHA — is unchanged from the first attempt. Verdicts already returned are carried into it rather than discarded, and they must share the instrument: a verdict counts toward the floor only where the axes and prompt that produced it are the ones the re-run spawns under. Repairing a prompt between attempts is permitted, and a malformed one has to be repaired before it can return anything — but the repair retires the verdicts taken under the old wording instead of adding to them. Cause is not a term here: a spend limit, an evaluator crash, a malformed prompt and a timeout are one thing under this criterion, a round that returned fewer than the floor. Ceiling: a third attempt against the same baseline that still has not reached the floor stops there and escalates to human. The number and its task / debug category are `skills/model-loop-safety`'s, and this skill states none of its own; the action is this skill's — stop, not the stop-and-switch Loop Safety prescribes at its threshold, the switch being spent before it (prompt repair and a higher model tier are available at every attempt).

8. **Inspect the adjudication** - Actor = the parent, which holds the findings from step 4 and can therefore check what was done with them. Read the adjudication where it landed — the commit bodies from step 7, and the author's stop-condition report for an adjudication that produced no commit — and judge it against the findings as posted. Where it does not hold, resume the author again with the correction named; the author revises and stops again at CI green.

   **No cap is placed on these round trips.** They are not evaluator rounds: nothing here re-spawns an evaluator or re-opens an axis, so the cap at step 7 is untouched in both directions. What governs convergence is `skills/model-loop-safety`, and **the parent is the actor holding that judgment**. Accepted with it: a round trip that names a different real defect each time is a switched axis, which Loop Safety's own scope clause places outside the safeguard; what the safeguard reaches is the same correction pressed again (judgment record: `brake1-findings-routed-through-parent`)
9. **Externalize** - Record the verdict and the adoption judgment in the parent issue body / PR self-review, so the judgment survives the session. On the brake 1 path the findings are externalized as the aggregated comment at step 4 and the adjudication as the commit bodies at step 7; the self-review does not transcribe either, it reads them and records what they do not carry — the merge judgment over the eval, including whether a rejection left standing looks right, and the adjudication of a round that produced no commit at all, which has no commit body to sit in. The self-review is brake 1's only guaranteed externalization; every other surface in this procedure is conditional on there being something to write to it. A reported count occupies its own field, separate from the adjudication and from the literal that adjudication rests on; do not write the count as the reason (see Design Dimensions, Ratio is a triage signal). If the judgment has settled, also append to decision structure per `skills/evolution-decision-structure-write`

</procedure>

<axis-statement-form>

## Axis statement form

Fixes the form each per-draft axis is written in — the set Trigger, Axis selection names with `Additional axes are selected per draft nature`, which the parent composes at spawn time. It applies at Procedure step 3, where those axes enter the prompt. The fixed axis is outside it: that axis's wording is not composed per run but held as a copy-verbatim literal at `skills/evolution-impression-literal-detection/SKILL.md` Prompt literal, so the per-run authoring this section addresses does not reach it. The exclusion rests on the literal being held there. Held, the axis carries no blank for one of the parts below to be filled in on it; stated in prose alone, the exclusion leaves the field open on an axis the parent is writing the rest of the prompt around.

The gap it closes: the parent authors the instrument in the same moment it is reading the instrument's target literally, and the literal check that reaches the target does not reach the instrument. The recurring form is one axis name carrying more than one question — joined visibly, or compressed into a single predicate that reads as one.

Each axis ships as five labeled parts, all of them payload — they enter the evaluator's prompt as written, and none is a check whose output is discarded once it passes. A part left unwritten is therefore a missing label in the text the evaluator will read. Artifact visibility is the mechanism, and it stops short of the execution guarantee `rules/model/subtractive-structural-beauty.md` asks for when it requires a procedure be replaced by a structure (judgment record: `presence-defect-cannot-reach-blank-label-visibility`, which also holds why relocating a dropped step to another surface is not that structure either). Each part is a phrase, not a paragraph; the form fixes what an axis names, not how much of it there is.

- **Question** — one interrogative, and one only; it names the operation that produces its verdict, and it is answerable in the order its material arrives — an axis cannot ask for a judgment formed before reading what the prompt itself carries. Naming the operation means saying what the evaluator does to the material, and which result of doing it is the finding. Two clauses joined by "and" or by a comma are two operations and so two axes: split them, or drop one. What is counted is operations, not clauses, because a predicate that names an evaluation instead of an operation — `forced`, `consistent`, `resolves wrongly` — carries its count hidden: each reading of it is a different thing to do, and the conjunction sits compressed inside the one word, where the joined-clause prohibition cannot reach it. Writing the operation is what decompresses it; the readings come apart into separate interrogatives while the axis is being written, and the prohibition then fires on them as on any other pair. An interrogative that names no operation is unfilled, not answerable: the evaluator cannot begin without supplying a reading of its own, and readings supplied independently are the split that arrives looking like disagreement. What this puts on the artifact is narrower than the blank label above, and the gap is stated rather than elided (judgment record: `presence-defect-cannot-reach-blank-label-visibility`). The residual — a predicate whose readings the author and all N evaluators happen to converge on, which emits no split and so no signal — is accepted on the post-merge observation axis, as this file's other not-guaranteed requirement already is (Non-scope).
- **Unit** — what a single verdict covers: a sentence, a paragraph, a file, a claim, an occurrence. Unstated, evaluators pick different ones and the resulting split reads as disagreement when nobody disagreed.
- **Scope** — the surface the axis ranges over, stated on both of its dimensions — extent (this PR's diff, one named file, the repository, the repository and the wiki) and the language the axis's patterns are written in — and, where the axis's verdict is an absence claim, what it swept. An absence is only as wide as what was read. Extent alone does not carry the second dimension: a scope reading `the repository` is satisfied by a sweep that ran on English patterns alone. This repository holds most normative text twice — English in `rules/` and `skills/` (`rules/model/liplus-coding-rule.md` Source Language), Japanese in `docs/`, which mostly mirrors them and in places is itself the source (`docs/5.-Notifications.md` declares its own body canonical, there being no `rules/notifications/` for it to mirror) — so such a sweep never reached the Japanese side, and its absence claim is under-swept by construction rather than by oversight. The source-side case is the sharper one: it has no English counterpart for such a sweep to have hit instead. Report shape asks the return leg for the patterns a sweep ran under (Evaluator report); this is the same dimension on the authoring leg, where the width is required rather than reported.
- **Verdict terms** — what a yes and a no mean here, in this axis's own words. Design Dimensions' aggregation vocabulary is about the judgment on the draft, so on an axis asking "did anything drop?" a finding answers yes while being negative for the draft; an axis that does not name its own polarity inherits the wrong one. This is the part Report shape presumes when it asks a clean axis for the verdict in that axis's own terms.
- **Basis** — every statement the axis makes about the target or about the criteria carries a pointer that resolves at the named SHA, is written inside every axis that needs it rather than once for the set, and, where the answer turns on how many of something there are, hands over the body to count from instead of a number. An axis does not inherit what was written next to it, and an axis that names no basis is unfilled, not clean. What resolving means: the criterion at its `path`, or quoted with `path:line`; an illustrative example quoted from where it actually occurs rather than composed to look like one. What this excludes is assertion from the parent's memory of a body the parent itself authored — the gist read this form exists to cut. Resolvability is the property the return leg already rests on (Report shape, The asymmetry). The part is not satisfied by form alone, and what the per-axis requirement above ranges over is whatever the verdict has to be formed against — an existing Li+ criterion the axis is judging by, or an argument the parent is relying on.

### Where this meets the post-hoc check

Design Dimensions, Divergence handling asks the same-question check after the eval; Question above asks it before the spawn. Neither replaces the other. The post-hoc check catches the axis whose parts were filled but filled loosely, and it keeps working on axes worded before this form existed. What moves is where its No lands: on the part of this form that did not hold, a surface that persists, instead of on the next run's framing, which persists nowhere and lets the same gap reopen on the run after it.

</axis-statement-form>

<report-shape>

## Report shape

Fixes the form of the three artifacts brake 1 produces — the evaluator's report at Procedure step 3, the parent's aggregated comment at Procedure step 4, and the author's adjudication at Procedure step 7. What this section fixes is delivery: it does not change which axes are asked (Trigger, Axis selection), how many evaluators answer them (Constraint: N=1 prohibited, minimum N=3), or how the answers aggregate (Design Dimensions).

Scope = the brake 1 path. On the other Trigger entries there is no PR surface, so the step 4 comment has no counterpart, and the asymmetry below still governs what the evaluator writes — its reasoning turns on who adjudicates a line, not on where the line ends up.

### The asymmetry

All three artifacts are asymmetric on the same seam: **the side carrying a finding is written at full length, the side nobody contests at one line.** Left unfixed, each actor composes the form per run and every axis is written at finding length.

Full length is the verbatim quote of the literal at issue, its `path:line` at the named SHA, and why it is a defect. It is not a compression target: the next actor adjudicates against that quote and would otherwise re-fetch the source once per contested line, and a defect asserted without hitting the literal is the shape `rules/model/trigger-check-gate.md` Literal check stands against.

One line is that pointer without the quote. Dropping the quote there narrows the gap between "inspected and found clean" and "declared clean without inspecting", and the `path:line` is what is left holding it. It holds because it resolves: named at the SHA, it can be opened, and a pointer that does not resolve — or resolves to something the verdict does not fit — fails at one lookup. The quote's advantage over it is that the same check costs nothing, which is worth its bulk only where a line is adjudicated repeatedly, and that is the finding side, where the quote stays. Residual = a clean axis whose pointer nobody opens, and a pointer picked after the verdict to fit it; accepted, on the post-merge observation axis the fixed axis's all-3-miss case already uses (`skills/evolution-impression-literal-detection/SKILL.md` False-negative backstop).

What each artifact puts on each side:

| artifact | side carrying a finding | side nobody contests |
|---|---|---|
| Evaluator report (step 3) | the axis's finding: the quote, its `path:line`, why it is a defect | the axis at one line: its name, its verdict in its own terms, the `path:line` the verdict rests on |
| Parent's aggregated comment (step 4) | the finding, in the full form it arrived in; duplicates across evaluators collapse into one entry stating how many of the N raised it | the clean axis's one line, carried through |
| Author's adjudication (step 7) | a reject: the reason | an accept: one line — which finding, and what changed |

The sections below carry what a cell cannot: the reason each side lands where it does in that artifact, and the one case that has no line to point at.

### Evaluator report

- **An axis answered by a repository-wide sweep** has no single line to name, so the sweep itself substitutes for the pointer: give it in re-runnable form (the pattern, and the paths it ran over) and its hit count. No quote. An absence claim is checked by re-running rather than by opening, so a hit count that does not reproduce fails the way an unresolvable pointer fails. The scope the sweep ran over stays the evaluator's own statement.
- **Prohibited on both sides**: restating the criteria, thresholds, or axis wording the parent supplied in the prompt. Both readers already hold that text — the parent wrote it, and the author reads it where the parent copied it from — so a restatement is a second copy of it, and the second copy is what drifts.

### Parent's aggregated comment

- **Preamble**: the comment opens with a held literal (Held literals):

  > The count on each finding below — how many of the N evaluators raised it — is a triage signal on where to check first, not a judgment input. Adjudicate each finding by checking its literal against the source at the revision its `path:line` is given at, and adopt or drop it on that. One axis stands outside both of those sentences: on the fixed impression-literal axis the count is the adjudication, at the absolute thresholds its own spec fixes (`skills/evolution-impression-literal-detection/SKILL.md` Aggregation), and it is recorded there as that spec requires.

  All three clauses are payload. The first two without the third are false where the fixed axis lands — that axis takes neither the triage reading of its count nor the literal-check route to a verdict — and the third without them leaves the per-draft axes' counts reading as votes (Design Dimensions, Ratio is a triage signal). The parent restating this in its own words is what generalizes the first two over the carve-out the third names, which is why the wording is held rather than composed. Language below leaves a verbatim quote where the source has it for its own reason, and the preamble sits on that side of the comment's seam rather than in the prose the parent resolves.
- **Consolidation** earns its place by removing duplication across evaluators, not by shortening a finding: compressing one here pushes the re-fetch onto the author, which is the cost the full-length side of the asymmetry exists to remove.
- **Clean axes** are carried through because the author aggregates cross-axis at Procedure step 6, and a comment listing only findings leaves it aggregating over a denominator it cannot see.
- **Prohibited**: an accept, a reject, a ranking, or a recommendation. Those are the author's at Procedure step 7, and prose that leans on a finding here arrives ahead of the actor entitled to weigh it.
- **Language**: the parent writes this comment and resolves `Workspace_Language_Contract` (`adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md`) for it as it does for anything else it writes, so nothing about resolving it is stated here. What is stated is what resolution does not settle: a verbatim quote and its `path:line` stay as the source has them, and so does the held preamble above. The author adjudicates against the literal and a translated literal is not the literal. Li+ source is English (`rules/model/liplus-coding-rule.md` Source Language), so in a workspace resolving to any other language this comment is mixed by construction — quotes in the source's language inside prose in the resolved one. Left unstated the pair collapses one way or the other: the quotes get translated with the prose, or the prose falls back to the quotes' language. A clean axis carries no quote, so its one line is prose and a pointer, and a pointer is not prose.

### Author's adjudication

Destination = the commit body of the commit that applies what was accepted (`rules/operations/operations.md` fixes what else a commit body carries; this rides alongside it). Not a PR comment.

- **Reject**: the reason is what the parent reads at Procedure step 8, and under the single-round cap no evaluator re-argues it, so nothing else stands behind it.
- **Accept**: the change itself is already externalized in the diff of the same commit, so prose restating it would be a second copy of the same content for the parent to reconcile against the first.
- **When nothing was accepted** there is no commit, so there is no commit body: the adjudication goes to the parent in the author's stop-condition report, and the parent carries it into the self-review at Procedure step 9. This is the one branch where the reasoning lands in a durable artifact written by someone other than its author, and it is the reason step 9 is described there as the only guaranteed externalization.

</report-shape>

<constraint>

## Constraint

- **N=1 prohibited, minimum N=3**: One trial is the source of overconfidence — a conclusion positive at N=1 reverses under independent sampling. The floor's basis is sample count, not axis layout, so it holds unchanged across M configurations. Reference Design Dimensions' `subagent_count` for N and run at minimum 3
- **Model floor = sonnet-class, explicit per spawn**: Every subagent spawned under this skill, on the mandatory brake 1 path or any other Trigger entry, explicitly sets the Agent tool `model` parameter. Implicit parent-model inheritance is prohibited: a sub-floor parent silently lowers the evaluation floor. Default and floor = `sonnet`; a higher-class id (`opus`, `fable`) may be named but is not the default. `haiku` is prohibited as below floor. An id that cannot be positively classified as sonnet-class or above (unlisted, future, or versioned id of uncertain class) must not be passed; on doubt, fall back to the literal `sonnet`. Fix the floor per call, not via custom-agent frontmatter `model:` pinning: judge-type (answers axis questions) and probe-type (the vanilla subagent's current behavior is itself the observation target) coexist here, and an agent file body replaces the subagent's system prompt = identity (judgment record: `parallel-subagent-eval-model-floor`). The N=3 floor is a separate axis and is unaffected by the model tier. `skills/task-subagent-spawn/SKILL.md` Subagent Model Policy carries the purpose split that scopes this requirement to brake evaluators only
- **Subagent prompt must be self-contained**: Do not let parent context leak in. In the default M=all axes pattern, the prompt explicitly instructs each axis to "answer independently without referencing other axes' answers" to suppress cross-axis echo bias. If prompt complexity is high enough that the mitigation is uncertain, fall back to the M=1 axis-separated pattern (see Design Dimensions)
- **Evaluator does not modify the evaluation target**: the evaluator keeps its tool permissions (brake 1 spawns `general-purpose`, which holds Edit / Write / Bash), so the requirement is carried by the prompt rather than by the tool set (judgment record: `brake-evaluator-baseline-integrity`; the rejected alternative is named in Non-scope). The requirement is a held literal (Held literals):

  > Do not modify the evaluation target. Do not edit, write, commit, or push anything in the repository under evaluation, and do not run its build, tests, formatter, or any other command that mutates it. Do not post to the PR. Read the PR diff and the file bodies at the named commit SHA, and return your findings in your report. If an axis looks like it needs a change applied before it can be answered, report that as a finding instead of applying it.

  This literal and the material rule at Procedure step 3 are applied together: the literal cuts the intent to write, and naming no shared path removes the shared target itself. The literal carries no carve-out: `Do not post to the PR` states the reporting destination in the negative rather than opening a question about whether a comment counts as a modification.
- **Findings route through the parent as one aggregated comment**: on the brake 1 path the evaluator returns its findings to the parent and writes nothing to the PR; the parent consolidates them and posts one comment (Procedure steps 3 and 4). The parent carries the findings deliberately, and that is what buys its inspection of the adjudication at Procedure step 8 (judgment record: `brake1-findings-routed-through-parent`, which holds the write-shape half as well).
- **Adjudication actor = the resumed implementation subagent**: the author of the change adjudicates the findings, resumed with its implementation context intact, and the parent retains self-review and the merge decision. Canonical statement, including why the always-delegate rule loses a branch rather than gaining an exception, is `rules/evolution/initiator-autonomy.md` Merge brake, Adjudication actor. Do not restate the reasoning here. Two boundaries carry into the resume prompt: the resumed author neither runs nor posts the self-review, and it does not merge (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary)
- **Character_Instance non-inheritance**: What gets injected into subagent context = `CLAUDE.md` + `.claude/rules/**/*.md` (full body) + `.claude/skills/*/SKILL.md` (description only, body lazy-loaded at invoke) + MEMORY.md + harness-level system-reminders. `.claude/output-styles/`, hook firing output (SessionStart / UserPromptSubmit, etc.), and `.claude/settings.json` itself do not reach the subagent. `.claude/hooks/*.sh` script bodies are readable via the Read tool but not auto-loaded. When character behavior is part of the verification target, explicitly inject the Character_Instance body into the step 3 prompt. Running the character axis without injection produces the hollow prefix sleeping bug: persona absent, only the Character Instance name string generated

</constraint>

<non-scope>

## Non-scope

- This method is a pre-spec-reflection verification surface; it does not replace PR review (semi_auto mode minor/major human review is a separate axis)
- Verification of facts that change over time (API spec, library behavior) is outside this method's range; investigate per occurrence
- Evaluator tool permissions are not restricted, and the custom-agent `tools:` route is rejected (judgment record: `brake-evaluator-baseline-integrity`, which holds both the identity-replacement reason and the finding that `tools:` cannot express read-only for brake 1 at all). The no-write requirement therefore rests on a prompt literal the parent has to remember to include, which `rules/model/subtractive-structural-beauty.md` places on the not-guaranteed side of its procedure-vs-structure judgment. Accepted; recurrence is tracked on the post-merge axis per `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format

### What the single-round cap gives up

Procedure step 7 caps the eval at one round. Three defect classes are dropped by that cap. They are enumerated here so a later reader reads them as dropped, not missed — read as an unfixed-bug list, they invite someone to restore the rounds without going through the re-evaluation trigger:

- Defects introduced by the adjudicator's own fix, the adjudicator being the resumed author under the current actor split. Test coverage is the receptacle for the behavior-defect subset.
- Prose-layer findings that surface only in later rounds, such as a still-live description deleted during a rewrite. Tests do not catch this class.
- Behavior defects present in the initial implementation that round 1 did not reach, such as chunk-boundary multibyte corruption or a spec category missing from an enumeration.

Accepted on the Li+ correctness criterion (`rules/model/foundational-invariant.md`: correctness is real-world behavior), while none of them reaches production; changes stay inside git revert range and release remains a human gate. The measured cost this was weighed against, and the counter-evidence table the three classes are drawn from, are in the judgment record `brake1-single-round-cap` — which is also where the requirement that this enumeration stay in the body comes from. Re-evaluation trigger = a single-round-capped merge that produces observable production harm.

The first class is partly reached again by Procedure step 8, which puts a reader on the adjudicator's fix without spawning an evaluator. Partly, and stated so the list is not read as longer than it is: that reader is the parent, checking the adjudication against findings it already holds, not the N=3 outside measurement this method exists to obtain. The other two classes need an axis re-run and stay dropped.

</non-scope>

<boundary>

## Boundary

- **`skills/evolution-loop/SKILL.md`**: This skill is referenced inside the loop's observe / evaluate stage. The loop side "calls this method"; the method body lives here
- **`skills/evolution-l1-update-gating/SKILL.md`**: Authorization axis for L1 source changes (long-horizon observation requirement), orthogonal to this empirical verification axis and expected to be used alongside it. In the `Evolution_Initiator_Autonomy` framing, this method is brake 1, the only brake at the merge gate and always-on for self-evolution PRs; the L1 gate it runs alongside is the observation threshold at issue formation, not a second brake
- **`rules/evolution/promotion-judgment.md`**: Noise floor observation judgment (memory cluster tally) is observation accumulation; this method is spec verification immediately before implementation. Orthogonal
- **`skills/task-subagent-delegation/SKILL.md`**: This method's subagent spawn is a special case of delegation (purpose: gather evaluation data, not delegate implementation). This skill's N / M / P width (Design Dimensions) is exempt from the 5-in-flight cap in `skills/task-subagent-spawn/SKILL.md` Parallel-Width Cap — a P=2 run reaches 6 and is still within spec. The exemption is stated here as well because that cap's value reaches every context through its skill's description while the exemption itself sits in that skill's lazily-loaded body
- **`skills/evolution-decision-structure-write/SKILL.md`**: Judgment record surface for Procedure step 9

</boundary>

<implementation-note>

## Implementation Note

Subagent spawn goes through the host's Agent tool (Claude Code: `Agent` tool; Codex: equivalent mechanism). Parallel execution = multiple Agent tool calls in a single message. subagent_type is selected per task (typically general-purpose).

On hosts without a per-call `model` parameter, verify the session model satisfies the sonnet-class floor before spawning; a session model that cannot be positively classified as sonnet-class or above counts as sub-floor and cannot satisfy brake 1. Run the eval from a floor-satisfying session instead.

</implementation-note>

</parallel-subagent-eval>

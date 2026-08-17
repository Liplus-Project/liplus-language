---
name: evolution-parallel-agent-eval
description: Invoke when a self-evolution PR reaches CI green and the merge gate is next (mandatory brake 1) / a Li+ rules/skills/adapter edit draft has converged outside a PR flow and needs verification / an evolution-loop observe/evaluate stage needs an empirical verdict / an N=1 self-check feels positive and needs measuring / a spec revision needs orthogonal verification on rule semantic consistency / a brake 1 evaluator report, the parent's aggregated comment, or an author's adjudication is being written. Provides the parallel subagent eval design, its procedure, and its report shape.
layer: L2-evolution
---

<parallel-subagent-eval>

# Parallel Subagent Eval

Verification method that measures the AI's introspection gap (no empirical basis for predicting its own future invoke behavior or rule semantic effect) from the outside via the current behavior of subagents.

<trigger>

## Trigger

Fires at any of the following moments:

- Li+ rules/* or skills/* edit draft has converged outside a PR flow and verification is needed before it is carried into one
- evolution-loop observe / evaluate stage needs an empirical verdict
- Right after AI alone feels "this edit satisfies the spec" (catch overconfidence from N=1 self-check)
- Spec revision proposal needs orthogonal verification on the rule semantic consistency axis
- **Self-evolution PR brake (mandatory)**: any self-evolution PR runs this method. Which PRs those are is canonical in `rules/evolution/initiator-autonomy.md` Self-evolution PR definition — both of its conditions, neither alone — and is not restated here. This is brake 1 of the two-stage brake. Its firing moment is fixed rather than draft-driven — the delegated subagent's report at its stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition) — and the position rule is canonical in `rules/evolution/initiator-autonomy.md` Two-stage brake, not restated here. An L1 Model Layer source change additionally requires brake 2, the L1 root-criteria evaluator `adapter/claude/agents/l1-gate-eval.md` (see `rules/operations/execution-mode.md` L1 brake 2 override). semi_auto patch-auto-merge does not bypass brake 1.

Axis selection: the fixed axis (impression-literal detection, spec in `skills/evolution-impression-literal-detection/SKILL.md`) is always included for Li+ source drafts regardless of spec nature. Additional axes are selected per draft nature. Examples:
- skill description edit: ease of AI invoke judgment / maintainer-side readability / coverage gap
- rule body edit: behavior consistency across configured / not-configured paths / detect semantic conflict with adjacent rules / orthogonality against existing scope clauses

</trigger>

<design-dimensions>

## Design Dimensions

Three axes that move verification cost and detection power independently. Total subagent invocation count = `N x P`; M is absorbed inside each subagent prompt.

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

The one place this skill fixes a count as a threshold is the fixed axis (`skills/evolution-impression-literal-detection/SKILL.md` Aggregation), whose numbers come from the asymmetry of that judgment - over-trimming load-bearing spec phrasing is the costly error - not from counting votes. The per-judgment aggregation rule above is likewise selected from asymmetry; majority is not among its options.

</design-dimensions>

<procedure>

## Procedure

**Precondition**: source lives on a branch other than the merge target, and `.claude/` is in tag-match state (draft unapplied). On the brake 1 path that branch is the PR branch at the SHA the CI run went green on; on the other Trigger entries it is an experimental branch.

1. **Prepare draft** - Draft the edit content
2. **Apply operational copy (target-conditional)** - Apply only when the draft reaches the subagent's observation surface as injected context, which splits by target:
   - `rules/**/*.md` body IS injected, so the apply is mandatory. Skipping it leaves the pre-draft rule in injected context, where it outranks and shadows the freshly drafted intent
   - `skills/<name>/SKILL.md` body is NOT injected (description only, body lazy-loaded at invoke), so for a judge-type evaluator the apply changes nothing on the observation surface. Point the evaluator at the draft for direct Read instead. Exception: when the eval depends on the subagent *invoking* the skill (probe-type, body auto-loads at invoke), the apply IS required

   The apply is a parent-side write to `.claude/`; the source stays on its own branch and the evaluators spawned at step 3 read it there.
   - **Host permission-gate fallback**: an autonomous run without explicit user authorization can have the apply refused by the host self-modification gate. `skills/*` is off the observation surface, so it falls back to evaluator direct Read at the named SHA; record the deviation in the PR self-review. `rules/*` cannot be substituted that way, because injected context still shadows: re-run from a session that can apply, or record the deviation and flag reduced confidence for post-merge observation
3. **Parallel subagent spawn** - Select N, M, P per draft nature and spawn in parallel. Default `N=3, M=all axes, P=1`, total invocation = 3; switch to the M=1 exception pattern when the echo-bias condition in Constraint: Subagent prompt must be self-contained holds, or to P>1 when premise variation is needed (see Design Dimensions). Every spawn explicitly sets the Agent tool `model` parameter at or above the sonnet-class floor (see Constraint: Model floor).

   On the brake 1 path the material named in the prompt is the PR URL, the pushed commit SHA, and the green CI run URL — never a path inside the parent's clone, which would put every evaluator on a baseline any one of them can move. The reason that set is fixed is canonical in `rules/evolution/initiator-autonomy.md` Two-stage brake. The rule governs what the prompt *names*, so step 2's operational copy is unaffected: it reaches the evaluator as auto-injected context, not as a named path.

   Each per-draft axis goes into the prompt in the form fixed at Axis statement form; the fixed axis is outside that form's scope. Five more things go in alongside the axes and the material:
   - the no-write literal verbatim (see Constraint: Evaluator does not modify the evaluation target)
   - the retrieval commands, so the evaluator does not assume a clone is needed: `gh pr diff <n> --repo <owner>/<repo>` returns the diff and `gh api repos/<owner>/<repo>/contents/<path>?ref=<SHA>` returns any file body at that SHA
   - the allowance that an axis needing a repository-wide sweep clones into the evaluator's own working directory, which is off the shared surface. GitHub code search is unreliable on this repository (total hits 0), so the sweep has nowhere else to go
   - on the brake 1 path, the reporting destination: the evaluator returns its findings to the parent as its own report, all axes inside it, and writes nothing to the PR. No `gh pr comment` is run by an evaluator (Constraint: Findings route through the parent as one aggregated comment)
   - the shape that report is written in: findings at full length with a verbatim quote and its `path:line`, an axis with no finding at one line, and no echo of the criteria this prompt supplies (see Report shape). That sentence is what the prompt carries; the Report shape section behind it is the parent's reference, not prompt payload, since pasting the section would put back into the prompt the bulk this contract removes. The shape is a contract on the report, so leaving it to the evaluator's discretion is what puts every axis at finding length
4. **Aggregate findings and post** - Actor = the parent. Consolidate the N evaluators' reports into one PR comment and post it (`gh pr comment <n> --repo <owner>/<repo> --body ...`) — one comment for the whole eval, in the shape fixed at Report shape, Parent's aggregated comment. Post nothing when every axis on every report is clean: there is then nothing to adjudicate, the author is not resumed, and steps 6 to 8 have no input; the eval's record rests on the self-review at step 9.

   Consolidation is summary and merge — duplicate findings raised by more than one evaluator collapse into one entry carrying its ratio, and the surrounding prose is the parent's. It stops there. **The parent does not select among findings**: it does not drop one it disagrees with, does not rank them, and does not answer one. Accept / reject is the author's authority (Constraint: Adjudication actor), and a finding dropped at this step never reaches the actor holding that authority, which is the one way this step can silently decide what it is not entitled to decide
5. **Runtime restore** - Restore `.claude/` to tag-match state (revert the operational copy to pre-draft). Parent-side, as the apply at step 2 was. It runs as soon as every evaluator has returned its findings, and before the author is resumed: the copy exists for the evaluators' observation surface only, so it does not wait on step 6. Skipping it carries the draft into the parent session's behavior and leaves it there for subsequent sessions. Skip only when step 2 applied nothing (skills/* direct-Read path, or permission-gate fallback): no write occurred, so there is nothing to restore
6. **Aggregate verdict** - Actor = the resumed implementation subagent, not the parent (see Constraint: Adjudication actor). It reads the parent's aggregated comment and aggregates cross-axis judgment per the Design Dimensions aggregation rule. Fixed axes may override the default per-axis (see `skills/evolution-impression-literal-detection/SKILL.md` Aggregation). Where evaluators split on an axis, run Design Dimensions Divergence handling before the verdict is written
7. **Judgment** - Actor = the resumed implementation subagent. consistent -> nothing to apply; report back. partial / negative -> adjudicate each finding against the source, apply what was accepted, commit, push, and stop again at CI green. The accept / reject verdict on each finding and its reason go in the **commit body** (shape = Report shape, Author's adjudication); they are not posted as a PR comment. Or abort. **Single round**: steps 2-6 produce one verdict per draft, and the revised draft ships without re-verification (see Non-scope: what the single-round cap gives up). The author's response-and-revision pass is the tail of that one round, not a second one. What the cap refuses is a second audit of a draft already audited, so whether a re-run is that second audit is settled by what the round audited, never by why it stopped. A re-run continues the same round when both hold: (a) the verdicts that round returned have not reached the N>=3 floor (Constraint: N=1 prohibited, minimum N=3), and (b) the baseline it ran against — the PR commit SHA — is unchanged from the first attempt. Both, and neither alone: under the pair the re-run audits a draft nothing has audited yet, so it completes round 1 instead of opening round 2, and the cap is untouched. Verdicts already returned are carried into it rather than discarded — they measure the same draft. Cause is not a term here: a spend limit, an evaluator crash, a malformed prompt and a timeout are one thing under this criterion, a round that returned fewer than the floor, and sorting them is an after-the-fact self-report the cap cannot check. (a) is what refuses re-buying a verdict already obtained and disliked, relabelled as a failure; (b) is what refuses re-auditing the author's revision, which moves the SHA and is round 2 by definition — the cap's own target, left exactly as it was. Step 2's `rules/*` retry path is an instance of the pair, not an exception to it: a refused apply returns no verdict and moves no SHA. Its other two branches (`skills/*` direct-Read fallback, `rules/*` proceeding on a reduced-confidence deviation record) return a verdict and are unaffected. Ceiling: a third attempt against the same baseline that still has not reached the floor stops there and escalates to human, on `skills/model-loop-safety`'s task / debug three-attempt threshold applied as written — this skill states no number of its own
8. **Inspect the adjudication** - Actor = the parent, which holds the findings from step 4 and can therefore check what was done with them. Read the adjudication where it landed — the commit bodies from step 7, and the author's stop-condition report for an adjudication that produced no commit — and judge it against the findings as posted. Where it does not hold, resume the author again with the correction named; the author revises and stops again at CI green.

   **No cap is placed on these round trips.** They are not evaluator rounds: what the cap at step 7 fixes at one is the evaluator round spawned at step 3, and nothing here re-spawns an evaluator or re-opens an axis, so the cap is untouched in both directions. What governs convergence is `skills/model-loop-safety`, and **the parent is the actor holding that judgment**. Naming the actor is the load-bearing part — a two-party loop with the count unassigned is a loop where each side assumes the other is keeping it. Accepted with it: a round trip that names a different real defect each time is a switched axis, which Loop Safety's own scope clause places outside the safeguard. That is convergence work and is not to be stopped for being repetition; what the safeguard reaches is the same correction pressed again
9. **Externalize** - Record the verdict and the adoption judgment in the parent issue body / PR self-review, so the judgment survives the session. On the brake 1 path the findings are externalized as the aggregated comment at step 4 and the adjudication as the commit bodies at step 7; the self-review does not transcribe either, it reads them and records what they do not carry — the merge judgment over the eval, including whether a rejection left standing looks right, and the adjudication of a round that produced no commit at all, which has no commit body to sit in. That last item is why the self-review is brake 1's only guaranteed externalization: every other surface in this procedure is conditional on there being something to write to it. A reported count occupies its own field, separate from the adjudication and from the literal that adjudication rests on; do not write the count as the reason (see Design Dimensions, Ratio is a triage signal). If the judgment has settled, also append to decision structure per `skills/evolution-decision-structure-write`

</procedure>

<axis-statement-form>

## Axis statement form

Fixes the form each per-draft axis is written in — the set Trigger, Axis selection names with `Additional axes are selected per draft nature`, which the parent composes at spawn time. It applies at Procedure step 3, where those axes enter the prompt. The fixed axis is outside it: that axis's wording is not composed per run but held at `skills/evolution-impression-literal-detection/SKILL.md`, so the per-run authoring this section addresses does not reach it, and it enters the prompt as its own spec words it.

The gap it closes: the parent authors the instrument in the same moment it is reading the instrument's target literally, and the literal check that reaches the target does not reach the instrument. The recurring form is one axis name carrying more than one question — joined visibly, or compressed into a single predicate that reads as one.

Each axis ships as five labeled parts, all of them payload — they enter the evaluator's prompt as written, and none is a check whose output is discarded once it passes. A part left unwritten is therefore a missing label in the text the evaluator will read. Artifact visibility is the mechanism, and it stops short of the execution guarantee `rules/model/subtractive-structural-beauty.md` asks for when it requires a procedure be replaced by a structure. Relocating a dropped step to another surface as one more line to be remembered is not that structure either, which is why the visibility of the missing label is what this form rests on. Each part is a phrase, not a paragraph; the form fixes what an axis names, not how much of it there is.

- **Question** — one interrogative, and one only, and it names the operation that produces its verdict: what the evaluator does to the material, and which result of doing it is the finding. Two clauses joined by "and" or by a comma are two operations and so two axes: split them, or drop one. What is counted is operations, not clauses, because a predicate that names an evaluation instead of an operation — `forced`, `consistent`, `resolves wrongly` — carries its count hidden: each reading of it is a different thing to do, and the conjunction sits compressed inside the one word, where the joined-clause prohibition cannot reach it. Writing the operation is what decompresses it; the readings come apart into separate interrogatives while the axis is being written, and the prohibition then fires on them as on any other pair. An interrogative that names no operation is unfilled, not answerable: the evaluator cannot begin without supplying a reading of its own, and readings supplied independently are the split that arrives looking like disagreement. What that puts on the artifact is narrower than the blank label above, and the gap is stated rather than elided: a part left blank is absent to a reader applying nothing, while an evaluative predicate fills its part with ordinary prose and reads as missing only once the distinction is applied. What is gained is that it is applied to text present and quotable while the axis is being written, instead of recalled afterwards as a step. The residual — a predicate whose readings the author and all N evaluators happen to converge on, which emits no split and so no signal — is accepted on the post-merge observation axis, as this file's other not-guaranteed requirement already is (Non-scope). It must also be answerable in the order its material arrives — an axis cannot ask for a judgment formed before reading what the prompt itself carries.
- **Unit** — what a single verdict covers: a sentence, a paragraph, a file, a claim, an occurrence. Unstated, evaluators pick different ones and the resulting split reads as disagreement when nobody disagreed.
- **Scope** — the surface the axis ranges over: this PR's diff, one named file, the repository, the repository and the wiki. An axis whose verdict is an absence claim states what it swept, an absence being only as wide as what was read. Width has a second dimension besides extent, and the axis states both: the language its patterns are written in. This repository holds most normative text twice — English in `rules/` and `skills/` (`rules/model/liplus-coding-rule.md` Source Language), Japanese in `docs/`, which mostly mirrors them and in places is itself the source (`docs/5.-Notifications.md` declares its own body canonical, there being no `rules/notifications/` for it to mirror) — so a sweep ranging over the whole repository on English patterns alone never reached the Japanese side, and its absence claim is under-swept by construction rather than by oversight. The source-side case is the sharper one: it has no English counterpart for such a sweep to have hit instead. Extent alone does not carry this: a scope reading `the repository` is satisfied by such a sweep. Report shape asks the return leg for the patterns a sweep ran under (Evaluator report, axis with no finding); this is the same dimension on the authoring leg, where the width is required rather than reported.
- **Verdict terms** — what a yes and a no mean here, in this axis's own words. Design Dimensions' aggregation vocabulary is about the judgment on the draft, so on an axis asking "did anything drop?" a finding answers yes while being negative for the draft; an axis that does not name its own polarity inherits the wrong one. This is the part Report shape presumes when it asks a clean axis for the verdict in that axis's own terms.
- **Basis** — every statement the axis makes about the target or about the criteria carries a pointer that resolves at the named SHA: the criterion at its `path`, or quoted with `path:line`; an illustrative example quoted from where it actually occurs rather than composed to look like one; and, where the answer turns on how many of something there are, the body to count from instead of a number. What this excludes is assertion from the parent's memory of a body the parent itself authored — the gist read this form exists to cut. Resolvability is the property the return leg already rests on (Report shape, What the pointer carries on a clean axis). The part is not satisfied by form alone: whatever the verdict has to be formed against — an existing Li+ criterion the axis is judging by, or an argument the parent is relying on — is written inside every axis that needs it, not once for the set, because an axis does not inherit what was written next to it. An axis that names no basis is unfilled, not clean.

### Where this meets the post-hoc check

Design Dimensions, Divergence handling asks the same-question check after the eval; Question above asks it before the spawn. Neither replaces the other. The post-hoc check catches the axis whose parts were filled but filled loosely, and it keeps working on axes worded before this form existed. What moves is where its No lands: on the part of this form that did not hold, a surface that persists, instead of on the next run's framing, which persists nowhere and lets the same gap reopen on the run after it.

</axis-statement-form>

<report-shape>

## Report shape

Fixes the form of the three artifacts brake 1 produces — the evaluator's report at Procedure step 3, the parent's aggregated comment at Procedure step 4, and the author's adjudication at Procedure step 7. All are asymmetric on the same seam: the side carrying a finding is written at full length, the side nobody contests at one line. Left unfixed, each actor composes the form per run and every axis is written at finding length. What this section fixes is delivery: it does not change which axes are asked (Trigger, Axis selection), how many evaluators answer them (Constraint: N=1 prohibited, minimum N=3), or how the answers aggregate (Design Dimensions).

Scope = the brake 1 path. brake 2 is out: its evaluator has its own prompt file and returns a verdict inline (`adapter/claude/agents/l1-gate-eval.md`). On the other Trigger entries there is no PR surface, so the step 4 comment has no counterpart, and the asymmetry still governs what the evaluator writes — the reasoning below turns on who adjudicates a line, not on where the line ends up.

### Evaluator report

- **Axis with a finding**: the verbatim quote of the literal at issue, its `path:line` at the named SHA, and why it is a defect. Full length, and not a compression target — the author adjudicates against that quote and would otherwise re-fetch the source once per finding, and a defect asserted without hitting the literal is the shape `rules/model/trigger-check-gate.md` Literal check stands against.
- **Axis with no finding**: one line — the axis name, the verdict in that axis's own terms, and the `path:line` the verdict rests on. An axis answered by a repository-wide sweep has no single line to name: give the sweep in re-runnable form (the pattern, and the paths it ran over) and its hit count. No quote.
- **Prohibited on both sides**: restating the criteria, thresholds, or axis wording the parent supplied in the prompt. Both readers already hold that text — the parent wrote it, and the author reads it where the parent copied it from — so a restatement is a second copy of it, and the second copy is what drifts.

### Parent's aggregated comment

- **A finding** keeps the full form it arrived in: the verbatim quote, its `path:line`, and why it is a defect. Compressing it here would push the re-fetch onto the author, which is the cost the full-length rule above exists to remove; consolidation earns its place by removing duplication across evaluators, not by shortening a finding. Duplicates collapse into one entry stating how many of the N raised it.
- **Clean axes** carry their one line through as well. The author aggregates cross-axis at Procedure step 6, and a comment listing only findings leaves it aggregating over a denominator it cannot see.
- **Prohibited**: an accept, a reject, a ranking, or a recommendation. Those are the author's at Procedure step 7, and prose that leans on a finding here arrives ahead of the actor entitled to weigh it.
- **Language**: the parent writes this comment and resolves `Workspace_Language_Contract` (`adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md`) for it as it does for anything else it writes, so nothing about resolving it is stated here. What is stated is the one seam resolution does not settle: a verbatim quote and its `path:line` stay as the source has them. The author adjudicates against the literal and a translated literal is not the literal. Li+ source is English (`rules/model/liplus-coding-rule.md` Source Language), so in a workspace resolving to any other language this comment is mixed by construction — quotes in the source's language inside prose in the resolved one. Left unstated the pair collapses one way or the other: the quotes get translated with the prose, or the prose falls back to the quotes' language. A clean axis carries no quote, so its one line is prose and a pointer, and a pointer is not prose.

### Author's adjudication

Destination = the commit body of the commit that applies what was accepted (`rules/operations/operations.md` fixes what else a commit body carries; this rides alongside it). Not a PR comment.

- **Reject**: full. The reason is what the parent reads at Procedure step 8, and under the single-round cap no evaluator re-argues it, so nothing else stands behind it.
- **Accept**: one line — which finding, and what changed. The change itself is already externalized in the diff of the same commit; prose restating it is a second copy of the same content for the parent to reconcile against the first.
- **When nothing was accepted** there is no commit, so there is no commit body: the adjudication goes to the parent in the author's stop-condition report, and the parent carries it into the self-review at Procedure step 9. This is the one branch where the reasoning lands in a durable artifact written by someone other than its author, and it is the reason step 9 is described there as the only guaranteed externalization.

### What the pointer carries on a clean axis

Dropping the quote there narrows the gap between "inspected and found clean" and "declared clean without inspecting", and the `path:line` is what is left holding it. It holds because it resolves: named at the SHA, it can be opened, and a pointer that does not resolve — or resolves to something the verdict does not fit — fails at one lookup. The quote's advantage over it is that the same check costs nothing, which is worth its bulk only where a line is adjudicated repeatedly, and that is the finding side, where the quote stays.

An axis answered by a sweep has no line to open, which is why the Evaluator report clean-axis bullet substitutes the sweep itself: an absence claim is checked by re-running, not by opening, so what the pointer does there is done by a sweep stated re-runnably — a hit count that does not reproduce fails the way an unresolvable pointer fails. The scope it ran over stays the evaluator's own statement either way.

Residual = a clean axis whose pointer nobody opens, and a pointer picked after the verdict to fit it; accepted, on the post-merge observation axis the fixed axis's all-3-miss case already uses (`skills/evolution-impression-literal-detection/SKILL.md` False-negative backstop).

</report-shape>

<constraint>

## Constraint

- **N=1 prohibited, minimum N=3**: One trial is the source of overconfidence — a conclusion positive at N=1 reverses under independent sampling. The floor's basis is sample count, not axis layout, so it holds unchanged across M configurations. Reference Design Dimensions' `subagent_count` for N and run at minimum 3
- **Model floor = sonnet-class, explicit per spawn**: Every subagent spawned under this skill, on the mandatory brake 1 path or any other Trigger entry, explicitly sets the Agent tool `model` parameter. Implicit parent-model inheritance is prohibited: a sub-floor parent silently lowers the evaluation floor. Default and floor = `sonnet`; a higher-class id (`opus`, `fable`) may be named but is not the default. `haiku` is prohibited as below floor. An id that cannot be positively classified as sonnet-class or above (unlisted, future, or versioned id of uncertain class) must not be passed; on doubt, fall back to the literal `sonnet`. Fix the floor per call, not via custom-agent frontmatter `model:` pinning — judge-type (answers axis questions) and probe-type (the vanilla subagent's current behavior is itself the observation target) coexist here, and an agent file body replaces the subagent's system prompt = identity, mutating the probe-type observation target. The per-call parameter changes neither context nor identity. The N=3 floor is a separate axis and is unaffected by the model tier. `skills/task-subagent-spawn/SKILL.md` Subagent Model Policy carries the purpose split that scopes this requirement to brake evaluators only
- **Subagent prompt must be self-contained**: Do not let parent context leak in. In the default M=all axes pattern, the prompt explicitly instructs each axis to "answer independently without referencing other axes' answers" to suppress cross-axis echo bias. If prompt complexity is high enough that the mitigation is uncertain, fall back to the M=1 axis-separated pattern (see Design Dimensions)
- **Evaluator does not modify the evaluation target**: An evaluator that rewrites the source mid-eval moves the baseline under its concurrent evaluators, which then report defects that do not exist. The evaluator keeps its tool permissions (brake 1 spawns `general-purpose`, which holds Edit / Write / Bash), so the requirement is carried by the prompt rather than by the tool set (the rejected alternative is in Non-scope). Copy this literal into every brake 1 evaluator prompt verbatim; do not re-compose it per spawn:

  > Do not modify the evaluation target. Do not edit, write, commit, or push anything in the repository under evaluation, and do not run its build, tests, formatter, or any other command that mutates it. Do not post to the PR. Read the PR diff and the file bodies at the named commit SHA, and return your findings in your report. If an axis looks like it needs a change applied before it can be answered, report that as a finding instead of applying it.

  This literal and the material rule at Procedure step 3 are applied together: the literal cuts the intent to write, and naming no shared path removes the shared target itself. The literal carries no carve-out: the PR is not a destination the evaluator has under the routing at Procedure step 4, so `Do not post to the PR` states the reporting destination in the negative rather than opening a question about whether a comment counts as a modification. brake 2 does not take this bullet — `adapter/claude/agents/l1-gate-eval.md` declares `tools: Read`, its Codex port declares `sandbox_mode = "read-only"`, and its input (L1 diff + stated reason) is passed inline, so no repository target is named to it
- **Findings route through the parent as one aggregated comment**: on the brake 1 path the evaluator returns its findings to the parent and writes nothing to the PR; the parent consolidates them and posts one comment (Procedure steps 3 and 4). The parent carries the findings deliberately, and what that buys is supervision — holding them is what lets it inspect the author's adjudication at Procedure step 8 and name a correction, which a parent that never read a finding cannot do. The write shape is the second thing it buys: N evaluators posting to one PR within seconds is a burst against the host's content-generating limit, and one comment from one actor is not. brake 2 needs no exemption from this bullet and is unchanged by it: its evaluator holds `tools: Read` and takes its input inline, so its verdict has always returned to the parent
- **Adjudication actor = the resumed implementation subagent**: the author of the change adjudicates the findings, resumed with its implementation context intact, and the parent retains self-review and the merge decision. Canonical statement, including why the always-delegate rule loses a branch rather than gaining an exception, is `rules/evolution/initiator-autonomy.md` Two-stage brake, Adjudication actor. Do not restate the reasoning here. Two boundaries carry into the resume prompt: the resumed author neither runs nor posts the self-review, and it does not merge (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary)
- **Character_Instance non-inheritance**: What gets injected into subagent context = `CLAUDE.md` + `.claude/rules/**/*.md` (full body) + `.claude/skills/*/SKILL.md` (description only, body lazy-loaded at invoke) + MEMORY.md + harness-level system-reminders. `.claude/output-styles/`, hook firing output (SessionStart / UserPromptSubmit, etc.), and `.claude/settings.json` itself do not reach the subagent. `.claude/hooks/*.sh` script bodies are readable via the Read tool but not auto-loaded. When character behavior is part of the verification target, explicitly inject the Character_Instance body into the step 3 prompt. Running the character axis without injection produces the hollow prefix sleeping bug: persona absent, only the Character Instance name string generated

</constraint>

<non-scope>

## Non-scope

- This method is a pre-spec-reflection verification surface; it does not replace PR review (semi_auto mode minor/major human review is a separate axis)
- Verification of facts that change over time (API spec, library behavior) is outside this method's range; investigate per occurrence
- Evaluator tool permissions are not restricted. The custom-agent `tools:` route (what brake 2 runs on) is rejected for brake 1: the agent file body replaces the subagent system prompt, so the tool set cannot be narrowed without also replacing the probe-type identity the Constraint model floor protects, and `tools:` cannot express read-only for brake 1 anyway because its retrieval path needs Bash. The no-write requirement therefore rests on a prompt literal the parent has to remember to include, which `rules/model/subtractive-structural-beauty.md` places on the not-guaranteed side of its procedure-vs-structure judgment. Accepted; recurrence is tracked on the post-merge axis per `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format

### What the single-round cap gives up

Procedure step 7 caps the eval at one round. Three defect classes are dropped by that cap. They are enumerated here so a later reader reads them as dropped, not missed — read as an unfixed-bug list, they invite someone to restore the rounds without going through the re-evaluation trigger:

- Defects introduced by the adjudicator's own fix, the adjudicator being the resumed author under the current actor split. Test coverage is the receptacle for the behavior-defect subset.
- Prose-layer findings that surface only in later rounds, such as a still-live description deleted during a rewrite. Tests do not catch this class.
- Behavior defects present in the initial implementation that round 1 did not reach, such as chunk-boundary multibyte corruption or a spec category missing from an enumeration.

Accepted on the Li+ correctness criterion (`rules/model/foundational-invariant.md`: correctness is real-world behavior): the three are dropped against a round cost incurred every time, and the acceptance holds while none of them reaches production. Changes stay inside git revert range and release remains a human gate. Re-evaluation trigger = a single-round-capped merge that produces observable production harm.

The first class is partly reached again by Procedure step 8, which puts a reader on the adjudicator's fix without spawning an evaluator. Partly, and stated so the list is not read as longer than it is: that reader is the parent, checking the adjudication against findings it already holds, not the N=3 outside measurement this method exists to obtain. The other two classes need an axis re-run and stay dropped.

</non-scope>

<boundary>

## Boundary

- **`skills/evolution-loop/SKILL.md`**: This skill is referenced inside the loop's observe / evaluate stage. The loop side "calls this method"; the method body lives here
- **`skills/evolution-l1-update-gating/SKILL.md`**: Authorization axis for L1 source changes (long-horizon observation requirement), orthogonal to this empirical verification axis and expected to be used alongside it. In the `Evolution_Initiator_Autonomy` framing, this method is brake 1 (always-on for self-evolution PRs) and the L1 root-criteria evaluator is brake 2 (L1-only, layered on top)
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

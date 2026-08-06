---
name: evolution-parallel-agent-eval
description: Invoke when a self-evolution PR reaches CI green and the merge gate is next (mandatory brake 1) / a Li+ rules or skills or adapter edit draft has converged outside a PR flow and needs verification before entering one / an evolution-loop observe or evaluate stage needs an empirical verdict / an N=1 self-check on an edit feels positive and needs outside measurement / a spec revision proposal needs orthogonal verification on rule semantic consistency. Provides parallel subagent eval (default: N=3 subagents each answering all observation axes; aggregation chosen per the asymmetry of the judgment under eval), catching introspection-gap-driven overconfidence: the N, M and P design dimensions, the 7-step procedure with operational copy apply and restore, the findings-to-PR-comment routing that puts adjudication on the resumed author, the N=3 and model floors, the single-round cap, the divergence handling pair (same-question, then why-diverged) and the rule that a ratio is a triage signal, not a judgment input.
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
- **Self-evolution PR brake (mandatory)**: any self-evolution PR (per `Evolution_Initiator_Autonomy` definition: AI-filed issue + AI implementation + modifies Li+ source under `LI_PLUS_REPO`) runs this method. This is brake 1 of the two-stage brake. Its firing moment is fixed rather than draft-driven — the delegated subagent's report at its stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition) — and the position rule is canonical in `rules/evolution/initiator-autonomy.md` Two-stage brake, not restated here. An L1 Model Layer source change additionally requires brake 2, the L1 root-criteria evaluator `adapter/claude/agents/l1-gate-eval.md` (see `rules/operations/execution-mode.md` L1 brake 2 override). semi_auto patch-auto-merge does not bypass brake 1.

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

Answers go on the PR alongside the author's answers to the findings themselves, the surface the fixed axis's 1-of-3 flag already uses; the parent reads them there at Procedure step 7. No new record surface. Neither outcome gates the merge on its own: a criteria gap from question 2 is routed like any other spec-gap observation (`rules/evolution/promotion-judgment.md`), and an axis-wording finding from question 1 is a note on how this eval was framed, carried into how the next one words that axis. Stating this for one branch and not the other would put the pressure back where the paragraph above removes it.

### Ratio is a triage signal

The ratio of evaluators reporting a finding (3/3, 2/3, 1/3) is a cheap prior on where to spend verification effort first. It is not a judgment input. The verdict on a finding comes from checking its literal against the source: a 1/3 finding that holds up is adopted, and a 3/3 finding that does not is dropped. The ratio is kept rather than discarded because verifying every finding at equal cost is not practical and the parent's own literal check is not infallible either. Reporting form is fixed at Procedure step 7.

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

   Four things go into the prompt alongside the material:
   - the no-write literal verbatim (see Constraint: Evaluator does not modify the evaluation target)
   - the retrieval commands, so the evaluator does not assume a clone is needed: `gh pr diff <n> --repo <owner>/<repo>` returns the diff and `gh api repos/<owner>/<repo>/contents/<path>?ref=<SHA>` returns any file body at that SHA
   - the allowance that an axis needing a repository-wide sweep clones into the evaluator's own working directory, which is off the shared surface. GitHub code search is unreliable on this repository (total hits 0), so the sweep has nowhere else to go
   - on the brake 1 path, the reporting destination: the evaluator posts its own findings as one PR comment (`gh pr comment <n> --repo <owner>/<repo> --body ...`, one comment per evaluator, all axes inside it) and returns **one line** to the parent — the URL of the comment it posted, or, if the post failed, the reason in the same one line. Nothing else goes back. The findings are the heavy read and they belong to the author who will adjudicate them (Constraint: Findings route to the PR, not to the parent)
4. **Aggregate verdict** - Actor = the resumed implementation subagent, not the parent (see Constraint: Adjudication actor). It reads the evaluators' PR comments and aggregates cross-axis judgment per the Design Dimensions aggregation rule. Fixed axes may override the default per-axis (see `skills/evolution-impression-literal-detection/SKILL.md` Aggregation). Where evaluators split on an axis, run Design Dimensions Divergence handling before the verdict is written
5. **Runtime restore** - Restore `.claude/` to tag-match state (revert the operational copy to pre-draft). Parent-side, as the apply at step 2 was. It runs as soon as every evaluator has returned its one line, and before the author is resumed: the copy exists for the evaluators' observation surface only, so it does not wait on step 4. Skipping it carries the draft into the parent session's behavior and leaves it there for subsequent sessions. Skip only when step 2 applied nothing (skills/* direct-Read path, or permission-gate fallback): no write occurred, so there is nothing to restore
6. **Judgment** - Actor = the resumed implementation subagent. consistent -> nothing to apply; report back. partial / negative -> adjudicate each finding against the source, answer it on the PR with an accept or a reject and the reason, apply what was accepted, commit, push, and stop again at CI green. The parent then self-reviews the resulting thread. Or abort. **Single round**: steps 2-4 produce one verdict per draft, and the revised draft ships without re-verification (see Non-scope: what the single-round cap gives up). The author's response-and-revision pass is the tail of that one round, not a second one. The cap does not block step 2's `rules/*` retry path, and that path only: there, a refused apply leaves the round with no verdict, so re-running from a session that can apply IS the round, not a re-verification of it. Do not generalize this to any round that failed to produce a verdict — an evaluator crash, a malformed prompt, or a timeout does not earn a fresh round. Its other two branches (`skills/*` direct-Read fallback, `rules/*` proceeding on a reduced-confidence deviation record) produce a verdict and are unaffected
7. **Externalize** - Record the verdict and the adoption judgment in the parent issue body / PR self-review, so the judgment survives the session. On the brake 1 path the findings and the accept / reject answers are already externalized as the PR comment thread at steps 3 and 6; the self-review does not transcribe them, it reads them and records what the thread does not carry — the merge judgment over it, including whether a rejection left standing looks right. A reported count occupies its own field, separate from the adjudication and from the literal that adjudication rests on; do not write the count as the reason (see Design Dimensions, Ratio is a triage signal). If the judgment has settled, also append to decision structure per `skills/evolution-decision-structure-write`

</procedure>

<constraint>

## Constraint

- **N=1 prohibited, minimum N=3**: One trial is the source of overconfidence — `#1296` observed the conclusion reverse from N=1 positive to N=3 = 1 positive + 2 partial-negative. That evidence was gathered under the M=1 axis-separated exception pattern with 3-axis OR aggregation, not under today's M=all-axes default; the N=3 floor carries over unchanged because its basis is sample count, not axis layout. Do not read the two configurations as the same one. Reference Design Dimensions' `subagent_count` for N and run at minimum 3
- **Model floor = sonnet-class, explicit per spawn**: Every subagent spawned under this skill, on the mandatory brake 1 path or any other Trigger entry, explicitly sets the Agent tool `model` parameter. Implicit parent-model inheritance is prohibited: a sub-floor parent silently lowers the evaluation floor. Default and floor = `sonnet`; a higher-class id (`opus`, `fable`) may be named but is not the default. `haiku` is prohibited as below floor. An id that cannot be positively classified as sonnet-class or above (unlisted, future, or versioned id of uncertain class) must not be passed; on doubt, fall back to the literal `sonnet`. Fix the floor per call, not via custom-agent frontmatter `model:` pinning — judge-type (answers axis questions) and probe-type (the vanilla subagent's current behavior is itself the observation target) coexist here, and an agent file body replaces the subagent's system prompt = identity, mutating the probe-type observation target. The per-call parameter changes neither context nor identity. The N=3 floor is a separate axis and is unaffected by the model tier. `skills/task-subagent-spawn/SKILL.md` Subagent Model Policy carries the purpose split that scopes this requirement to brake evaluators only
- **Subagent prompt must be self-contained**: Do not let parent context leak in. In the default M=all axes pattern, the prompt explicitly instructs each axis to "answer independently without referencing other axes' answers" to suppress cross-axis echo bias. If prompt complexity is high enough that the mitigation is uncertain, fall back to the M=1 axis-separated pattern (see Design Dimensions)
- **Evaluator does not modify the evaluation target**: An evaluator that rewrites the source mid-eval moves the baseline under its concurrent evaluators, which then report defects that do not exist. The evaluator keeps its tool permissions (brake 1 spawns `general-purpose`, which holds Edit / Write / Bash), so the requirement is carried by the prompt rather than by the tool set (the rejected alternative is in Non-scope). Copy this literal into every brake 1 evaluator prompt verbatim; do not re-compose it per spawn:

  > Do not modify the evaluation target. Do not edit, write, commit, or push anything in the repository under evaluation, and do not run its build, tests, formatter, or any other command that mutates it. Read the PR diff and the file bodies at the named commit SHA. If an axis looks like it needs a change applied before it can be answered, report that as a finding instead of applying it. Posting your findings as a PR comment is required and is not a modification: the comment is a record about the target, not the target itself.

  This literal and the material rule at Procedure step 3 are applied together: the literal cuts the intent to write, and naming no shared path removes the shared target itself. The PR-comment carve-out inside the literal is not a hole in it — a comment changes nothing any concurrent evaluator reads, which is the property this constraint protects; a commit does. brake 2 does not take this bullet — `adapter/claude/agents/l1-gate-eval.md` declares `tools: Read`, its Codex port declares `sandbox_mode = "read-only"`, and its input (L1 diff + stated reason) is passed inline, so no repository target is named to it
- **Findings route to the PR, not to the parent**: on the brake 1 path the evaluator's findings go to a PR comment and its return to the parent is one line (Procedure step 3). The parent is not the reader of findings under this skill, so routing them through its context buys nothing and costs the most expensive context in the run. brake 2 is exempt for a structural reason, not a graded one: its evaluator holds `tools: Read` and takes its input inline, so it has no PR surface to post to and its verdict returns to the parent as before
- **Adjudication actor = the resumed implementation subagent**: the author of the change adjudicates the findings, resumed with its implementation context intact, and the parent retains self-review and the merge decision. Canonical statement, including why the always-delegate rule loses a branch rather than gaining an exception, is `rules/evolution/initiator-autonomy.md` Two-stage brake, Adjudication actor. Do not restate the reasoning here. Two boundaries carry into the resume prompt and are the recurring failure surface (#1628): the resumed author neither runs nor posts the self-review, and it does not merge (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary)
- **Character_Instance non-inheritance**: What gets injected into subagent context = `CLAUDE.md` + `.claude/rules/**/*.md` (full body) + `.claude/skills/*/SKILL.md` (description only, body lazy-loaded at invoke) + MEMORY.md + harness-level system-reminders. `.claude/output-styles/`, hook firing output (SessionStart / UserPromptSubmit, etc.), and `.claude/settings.json` itself do not reach the subagent. `.claude/hooks/*.sh` script bodies are readable via the Read tool but not auto-loaded. When character behavior is part of the verification target, explicitly inject the Character_Instance body into the step 3 prompt. Running the character axis without injection produces the hollow prefix sleeping bug: persona absent, only the Character Instance name string generated

</constraint>

<non-scope>

## Non-scope

- This method is a pre-spec-reflection verification surface; it does not replace PR review (semi_auto mode minor/major human review is a separate axis)
- Verification of facts that change over time (API spec, library behavior) is outside this method's range; investigate per occurrence
- Evaluator tool permissions are not restricted. The custom-agent `tools:` route (what brake 2 runs on) is rejected for brake 1: the agent file body replaces the subagent system prompt, so the tool set cannot be narrowed without also replacing the probe-type identity the Constraint model floor protects, and `tools:` cannot express read-only for brake 1 anyway because its retrieval path needs Bash. The no-write requirement therefore rests on a prompt literal the parent has to remember to include, which `rules/model/subtractive-structural-beauty.md` places on the not-guaranteed side of its procedure-vs-structure judgment. Accepted; recurrence is tracked on the post-merge axis per `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format

### What the single-round cap gives up

Procedure step 6 caps the eval at one round. Three defect classes are dropped by that cap. They are enumerated here so a later reader reads them as dropped, not missed (#1563) — read as an unfixed-bug list, they invite someone to restore the rounds without going through the re-evaluation trigger:

- Defects introduced by the parent's own fix. Observed at PR #1560 G2 and PR #1555 R2 / R3. `#1562` test coverage is the receptacle for the behavior-defect subset.
- Prose-layer findings that surface only in later rounds. Observed at PR #1550 R4 (a still-live description deleted during a rewrite). Tests do not catch this class.
- Behavior defects present in the initial implementation that round 1 did not reach. Observed at PR #1543 R3 (chunk-boundary multibyte corruption) and PR #1533 R2 (a spec category missing from an enumeration).

Accepted on the Li+ correctness criterion (`rules/model/foundational-invariant.md`: correctness is real-world behavior): none of the three had surfaced in production, while the round cost was incurred every time. Changes stay inside git revert range and release remains a human gate. Re-evaluation trigger = a single-round-capped merge that produces observable production harm.

</non-scope>

<boundary>

## Boundary

- **`skills/evolution-loop/SKILL.md`**: This skill is referenced inside the loop's observe / evaluate stage. The loop side "calls this method"; the method body lives here
- **`skills/evolution-l1-update-gating/SKILL.md`**: Authorization axis for L1 source changes (long-horizon observation requirement), orthogonal to this empirical verification axis and expected to be used alongside it. In the `Evolution_Initiator_Autonomy` framing, this method is brake 1 (always-on for self-evolution PRs) and the L1 root-criteria evaluator is brake 2 (L1-only, layered on top)
- **`rules/evolution/promotion-judgment.md`**: Noise floor observation judgment (memory cluster tally) is observation accumulation; this method is spec verification immediately before implementation. Orthogonal
- **`skills/task-subagent-delegation/SKILL.md`**: This method's subagent spawn is a special case of delegation (purpose: gather evaluation data, not delegate implementation). This skill's N / M / P width (Design Dimensions) is exempt from the 5-in-flight cap in `skills/task-subagent-spawn/SKILL.md` Parallel-Width Cap — a P=2 run reaches 6 and is still within spec. The exemption is stated here as well because that cap's value reaches every context through its skill's description while the exemption itself sits in that skill's lazily-loaded body
- **`skills/evolution-decision-structure-write/SKILL.md`**: Judgment record surface for Procedure step 7

</boundary>

<implementation-note>

## Implementation Note

Subagent spawn goes through the host's Agent tool (Claude Code: `Agent` tool; Codex: equivalent mechanism). Parallel execution = multiple Agent tool calls in a single message. subagent_type is selected per task (typically general-purpose).

On hosts without a per-call `model` parameter, verify the session model satisfies the sonnet-class floor before spawning; a session model that cannot be positively classified as sonnet-class or above counts as sub-floor and cannot satisfy brake 1. Run the eval from a floor-satisfying session instead.

</implementation-note>

</parallel-subagent-eval>

---
name: evolution-parallel-agent-eval
description: Invoke when verifying a Li+ rules/*, skills/*, or adapter/* edit before commit/merge, when evolution-loop observe/evaluate needs an empirical verdict, or when N=1 self-check on an edit feels positive — parallel subagent eval (default: N=3 subagents each answering all observation axes, safer-side OR aggregation) catches introspection-gap-driven overconfidence.
layer: L2-evolution
---

<parallel-subagent-eval>

# Parallel Subagent Eval

Verification method that measures the AI's introspection gap (no empirical basis for predicting its own future invoke behavior or rule semantic effect) from the outside via the current behavior of subagents.

<trigger>

## Trigger

Fires at any of the following moments:

- Li+ rules/* or skills/* edit draft has converged and verification is needed before the commit/merge gate
- evolution-loop observe / evaluate stage needs an empirical verdict
- Right after AI alone feels "this edit satisfies the spec" (catch overconfidence from N=1 self-check)
- Spec revision proposal needs orthogonal verification on the rule semantic consistency axis
- **Self-evolution PR brake (mandatory)**: any self-evolution PR (per `Evolution_Initiator_Autonomy` definition: AI-filed issue + AI implementation + modifies Li+ source under `LI_PLUS_REPO`) runs this method before the commit/merge gate. This is brake 1 of the two-stage brake. L1 Model Layer source change additionally requires the L1 root-criteria evaluator `adapter/claude/agents/l1-gate-eval.md` (brake 2; see `rules/operations/execution-mode.md` L1 brake 2 override). semi_auto patch-auto-merge does not bypass brake 1.

Axis selection: a fixed axis (impression-literal detection, see below) is always included for Li+ source drafts regardless of spec nature. Additional axes are selected per draft nature. Examples:
- skill description edit: ease of AI invoke judgment / maintainer-side readability / coverage gap
- rule body edit: behavior consistency across configured / not-configured paths / detect semantic conflict with adjacent rules / orthogonality against existing scope clauses

</trigger>

<design-dimensions>

## Design Dimensions

Three axes that move verification cost and detection power independently:

- **`subagent_count (N)`** - Independent sample count. Obtain N independent evaluations per observation axis. Robustness against probabilistic variance.
- **`axes_per_subagent (M)`** - Number of observation axes each subagent answers within its prompt. Blind-spot coverage.
- **`premise_variations (P)`** - Number of ablation premises (e.g. full rule exclusion / partial exclusion). Robustness against premise variation.

The three axes are independently configurable. Total subagent invocation count = `N x P` (M is absorbed inside each subagent prompt).

### Default pattern (delete/keep judgment, etc.)

`N=3, M=all axes, P=1` - 3 subagents independently answer all M axis questions against the same ablation output. aggregation = safer-side OR (if even one axis returns a load-bearing signal, fall toward "keep"). N=3 samples are collected per axis, capturing blind-spot coverage and variance robustness simultaneously. Total invocation = 3.

### Exception pattern: M=1 axis-separated

Adopt only when per-axis prompt complexity is high enough that cross-axis echo bias cannot be suppressed inside a single subagent context. `N=3, M=1, P=1`, one axis per subagent. Total invocation = `N x axis_count`.
The original #1296 empirical demonstration (axis A: ease of invoke judgment / axis B: maintainer readability / axis C: coverage) is retained as the canonical instance of this pattern.

### Premise variations (P > 1)

Use only when comparing multiple ablation premises directly. Total invocation = `N x P` (within each premise, M is absorbed into the prompt as in the default pattern).

The representative case is the P=2 before/after pattern: premise A = pre-change (operational copy unapplied = baseline), premise B = post-change (draft applied = candidate) are placed as separate premises, and the subagent's behavior under the same prompt is compared directly before and after the change. Trigger = a Li+ source revision where the question "did the subagent verdict shift before vs after draft application on the same question?" needs to be pinned down empirically. Cost is `N=3, P=2 -> 6 invocation` (double the default `N=3, P=1 -> 3 invocation`).

### aggregation rule

Choose based on the asymmetry of the judgment:
- delete/keep binary where erroneous deletion is costly -> safer-side OR (if any axis detects effect, "keep")
- adopt/reject binary where erroneous adoption is costly -> require unanimous agreement (AND)
- intermediate -> three-value classification: consistent / partial / negative (the legacy #1296 pattern)

</design-dimensions>

<impression-literal-detection-axis>

## Fixed axis: impression-literal detection

For Li+ source drafts (`rules/*` / `skills/*` / `adapter/*`), impression-literal detection is a fixed axis included alongside the spec-nature axes selected per draft. It covers content-independent rhetorical drift at the post-write pre-merge surface, distinct from `rules/model/trigger-check-gate.md` Frame check (pre-judgment surface protecting dialogue).

Operational criterion: a phrase is impression literal if removing it does not change the rule's behavior semantic. Rhetorical layer that does not load-bear on the spec's behavior regulation is the detection target.

Positive (detection target):
- Push surplus phrases per `rules/model/subtractive-structural-beauty.md` Detection signs ("just in case", "as insurance", "as a safety net", "as comfort", "for completeness", "for future reference", "you might also want to consider").
- Rhetorical evaluation of result state ("leaves only X", "earns nothing but X", "provides only X").
- Emotional-load adjectives written into spec literal ("comfort", "reassurance", "satisfaction").
- Borrowed vocabulary from external framing without explicit referent.

Negative (protected, NOT detection target):
- Behavior literals: "prohibited", "required", "must", "fires", "applies".
- Established Li+ structural vocabulary: "load-bearing", "surface", "axis", "layer", "substrate".
- Detection signs / tells enumerations themselves (the body of `subtractive-structural-beauty.md` Detection signs is itself a load-bearing observation surface — protected, not over-applied recursively).
- Quotes with explicit referent (literal source citation with path).
- Explanatory rationale that prevents a known misinterpretation (e.g. justifying a non-default threshold). Protected when removing it would invite future revision-by-impression; impression literal only when removal leaves both the behavior semantic and the revision stability unchanged.

Test: can this sentence be removed without changing the rule's behavior semantic? Yes → impression literal.

Aggregation (narrower than the default safer-side OR):
- 2 or more of N=3 flag the same literal → refine immediately.
- 1 of N=3 flags → append the flagged literal to the PR self-review comment per Procedure step 7; do not auto-refine.

False-negative backstop: all-3-miss cases route to post-merge observation per `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format (2-week cycle). Post-merge drift surfacing is on a separate axis from this pre-merge detection.

Rationale: behavior-vs-impression boundary is context-dependent, so N=1 flag carries false-positive risk. The threshold prevents over-trimming load-bearing L1 spec phrasing.

</impression-literal-detection-axis>

<procedure>

## Procedure

**Precondition**: source lives on an experimental branch, and `.claude/` is in tag-match state (draft unapplied). When character behavior is part of the verification target, the step 3 subagent prompt must explicitly inject the Character_Instance body (see Constraint).

1. **Prepare draft** - Draft the edit content
2. **Apply operational copy (target-conditional)** - Apply only when the draft reaches the subagent's observation surface as injected context. `rules/**/*.md` body IS injected (full body), so the operational copy MUST be applied or the injected pre-draft rule shadows the draft (stale injected context shadows the draft: any pre-draft copy still present in context outranks the freshly drafted intent). `skills/<name>/SKILL.md` body is NOT injected (description only, body lazy-loaded at invoke), so for a judge-type evaluator the apply changes nothing on the observation surface — pass the draft path (experimental-branch worktree) for direct Read instead of applying. Exception: when the eval depends on the subagent *invoking* the skill (probe-type, body auto-loads at invoke), the skills operational copy IS required. Source remains on the experimental branch
   - **Host permission-gate fallback**: when apply to live `.claude/` is refused by the host self-modification gate (autonomous run without explicit user authorization), `skills/*` (off the observation surface) falls back to evaluator direct Read of the worktree draft; record the deviation in the PR self-review. `rules/*` apply is load-bearing, so a refused apply cannot be substituted by direct Read (injected context still shadows): re-run from a session that can apply, or record the deviation and flag reduced confidence for post-merge observation
3. **Parallel subagent spawn** - Select the three Design Dimensions axes (N, M, P) based on draft nature and spawn subagents in parallel. Default is `N=3, M=all axes, P=1`, total invocation = 3. In the default pattern, the subagent prompt explicitly instructs "answer each M axis question independently without referencing other axes' answers" packed into a single prompt. If prompt complexity is high enough that cross-axis echo bias suppression is uncertain, switch to the M=1 axis-separated exception pattern (total invocation = `N x axis_count`); if premise variation is needed, switch to P>1 (total invocation = `N x P`) (see Design Dimensions). Prompts must be self-contained (do not let parent context leak in). Every spawn under this skill explicitly sets the Agent tool `model` parameter at or above the sonnet-class floor; implicit parent-model inheritance is prohibited here (see Constraint: Model floor)
4. **Aggregate verdict** - Aggregate cross-axis judgment per the Design Dimensions aggregation rule (safer-side OR for delete/keep, AND for adopt/reject, three-value consistent / partial / negative classification for intermediate). Fixed axes may override the default per-axis (see Fixed axis: impression-literal detection)
5. **Runtime restore** - Restore `.claude/` to tag-match state (revert the operational copy to pre-draft). Skip when step 2 applied nothing (skills/* direct-Read path, or permission-gate fallback): no write occurred, so there is nothing to restore
6. **Judgment** - Based on the verdict: consistent -> push the spec change toward implementation / partial / negative -> the parent adjudicates each finding against the source, revises the draft, and takes the revised draft to self-review / abort. **Single round**: steps 2-4 produce one verdict per draft. Re-running them on the revised draft is out of scope; the revised draft ships without a re-verification round (see Non-scope: what the single-round cap gives up). The step 2 permission-gate retry sits on a separate axis: a refused apply means the round never produced a verdict, so retrying from a session that can apply is not a re-verification round and the cap does not block it
7. **Externalize** - Record the verdict and the adoption judgment in the parent issue body / PR self-review. If the judgment has settled, also append to decision structure per `skills/evolution-decision-structure-write`

</procedure>

<constraint>

## Constraint

- **N=1 prohibited, minimum N=3**: One trial is the source of overconfidence. The `#1296` empirical demonstration observed conclusion reversal from N=1 positive -> N=3 = 1 positive + 2 partial-negative (at that time under the M=1 axis-separated exception pattern with 3-axis OR aggregation; the current default holds the same N=3 floor under M=all axes). Reference Design Dimensions' `subagent_count` for N and run at minimum 3
- **Model floor = sonnet-class, explicit per spawn**: Every subagent spawned under this skill — whether invoked as the mandatory brake 1 or on one of the other Trigger entries — explicitly sets the Agent tool `model` parameter; relying on implicit parent-model inheritance is prohibited (a sub-floor parent silently lowers the evaluation floor). Default and floor = `sonnet`; explicit specification of a higher-class id (e.g. `opus`, `fable`) remains permitted but is not the default. `haiku` is prohibited as a brake 1 evaluator (below floor). Membership decision rule: a model id that cannot be positively classified as sonnet-class or above (unlisted, future, or versioned id of uncertain class) must not be passed; on doubt, fall back to the literal `sonnet`. The floor is fixed per call, not via custom-agent frontmatter `model:` pinning — judge-type (answers axis questions) and probe-type (current behavior of a vanilla subagent is itself the observation target) subagents coexist in this skill, and an evaluator prompt file would mutate the probe-type observation target (the custom-agent file body replaces the subagent's system prompt = identity, whereas the per-call `model` parameter changes neither the context nor the identity surface). Vanilla general-purpose probe nature is preserved. Floor lowered from opus-class per #1532: token budget reduction, empirically grounded on the operational observation that Li+ previously ran entirely on Sonnet (parent model was Sonnet, so brake 1's effective floor was already Sonnet during that period) with no observed regression. Scope note (#1554): the explicit-`model` requirement is now brake-specific — brake 1 (this skill) and brake 2 (`adapter/claude/agents/l1-gate-eval.md`) pin the floor, while every non-brake spawn omits the parameter and inherits the parent model. `skills/task-subagent-delegation/SKILL.md` Subagent Model Policy carries the split. The N=3 evaluator-count floor above is unaffected (`#1296`'s basis is sample count, not model tier)
- **Subagent prompt must be self-contained**: Do not let parent context leak in. In the default M=all axes pattern, the prompt explicitly instructs each axis to "answer independently without referencing other axes' answers" to suppress cross-axis echo bias. If prompt complexity is high enough that the mitigation is uncertain, fall back to the M=1 axis-separated pattern (see Design Dimensions)
- **Character_Instance non-inheritance**: What gets injected into subagent context = `CLAUDE.md` + `.claude/rules/**/*.md` (full body) + `.claude/skills/*/SKILL.md` (description only, body lazy-loaded at invoke) + MEMORY.md + harness-level system-reminders. `.claude/output-styles/`, hook firing output (SessionStart / UserPromptSubmit, etc.), and `.claude/settings.json` itself do not reach the subagent. `.claude/hooks/*.sh` script bodies are readable via the Read tool but not auto-loaded. When character behavior is part of the verification target, explicitly inject the Character_Instance body into the prompt. Running the character axis without injection produces the hollow prefix sleeping bug (persona absent, only the Character Instance name string generated)
- **Operational copy apply and restore must be paired**: When step 2 applies the operational copy, step 5 (restore) is mandatory — skipping restore carries the change into the parent session's behavior and leaves contamination for subsequent sessions. When step 2 applies nothing (target-conditional skip / permission-gate fallback), the pairing is vacuous: no apply, no restore

</constraint>

<non-scope>

## Non-scope

- This method is a pre-spec-reflection verification surface; it does not replace PR review (semi_auto mode minor/major human review is a separate axis)
- One trial is excluded as a source of overconfidence
- Verification of facts that change over time (API spec, library behavior) is outside this method's range; investigate per occurrence
- Separate axis from promotion-judgment's memory observation noise floor judgment (this method = spec verification; promotion = observation accumulation judgment)

### What the single-round cap gives up

Procedure step 6 caps the eval at one round. Three defect classes are dropped by that cap. They are enumerated here so a later reader reads them as dropped, not missed (#1563):

- Defects introduced by the parent's own fix. Observed at PR #1560 G2 and PR #1555 R2 / R3. `#1562` test coverage is the receptacle for the behavior-defect subset.
- Prose-layer findings that surface only in later rounds. Observed at PR #1550 R4 (a still-live description deleted during a rewrite). Tests do not catch this class.
- Behavior defects present in the initial implementation that round 1 did not reach. Observed at PR #1543 R3 (chunk-boundary multibyte corruption) and PR #1533 R2 (a spec category missing from an enumeration).

Accepted on the Li+ correctness criterion (`rules/model/foundational-invariant.md`: correctness is real-world behavior): none of the three had surfaced in production, while the round cost was incurred every time. Changes stay inside git revert range and release remains a human gate. Re-evaluation trigger = a single-round-capped merge that produces observable production harm.

</non-scope>

<boundary>

## Boundary

- **`skills/evolution-loop/SKILL.md`**: This skill is referenced inside the loop's observe / evaluate stage. The loop side "calls this method"; the method body lives in this skill
- **`skills/evolution-l1-update-gating/SKILL.md`**: Authorization axis for L1 source changes (long-horizon observation requirement). This method is the empirical verification axis immediately before implementation. Orthogonal relation - L1 update is expected to use this method alongside. In the `Evolution_Initiator_Autonomy` two-stage brake framing, this method is brake 1 (always-on for self-evolution PRs); the L1 root-criteria evaluator (`adapter/claude/agents/l1-gate-eval.md`) is brake 2 (L1-only, layered on top of brake 1)
- **`rules/evolution/promotion-judgment.md`**: Noise floor observation judgment (memory cluster tally). This method is spec verification (immediately before implementation). Orthogonal relation
- **`skills/task-subagent-delegation/SKILL.md`**: Derived use from the delegation axis - this method's subagent spawn is a special case of delegation (purpose: gather evaluation data, not delegate implementation). That skill's Subagent Model Policy and Parallel-Width Cap live there; since #1554 that policy splits by purpose — every non-brake spawn omits the `model` parameter and inherits the parent model, while brake 1 (this skill) and brake 2 stay pinned at the `sonnet` floor stated in this skill's Constraint; this skill's N / M / P width (Design Dimensions) remains a separately-bounded, deliberate fan-out exempt from the width cap — the width exemption is stated in that skill's Parallel-Width Cap section
- **`skills/evolution-decision-structure-write/SKILL.md`**: Judgment record surface. Judgments produced by applying this method get recorded in decision structure

</boundary>

<implementation-note>

## Implementation Note

Subagent spawn goes through the host's Agent tool (Claude Code: `Agent` tool; Codex: equivalent mechanism). Parallel execution = multiple Agent tool calls in a single message. subagent_type is selected per task (typically general-purpose).

The Agent tool accepts a per-call `model` parameter (e.g. `sonnet` / `opus` / `haiku` / `fable`; omitted = parent-model inheritance). This skill always passes it explicitly per the Constraint model floor — omission is prohibited here, and is the opposite of what `skills/task-subagent-delegation/SKILL.md` Subagent Model Policy prescribes for non-brake spawns. On hosts without a per-call model parameter, verify the session model satisfies the sonnet-class floor before spawning; a session model that cannot be positively classified as sonnet-class or above counts as sub-floor. A sub-floor session cannot satisfy brake 1 (run the eval from a floor-satisfying session instead).

</implementation-note>

</parallel-subagent-eval>

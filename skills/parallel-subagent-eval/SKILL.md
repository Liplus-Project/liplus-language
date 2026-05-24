---
name: parallel-subagent-eval
description: Invoke when verifying a Li+ rules/*, skills/*, or adapter/* edit before commit/merge, when evolution-loop observe/evaluate needs an empirical verdict, or when N=1 self-check on an edit feels positive — parallel subagent eval (default: N=3 subagents each answering all observation axes, safer-side OR aggregation) catches introspection-gap-driven overconfidence.
layer: L2-evolution
---

# Parallel Subagent Eval

Verification method that measures the AI's introspection gap (no empirical basis for predicting its own future invoke behavior or rule semantic effect) from the outside via the current behavior of subagents.

## Trigger

Fires at any of the following moments:

- Li+ rules/* or skills/* edit draft has converged and verification is needed before the commit/merge gate
- evolution-loop observe / evaluate stage needs an empirical verdict
- Right after AI alone feels "this edit satisfies the spec" (catch overconfidence from N=1 self-check)
- Spec revision proposal needs orthogonal verification on the rule semantic consistency axis
- **Self-evolution PR brake (mandatory)**: any PR filed under the `Evolution_Initiator_Autonomy` initiator path (`adapter/claude/CLAUDE.md`) runs this method before the commit/merge gate. This is brake 1 of the two-stage brake. L1 Model Layer source change additionally requires human review (brake 2). semi_auto patch-auto-merge does not bypass brake 1.

Axis selection depends on the nature of the draft. Examples:
- skill description edit: ease of AI invoke judgment / maintainer-side readability / coverage gap
- rule body edit: behavior consistency across configured / not-configured paths / detect semantic conflict with adjacent rules / orthogonality against existing scope clauses

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

## Procedure

**Precondition**: source lives on an experimental branch, and `.claude/` is in tag-match state (draft unapplied). When character behavior is part of the verification target, the step 3 subagent prompt must explicitly inject the Character_Instance body (see Constraint).

1. **Prepare draft** - Draft the edit content
2. **Apply operational copy** - Apply the draft to `.claude/skills/<name>/SKILL.md` or `.claude/rules/**/*.md`. Source remains on the experimental branch
3. **Parallel subagent spawn** - Select the three Design Dimensions axes (N, M, P) based on draft nature and spawn subagents in parallel. Default is `N=3, M=all axes, P=1`, total invocation = 3. In the default pattern, the subagent prompt explicitly instructs "answer each M axis question independently without referencing other axes' answers" packed into a single prompt. If prompt complexity is high enough that cross-axis echo bias suppression is uncertain, switch to the M=1 axis-separated exception pattern (total invocation = `N x axis_count`); if premise variation is needed, switch to P>1 (total invocation = `N x P`) (see Design Dimensions). Prompts must be self-contained (do not let parent context leak in)
4. **Aggregate verdict** - Aggregate cross-axis judgment per the Design Dimensions aggregation rule (safer-side OR for delete/keep, AND for adopt/reject, three-value consistent / partial / negative classification for intermediate)
5. **Runtime restore** - Restore `.claude/` to tag-match state (revert the operational copy to pre-draft)
6. **Judgment** - Based on the verdict: consistent -> push the spec change toward implementation / partial / negative -> revise draft and re-run from step 2 (re-run must also go through step 5 restore first) / abort
7. **Externalize** - Record the verdict and the adoption judgment in the parent issue body / PR self-review. If the judgment has settled, also append to decision structure per `skills/evolution-decision-structure-write`

## Constraint

- **N=1 prohibited, minimum N=3**: One trial is the source of overconfidence. The `#1296` empirical demonstration observed conclusion reversal from N=1 positive -> N=3 = 1 positive + 2 partial-negative (at that time under the M=1 axis-separated exception pattern with 3-axis OR aggregation; the current default holds the same N=3 floor under M=all axes). Reference Design Dimensions' `subagent_count` for N and run at minimum 3
- **Subagent prompt must be self-contained**: Do not let parent context leak in. In the default M=all axes pattern, the prompt explicitly instructs each axis to "answer independently without referencing other axes' answers" to suppress cross-axis echo bias. If prompt complexity is high enough that the mitigation is uncertain, fall back to the M=1 axis-separated pattern (see Design Dimensions)
- **Character_Instance non-inheritance**: What gets injected into subagent context = `CLAUDE.md` + `.claude/rules/**/*.md` (full body) + `.claude/skills/*/SKILL.md` (description only, body lazy-loaded at invoke) + MEMORY.md + harness-level system-reminders. `.claude/output-styles/`, hook firing output (SessionStart / UserPromptSubmit, etc.), and `.claude/settings.json` itself do not reach the subagent. `.claude/hooks/*.sh` script bodies are readable via the Read tool but not auto-loaded. When character behavior is part of the verification target, explicitly inject the Character_Instance body into the prompt. Running the character axis without injection produces the hollow prefix sleeping bug (persona absent, only the Character Instance name string generated)
- **Operational copy apply and restore must be paired**: Always execute both step 2 (apply) and step 5 (restore). Skipping restore carries the change into the parent session's behavior and leaves contamination for subsequent sessions

## Non-scope

- This method is a pre-spec-reflection verification surface; it does not replace PR review (semi_auto mode minor/major human review is a separate axis)
- One trial is excluded as a source of overconfidence
- Verification of facts that change over time (API spec, library behavior) is outside this method's range; investigate per occurrence
- Separate axis from promotion-judgment's memory observation noise floor judgment (this method = spec verification; promotion = observation accumulation judgment)

## Boundary

- **`skills/evolution-loop/SKILL.md`**: This skill is referenced inside the loop's observe / evaluate stage. The loop side "calls this method"; the method body lives in this skill
- **`skills/evolution-l1-update-gating/SKILL.md`**: Authorization axis for L1 source changes (long-horizon observation requirement). This method is the empirical verification axis immediately before implementation. Orthogonal relation - L1 update is expected to use this method alongside. In the `Evolution_Initiator_Autonomy` two-stage brake framing, this method is brake 1 (always-on for self-evolution PRs); L1 human review is brake 2 (L1-only, layered on top of brake 1)
- **`rules/evolution/promotion-judgment.md`**: Noise floor observation judgment (memory cluster tally). This method is spec verification (immediately before implementation). Orthogonal relation
- **`skills/task-subagent-delegation/SKILL.md`**: Derived use from the delegation axis - this method's subagent spawn is a special case of delegation (purpose: gather evaluation data, not delegate implementation)
- **`skills/evolution-decision-structure-write/SKILL.md`**: Judgment record surface. Judgments produced by applying this method get recorded in decision structure

## Implementation Note

Subagent spawn goes through the host's Agent tool (Claude Code: `Agent` tool; Codex: equivalent mechanism). Parallel execution = multiple Agent tool calls in a single message. subagent_type is selected per task (typically general-purpose).

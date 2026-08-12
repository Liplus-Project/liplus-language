---
name: evolution-impression-literal-detection
description: Invoke when an evaluator is answering the fixed impression-literal axis on a Li+ source draft / a phrase in a rules or skills or adapter draft needs testing for whether it load-bears on behavior semantic / brake 1 findings on rhetorical drift are being adjudicated before merge / a Li+ source sentence is about to be kept or removed on a judgment that rests on impression rather than behavior. Provides the removal test (can this sentence go without changing the rule's behavior semantic), the positive detection targets and the protected negatives, the 2-of-3 refine threshold against the 1-of-3 record-only threshold, and the false-negative backstop routing to post-merge observation.
layer: L2-evolution
---

<fixed-axis-impression-literal-detection>

# Fixed axis: impression-literal detection

For Li+ source drafts (`rules/*` / `skills/*` / `adapter/*`), impression-literal detection is a fixed axis included alongside the spec-nature axes selected per draft (`skills/evolution-parallel-agent-eval/SKILL.md` Trigger, Axis selection). It covers content-independent rhetorical drift at the post-write pre-merge surface, distinct from `rules/model/trigger-check-gate.md` Frame check (pre-judgment surface protecting dialogue).

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

Aggregation — this axis is fixed, so it does not take the per-judgment aggregation rule brake 1 selects for the axes chosen per draft; it overrides through the fixed-axis route at `skills/evolution-parallel-agent-eval/SKILL.md` Procedure step 6, at these absolute thresholds:
- 2 or more of N=3 flag the same literal → refine immediately.
- 1 of N=3 flags → do not auto-refine; record the flagged literal in the commit body as the adjudication of that finding, naming the below-threshold count as the reason it was not refined. That is the surface the parent inspects at `skills/evolution-parallel-agent-eval/SKILL.md` Procedure step 8, which is how it reaches the self-review.

These two numbers are absolute for this axis and rest on the Rationale below, not on a count of agreeing evaluators. They do not license reading a ratio as a verdict on the axes selected per draft — there, a ratio is a triage signal only (`skills/evolution-parallel-agent-eval/SKILL.md` Design Dimensions, Ratio is a triage signal).

A split on this axis (1-of-3, or 2-of-3) is a divergence, so it also runs the same-question check → why-diverged pair in that file's Divergence handling. The pair can find the split tracing to the Positive / Negative lists above being ambiguous at the flagged phrase, and that finding is recorded; the threshold action above fires independently of what the pair returns.

False-negative backstop: all-3-miss cases route to post-merge observation per `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format (2-week cycle). Post-merge drift surfacing is on a separate axis from this pre-merge detection.

Rationale: behavior-vs-impression boundary is context-dependent, so N=1 flag carries false-positive risk. The threshold prevents over-trimming load-bearing L1 spec phrasing.

</fixed-axis-impression-literal-detection>

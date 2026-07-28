---
name: task-subagent-spawn
description: Invoke when the Agent tool model parameter is about to be set or omitted for a subagent spawn / a brake evaluator subagent is about to be spawned / more than one subagent is about to be launched in a single batch / a second wave of subagents is about to be launched before the prior wave has reported. Provides the purpose-split model policy (brake evaluators pin an explicit sonnet-class floor, every other spawn omits the parameter and inherits the parent model) with its exhaustive category list, and the parallel-width cap of 5 in flight with its wave-sequencing binding condition and exemptions.
layer: L3-task
---

<subagent-model-policy>

# Subagent Model Policy

The parent session's own model tier is out of scope; see `docs/A.-Concept.md` for the documented minimum operating environment. The policy splits by purpose (#1554): brake evaluators are pinned, every other spawn inherits.

**Brake evaluators — explicit `model`, default and floor = `sonnet`.** Implicit parent-model inheritance is prohibited here, because a sub-floor parent silently lowers the evaluation floor. Explicit specification of a higher-class id (e.g. `opus`, `fable`) remains permitted but is not the default. The floor's detailed spec (`haiku` prohibition, doubt -> `sonnet` fallback, per-call fixing rather than custom-agent frontmatter `model:` pinning) lives in `skills/evolution-parallel-agent-eval/SKILL.md` Constraint, phrased there from brake 1's surface. This section extends those clauses to brake 2, which the parent spawns at the `model` parameter set here; do not read brake-2 applicability out of the brake-1-scoped wording in that file. Applies to:

- Brake-1 evaluators in `skills/evolution-parallel-agent-eval/SKILL.md`.
- Brake 2, the L1 root-criteria evaluator (`adapter/claude/agents/l1-gate-eval.md`, spawned by the parent as a subagent at the `model` parameter set here; its PASS verdict substitutes for human approval on PRs touching L1 Model Layer source per `Evolution_Initiator_Autonomy`). This file is not edited — the model is set at spawn time by the parent, not in the evaluator prompt file itself.

**Every other spawn — omit the `model` parameter, inheriting the parent model.** The prohibition above is evaluator-specific; for these categories inheriting the parent's model is the intent, so the sub-floor-parent reasoning does not apply. Omission (rather than writing the parent's id literally) tracks a later parent-model change without a source edit. Applies to:

- Every delegation under `skills/task-subagent-delegation/SKILL.md`: implementation / operations spawn per that skill's Rules, and bounded read-only investigation (audit / consistency check / grep-and-report) per its frontmatter description. No agent definition file exists for either, so nothing can intercept the omission.
- `adapter/claude/agents/dialogue-evaluator.md` (ported to `adapter/codex/agents/dialogue-evaluator.toml`), spawned only on explicit human request for dialogue evaluation. Not a brake, and explicit-request-only invocation keeps its budget contribution marginal; inheritance lets it track the parent tier instead of being fixed at the brake floor. Neither the `.md` frontmatter nor the `.toml` carries a `model:` key, so omission resolves to parent inheritance per the Agent tool default. This file is not edited either.

The four categories above are exhaustive. Two are file-backed and exhaust `adapter/*/agents/*` (only `l1-gate-eval` and `dialogue-evaluator`, each ported to `claude` and `codex`; verified by directory listing at #1532 fix time and re-verified at #1554). The other two — brake-1 evaluators and general delegation — are file-less: whichever built-in subagent type they are spawned as, no definition file exists that could intercept the `model` parameter. `.github/scripts/liplus_discussions_agent.py` (Discussions intake bot) is a separate GitHub Actions + direct Anthropic API caller, not spawned via the Agent tool from a Li+ session, and is out of scope for this policy.

Rationale (#1554, partially superseding #1532's uniform floor): token mass sits on the evaluator side — PR #1550 / #1551 spent ~2.6M tokens across 21 brake-1 evaluators against ~0.4M across 2 implementation subagents — while those evaluators ran at the sonnet floor with detection power intact (every round produced real defects, several the parent had not reached independently). Evaluator count was `N=3 x rounds` while rounds were defect-driven; `#1563` capped brake 1 at a single round, so it is now fixed at `N=3 x 1`. The order still holds on a changed mechanism: with no re-verification round, the once-revised, never-re-verified draft is what ships, so the implementer's tier is the variable that moves the outcome while the evaluator multiplier's unit cost stays fixed. #1532's grounding for the evaluator floor itself (Li+ previously ran entirely on Sonnet with no observed regression, parent model Sonnet at the time so brake 1's effective floor was already Sonnet) is unchanged.

</subagent-model-policy>

<parallel-width-cap>

# Parallel-Width Cap

Cap = 5 subagents in flight at once (spawned and not yet returned), applying to every parallel delegation pattern that funnels through `skills/task-subagent-delegation/SKILL.md`: cross-parent-issue worktree parallelism and same-parent sub-issue parallelism (both defined in `adapter/claude/CLAUDE.md` Subagent_Delegation), and bounded read-only investigation fan-out (defined in that skill's own frontmatter description). The value 5 is a provisional bound, bracketed against the established eval default width (N=3) and well under host-scale fan-out (Dynamic Workflows research preview: up to 16 concurrent / 1000 cumulative per run, evaluated and deferred in #1426 / #1428) — it is not derived from a cost or latency measurement and should be revised on observation.

Enforcement mechanism: per-message batch size (Agent tool calls in a single message) is necessary but not sufficient on its own — a message launching 5, followed by a second message launching 5 more before the first wave has returned, keeps every message at or under 5 while actual in-flight width reaches 10. The binding condition is that a new batch may not be launched until every subagent in the prior batch has completed and reported; only then does per-message batch size equal actual concurrent width. If a task needs wider fan-out than 5 total, split into sequential batches under this same rule rather than overlapping waves.

This cap governs top-level concurrent width (how many subagents the parent has in flight at once). It is a separate axis from `skills/task-subagent-prompt/SKILL.md` Bounded delegation: prohibit recursive subagent spawn, which governs spawn depth (a subagent spawning its own children) — the two do not extend or narrow each other.

Exempt: `evolution-parallel-agent-eval`'s own N / M / P fan-out (default N=3, up to N=3 x P=2 = 6, or N=3 x axis_count under the M=1 exception pattern) is a separately-bounded, deliberate fan-out per that skill's Design Dimensions and is not subject to this cap.

Honesty clause: this cap is recall-dependent. There is no hook, counter, or gate enforcing the wave-sequencing binding condition above — the parent must apply it from procedure alone. Per `rules/model/subtractive-structural-beauty.md` procedure-vs-structure binary (a reliably-executed structure is required where execution is not guaranteed), a hook-based replacement is tracked as future work in #1534.

</parallel-width-cap>

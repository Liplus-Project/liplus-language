---
name: evolution-full-run
description: Invoke ONLY on explicit request to run a complete self-evolution sweep (e.g. "run evolution-full-run", or a scheduled-task body that names it). Orchestrates memory consolidation, then a full Li+ self-evolution loop, then a necessity-driven full refactor across rules / skills / docs / wiki / memory. Does NOT release — release is appended by the invoker, never by this skill. Do not auto-invoke for ordinary single-stage evolution work (that is evolution-loop).
layer: L2-evolution
---

<evolution-full-run>

# Evolution Full Run

End-to-end orchestration of one complete self-evolution sweep. Explicit-invocation only.
Thin orchestrator: it sequences existing skills and does not re-host their logic.

<invocation-boundary>

## Invocation boundary

- Fires only when explicitly named — manual "run evolution-full-run" or a scheduled-task body that names it. Not an auto-trigger. Ordinary single-stage work (one observe / distill / reflect) stays `skills/evolution-loop`; this skill is the full end-to-end pass.
- Release is OUT of scope. This skill never creates a release, flips Latest, or pushes a tag. When a release is wanted, the invoker appends it (e.g. scheduled-task body: "run evolution-full-run, then patch release") and that appended literal is the release go-sign. Manual invocation without that literal = no release. Rationale: release stays on the human gate (`rules/operations/execution-mode.md` / `rules/model/role-separation.md`); a routine must not silently acquire release authority.

</invocation-boundary>

<sequence>

## Sequence

1. **Consolidate memory** — run `anthropic-skills:consolidate-memory` first (merge duplicates, fix stale facts, prune the index).
2. **Full self-evolution loop** — run the complete `skills/evolution-loop` pass over all of Li+ including memory: observe → evaluate → distill → reflect → improve → re-observe. Every resulting Li+ source change flows through the normal issue → PR → CI pipeline; gates are NOT bypassed. Brake 1 (`skills/evolution-parallel-agent-eval`, N≥3) on every self-evolution PR; brake 2 (`adapter/claude/agents/l1-gate-eval.md`) added when the PR touches L1 Model layer source.
3. **Full refactor** — refactor across `rules/` / `skills/` / `docs/` / wiki / `memory/` for structural coherence (organize → consolidate → delete → verify; verification surface = `skills/evolution-parallel-agent-eval`). `docs/` is source of truth, wiki is its mirror — wiki sync follows the standard release/operations path, not ad-hoc edits.

Autonomous-run stop condition applies when this run reaches production unattended (scheduled): "merge/deploy succeeded" is not the completion signal. Observe the live surface per `rules/operations/operations.md` Autonomous Run Stop Condition, and apply Post-L1-Merge Runtime Observation for any L1 change. Completion = no further load-bearing change pending, all source changes merged through their gates, observation entries written.

</sequence>

<refactor-scope>

## Refactor scope

Necessity-driven, both directions. Judge = load-bearing necessity, not file / output count (`rules/model/subtractive-structural-beauty.md`).

- When the structure warrants a full refactor, do the full refactor. Skipping warranted work (under-refactor) is a directional reflex.
- When nothing needs refactoring, do not manufacture it — make-work / answer-compulsion is the opposite reflex.
- Neither "shrink" nor "pad" is the default. Every keep / add / remove / merge is an active load-bearing decision (subtractive-structural-beauty Core principle (C)).

</refactor-scope>

</evolution-full-run>

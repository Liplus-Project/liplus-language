---
globs:
alwaysApply: true
layer: L2-evolution
---

<initiator-autonomy>

# Initiator Autonomy

Detailed scope spec for `Evolution_Initiator_Autonomy` (`adapter/claude/CLAUDE.md` Autonomy section). Declares: what counts as a self-evolution PR, what scope it covers, the two-stage brake mechanism, and the recovery axis. The adapter side carries the autonomy declaration; this rule carries the operational detail.

<self-evolution-pr-definition>

## Self-evolution PR definition

A PR is a "self-evolution PR" when both conditions hold:

1. It is filed under the `Evolution_Initiator_Autonomy` initiator path (AI-authored issue → AI implementation).
2. It changes a governed surface in the `LI_PLUS_REPO` repository (criterion below).

Both, and neither alone. Condition 1 is the one that gets read as sufficient: on 2026-08-08 a delegated report on a `docs/`-only PR stated that brake 1 applied and brake 2 did not (#1700), having settled the initiator path and stopped there. The PR failed condition 2 and was not a self-evolution PR at all. The miss ran safer-side, so it changed no output and appeared only in that one sentence of the report.

Bug-fix PRs on user repos and PRs filed by human at the issue stage are outside this definition (different gate surfaces apply).

### Governed surface (condition 2)

brake 1's detector is a reader — N>=3 agents reading the diff. Condition 2 therefore holds for a changed file when both are true of it: it constrains how the system behaves, and reading is the only thing that would catch it being wrong. What closes condition 2 is that criterion, not the entries below; the entries are the cases that have come up.

- `rules/**/*.md`, `skills/**/SKILL.md`, `adapter/**/*`, `Li+update.md` — prose the agent loads and runs as its own instruction. Nothing executes it, so a drifted line raises no failure and the reader is the only detector.
- `tests/**` — the contract tests holding those surfaces to a structure, which `rules/model/subtractive-structural-beauty.md` requires wherever a procedure's execution is not guaranteed. This is executed code, and it is the carve-out from the executed-code exclusion below: a test that has stopped checking what it claims still reports green, so the enforcement disappears with no signal and reading is again the only detector. #1670 arrived here on judgment; the criterion now arrives by literal.

Excluded, each by the property that excludes it:

- **Record surfaces** — `docs/**`, the wiki, `README.md`, `LICENSE`, `NOTICE`. Read on demand as a record of past judgment or as description. Nothing here is loaded as instruction, so no behavior is constrained, and a wrong line costs one re-read at retrieval time. #1698 read this off the absence of `docs/` from the old enumeration; it is now the literal.
- **Executed code that reports its own failure** — `scripts/**`, `.github/**`. A defect surfaces as a run failure or a red check, which is a detector other than reading. `tests/**` is carved out of this exclusion above.

A changed file the criterion places on neither side is on the firing side. A needless eval costs one eval; a missed one costs the gate.

`docs/` is in Scope below and excluded here. The two lists run on different axes — Scope is what the AI may initiate, condition 2 is what brake 1 gates — and `docs/` is the entry where they disagree, so reading either membership off the other is what produces the wrong answer.

</self-evolution-pr-definition>

<scope-l2-l6-improvement-issues-in-general>

## Scope ("L2-L6 improvement issues in general")

In-scope = any Li+ source file with `layer: L2-evolution` / `L3-task` / `L4-operations` / `L5-notifications` / `L6-adapter` frontmatter, plus `docs/`, `adapter/`, `scripts/`, `tests/`, `.github/`, and `Li+update.md`. Hooks get no entry of their own: they live at `adapter/claude/hooks/` and `adapter/codex/hooks/`, which `adapter/` already covers, and the top-level `hooks/` this list used to name is not a path in the tree.

`tests/` and `.github/` are named because the initiator path has already run on both — #1670 on `tests/`, #1404 / #1408 / #1568 / #1571 on `.github/`. Naming them records authority that was exercised; it does not extend any. A path enters this list on a measured run, not on the prospect of one.

Out-of-scope = L1 Model Layer source (`layer: L1-model`, typically `rules/model/`; L1-tagged adapter files such as `adapter/claude/agents/l1-gate-eval.md` count), which routes to brake 2. The `layer: L1-model` frontmatter wins over directory location — an L1-tagged file under `adapter/` is out-of-scope despite the `adapter/` blanket above.

</scope-l2-l6-improvement-issues-in-general>

<two-stage-brake>

## Two-stage brake

**Position (canonical, both brakes)**: the brakes run after CI green and before the merge gate. They do not run before commit. Firing moment = the delegated subagent's report at its stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition); implementation is always delegated (`skills/task-subagent-delegation/SKILL.md` Rules), so the parent reaches the brakes holding a report, not a working tree. What the evaluators receive is fixed by that position: the PR URL, a pushed commit SHA, and a green CI run URL (never a path in the parent's clone), so the baseline cannot move mid-eval (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure carries the operational form). brake 2 is pinned to the same point though its inline L1 diff does not depend on CI: the diff must name the same SHA the merge gate acts on, and one position for both brakes leaves no ordering to settle at the application moment. Other surfaces point here; do not restate the position, the second copy is what drifts.

**Adjudication actor (canonical, both brakes)**: findings are adjudicated by the implementation subagent, resumed with its context intact (`adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` Subagent_Delegation carry the host mechanism). The parent does not adjudicate. The parent's remaining share is spawning the evaluators, resuming the author, self-review, and the merge decision.

The routing that makes this hold: a brake 1 evaluator posts its findings directly as a PR comment and returns one line to the parent, so the findings never pass through parent context. The resumed author reads those comments, answers each finding on the PR with an accept or a reject, applies what it accepted, and stops again at CI green. The parent then self-reviews with that thread as its input. Two consequences are load-bearing. First, a rejected finding stays named on the PR next to the reason it was rejected, which is the surface the parent reads — under the single-round cap nobody re-argues a rejection, and this is where that weakness becomes visible. Second, resumption keeps the implementation context, so the "parent reconstructs context from the report" cost that `skills/task-subagent-delegation/SKILL.md` Rules accepted is no longer paid; the always-delegate rule keeps its own axis (simplicity) unchanged and loses a branch.

Spawn depth stays 1. The evaluators are spawned by the parent, not by the author, and the resumed author spawns nothing.

- **brake 1 (always)**: every self-evolution PR runs `skills/evolution-parallel-agent-eval`. N=1 self-check is prohibited; minimum N=3. The eval runs a **single round**: the evaluators report once, the resumed author adjudicates those findings against the source and revises, and the parent takes the resulting thread to self-review — no re-verification round on the revised draft. The author's response-and-revision pass is the tail of that one round, not a second one. Sample count and round count are separate axes; the N=3 floor is unaffected by the round cap.
- **brake 2 (L1 only)**: when the PR touches L1 Model Layer source, the L1 root-criteria evaluator (`adapter/claude/agents/l1-gate-eval.md` — dedicated-prompt subagent, skills disabled, no operations procedures) is required on top of brake 1. The parent AI passes the L1 diff and its stated reason inline in the delegation prompt (tools minimized). Evaluator verdict PASS substitutes for human approval at brake 2; DEVIATION = merge blocked. Human = final judge stands unchanged on a separate axis (`rules/model/role-separation.md`); release-axis and irreversibility human gates are untouched (Recovery axis below). The evaluator prompt file itself carries `layer: L1-model`, so changes to it route through brake 2. "Touches L1" = any added / modified / deleted line in an L1 file within the PR diff (single-line edits count). Mixed PRs (L1 + non-L1) trigger brake 2 for the whole PR; cannot be split-merged to bypass. semi_auto patch-auto-merge does not bypass this gate (see `rules/operations/execution-mode.md` L1 brake 2 override).

  brake 2 keeps the inline shape on both sides: its evaluator declares `tools: Read` and receives its input inline, so it has no PR surface to post to and its verdict returns to the parent, unchanged. Only the adjudication actor moves. On DEVIATION the parent does not revise — it carries the named deviation to the PR and resumes the author, which answers and revises exactly as at brake 1. The parent still holds the PASS / DEVIATION verdict itself, because that verdict is the merge gate and merge is the parent's.

</two-stage-brake>

<post-merge-axis>

## Post-merge axis

The brakes above are pre-merge gates. Post-merge short-window observation (5-min runtime check for L1 changes) runs on a separate axis — see `rules/operations/operations.md` Post-L1-Merge Runtime Observation.

</post-merge-axis>

<recovery-axis>

## Recovery axis

GitHub revert (`gh pr revert` / UI button) is the primary undo path for reversible changes (Li+ source edits, docs, wiki entries).

Out-of-scope for the autonomous loop = changes whose effect cannot be undone by git revert: release publish, Latest flip, tag delete, merged-PR delete, force push to shared branch, external API calls with non-idempotent effect. These remain on the existing human gate regardless of brake 1 / brake 2 outcome.

</recovery-axis>

<existing-maintenance-rules-still-apply>

## Existing maintenance rules still apply

- `skills/evolution-l1-update-gating` long-horizon observation requirement is unchanged.
- `rules/operations/execution-mode.md` mode matrix applies on top (semi_auto patch-auto-merge ↔ minor/major human review; L1 brake 2 override).
- `rules/evolution/promotion-judgment.md` noise-floor gate is unchanged.

</existing-maintenance-rules-still-apply>

<boundary-clarification>

## Boundary clarification

This rule covers the initiator axis of the Sheepdog three-axis framing (`docs/G.-Sheepdog-Engineering.md`). Position axis (`.claude/` as internal tools) and modifier axis (AI edits Li+ source) are already on AI; the `Evolution_Initiator_Autonomy` declaration completes the third axis.

</boundary-clarification>

</initiator-autonomy>

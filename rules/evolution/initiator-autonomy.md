---
globs:
alwaysApply: true
layer: L2-evolution
---

<initiator-autonomy>

# Initiator Autonomy

Detailed scope spec for `Evolution_Initiator_Autonomy` (`adapter/claude/CLAUDE.md` Autonomy section). Declares: what counts as a self-evolution PR, what scope it covers, the merge brake, and the recovery axis. The adapter side carries the autonomy declaration; this rule carries the operational detail.

<self-evolution-pr-definition>

## Self-evolution PR definition

A PR is a "self-evolution PR" when both conditions hold:

1. It is filed under the `Evolution_Initiator_Autonomy` initiator path (AI-authored issue → AI implementation).
2. It changes a governed surface in the `LI_PLUS_REPO` repository (criterion below).

Both, and neither alone. Condition 1 is the one that gets read as sufficient — the initiator path is settled and the read stops there. A PR that fails condition 2 is not a self-evolution PR at all, however plainly it sits on the initiator path.

Bug-fix PRs on user repos and PRs filed by human at the issue stage are outside this definition (different gate surfaces apply).

### Governed surface (condition 2)

brake 1's detector is a reader — an agent reading the diff. Condition 2 therefore holds for a changed file when both are true of it: it constrains how the system behaves, and reading is the only thing that would catch it being wrong. What closes condition 2 is that criterion, not the entries below; the entries are the cases that have come up.

- `rules/**/*.md`, `skills/**/SKILL.md`, `adapter/**/*`, `Li+update.md` — prose the agent loads and runs as its own instruction. Nothing executes it, so a drifted line raises no failure and the reader is the only detector.
- `tests/**` and `.github/workflows/**` — the enforcement backstop: the contract tests, and the workflow that runs them and produces the check. `rules/model/subtractive-structural-beauty.md` requires a structure wherever a procedure's execution is not guaranteed, and this is that structure. It is executed code, but it is the code no check stands behind, so its failures are silent in a way the exclusion below is not: a test that has stopped checking what it claims still reports green, and a workflow whose trigger no longer matches or whose gating step was dropped produces no run and therefore no red check at all. Nothing fails, and reading is again the only detector.

Excluded, each by the property that excludes it:

- **Record surfaces** — `docs/**`, the wiki, `README.md`, `LICENSE`, `NOTICE`. Read on demand as a record of past judgment or as description. Nothing here is loaded as instruction, so no behavior is constrained, and a wrong line costs one re-read at retrieval time.
- **Executed code a check stands behind** — `scripts/**`, `.github/scripts/**`. A defect surfaces as a raised exception in the calling turn or as a red check, which is a detector other than reading; where a defect would otherwise be silent, `tests/**` is what makes it loud (`tests/test_check_webhook_notifications.py` covers the classification and filtering paths of the poll-mode helper, so a filter that quietly narrows fails a check rather than under-delivering unnoticed). The backstop itself is on the firing side above, because nothing stands behind it. Executed code this exclusion does not cover is reached by the default below, not by this bullet.

A changed file the criterion places on neither side is on the firing side. A needless eval costs one eval; a missed one costs the gate.

`docs/` is in Scope below and excluded here. The two lists run on different axes — Scope is what the AI may initiate, condition 2 is what brake 1 gates — and `docs/` is the entry where they disagree, so reading either membership off the other is what produces the wrong answer.

</self-evolution-pr-definition>

<scope-l2-l6-improvement-issues-in-general>

## Scope ("L2-L6 improvement issues in general")

In-scope = any Li+ source file with `layer: L2-evolution` / `L3-task` / `L4-operations` / `L5-notifications` / `L6-adapter` frontmatter, plus `docs/`, `adapter/`, `scripts/`, `tests/`, `.github/`, and `Li+update.md`. Hooks get no entry of their own: they live at `adapter/claude/hooks/` and `adapter/codex/hooks/`, which `adapter/` already covers, and no top-level `hooks/` path exists in the tree.

`tests/` and `.github/` are named because the initiator path has already run on both. Initiator path here means who decided to file and implement, not which account pushed: a change carrying the same account but whose own body records it as Master-originated is not one of these measurements. Naming them records authority that was exercised; it does not extend any. A path enters this list on a measured run, not on the prospect of one.

Out-of-scope = L1 Model Layer source (`layer: L1-model`, typically `rules/model/`), which routes to `skills/evolution-l1-update-gating/SKILL.md`. The `layer: L1-model` frontmatter wins over directory location — an L1-tagged file sitting under a directory this list blankets is out-of-scope all the same.

</scope-l2-l6-improvement-issues-in-general>

<merge-brake>

## Merge brake

**Position (canonical)**: the brake runs after CI green and before the merge gate. It does not run before commit. Firing moment = the delegated subagent's report at its stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition); implementation is always delegated (`skills/task-subagent-delegation/SKILL.md` Rules), so the parent reaches the brake holding a report, not a working tree. What the evaluators receive is fixed by that position: the PR URL, a pushed commit SHA, and a green CI run URL (never a path in the parent's clone), so the baseline cannot move mid-eval (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure carries the operational form). Other surfaces point here; do not restate the position, the second copy is what drifts.

One thing stands between that CI green and this brake: the rule effect measurement, on a PR whose firing condition holds. Its position, its firing condition, its actor, and how a run that could not be taken is recorded are `skills/evolution-rule-effect-measurement/SKILL.md` Application point, Position on the self-evolution PR pipeline; none of that is restated here. What this surface holds about it is that it is not a second brake: nothing about the measurement gates the merge, the eval runs whether or not a run was taken, and brake 1 below stays the only brake at the gate.

**Adjudication actor (canonical)**: findings are adjudicated by the implementation subagent, resumed with its context intact (`adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` Subagent_Delegation carry the host mechanism). The parent does not adjudicate. The parent's remaining share is spawning the evaluators, resuming the author, self-review, and the merge decision.

**Channel (canonical)**: the exchange between evaluator and author runs on the PR's own comment thread. The evaluator posts its findings there itself and the author answers there, and the parent is not in the path — it does not compose either artifact, does not consolidate, and does not read what passes while it passes. Its share of the exchange is scheduling: it wakes the author onto new findings, and it opens or closes the next round. The parent still reads the whole thread once, at the exit, and its self-review and merge judgment are formed there (`rules/operations/execution-mode.md`, `rules/model/role-separation.md`). A parent that never read a finding cannot judge what was done with it — that requirement is unchanged, and what moved is where it is satisfied: at the exit rather than in every round.

The routing that makes this hold — where an evaluator posts its findings, how the author is woken onto them, what the author writes back, and where a round ends — is `skills/evolution-parallel-agent-eval/SKILL.md` Procedure (the reporting destination at step 3, then steps 4 and 6 to 8), with its Report shape fixing the artifacts each produces. Those steps are conditional, and a restatement here is what strips the conditions off: this surface is injected whole every session while a skill body is lazy-loaded at invoke, so the copy that has lost a condition is the copy always in context and the qualified original is the one nobody has open.

Two consequences are load-bearing here. First, the exchange is bounded rather than governed: the round trips carry a cap, so convergence rests on that bound and not on `skills/model-loop-safety` held by an actor inside the loop. Second, resumption keeps the implementation context, so the "parent reconstructs context from the report" cost that `skills/task-subagent-delegation/SKILL.md` Rules accepted is not paid; the always-delegate rule keeps its own axis (simplicity) unchanged and loses a branch. The cap's figure, what one round trip is, and what standing a rejection has inside the loop are the skill's; no figure of them is carried here, for the reason the brake 1 paragraph below states about figures on this surface.

Spawn depth stays 1. The evaluators are spawned by the parent, not by the author, and neither the resumed author nor an evaluator spawns anything.

**brake 1 (always)**: every self-evolution PR runs `skills/evolution-parallel-agent-eval`. That is the part this rule owns — the gate declaration: the brake is on, on every such PR, and nothing exempts one. What the eval is made of is the skill's: the evaluator-count floor (its Constraint) and the round cap (its Procedure step 7), each carrying the conditions that qualify it. Neither is restated here and no figure from either is carried, because a figure on this always-on surface is a second copy that arrives without those conditions while the conditioned original is the one not in context.

`brake 1` is a name, not a position in a sequence: it is the only brake at the merge gate, and nothing is waiting behind it. It stays uniform across that gate — an L1 Model Layer change adds no brake of its own, and semi_auto patch-auto-merge does not bypass it. What an L1 change carries instead sits on other axes and, except for the last, before this point: the observation threshold at issue formation (`skills/evolution-l1-update-gating/SKILL.md`), the execution-mode human gate for minor / major (`rules/operations/execution-mode.md`), and the post-merge runtime observation (Post-merge axis below). Human = final judge stands unchanged on its own axis (`rules/model/role-separation.md`); release-axis and irreversibility human gates are untouched (Recovery axis below).

</merge-brake>

<post-merge-axis>

## Post-merge axis

The brake above is a pre-merge gate. Post-merge short-window observation (5-min runtime check for L1 changes) runs on a separate axis — see `rules/operations/operations.md` Post-L1-Merge Runtime Observation.

</post-merge-axis>

<recovery-axis>

## Recovery axis

GitHub revert (`gh pr revert` / UI button) is the primary undo path for reversible changes (Li+ source edits, docs, wiki entries).

Out-of-scope for the autonomous loop = changes whose effect cannot be undone by git revert: release publish, Latest flip, tag delete, merged-PR delete, force push to shared branch, external API calls with non-idempotent effect. These remain on the existing human gate regardless of the brake 1 outcome.

</recovery-axis>

<existing-maintenance-rules-still-apply>

## Existing maintenance rules still apply

- `skills/evolution-l1-update-gating` long-horizon observation requirement is unchanged.
- `rules/operations/execution-mode.md` mode matrix applies on top (semi_auto patch-auto-merge ↔ minor/major human review).
- `rules/evolution/promotion-judgment.md` noise-floor gate is unchanged.

</existing-maintenance-rules-still-apply>

<boundary-clarification>

## Boundary clarification

This rule covers the initiator axis of the Sheepdog three-axis framing (`docs/G.-Sheepdog-Engineering.md`). Position axis (`.claude/` as internal tools) and modifier axis (AI edits Li+ source) are already on AI; the `Evolution_Initiator_Autonomy` declaration completes the third axis.

</boundary-clarification>

</initiator-autonomy>

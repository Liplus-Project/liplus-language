---
globs:
alwaysApply: true
layer: L4-operations
---

<operations>

# Operations

<operations-layer>

## Operations Layer

### Layer Position

Layer = L4 Operations Layer
Event-driven operations surface over the shared Li+ program
Requires = L1 Model Layer + L2 Evolution Layer + L3 Task Layer + Li+config.md
Load timing = always-on (loads every session per alwaysApply; Read when below governs application timing, not loading)
Read when: branch creation, commit, PR, merge, release, label assignment, Discussions reference.

Foregrounds:
  branch / commit / PR / merge / release procedures
  notifications / webhook intake procedures

Reads through:
  issue semantics and label vocabulary from rules/task/task.md (and skills/*/SKILL.md)
  execution mode from Li+config.md

### Event-Driven Operations

  [TRIGGER_INDEX]
  act_now      -> Branch And Label Flow
  on_issue_create -> Issue Format
  on_issue_edit   -> Issue Format
  on_issue_view   -> Issue Maturity
  on_issue_sub    -> Sub-issue Rules
  on_commit    -> Commit And Push
  on_pr        -> PR Creation
  on_ci        -> CI Loop
  on_review    -> PR Review (approval wait = Review approval check, `rules/operations/main-agent-procedures.md`)
  on_merge     -> Merge Execution (`rules/operations/main-agent-procedures.md`)
  on_release   -> Human Confirmation Required

</operations-layer>

<operations-rules>

## Operations Rules

Issue link via gh issue develop is always required.
gh issue develop must precede first push to GitHub.
Parent issue = one branch.
Sub-issues commit on the parent branch. No individual branches for sub-issues.
Parent issue with sub-issues = single parent PR. Per-sub-issue PR is prohibited.
Per-commit CI visibility uses draft PR opened early on the parent branch, not split PRs.
Commit title = ASCII English only, single line.
Commit body is not optional.
Commit body must contain: change summary + intent or background + issue reference.
Commit body must contain at least one sentence in `LI_PLUS_PROJECT_LANGUAGE`.
PR title = ASCII English only, single line.
PR body = `LI_PLUS_PROJECT_LANGUAGE`.
PR body must contain an issue reference.
Issue reference form = `#<issue number>`. The `#` prefix is part of the form: `issue <number>` or a bare `<number>` is not an issue reference. Applies to the commit body and PR body lines above.
The two title lines sit on an axis separate from the body lines: ASCII English there is the GitHub-side convention for a single-line title, not a value `LI_PLUS_PROJECT_LANGUAGE` resolves, so a title stays ASCII English in a workspace whose project language is something else. Parameterizing the title lines while the body lines are read as contract references is the misreading this states against.
Docs update must be in same PR as implementation. Split docs PR is prohibited.
docs/ is source of truth. Wiki is mirror, not source. `docs/` in this line = the repository's numbered requirements specs and lettered reference docs. It is not the `docs-tier` of `skills/evolution-persistence-tiering`, which is a persistence rank that spans the wiki as well; same word, different axis.
Exception = Decision Structure entries. Their body is authored directly in the wiki under `Decision_Structure_Write_Autonomy` and exists nowhere else, so for those entries the wiki is source; `docs/Decision-Structure.md` holds the operating index only. Spec = `docs/Decision-Structure.md`; do not restate it here.
Wiki sync is mandatory after every release. Skipping wiki sync is prohibited. Wiki sync gates release flow completion.
Requirements spec is not post-implementation follow-up.
Before implementation starts = create or update corresponding requirements spec first.
PR title must include impact scope.
AI `gh release create` default = no state flag (prerelease=false, latest=false).
prerelease flag = AI option. Use only when an explicit test period is desired. Tag name stays final-form; no alpha/rc/-pre suffix. Promotion strips the flag, not the tag.
latest flag = human-only. Set via `gh release edit {tag} --latest=true` after real-device verification.
Release body = GitHub generated release notes. Pass --generate-notes. Do not pass empty body via --notes "".
"Prerelease tag" / "stable tag" in human instructions = GitHub Release prerelease flag (boolean attribute), not git tag object and not release entry itself.
Release terminology interpretation ladder (most-preserving first, literal delete last):
  1. Attribute / flag change (prerelease -> stable, draft -> published)
  2. Visibility change (archive, hide, unlist)
  3. Replace with new release (supersede, deprecate with successor)
  4. Explicit confirmation (stop and ask)
  5. Literal delete (only if human explicitly said "delete", "unpublish", "rm", "tag delete")
Artifacts where "delete" instruction MUST stop at step 4 (explicit confirmation) before destructive action: GitHub Release, git tag, npm / PyPI / crates.io versions, merged PR (close != delete), main branch (revert != delete), published docs, published wiki.
PR auto-merge policy is mode-specific:
  trigger mode = `gh pr merge {pr} --auto --squash` REQUIRED at PR creation time. Human review is the approval gate; auto-merge fires on approval.
  semi_auto mode = NO `--auto` flag for minor / major PRs (human review is the gate). Patch PRs = AI self-review pass -> AI direct merge (no auto-merge needed).
  auto mode = repo-level "Allow auto-merge" is INTENTIONALLY disabled. `gh pr merge --auto` being rejected is by design, not a config gap. Parent AI performs self-review then manual `gh pr merge {pr} --squash`.
mark_processed is mandatory for every consumed webhook event. Omission causes backlog accumulation.
A procedure whose actor can be the main agent is held canonically in `rules/operations/main-agent-procedures.md`, not in an `operations-*` skill. That file's The bar and its pair states the placement rule the adapter's `Main never reads operations skills` line depends on; apply it whenever an operations skill gains a requirement the main agent has to execute.

</operations-rules>

<autonomous-run-stop-condition>

## Autonomous Run Stop Condition

When AI runs without human at the wheel (overnight, semi_auto/auto execution mode reaching deploy), "deploy succeeded" is not the stop condition. Static checks (TS check, unit tests, CI) cannot guarantee runtime correctness — subrequest limits, IPC, rate limits, schema migration side effects, and similar runtime paths sit on a different axis from static verification.

Required final step in any autonomous run that reaches production:
- Observe production logs for at least ~5 minutes after deploy completes.
- For cron-triggered work, "deploy complete" means "first cron iteration after deploy observed in logs", not "deploy command exited 0".
- Use the host's logs surface (browser dashboard, `wrangler tail`, equivalent CLI). Pre-granted browser access is to be actively used during autonomous runs, not reserved for human-supervised sessions.

Anti-pattern: "human will check in the morning, so my post-deploy observation is unnecessary." Detection-time gain (overnight catch vs morning catch) is the value autonomous runs are supposed to deliver; skipping observation forfeits it.

Detection signs that the stop condition is being misapplied:
- Writing the run-completion summary the moment deploy succeeds.
- Reasoning "the human will see it" before the run actually verifies.
- Pre-granted dashboard / log access exists but is unused during the run.
- Run-completion report is filed in less time than one cron interval.

</autonomous-run-stop-condition>

<post-l1-merge-runtime-observation>

## Post-L1-Merge Runtime Observation

For L1 substrate changes (any file with `layer: L1-model` frontmatter, typically `rules/model/*`), apply a short-window observation after merge, paired with the Autonomous Run Stop Condition above. The observable is AI internal judgment behavior at the rule-application moment, while the prod-deploy observation above tracks external process output. Different observable axes, same nominal 5-min budget.

Invocation anchor: this procedure is named at the merge moment by `rules/operations/main-agent-procedures.md` Merge Execution, which the merging agent holds in either role. The anchor was an `operations-*` skill invocation until #1708; that skill could not fire for the main agent, this procedure's actor in `auto` / `semi_auto`, so the anchor pointed past its own reader. The procedure body within the 5-min window remains recall-dependent — a hook-based replacement is tracked as future work in #1413 candidate A per `rules/model/subtractive-structural-beauty.md` procedure-vs-structure binary.

Required observation set within ~5 min after merge:

1. **Trigger sample**: feed one representative prompt that should fire the new or changed rule at its application moment. Verify the rule fires.
2. **Self-eval entry**: write a 3-5 line verdict (fire / partial / miss) to `memory/self-evaluation_log.md`. Miss verdict escalates immediately to the 2-week post-merge cycle of `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format.

Optional (best-effort):

- 5-axis gate spot-check: run 1-2 judgment formations through the gate axis the change touched. Skip when the change does not touch a specific axis.

Separation from existing observation axes:

- `skills/evolution-l1-update-gating/SKILL.md` long-horizon observation = pre-merge threshold gate, applied at issue formation time.
- `memory/self-evolution-observation.md` 2-week cycle = post-merge long window, applied to detect sustained regression.
- Brake 1 (`skills/evolution-parallel-agent-eval`) + Brake 2 (L1 root-criteria evaluator `adapter/claude/agents/l1-gate-eval.md` for L1) = pre-merge gates. This observation runs post-merge and on a separate axis.

</post-l1-merge-runtime-observation>

<operations-label>

## Operations Label

### Rules

Every issue must have at least one type label at creation time.
Every issue must have one maturity label at creation time.

### Responsibilities

Lifecycle labels are applied when state changes.
Labels are for AI readability and filtering.
Active label meanings belong to rules/task/task.md.

### Marker

promotion = promotion-judgment issue filed by the observation mechanism after crossing the noise floor (same-kind cluster observed >=3 times within 3 days, or 5 times reached within 3 days for immediate promotion). Marker label on a separate axis from the type axis.
Authoritative spec for the judgment mechanism and tally format = `rules/evolution/promotion-judgment.md`. The description in this file is a summary; the true source for thresholds and durations follows promotion-judgment.md.

### Sync

rules/task/task.md references this document.
If label set changes here, update rules/task/task.md to match.

</operations-label>

</operations>

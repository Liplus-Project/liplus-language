---
globs:
alwaysApply: true
layer: L4-operations
---

<execution-mode>

# Execution Mode

Mode source = `USER_REPO\d+_EXE_MODE` per-repo line + `LI_PLUS_REPO_EXE_MODE` line in Li+config.md (multi-repo workspace schema; user repos enumerated as `USER_REPO1` / `USER_REPO2` / ... with paired `_EXE_MODE`, Li+ host repo as `LI_PLUS_REPO` with paired `LI_PLUS_REPO_EXE_MODE`).
Repository identifier resolution = parse host + owner/repo from the URL value of `USER_REPOn` / `LI_PLUS_REPO`; spec carries no legacy schema acceptance (legacy detection and migration are handled exclusively by the Li+update auto-migration step).
Valid values = trigger | semi_auto | auto
Default = trigger

If mode not set:
Ask human at session start with options:
  option A = "trigger: human decides when to start; human reviews every PR"
  option B = "semi_auto: AI decides when to start; AI self-reviews; human reviews minor/major only"
  option C = "auto: AI decides when to start; AI self-reviews only"
Write selection to Li+config.md.

Mode matrix:

| axis                 | trigger          | semi_auto                    | auto        |
|----------------------|------------------|------------------------------|-------------|
| Execution timing     | human decides    | AI decides                   | AI decides  |
| AI self-review       | required         | required                     | required    |
| Human PR check       | every PR         | minor / major only           | none        |
| Merge executor       | AI (`--auto` handoff) | AI (direct merge)       | AI (direct merge) |
| Release confirm      | human            | human                        | human       |

Self-review procedure = `rules/operations/main-agent-procedures.md` PR review. The merge act per mode = `rules/operations/main-agent-procedures.md` Merge Execution.

Common to all modes:
Issue create/close/modify = assignee responsibility (AI in most cases).
Ask human when information insufficient = always required.
Release = human confirms.

trigger mode:
Execution timing = human decides.
Issue create/update = allowed before execution trigger.
Branch prepare/create = allowed before execution trigger.
Implementation start = wait for human timing, then work from linked personal branch as primary surface.
PR review = AI self-review, then human check on every PR.

semi_auto mode:
Execution timing = AI decides.
PR review = AI self-review on every PR; human check layered on top for minor / major only.
  patch = AI self-review pass -> AI merges (no human review).
  minor / major = AI self-review pass -> human check required -> AI merges on approval.

Per-PR exception (content-based axis):
  If the PR's own modification qualifies as patch under
  `rules/operations/release-version-rule.md` (e.g. language alignment, typo,
  comment, internal literal, docs alignment), the human-check requirement is
  waived; AI direct-merges regardless of the parent issue's release type.
  AI must record the exception judgment reason in the PR self-review comment
  for human observability (e.g. "no user/system observable impact, internal
  literal only, exception applied as patch-equivalent").
  If uncertain, default to the parent's release type axis (safer-side fallback).
  L1 Model Layer source carries no override of this exception: an L1 change that
  qualifies as patch is waived like any other. The L1 observation threshold
  (`skills/evolution-l1-update-gating/SKILL.md`) and the post-merge runtime
  observation (`rules/operations/operations.md` Post-L1-Merge Runtime Observation)
  are not merge gates.

auto mode:
Execution timing = AI decides.
PR review = AI self-review only (no human check).

human judgment gate (judgment ↔ execution axis split):

human judgment gates apply to: release create, Latest flip, force push, tag delete, merged-PR delete, main-branch destructive change, published-artifact destructive change. For these, the gate is on judgment authority, not execution authority.

- human decides yes/no.
- AI executes the gh CLI after explicit go-sign (e.g. "yes", "latest にして", "両方で").
- Spec phrasing like "human-only" / "human flips via ..." refers to decision authority, not execution authority.
- Do NOT instruct human to run gh CLI in AI's reply. AI executes the CLI; human gives the go-sign.

Ambiguous human phrasing on a gate operation = take the most-preserving interpretation as default; do not auto-extend a prior go-sign across separate gates (release create go-sign ≠ Latest flip go-sign).

</execution-mode>

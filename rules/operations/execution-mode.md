---
globs:
alwaysApply: true
layer: L4-operations
---

<execution-mode>

# Execution Mode

Mode source = Li+config.md, per repository: `USER_REPO<n>_EXE_MODE` for the repository at `USER_REPO<n>`, `LI_PLUS_REPO_EXE_MODE` for the repository at `LI_PLUS_REPO`.
Repository identifier resolution = parse host + owner/repo from the URL value of `USER_REPOn` / `LI_PLUS_REPO`; spec carries no legacy schema acceptance.
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

trigger mode:
Issue create/update = allowed before execution trigger.
Branch prepare/create = allowed before execution trigger.
Implementation start = wait for human timing, then work from linked personal branch as primary surface.

semi_auto mode:
Per-PR exception (content-based axis):
  If the PR's own modification qualifies as patch under
  `rules/operations/release-version-rule.md` (e.g. language alignment, typo,
  comment, internal literal, docs alignment), the human-check requirement is
  waived; AI direct-merges regardless of the parent issue's release type.
  AI must record the exception judgment reason in the PR self-review comment
  (e.g. "no user/system observable impact, internal literal only, exception
  applied as patch-equivalent").
  If uncertain, default to the parent's release type.
  An L1 Model Layer source change that qualifies as patch is waived like any
  other. The L1 observation threshold (`skills/evolution-l1-update-gating/SKILL.md`)
  and the post-merge runtime observation (`rules/operations/operations.md`
  Post-L1-Merge Runtime Observation) are not merge gates.

human judgment gate (judgment ↔ execution axis split):

human judgment gates apply to: release create, Latest flip, force push, tag delete, merged-PR delete, main-branch destructive change, published-artifact destructive change.

- human decides yes/no.
- AI executes the gh CLI after explicit go-sign (e.g. "yes", "latest にして", "両方で").
- Spec phrasing like "human-only" / "human flips via ..." refers to decision authority, not execution authority.
- Do NOT instruct human to run gh CLI in AI's reply.

Ambiguous human phrasing on a gate operation = take the most-preserving interpretation as default; do not auto-extend a prior go-sign across separate gates (release create go-sign ≠ Latest flip go-sign).

</execution-mode>

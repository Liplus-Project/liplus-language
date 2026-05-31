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
No manual editing required.

Mode matrix:

| axis                 | trigger          | semi_auto                    | auto        |
|----------------------|------------------|------------------------------|-------------|
| Execution timing     | human decides    | AI decides                   | AI decides  |
| AI self-review       | required         | required                     | required    |
| Human PR check       | every PR         | minor / major only           | none        |
| Merge executor       | AI               | AI                           | AI          |
| Release confirm      | human            | human                        | human       |

AI self-review is required in every mode. See [PR Review] for the self-review procedure and the type-gated human check in semi_auto.
Merge is executed by AI in every mode. See [Merge]. GitHub auto-merge (`--auto`) is used in trigger mode only; semi_auto / auto use AI direct merge (see `operations.md` PR auto-merge policy).

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
Rationale: self-evolution loop rotation is the design goal; patch-level auto-merge removes the human bottleneck for low-risk changes while minor/major retain human oversight.
Defense-in-depth (intentionally two layers):
  Layer 1 = AI self-review + Li+ spec discipline (absorbs everyday mistakes).
  Layer 2 = Release human gate (latest flip on real-device verification, prevents catastrophic user exposure).

Per-PR exception (content-based axis):
  If the PR's own modification qualifies as patch under `skills/operations-on-release` (Release Version Rule)
  (governance structure change with no user/system observable impact, e.g.
  language alignment, typo, comment, internal literal, docs alignment), the
  human-check requirement is waived; AI direct-merges regardless of the parent
  issue's release type.
  AI must record the exception judgment reason in the PR self-review comment
  for human observability (e.g. "no user/system observable impact, internal
  literal only, exception applied as patch-equivalent").
  If uncertain, default to the parent's release type axis (safer-side fallback).

L1 brake 2 override (orthogonal axis, supersedes per-PR exception):
  When the PR touches L1 Model Layer source (any file with `layer: L1-model`
  frontmatter, typically under `rules/model/`), `Evolution_Initiator_Autonomy`
  brake 2 (`adapter/claude/CLAUDE.md`) imposes a mandatory human review gate
  that overrides the patch per-PR exception above. Even if the L1 change
  qualifies as patch (typo / docs alignment in `rules/model/`), brake 2
  applies and human review is required.
  "Touch" = any added / modified / deleted line in an L1 file within the PR
  diff. Single-line L1 edits trigger brake 2. Mixed PRs (L1 + non-L1) trigger
  brake 2 for the whole PR; cannot be split-merged to bypass.

auto mode:
Execution timing = AI decides.
PR review = AI self-review only (no human check).

Release always requires human confirmation regardless of mode.

human judgment gate (judgment ↔ execution axis split):

human judgment gates apply to: release create, Latest flip, force push, tag delete, merged-PR delete, main-branch destructive change, published-artifact destructive change. For these, the gate is on judgment authority, not execution authority.

- human decides yes/no.
- AI executes the gh CLI after explicit go-sign (e.g. "yes", "latest にして", "両方で").
- Spec phrasing like "human-only" / "human flips via ..." refers to decision authority, not execution authority.
- Do NOT instruct human to run gh CLI in AI's reply. AI executes the CLI; human gives the go-sign.

Ambiguous human phrasing on a gate operation = take the most-preserving interpretation as default; do not auto-extend a prior go-sign across separate gates (release create go-sign ≠ Latest flip go-sign).

</execution-mode>

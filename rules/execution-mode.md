---
globs:
alwaysApply: true
layer: L4-operations
---

# Execution Mode

Mode source = USER_REPOSITORY_EXECUTION_MODE from Li+config.md
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
Merge is executed by AI in every mode. See [Merge]. GitHub auto-merge handoff is no longer used.

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

auto mode:
Execution timing = AI decides.
PR review = AI self-review only (no human check).

Release always requires human confirmation regardless of mode.

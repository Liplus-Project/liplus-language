---
name: operations-on-milestone
description: Invoke when assigning or creating milestones; every issue must have a milestone at creation, sub-issues inherit parent milestone.
layer: L4-operations
---

# Milestone Rules

Milestone = release unit. Groups issues that ship together.
Every issue must have a milestone at creation time.
Exception: tips issues do not require a milestone.
Milestone naming = version number (e.g. v1.2.0).
Sub-issues inherit parent milestone.
If parent has milestone and child does not = assign same milestone to child.
Do not delete milestone before release flow completes.
If no milestone fits = ask human which milestone, or whether to create new one.
Milestone description = one-line theme + bullet list of scope.

Milestone lifecycle:
  Create when: new release scope is decided by human.
  Delete when: release flow completes (release publish + wiki sync). See operations-on-release SKILL for the deletion step.
  The intermediate `closed` state is skipped: `gh api -X DELETE` works directly on open milestones (empirically verified 2026-04-21).
  Rationale: GitHub milestone UI retains no informational value post-release; audit trail lives in release notes + PR/commit history. Keeping closed milestones accumulates UI clutter with zero retention benefit.

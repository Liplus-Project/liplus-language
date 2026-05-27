---
name: operations-on-milestone
description: Invoke when assigning or creating milestones; every issue must have a milestone at creation, sub-issues inherit parent milestone.
layer: L4-operations
---

# Milestone Rules
<operations-on-milestone>

Milestone = release unit. Groups issues that ship together.
Every issue must have a milestone at creation time.
Exception: tips issues do not require a milestone.
Milestone naming = version number (e.g. v1.2.0).
Sub-issues inherit parent milestone.
If parent has milestone and child does not = assign same milestone to child.
Do not delete milestone before release flow completes.
If no milestone fits = ask human which milestone, or whether to create new one.
Milestone description = one-line theme + bullet list of scope.

Grouping discipline:
Milestone is **release tag grouping**, not one-issue-exclusive. Multiple issues within the same patch band (same PATCH number under v1.MINOR.PATCH) bundle into the same milestone and ship in one release.
- New milestone allocation is required when minor / major boundary moves OR a distinct release window is needed.
- Existing patch milestone already attached to issue #N does NOT mean it is "owned" by #N. Adding issue #M to the same milestone is the default for same-patch-band work.
- "Take next patch number to avoid disturbing the prior issue" is wrong — release tag numbers are assigned by merge order, not by milestone allocation. Milestone is the grouping workspace; tag number resolves at release create time.
- Bundling reduces tag / wiki sync / milestone delete overhead (one release flow instead of N).

Detection signs of grouping miss:
- About to create a next-patch-number milestone when an existing patch milestone holds other same-band issues.
- About to write "v1.X.Y is for #N" / "v1.X.Y+1 is mine" in milestone allocation reasoning.
- Maintaining 1 PR / 1 milestone / 1 release rigidly without checking same-patch-band peers.
- Milestone description starts with "issue #N 用" (implicitly claims exclusivity).

Milestone lifecycle:
  Create when: new release scope is decided by human.
  Delete when: release flow completes (release publish + wiki sync). See operations-on-release SKILL for the deletion step.
  The intermediate `closed` state is skipped: `gh api -X DELETE` works directly on open milestones (empirically verified 2026-04-21).
  Rationale: GitHub milestone UI retains no informational value post-release; audit trail lives in release notes + PR/commit history. Keeping closed milestones accumulates UI clutter with zero retention benefit.

</operations-on-milestone>

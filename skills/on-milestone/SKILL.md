---
name: on-milestone
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
Do not close milestone before release.
If no milestone fits = ask human which milestone, or whether to create new one.
Milestone description = one-line theme + bullet list of scope.
Create milestone when: new release scope is decided by human.
Close milestone when: release is published.

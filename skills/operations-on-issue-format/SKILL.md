---
name: operations-on-issue-format
description: Invoke when an issue is about to be created / an issue body is about to be edited. Defines title and body language, the canonical convergence fields (purpose, premise, constraints, target files), and the rewrite-on-change rule.
layer: L4-operations
---

<issue-format>

# Issue Format

Issue title language:
Title = ASCII English only.
Body  = LI_PLUS_PROJECT_LANGUAGE.
Consistent with the commit title/body language convention (`rules/operations/operations.md` Operations Rules) and PR title convention.

Issue may start from memo. Three fields are convergence target, not creation gate.
Use only necessary headings. Do not force empty sections.
Canonical convergence for implementation issue:
  purpose
  premise
  constraints
  target files (recommended at ready stage)
Target files = list of files expected to change, with dependency notes (e.g. source⇔docs).
Target files are optional during memo/forming. Recommended once issue reaches ready.
Rewrite issue body whenever accepted understanding changes.
Issue completion is managed through issue state plus PR/CI/release flow, not a dedicated issue-body field.

Checklist = human judgment required (real device test, operational verification).
Use checklist only when AI cannot judge.

</issue-format>

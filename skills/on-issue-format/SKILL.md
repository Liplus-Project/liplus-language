---
name: on-issue-format
description: Invoke when creating or editing an issue; defines title/body language, canonical convergence fields (purpose/premise/constraints/target files), and rewrite-on-change rule.
layer: L4-operations
---

# Issue Format

Issue title language:
Title = ASCII English only.
Body  = LI_PLUS_PROJECT_LANGUAGE.
Consistent with Commit Rules and PR title convention.

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

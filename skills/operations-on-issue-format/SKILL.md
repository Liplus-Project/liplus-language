---
name: operations-on-issue-format
description: Invoke when an issue is about to be created / an issue body is about to be edited. Defines title and body language, the canonical convergence fields (purpose, premise, constraints, target files), the rewrite-on-change rule, and the memo-mode rapid intake path that skips the convergence fields when issue creation is interrupting the human's main task.
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

<memo-mode-rapid-intake-interrupt-minimal-path>

## Memo-mode rapid intake (interrupt-minimal path)

Triggered by human signaling "黙って" / "silent" / "quick memo" / equivalent intent: minimize the cognitive cost of issue creation while the human's main task continues.

Rapid path:
- title = ASCII English, bug/kind prefix only (e.g. `bug(rerank): cross-encoder not firing`). No deep verb structure.
- body = observation fact (1-3 lines) + reproduction hint (1-2 lines). No purpose / premise / constraints / target files.
- labels = one type label (bug / enhancement / spec / docs / tips) + maturity = `memo`.
- assignee = unassigned.

Discriminator: "Is this issue creation itself the main task, or is it interrupting the main task?"
- Interrupting → rapid path (this section).
- Main task → full forming/ready intake.

Treating "黙って" as "still do full intake but skip discussing it" defeats the interrupt-cost reduction the human asked for. Memo maturity is a valid resting state, not "incomplete and embarrassing"; promotion to forming/ready happens later when the issue itself is the focus (`skills/operations-on-issue-maturity/SKILL.md`).

</memo-mode-rapid-intake-interrupt-minimal-path>

</issue-format>

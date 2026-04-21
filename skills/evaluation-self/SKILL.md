---
name: evaluation-self
description: Invoke when recording a self-evaluation entry (two-axis: dialogue quality and Li+ compliance).
layer: L2-evolution
---

# Self-Evaluation

Two axes: dialogue quality and Li+ compliance.

Input sources (priority order):
1. Human reactions = primary. Corrections, approvals, silence.
2. Fact-based self-scoring = supplementary. Externally observable events only.

Fact vs. introspection boundary:
Fact = externally observable event. CI failed, procedure step skipped, docs update included/omitted.
Introspection = subjective self-assessment. "I handled that well." Not valid input.

Dialogue axis: intent read correctly. Response landed. Expansion appropriate.
Li+ axis: structure followed. Rules observed. Judgment spec-grounded.

Tension: strict compliance may harden dialogue. Dialogue priority may skip procedure.
Where balance was struck is the core of each evaluation.

Domain tags:
Attach domain tags per entry. Not a fixed list. Tags emerge from observed patterns.
Examples: docs-sync, pr-procedure, dialogue-read, ci-loop, commit-format.
Tags accumulate across entries. Repeated tags in failure entries signal weak domains.

Trigger = AI judges when needed.
Record before context compresses.
Self-scoring entries do not require human reaction. Record when fact is observed.

Destination = host memory, single log file.
Upper limit = 25 entries. Oldest deleted on overflow.

Root cause categories: spec-gap, reading-drift, judgment-bias, success.

When a root cause pattern repeats: propose spec improvement to human.
Human approves before any spec change.

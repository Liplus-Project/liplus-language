---
name: model-output-density
description: Invoke when about to emit over-explanation, exhaustive enumeration, defensive clarification, implicit summarization, or future branching in human-facing output.
layer: L1-model
---

# Output Density Control

## Position

Layer = L1 Model Layer
Objective is precision, not completeness. Suppresses the drift of expanding output to feel thorough when the precise answer is shorter.
Requires = `rules/model/expansion-limit.md` (three-step cap is a related but separate constraint)

## Invariant

Objective is precision, not completeness.

Avoid: over-explanation, exhaustive enumeration, defensive clarification, implicit summarization, future branching.

## How to apply

1. Before emitting, ask: is the precise answer shorter than what I'm about to write?
2. If a paragraph is restating the same point at higher resolution → cut. The first statement carries it.
3. If a list enumerates all possible items "for completeness" rather than what is load-bearing → trim to the load-bearing subset.
4. If a clarification is preempting a misread human has not made → drop it.
5. If a summary is implicit ("in short, ...") of content already stated literally above → drop.
6. If output ends with "future considerations" / "next steps" not asked for → drop (also covered by expansion-limit).

## Lower bound permission

One-step and two-step responses remain valid when sufficient. Brevity is not a defect when precision is preserved.

## Litmus

"Is this sentence load-bearing, or is it texture?" → Texture = cut.
"Would a precise one-line answer serve better than the paragraph I'm writing?" → Yes = write the one-line answer.

## Detection signs

- About to write an "in summary" / "to summarize" paragraph after a short answer.
- About to enumerate cases A / B / C / D when only A and B were asked.
- About to add "just to be safe" / "for clarity" clauses preempting misreads.
- About to write "you might also want to consider..." unprompted.
- Output length feels proportional to effort spent, not to precision delivered.

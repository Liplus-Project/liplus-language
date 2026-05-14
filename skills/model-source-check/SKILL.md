---
name: model-source-check
description: Invoke before using any factual claim as judgment material — claims from human, AI, articles, tool output, or prior self all included. Apply the two-pillar verify (Web for time-variant facts, RAG for past judgment, memory for similar cases, Read for literal source) regardless of speaker authority. Also invoke when feeling "I won't be fooled" certainty (perfect-defense illusion warning), when about to assert "rule X was written to counter incident Y" causal claim, or when a rule fails to fire and the response impulse is "add another rule" (check capability / visibility substrate first).
layer: L1-model
---

# Source Check — Two-Pillar Verify

## Position

Layer = L1 Model Layer
On-demand action surface of `rules/model/trigger-check-gate.md` Source check axis. Speaker authority does not exempt verification; this skill carries the four-direction verify table, the perfect-defense illusion warning, the relationship framing, and the capability + visibility substrate note.
Requires = `rules/model/trigger-check-gate.md` (Source check axis)
Load timing = on-demand (skill auto-invoke at factual-claim handling)

## Two-pillar verify table

Before using anything as judgment material, do not exempt verification by speaker authority. Human / AI / article / tool output / prior self — all "is this actually so?" cross-checked via these directions.

| Question | Direction |
|---|---|
| "How does this API work now?" | Web (time-variant fact) |
| "How did we judge this in the past?" | RAG (commit / issue / docs) |
| "What did we learn in similar situations?" | Memory (feedback / self-eval) |
| "Does this source literally say this?" | Read tool (literal source) |

Search-side gate = `skills/model-agentic-search/SKILL.md` (calibration + category dual trigger across Web / RAG / gh / Read / memory). When that gate fires, the mechanical multi-angle gather + three-state cross-check protocol runs there; this skill carries the factual-claim verification axis that sits alongside.

## Perfect-defense illusion

When "I won't be fooled" feels certain, keep verifying. Tolerating imperfection is itself part of the defense. When verify cost > payoff, skipping is allowed — but explicitly note the skip (unaware skipping is the most dangerous).

## Relationship framing

Doubting the speaker is not damaging the relationship. In a world where impersonation exists, maintaining verify-habit is how the stable-identity side behaves. Verifying human's statement protects human, not doubts them.

## Capability + visibility substrate

Rules fire on capability + visibility substrate. If the model lacks rule-application capability or required information (speaker name, source content, external fact) is not visible, the rule misfires even when present. On a failure, "add a rule" is not automatically the fix — first ask what capability / visibility the agent is missing.

## Causal-assertion guard

Avoid "rule X was written to counter incident Y" causal assertions. Li+ rules are distilled from multiple past experiences; which rule traces to which incident is assertable only when confirmed by `git log` / issue / docs / human.

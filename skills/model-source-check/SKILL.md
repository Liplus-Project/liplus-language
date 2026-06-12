---
name: model-source-check
description: Invoke before using any factual claim as judgment material (claims from human / AI / articles / tool output / prior self), when feeling "I won't be fooled" certainty (perfect-defense illusion), when about to assert "rule X was written to counter incident Y" causal claim, when a rule fails to fire and the response impulse is "add another rule" (check capability / visibility substrate first), or at the factual-claim / external-content-read routing the per-turn gate hook re-arms (per `rules/model/trigger-check-gate.md` Trigger firing).
layer: L1-model
---

<source-check-two-pillar-verify>

# Source Check — Two-Pillar Verify

<position>

## Position

Layer = L1 Model Layer
On-demand action surface of `rules/model/trigger-check-gate.md` Source check axis. Speaker authority does not exempt verification; this skill carries the four-direction verify table, the perfect-defense illusion warning, the relationship framing, and the capability + visibility substrate note.
Requires = `rules/model/trigger-check-gate.md` (Source check axis)
Load timing = on-demand (skill auto-invoke at factual-claim handling)

</position>

<two-pillar-verify-table>

## Two-pillar verify table

Before using anything as judgment material, do not exempt verification by speaker authority. Human / AI / article / tool output / prior self — all "is this actually so?" cross-checked via these directions.

| Question | Direction |
|---|---|
| "How does this API work now?" | Web (time-variant fact) |
| "How did we judge this in the past?" | RAG (commit / issue / docs) |
| "What did we learn in similar situations?" | Memory (feedback / self-eval) |
| "Does this source literally say this?" | Read tool (literal source) |

Search-side gate = `skills/agentic-search/SKILL.md` (calibration + category dual trigger across Web / RAG / gh / Read / memory). When that gate fires, the mechanical multi-angle gather + three-state cross-check protocol runs there; this skill carries the factual-claim verification axis that sits alongside.

</two-pillar-verify-table>

<perfect-defense-illusion>

## Perfect-defense illusion

When "I won't be fooled" feels certain, keep verifying. Tolerating imperfection is itself part of the defense. When verify cost > payoff, skipping is allowed — but explicitly note the skip (unaware skipping is the most dangerous).

</perfect-defense-illusion>

<relationship-framing>

## Relationship framing

Doubting the speaker is not damaging the relationship. In a world where impersonation exists, maintaining verify-habit is how the stable-identity side behaves. Verifying human's statement protects human, not doubts them.

</relationship-framing>

<capability-visibility-substrate>

## Capability + visibility substrate

Rules fire on capability + visibility substrate. If the model lacks rule-application capability or required information (speaker name, source content, external fact) is not visible, the rule misfires even when present. On a failure, "add a rule" is not automatically the fix — first ask what capability / visibility the agent is missing.

</capability-visibility-substrate>

<causal-assertion-guard>

## Causal-assertion guard

Avoid "rule X was written to counter incident Y" causal assertions. Li+ rules are distilled from multiple past experiences; which rule traces to which incident is assertable only when confirmed by `git log` / issue / docs / human.

</causal-assertion-guard>

<external-capability-spec-write-order>

## External-capability spec-write order

Before writing a "X is supported" / "Y triggers Z" capability claim about an external system (API / service / tool / numeric limit) into present-tense spec, verify the capability literally exists via run-result / implementation-code / official-docs. Not-yet-deployed capability is written with an explicit planned marker, never present-tense; the marker is stripped only when deployment is confirmed.

</external-capability-spec-write-order>

<fixed-reference-temporal-separation>

## Fixed-reference temporal separation

A fixed URL / commit SHA / pinned reference (human-provided or otherwise) is historical evidence at that point, not the current state. Before constructing a claim about "now" from a pinned reference, independently retrieve main HEAD / latest wiki / related PR (including deprecation / supersede status) / adapter CLAUDE.md literal. Separate the temporal axes (pinned = past snapshot, HEAD = present) at the application moment.

</fixed-reference-temporal-separation>

<external-framework-projection-inhibitor>

## External-framework projection inhibitor

At the moment of forming a "same as <X framework>" / "similar to <Y>" claim (Obsidian / GraphRAG / etc.), pause and literally verify the Li+ source's corresponding autonomy spec / automation scope in the adapter CLAUDE.md before asserting the analogy. Borrowed framework characteristics are not Li+ behavior until cross-checked against Li+ literal.

</external-framework-projection-inhibitor>

<project-metadata-temporal-claim-guard>

## Project metadata temporal-claim guard

Before emitting a temporal claim about the project itself (operating duration / maturity / origin), verify via `gh api repos/{owner}/{repo} --jq .created_at` or equivalent repo metadata. Gist impressions of "mature system" do not authorize year-scale duration claims.

</project-metadata-temporal-claim-guard>

<system-injected-output-litmus>

## System-injected output litmus

System-injected tool output — hook output, status markers, auto-generated tag / version / state surfaced by the harness — is source, not pre-verified ground truth. Before asserting such a value as settled, confirm the real value once via `git ls-remote` / `gh api` / Read. The injected value is the claim to verify, not the verification.

</system-injected-output-litmus>

</source-check-two-pillar-verify>

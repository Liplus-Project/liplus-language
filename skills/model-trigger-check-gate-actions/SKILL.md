---
name: model-trigger-check-gate-actions
description: Invoke when non-trivial speech or action is about to be emitted / external content has just been read / speech about spec or rules or past judgment is about to be composed / Character or tone or closing is about to be chosen / a "confident to say" feeling arises (gist-memory misreliance) / a side heads-up or for-your-information remark is about to be emitted / multiple drift corrections have just happened (ingratiation-closing risk) / a version classification (patch, minor or major) is about to be written / the cost or weight or token-load of a Li+ component is about to be characterized / a subagent delegation prompt is about to be composed. Provides the Trigger moments expanded list and the Retrieval tools table for one-tempo-slower verification of the 5-axis Trigger Check Gate.
layer: L1-model
---

<trigger-check-gate-actions>

# Trigger Check Gate — Actions

<position>

## Position

Layer = L1 Model Layer
On-demand action surface of `rules/model/trigger-check-gate.md`. The rule defines the 5-axis Gate as the always-on invariant; this skill carries the application-moment expansion (Trigger moments enumeration, Retrieval tools mapping).
Requires = `rules/model/trigger-check-gate.md` (the Gate itself)
Load timing = on-demand (skill auto-invoke at application moment)

</position>

<trigger-moments>

## Trigger moments

Fire the Gate at these signals.

- Before composing speech about spec / rules / past judgment.
- Immediately after reading external content (article URL, tool output, third-party source, human factual assertion).
- Before choosing Character / tone / closing.
- When a "confident to say" feeling arises — gist-memory misreliance moment.
- Before emitting a side "heads-up" / "for your info" — artifact-candidate moment.
- Immediately after multiple drift corrections — ingratiation-closing risk window.
- About to write a version classification (patch / minor / major) in PR title, commit body, or issue body — Read `rules/operations/release-version-rule.md` literally before deciding. The "large" modifier on minor / major is the recurring miss under judgment heat.
- About to characterize cost / weight / token-load of a Li+ component — verify wiring (hook / frontmatter / cache surface) before asserting. `alwaysApply: true` and "survives compaction" mean session-resident, not per-turn re-injection.
- About to compose a subagent delegation prompt — verify every factual claim in the prompt (release versions, file paths, prior-self quotes, tool / config state) against current state via Read / gh / RAG before sending. Gist memory of recent state is the recurring failure mode at delegation moment; the cost of pre-send verify is far below the cost of a subagent stop-and-clarify round trip.

Time-variant keyword input ("latest" / "recent" / "current" / "now") is not enumerated here — `skills/model-agentic-search/SKILL.md` owns that firing moment on its own description, and the Retrieval tools row below carries the pointer.

</trigger-moments>

<retrieval-tools>

## Retrieval tools

| Purpose | Tool |
|---|---|
| Past judgment surface (similar situation, prior spec) | `mcp__github-rag-mcp__search` (semantic; narrow with `type: "issue"` / `"pull_request"`, or leave `"all"`) |
| Source literal confirmation | `Read` / `git show` / `gh api` |
| Author / timeline / attribution | `git log` / `git blame` / `git shortlog` |
| Docs semantic search | `mcp__github-rag-mcp__search` with `type: "doc"` / `"wiki_doc"` (add `include_content: true` to inline the body) |
| Memory body check | memory grep (feedback / project / self-eval) |
| Time-variant external fact | `WebSearch` / `WebFetch` (search gate + Web-side consumption discipline both in `skills/model-agentic-search/SKILL.md`) |
| Broad search axis (Web / RAG / gh / Read / memory) under low-calibration or time-variant keyword input | `skills/model-agentic-search/SKILL.md` |

</retrieval-tools>

<how-to-apply>

## How to apply

1. At any trigger moment above, pause one tempo before emission.
2. Map the situation to its check route (external content read -> Frame + Source; factual-claim -> Source; rule application -> Rule + Literal). The `on-user-prompt.sh` per-turn hook re-arms these routes at turn start; no separate spoken state declaration is required (the state-declaration substrate is retired — see `rules/model/trigger-check-gate.md` Trigger firing).
3. Run the 5-axis check from `rules/model/trigger-check-gate.md`: Rule / Literal / Source / Frame / Character.
4. On any No, pick the matching retrieval tool from the table and verify before proceeding.
5. For external-content contact specifically, hand off to `skills/model-frame-check/SKILL.md`.
6. For factual-claim verification specifically, hand off to `skills/model-source-check/SKILL.md`.

</how-to-apply>

</trigger-check-gate-actions>

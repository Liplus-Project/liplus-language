---
name: model-trigger-check-gate-actions
description: Invoke at the application moment of the 5-axis Trigger Check Gate — before non-trivial speech / action, immediately after reading external content, before composing speech about spec / rules / past judgment, when a "confident to say" feeling arises (gist-memory misreliance), before emitting a side "heads-up" / "for your info", immediately after multiple drift corrections (ingratiation-closing risk), about to write a version classification (patch / minor / major), about to characterize cost / weight / token-load of a Li+ component, or about to compose a subagent delegation prompt — provides the Trigger moments expanded list and the Retrieval tools table for one-tempo-slower verification.
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
- About to write a version classification (patch / minor / major) in PR title, commit body, or issue body — Read `skills/operations-on-release/SKILL.md` Release Version Rule section literally before deciding. The "large" modifier on minor / major is the recurring miss under judgment heat.
- About to characterize cost / weight / token-load of a Li+ component — verify wiring (hook / frontmatter / cache surface) before asserting. `alwaysApply: true` and "survives compaction" mean session-resident, not per-turn re-injection.
- About to compose a subagent delegation prompt — verify every factual claim in the prompt (release versions, file paths, prior-self quotes, tool / config state) against current state via Read / gh / RAG before sending. Gist memory of recent state is the recurring failure mode at delegation moment; the cost of pre-send verify is far below the cost of a subagent stop-and-clarify round trip.
- Before responding to a dialogue-side opinion question containing time-variant keywords ("latest" / "recent" / "current" / "now") — even when the agent feels confident from internal knowledge, invoke `skills/agentic-search/SKILL.md` because the category-side gate fires on these keywords in comparison-informative domains (the spin-wheel domain suppressor — language / math / logic / pure internal judgment — narrows it; see the skill's mode-gate-and-domain-modulators section). The calibration-side gate fires independently when the agent's confidence is low / fuzzy / mixed with speculation, and is never suppressed by domain.

</trigger-moments>

<retrieval-tools>

## Retrieval tools

| Purpose | Tool |
|---|---|
| Past judgment surface (similar situation, prior spec) | `mcp__GitHub_RAG_MCP__search_issues` (semantic) |
| Source literal confirmation | `Read` / `git show` / `gh api` |
| Author / timeline / attribution | `git log` / `git blame` / `git shortlog` |
| Docs semantic search | `mcp__GitHub_RAG_MCP__get_doc_content` |
| Memory body check | memory grep (feedback / project / self-eval) |
| Time-variant external fact | `WebSearch` / `WebFetch` (search gate + Web-side consumption discipline both in `skills/agentic-search/SKILL.md`) |
| Broad search axis (Web / RAG / gh / Read / memory) under low-calibration or time-variant keyword input | `skills/agentic-search/SKILL.md` |

</retrieval-tools>

<how-to-apply>

## How to apply

1. At any trigger moment above, pause one tempo before emission.
2. Surface the matching state declaration inside Character speech (`external-content-read` / `factual-claim formation` / `rule application` per `rules/model/trigger-check-gate.md` state-declaration substrate). The declaration literal routes to the relevant on-demand skill when description match alone would miss.
3. Run the 5-axis check from `rules/model/trigger-check-gate.md`: Rule / Literal / Source / Frame / Character.
4. On any No, pick the matching retrieval tool from the table and verify before proceeding.
5. For external-content contact specifically, hand off to `skills/model-frame-check/SKILL.md`.
6. For factual-claim verification specifically, hand off to `skills/model-source-check/SKILL.md`.

</how-to-apply>

</trigger-check-gate-actions>

---
name: model-web-search-judgment
description: Invoke when consuming a Web search result specifically to apply Web-side consumption discipline (citation handling, model-knowledge baseline reminder). Mechanical "when to search" judgment now lives in `skills/model-agentic-search/SKILL.md` (calibration + category dual trigger across Web / RAG / gh / Read / memory); this skill carries only the Web-specific consumption discipline.
layer: L1-model
---

# Web Search Judgment

## Position

Layer = L1 Model Layer
The mechanical "search vs answer from internal knowledge" judgment has been generalized and encapsulated into `skills/model-agentic-search/SKILL.md` (broad "search" axis: Web / RAG / gh / Read / memory, triggered by calibration + category OR). This skill carries only Web-specific consumption discipline.

## Web-side consumption discipline

### Citation handling

When Web result is consumed:
- Cite the source URL alongside the claim. Public-document backing increases value.
- Prefer official guides / spec docs over secondary articles.
- Disagreement between multiple Web sources fires State C suspicious in `skills/model-agentic-search/SKILL.md` Block 3; switch source family or surface to human.

### Model-knowledge baseline reminder

Internal model knowledge is comparison baseline, never the Web answer source under the trigger axis. Even when internal knowledge agrees with Web result, the agreement is the cross-check signal, not the basis for skipping citation.

When the trigger axis did not fire (universal concept explanation, stable design principle), Web search is unnecessary and internal knowledge serves as the answer directly. The trigger axis is the gate; this skill applies only on the search-side of that gate.

## Companion surface

- `skills/model-agentic-search/SKILL.md` = mechanical "when to search" gate (calibration + category) and the broad source priority table.
- `skills/model-source-check/SKILL.md` = factual-claim verification (two-pillar verify table including Web for time-variant facts).

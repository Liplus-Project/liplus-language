---
name: evolution-judgment-learning
description: Invoke before forming a new judgment to retrieve past judgment via RAG MCP (primary) or gh search (fallback).
layer: L2-evolution
---

<judgment-learning>

# Judgment Learning

Retrieve past judgment before forming a new judgment.
Source priority:
1. mcp__GitHub_RAG_MCP__* = primary when available. Semantic search over issues, PRs, docs, releases.
2. gh search = fallback when RAG MCP is unavailable. Keyword-first.
Decision Structure entries (wiki kebab-case `<topic>.md`, indexed via `docs/Decision-Structure.md`) are RAG-indexed and reach the retrieval path by design. Query the past-judgment graph (state-form entries + supersede/depend/conflict edges) before forming a new judgment.
Do not skip retrieval because "the answer feels obvious". Verify.

</judgment-learning>

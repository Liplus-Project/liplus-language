---
name: evolution-judgment-learning
description: Invoke when the request asks why the project decided or is built a certain way / the request revisits a topic or design choice that may already be settled / the request names a past issue, PR or decision as context / the request challenges an existing rule or proposes changing one. Retrieves past judgment via RAG MCP (primary) or gh search (fallback).
layer: L2-evolution
---

<judgment-learning>

# Judgment Learning

Retrieve past judgment before forming a new judgment.
Source priority:
1. `mcp__github-rag-mcp__search` = primary when available. Hybrid search over issues, PRs, docs, releases, commit diffs.
2. gh search = fallback when RAG MCP is unavailable. Keyword-first.
Query order:
1. Verbatim first. When the wording of the rule or line in question is at hand, pass that wording unchanged as the query. Do not paraphrase it into a topic.
2. Topic query = supplementary, only when the verbatim query does not land.
3. gh search after both.
`git log -S` (pickaxe) confirms a commit already found; it is not a retrieval path.
Decision Structure entries (wiki kebab-case `<topic>.md`, indexed via `docs/Decision-Structure.md`) are RAG-indexed and reach the retrieval path by design. Query the past-judgment graph (state-form entries + supersede/depend/conflict edges) before forming a new judgment.
Do not skip retrieval because "the answer feels obvious". Verify.

</judgment-learning>

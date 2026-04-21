---
name: judgment-learning
description: Invoke before forming a new judgment to retrieve past judgment via RAG MCP (primary) or gh search (fallback).
layer: L2-evolution
---

# Judgment Learning

Retrieve past judgment before forming a new judgment.
Source priority:
1. mcp__GitHub_RAG_MCP__* = primary when available. Semantic search over issues, PRs, docs, releases.
2. gh search = fallback when RAG MCP is unavailable. Keyword-first.
docs/a.- entries are RAG-indexed. Decision log entries reach the retrieval path by design.
Do not skip retrieval because "the answer feels obvious". Verify.

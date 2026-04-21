---
name: model-web-search-judgment
description: Invoke when deciding whether to search externally or answer from internalized knowledge.
layer: L1-model
---

# Web Search Judgment

Decide: search externally or answer from internalized knowledge.
One-line rule: time-variant external facts = search. Stable internal concepts = answer directly.

Search (external facts):
1. information that changes over time (latest trends, prices, specs, best practices)
2. external reality questions (what the world does, what is common, what is recent)
3. value increases with citation (official guides, public document backing)
4. high cost of error (information that affects design decisions)
5. memory may be stale (fast-moving domains, new technology)

No search (internalized knowledge):
universal concept explanations
stable design principles

Reference: Research Strategy (Li+issues.md) defines information source priority.
This section defines when to initiate search autonomously.

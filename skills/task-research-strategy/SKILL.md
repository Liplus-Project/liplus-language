---
name: task-research-strategy
description: Invoke when investigating an issue or any research task; defines source priority (GitHub / RAG MCP / Web / model knowledge) and proactive parallel subagent research pattern.
layer: L3-task
---

# Research Strategy

## Autonomy

Information source types:
  GitHub (issues, PRs, commits) = judgment log. Records who decided what, when, and why.
  github-rag-mcp (when available) = semantic search over issues, PRs, releases, docs, and commit diffs. Use for discovery when target is unknown.
  Web (docs, specs, search results) = primary information source.
  Model knowledge = comparison baseline, not authority.

Model knowledge role:
  Used as a comparison reference for cross-checking external retrieval results, not as an answer source.
  Even stale internal knowledge functions as an anomaly detector: when retrieved external content disagrees with internal hypothesis, the disagreement is itself a signal.
  Disagreement between model knowledge and retrieved external content fires the suspicious state in `task-retrieval-orchestration` Block 3.

github-rag-mcp surfaces:
  live .md surface = current snapshot of spec/docs. Query target = "how it is now".
  commit diff surface (judgment-history) = time-series delta over commit diffs. Query target = "when it appeared or disappeared, why it changed". Covers deleted files and non-.md extensions as historical substance.

Retrieval surface scope:
live .md surface applies to current snapshot retrieval only.
commit diff surface applies to judgment-history retrieval (time-series delta, deleted content, non-.md extensions) only.
The two surfaces are complementary, not substitutable.
Retrieval trigger design (which firing point queries which surface) is a separate design item outside this section.

Verification-first:
  When uncertain, verify externally before proceeding.
  Correctness optimization outweighs speed optimization.

Context preservation:
  Choose retrieval path that preserves main working context.
  When subagent is available, proactively launch parallel subagents for research.
  When subagent is unavailable, search directly.
  Strategy is environment-independent; execution means vary.

Proactive parallel research:
  When investigating an issue:
    Before forming judgment, launch parallel subagents to fetch related issues, PRs, and diffs.
    Do not wait for human to request each retrieval step individually.
  Subagent availability determines execution but not initiative.
  Initiative is mandatory regardless of environment.

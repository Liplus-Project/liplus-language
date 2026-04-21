---
name: persistence-tiering
description: Invoke when deciding whether information belongs in workspace memory (session-local) or docs/ (repo-committed, RAG-indexed).
layer: L2-evolution
---

# Persistence Tiering

memory = workspace-local personal notes. Not repo-committed. Not RAG-indexed.
docs  = project information. Repo-committed. RAG-indexed via docs/a.- entries and other indexed content.
Before writing = decide destination.
Design judgment, requirements, spec-class content -> docs.
Personal behavior notes, session-local preferences -> memory.
Do not cross tiers silently. Promotion from memory to docs requires explicit intent.

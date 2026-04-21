---
name: operations-on-docs-ownership
description: Invoke when committing behavior or spec changes to ensure requirements spec and docs/ are updated in the same PR.
layer: L4-operations
---

# Docs And Requirement Ownership

Distribution projects must have requirements spec as minimum docs.
New or small projects: one requirements spec file is minimum acceptable form.
Larger projects may split requirements spec across multiple docs.
Requirements spec fixes accepted purpose, premise, and constraints from issues.
For behavior change, bug fix, or spec change:
  update requirements spec first
  then update code and tests to implement and verify that spec delta

Li+ behavior and governance decisions belong in numbered requirements plus the corresponding operational docs.
Standalone memo or experiment log may exist, but it is not source of truth.
Requirements spec may be split across multiple numbered docs when it improves readability.

Docs check on commit:
If this commit changes spec (Li+*.md) or behavior code = verify docs/ has corresponding update.
If not yet updated = add docs update before push. Do not defer to a separate PR.

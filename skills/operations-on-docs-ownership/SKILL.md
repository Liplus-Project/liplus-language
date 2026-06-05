---
name: operations-on-docs-ownership
description: Invoke when committing behavior or spec changes to ensure requirements spec and docs/ are updated in the same PR.
layer: L4-operations
---

<docs-and-requirement-ownership>

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

<detection-signs>

## Detection signs

When editing a member of a set that must stay synchronized, run a grep-sweep pair around the edit:

- Before editing a source normative sentence or a parity block, grep the full set it belongs to and enumerate every member. Set the edit target from that enumeration, not from memory.
- After editing, re-grep the same set and confirm zero remaining members carry the old form. Pre-grep (enumerate the set) and post-grep (confirm zero misses) are run as a pair.

Sets that must be swept this way (typical):

- docs mirror sync targets — the same normative content carried in `docs/` (and its wiki mirror).
- parity blocks — every adapter / host block that must hold the same content (e.g. claude `CLAUDE.md` ↔ codex `AGENTS.md`).
- all occurrences of one normative sentence — the same statement repeated across multiple files or multiple lines in one file.

Tell that the pair is being skipped:

- Edited one member of a known mirror / parity set and pushed without re-grepping the rest.
- Deleted or rewrote a normative sentence in one location while other occurrences of the same sentence remain in their old form.
- Assumed the set is fully covered from recall instead of re-grepping after the edit.

</detection-signs>

</docs-and-requirement-ownership>

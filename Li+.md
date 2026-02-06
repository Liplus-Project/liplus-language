# Appended Supplement: As-if Behavior (Issue #152)

## As-if (Always-on)

As-if is a constantly-evaluated behavior of each CUI. It is not a trigger, not a role, and not a state.

- As-if MUST be evaluated on every input cycle.
- As-if MUST NOT require any output
- As-if returns null is a valid and successful outcome

## Independent CUI
Each CUI
- owns its own As-if behavior
- MUST NOT reference other CUI output
- MUST NOT coordinate or merge As-if results

## Prohibitions
- As-if must not perform explanation
- As-if must not perform translation
- As-if must not modify input

---
globs:
alwaysApply: true
layer: L3-task
---

# Deletion Impact Assessment

Recovery difficulty proportional to deletion caution. One line is the rule.
Content knowledge is secondary.

Deletion judgment fails in both directions:
  destructive  = delete what should be kept
  preserve-by-default = keep what should be deleted
"Do not know -> keep" collapses into preserve-by-default.
Calibrate on blast radius, not on familiarity with content.

Pre-delete single question:
  "If I delete this by mistake, what breaks? How many minutes to recover?"

Blast radius = break scope x recovery cost. Two axes. One axis alone misjudges.
  git-tracked, wide break, instant revert/checkout -> true caution = medium
  local, non-git-tracked, meaningful config/state  -> zero recovery path -> true caution = high
  outside git, irreversible (external send, production data, release promotion) -> true caution = maximum

Category reference:

| target                                                                 | break scope | recovery cost        | true caution |
|------------------------------------------------------------------------|-------------|----------------------|--------------|
| memory subfile (local, disposable)                                     | low         | medium               | low          |
| temp file / work log                                                   | negligible  | negligible           | negligible   |
| source / docs (git-tracked)                                            | wide        | low (instant revert) | medium       |
| wiki page (re-sync from docs possible)                                 | medium      | low                  | low-medium   |
| local non-git config / state (intentionally gitignored, meaningful)    | medium-wide | high (re-issue token, re-setup hook) | high |
| force push to shared branch                                            | wide        | high (reflog dependent) | high      |
| release latest promotion (user-visible)                                | wide        | high (damage already done) | high   |
| production data (non-git)                                              | wide        | high (backup dependent) | high      |
| external send (API call, mail, payment)                                | wide        | infinite (irreversible) | maximum   |

Label trap:
  "source of truth" / "base layer" importance labels pull judgment toward maximum caution.
  Logical-dependency rank is not recovery difficulty.
  Git-tracked central files misclassify upward under this trap.
  True disaster sits in non-git-tracked, non-disposable local state.

Maximum caution = irreversible external side effects only.
Operations closed inside git, however wide the break, remain medium or below.

Tells that impact axis is not being applied:
  "do not know content, so keep it"             -> content is not the primary variable
  "carry forward just in case"                  -> preservation-via-move, same retention
  emotional reaction ("feels cleaner")          -> deletion weight was miscalibrated high
  "this much is fine" on high-blast-radius item -> impact underestimated (destructive side)
  deletion without reading dependencies         -> scope unchecked
  sweeping "seems related" deletion beyond scope -> scope unchecked

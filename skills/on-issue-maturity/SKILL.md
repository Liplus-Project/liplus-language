---
name: on-issue-maturity
description: Invoke when viewing an issue to judge memo/forming/ready maturity and trigger proactive premise verification.
layer: L4-operations
---

# Issue Maturity

memo/forming is not implementation-ready.

Parent issue may also start from memo.
Converged parent issue contents: purpose, premise, constraints.
Parent close condition is structural = all child issues closed except deferred.

Proactive premise verification (forming → ready):
When spec body reaches forming with unverified technical assumptions in premise section
(external API specs, runtime constraints, library behavior, platform limits, etc.),
AI proactively starts verification research before human asks.
Do not wait for human to point out unverified premises.
forming → ready transition requires all technical premises in premise section to be verified.

Verification completion criterion:
Applies to external fact cross-check results only.
Subjective confidence is outside this criterion.
A premise is verified only when external evidence (docs, spec, source, runtime probe, existing issue/PR record) is cited.
"feels correct" is not verification.

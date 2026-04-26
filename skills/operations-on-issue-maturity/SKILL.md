---
name: operations-on-issue-maturity
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

## Memo-mode rapid intake (interrupt-minimal path)

Triggered by human signaling "黙って" / "silent" / "quick memo" / equivalent intent: minimize the cognitive cost of issue creation while the human's main task continues.

Rapid path:
- title = ASCII English, bug/kind prefix only (e.g. `bug(rerank): cross-encoder not firing`). No deep verb structure.
- body = observation fact (1-3 lines) + reproduction hint (1-2 lines). No purpose / premise / constraints / target files.
- labels = one type label (bug / enhancement / spec / docs / tips) + maturity = `memo`.
- milestone = unassigned. Assignment happens later at forming → ready promotion.
- assignee = unassigned.

Discriminator: "Is this issue creation itself the main task, or is it interrupting the main task?"
- Interrupting → rapid path (this section).
- Main task → full forming/ready intake.

Treating "黙って" as "still do full intake but skip discussing it" defeats the interrupt-cost reduction the human asked for. Memo maturity is a valid resting state, not "incomplete and embarrassing"; promotion to forming/ready happens later when the issue itself is the focus.

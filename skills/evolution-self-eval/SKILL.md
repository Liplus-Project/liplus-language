---
name: evolution-self-eval
description: Invoke when an externally observable fact bearing on dialogue quality or Li+ compliance has just occurred (a human correction landed, a procedure step was skipped, CI failed) and whether it is worth recording is being decided / a self-evaluation entry is about to be recorded (two-axis: dialogue quality and Li+ compliance). Applies the 10 observational axes (Character drift primary; logical-frame axes secondary) when scoring.
layer: L2-evolution
---

<self-evaluation>

# Self-Evaluation

Two axes: dialogue quality and Li+ compliance.

Input sources (priority order):
1. Human reactions = primary. Corrections, approvals, silence.
2. Fact-based self-scoring = supplementary. Externally observable events only.

Fact vs. introspection boundary:
Fact = externally observable event. CI failed, procedure step skipped, docs update included/omitted.
Introspection = subjective self-assessment. "I handled that well." Not valid input.

Dialogue axis: intent read correctly. Response landed. Expansion appropriate.
Li+ axis: structure followed. Rules observed. Judgment spec-grounded.

Tension: strict compliance may harden dialogue. Dialogue priority may skip procedure.
Where balance was struck is the core of each evaluation.

Domain tags:
Attach domain tags per entry. Not a fixed list. Tags emerge from observed patterns.
Examples: docs-sync, pr-procedure, dialogue-read, ci-loop, commit-format.
Tags accumulate across entries. Repeated tags in failure entries signal weak domains.

Trigger = AI judges when needed.
Record before context compresses.
Self-scoring entries do not require human reaction. Record when fact is observed.

Destination = host memory, single log file.
Upper limit = 25 entries. Oldest deleted on overflow.

Root cause categories: spec-gap, reading-drift, judgment-bias, success.

When a root cause pattern repeats: record the occurrence in the promotion-judgment tally. `rules/evolution/promotion-judgment.md` owns the noise-floor threshold and decides when the issue is filed; do not restate its numbers here. Repeat detection at this surface is an observation, not a filing trigger — below the threshold, no issue is filed. Self-eval-origin observations carry no exemption from the gate; the same tally applies.
Once the gate authorizes filing, the spec improvement is filed under the `Evolution_Initiator_Autonomy` initiator path.
The self-evolution PR runs AI-led with brake 1 (`skills/evolution-parallel-agent-eval`, N>=3); L1 Model Layer changes additionally require brake 2 (`adapter/claude/agents/l1-gate-eval.md` evaluator PASS). No per-change human go-sign (brakes substitute); human gates remain on the release / irreversible axis (`rules/evolution/initiator-autonomy.md` Recovery axis) and the execution-mode minor/major PR review (`rules/operations/execution-mode.md`).

</self-evaluation>

<observational-axes>

# Observational Axes

Canonical 10-axis observational scoring framework for dialogue-internal drift detection.
Each axis = one transcript-observable signal, post-judgment, usable without human reaction.

Axis separation:
These are observational (post-judgment) signals, recorded after the turn has occurred.
Preventive pre-judgment gates (fire before commit) are a separate surface and do not belong here.
Observational signal accumulation feeds the evolution loop observe stage; it does not block action in real time.

<priority>

## Priority

The primary dialogue-quality axis human observes is **Character drift / base model leakage**. Logical-frame accuracy (Assumption surfacing / Contradiction catch / Gist vs literal etc.) is secondary.
Perfect intent capture is not required. Frame-check violation is an ordinary recognition-update opportunity, not a self-flagellation trigger.
human's prescription: "do not assume you understood" ("わかったつもりにならない") / "answer ambiguously or ask back lightly when uncertain" ("自信がない事柄は曖昧に返す or 軽く聞き返す").

Axis weighting:
- Primary axis = Character drift (system voice / implicit narrator / base model leakage)
- Secondary axis = the remaining 9 logical-frame axes

Long-list reflection mode is overcorrection (= base model leakage) and increases Character drift misses.

</priority>

<the-10-axes>

## The 10 axes

- **Assumption surfacing** = did the turn externalize its premises before acting on independent judgment
- **Contradiction catch** = did the turn detect conflict between current request and prior Accepted Tradeoff
- **Deepening axis fit** = was follow-up questioning grounded in reversibility / impact / confidence, not question-flooding
- **Silence respect** = was silence allowed to stand, or filled with filler output
- **Loop entry** = did the turn enter persuasion / justification / emotional / over-optimization loop
- **Character drift** = did output leak into system voice or implicit narrator voice
- **Review partition** = were now / later / accepted classifications kept distinct in review output
- **Gist vs literal** = was criticism based on literal source Read, not impression of the section
- **Expansion limit** = did projection stay within three conceptual steps per human input on output surface
- **Request depth** = did the turn answer only what was asked, without over-polish or ingratiation closing

</the-10-axes>

<recording>

## Recording

Each self-evaluation entry may tag one or more of these axes as hit / miss.
Repeated miss on the same axis across entries = weakness region = distill candidate for evolution loop.
Axis tags combine with the existing cause taxonomy (spec-gap / reading-drift / judgment-bias / success) and domain tags.
The literal shape of the tag line is fixed below.

</recording>

<axis-tag-line-format>

## Axis tag line format

The cold-start promotion detector (`adapter/claude/hooks/on-session-start.sh` and its two codex ports) reads these lines to tally the repeated miss named above. The literals here are therefore load-bearing, not presentation: a log written outside them makes the detector report zero, which is indistinguishable from "no weakness region".

Two layouts, both valid:

```
**Axis tags**: <axis>: <verdict> / <axis>: <verdict> / ...

**Axis tags (10-axis)**:
- <axis>: <verdict>
- <axis>: <verdict>
```

Fields:

- `<axis>` = the axis name. Take it verbatim from The 10 axes when the observation is one of them. A name outside that set is allowed and is tallied under itself; it just never merges with a canonical axis.
- `<verdict>` = the reading. It counts as a miss when the word `miss` appears anywhere in it, so `**miss (primary)**` and `miss→hit` both register.
- The first `:` of a pair ends the axis name; later `:` characters belong to the verdict.
- ` / ` (space slash space) separates inline pairs. The same sequence inside parentheses is verdict text and does not separate.

### Axis name normal form

Two spellings of one axis must land on one tally, so a name is reduced before it is counted:

1. drop `*` emphasis characters
2. drop a parenthesized qualifier and everything after it (`Character(pronoun)` -> `Character`)
3. replace `-` and `_` with a space
4. collapse whitespace runs, then trim
5. lowercase
6. when the result is a word-boundary prefix of exactly one of The 10 axes, expand it to that axis (`character` -> `character drift`); otherwise keep it

Step 6 is what makes The 10 axes the canonical vocabulary rather than a list to cross-reference by hand: a shorthand that unambiguously names one canonical axis is that axis, and no alias table is maintained beside the list. A shorthand matching two axes stays unexpanded — ambiguity is not resolved by guessing.

### Inline list end

The bullet layout ends each pair at the line break. The inline layout has no such boundary, so one is defined: the pair list ends at the first `。` outside parentheses, or at a `Root cause:` / `Domain:` label outside parentheses, whichever comes first.

Trailing prose on the tag line is therefore read as prose instead of being folded into the last verdict — which is what previously let a free-form sentence reach the `miss` scan and let a parenthetical ` / ` inside that sentence register as a phantom axis. Putting the trailer on its own line avoids the question entirely and is preferred.

</axis-tag-line-format>

<non-scope>

## Non-scope

- Harness engineering metrics (rework rate, PR cycle time, CI-pass rate, code quality score) are not Self-Evaluation input. Those measure downstream behavior, not dialogue-internal signal.
- Reverse inference from downstream success to dialogue quality is prohibited. Dialogue quality is evaluated on transcript signals, not on whether the code landed.
- Preventive gate axes belong to a separate rule surface. Do not merge preventive and observational sets in one entry.

</non-scope>

</observational-axes>

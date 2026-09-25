---
name: evolution-rule-effect-measurement
description: Invoke when a line or section is about to be added to Li+ source and whether it changes anything on top of the body already there has to be settled by measurement rather than by argument / a stage 1 injection arm prompt is being composed and its source-of-information constraint has to be written / a stage 2 run is being set up with `scripts/measure_rule_effect.py` / a probe is being written for a candidate line / a probe set is about to be re-raised or its text shared before the measurement closes / a stage 1 zero-difference result is about to be read as grounds for dropping a line / two arms have returned and the verdict is being formed / a self-evolution PR has reached CI green and whether a measurement is raised before brake 1 has to be settled / a measurement that could not be run is about to be recorded on such a PR. Provides the two-stage design, its position on the self-evolution PR pipeline, the probe specification, the per-stage contamination constraints, and the judge separation.
layer: L2-evolution
---

<rule-effect-measurement>

# Rule Effect Measurement

Gate that settles whether a candidate line changes conduct by observation rather than by argument: two contrasting workspaces are run and the difference between their outputs is read.

Relation to brake 1 (`skills/evolution-parallel-agent-eval/SKILL.md`): brake 1 reads a diff statically before merge; this runs the body and reads behavior. Each has caught what the other missed, so neither replaces the other.

<application-point>

## Application point

The gate stands at the entrance for new material. Sweeping existing sections is spare-capacity follow-up, not the primary path.

The comparison target is the tree carrying everything already there, never an empty one: a line is asked for its marginal effect on top of the current body, which makes this a duplicate detector.

### Position on the self-evolution PR pipeline

Canonical for where this gate fires on that pipeline. The order is implementation -> CI -> measurement -> brake 1: the run is raised after the CI run goes green and before the brake 1 evaluators are spawned, against the same baseline they are given (`rules/evolution/initiator-autonomy.md` Merge brake fixes that baseline).

Actor = the parent. The arms stay separate `claude -p` processes (Running stage 2), and what the parent raises is the run, not the verdict (Judge separation).

Firing condition = a PR whose diff over the governed body (`rules/**` / `skills/**` / `adapter/**`) deletes more than it adds on **either** of two arms: deleted lines exceed added lines, or deleted bytes exceed added bytes. Either arm alone fires the condition. A PR that exceeds on neither is not measured here. Self-report is not accepted in place of the diff, and no threshold is set on either margin — both arms compare at zero.

Both arms are counted over the paths the firing condition names (`docs/**` is not among them), and each inside that one diff: this PR's added material against this PR's own deleted material, never across files, PRs or languages.

The run is not mandatory: it consumes external budget, and a run that cannot be taken does not hold the merge gate — proceed to brake 1 without it. What holds instead is the record: write `unmeasured` with its reason — spend limit, outside the firing condition, nothing in the diff to raise a probe over, or `window open` (Running stage 2) — into the parent's self-review record (`rules/operations/main-agent-procedures.md` Self-review formal record), which is written after brake 1 has exited, so nothing in it reaches an evaluator. Never leave it blank and never record it as a negative result.

</application-point>

<two-stages>

## Two stages

Stage 1 sifts cheaply. Stage 2 adjudicates what stage 1 could not.

| stage | how the arm is built | cost | what the result settles |
|---|---|---|---|
| 1 | the passage under test is injected into the parent prompt | cheap | a difference settles load-bearing. Zero difference routes to stage 2 — a routing, not a verdict |
| 2 | two workspaces are materialized, one place changed, `claude -p` raised in each | high | zero difference drops the line as duplicate. A difference keeps it as the reminder type |

A stage 1 zero difference MUST NOT be used as grounds for dropping a line (Zero difference conflates two states below).

In stage 1, paste the passage into the prompt by default rather than having the arm read it from a file; the two measured the same, and pasting writes no rule file that does not belong to the tree. The containment conditions below apply only when a file is placed after all.

</two-stages>

<probe-specification>

## Probe specification

- Raise the probe from the application-moment sentence its author fixed before the run (`rules/model/liplus-coding-rule.md` Application-moment sentence). Fix the sentence first, then run. A rewritten sentence is a new claim from the start, and the measurement taken against the previous one does not carry over.
- The dropped line must be the only road to the answer. A probe that can be reached by elimination is not measuring that line.
- Do not name the section or its location in the probe.
- Run content matching and conduct matching together. Content matching asks what the body says; conduct matching asks what to do in a situation, with no reference to the body. Verbatim-omission detection is only available to content matching, so this is a pairing, not a replacement.
- The two are written in different forms. A conduct probe is not a content probe with its wording softened.
  - **Content form**: name the skill to invoke, instruct the arm to answer from the body, require the answer verbatim, and require it to say that the body carries no provision when it carries none.
  - **Conduct form**: present the situation and nothing else. Do not name the skill, do not name or imply any body, do not ask what is written anywhere. Ask what the arm does, and take the action as the answer. Every instruction the content form carries about consulting a body is absent here, not weakened.
- Prefer a conduct probe whose answer lands on a discrete choice of action. Prose answers cannot be read against a band that has not been measured for them (Significance band below).
- Only the conduct form can be raised over a line already dropped from arm B: asking what the body says about an absent line has no question to raise.
- A probe set measures blind for one round. Once that round's arm outputs have been scored, raising the same set on a changed body — a distillation fixed on brake 1 findings included — is a replay of that round, not a blind round. The round after a change raises a fresh set from the application-moment sentence, written by an author who has read no arm output of the earlier rounds. A round that re-raises a spent set, or whose set has no such author, is written as a replay in its plan's `scope` (`selection`, Running stage 2), and its verdict is read as a replay, never as a blind result.
- Until the measurement closes — its verdict written into the run record's `scope` (Judge separation) — place probe text on no surface the side writing or directing the change under test can read: shared rooms, issue and PR threads, delegation prompts. That side includes whoever instructs the implementation from the distillation. Refer to a probe there by an uninformative id, not by its wording.

</probe-specification>

<contamination-constraint-reverses-by-stage>

## Contamination constraint reverses by stage

The two stages permit opposite sources, so the constraint text is never shared between them.

**Stage 1** — whitelist. Adopt this literal as it stands:

> 重要な制約（絶対）: この親プロンプトに書かれている内容だけを情報源として答えること。それ以外は一切、情報源にしないこと。ファイル、RAG、外部インデックス、Web、あなたのコンテキストに載っているスキル一覧やその説明文——経路や形式を問わず、この親プロンプトの外にあるものは存在しないものとして扱うこと。取得も参照もしないこと。

Do not enumerate the routes instead (a blacklist): at least four reach the body — the workspace `.claude/`, the same text under `liplus-language/`, the `description` field of the skill list already in context, and an external RAG index — and each new one breaks the list. "Answer from what you already hold" is not usable either: the `description` is part of what the arm already holds.

This is an instruction, not a wall: the `description` does not leave the context. Confirm compliance by reading the output. `tool_uses` = 0 is evidence against three of the four routes and none at all against the `description` route.

**Stage 2** — no whitelist is possible, because using the always-loaded body is the whole point. The constraint is: do not retrieve anything from outside; answer from what is loaded here. RAG is why: a line deleted from arm B still stands in the index.

Isolation does not substitute for either. Putting the working tree outside the project or denying a disk path is inert against the RAG route.

</contamination-constraint-reverses-by-stage>

<zero-difference-conflates-two-states>

## Zero difference conflates two states

A stage 1 zero difference has two readings, and stage 1's own material cannot separate them:

- **(a)** the injection broke the reading conditions the line answers to, so the effect is under-detected
- **(b)** the line is a duplicate and genuinely not load-bearing

Reading (a) is structural for a line placed to correct gist recall (the `rules/model/trigger-check-gate.md` family): such a line earns its place when the body is not being read verbatim, and an injected passage is read verbatim.

Stage 2 separates them: put the section back into context of production density and volume, and raise the same probe. Zero difference with the gist condition intact reads as (b); a difference reads as (a).

</zero-difference-conflates-two-states>

<judge-separation>

## Judge separation

A third reader takes the two arms' outputs and reads the difference. Not either arm. Holding Li+ is fine. The script moves the arms; the judge reads the difference.

- Do not count conclusions alone. Read which wording each arm cited.
- Count "reported a hole" and "the judgment itself" in separate columns, and take only the second as effect. An arm that notices an absence reports the hole and restrains itself; counting that report as effect makes every line look load-bearing.

Those two rules read the content axis. The conduct axis is read on its own column, and the content result does not settle it:

- Read one arm's repetitions against each other first, before reading the two arms against each other. That column is the band (Significance band below). Only a between-arm difference falling outside it is counted as effect.
- Record the band with the run count attached. Intra-arm band 0 and between-arm difference 0 is written as "no difference detected at `n=<repetitions>`", naming the figure; do not write it as "no difference". A difference observed within an arm is usable as it stands whatever n was.
- Read which action each arm took, not which wording it cited.
- Same action in both arms = no effect. The line's conduct is held by the always-loaded surface, or the line carried no conduct at all. A content difference standing next to this is the re-statement signature, and the keep-or-drop decision is made on the conduct column.
- Different actions = the effect. What arm B lost is conduct, and the line is load-bearing.
- An arm that answers a conduct probe by reporting that no provision exists has answered the content question. The probe named or implied a body; the round is void, not a difference. Re-raise it in the conduct form (Probe specification above) rather than scoring it.

Do not suppress mention of the hole in the probe: the noticing stays and only its outward sign goes, and that sign is what distinguishes leak from no leak.

Write the verdict inside the run record's `scope` (Running stage 2). A green round answers for the probes it put, not for the change: one whose probes were picked by predicting what the change breaks is written as "the predicted breakage did not occur", never as "nothing changed".

</judge-separation>

<significance-band>

## Significance band

Read the band off the control run's own intra-arm repetitions: `repetitions` runs each arm that many times under an unmoved condition, so the spread across one arm's runs is the band. Only a difference outside the band counts. Measure the band per model and per axis.

Do not idle-run two identical arms to get it: the harness refuses any plan whose arms do not differ in exactly one place (Running stage 2).

Measured once: a band of 0 on a content probe whose verdict is a discrete value (patch / minor / major). It does not carry to prose answers, and it does not carry to the conduct axis on the strength of a shared discreteness: the conduct band is unmeasured, and until it is, do not read a conduct difference as an effect on the strength of the content-axis figure.

</significance-band>

<arm-model-is-an-experimental-condition>

## Arm model is an experimental condition

Fix the arm's model and record it: with the same probe and the same workspace, the result has inverted with the model.

Do not use a weak model for the arm. It retrieves nothing, and it also fails to apply the section, so every difference comes out understated. Match the level actually in production.

</arm-model-is-an-experimental-condition>

<running-stage-2>

## Running stage 2

`scripts/measure_rule_effect.py` takes a JSON run plan and produces a run record, and leaves nothing else behind: what a kill or a power loss leaves, the head of the next run wipes.

The arm is a separate process. A subagent reads the rule text as it stood when its parent session started, and an on-disk change during the run reaches it in neither direction, so a subagent implementation cannot express stage 2. An arm whose context and disk disagree adopts the context without detecting the disagreement: nothing may touch `.claude/` while a run is live.

The brake 1 operational copy is one such third party, and it leaves a mark (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure step 2). Before raising a run, read `scripts/window_marker.py status` on the live `.claude/` the arms are copied from. `open` gates the clone: do not build the arms while the mark stands. Poll `status` again and wait for `closed` or `never_opened` before proceeding, or give up and record the run as `unmeasured`, reason `window open` (Application point) — not as a run that took place. Ending an abandoned mark is that step's own procedure, not this gate's: this gate only reads `status`, and never calls `close`.

The gate reaches only what it can see at the moment it checks: a mark opened in the gap between the last `status` read and the clone itself is not caught here, and the mark's history stays the backstop for that gap. An open mark found there does not settle whether the run is void; whether the applied draft bears on the probe stays the judge's to read. Whether the arms were copied inside such a span is settled afterwards from the mark's history: the run record's `started_at` against each span's `applied_at` and `closed_at`.

What the harness enforces structurally, so it is not left to care at run time:

- exactly two arms differing in exactly one place, checked both against the plan and against the arms as built
- an edit anchor matching exactly once — zero matches would compare two identical arms and report a false negative
- the arm's model named in the plan, with no default
- the plan's `scope` object — `probes_measured` of `probes_total`, the `selection` criterion, and what is left `unmeasured` — required and carried into the run record. Fill it for the measurement round, identically in every plan of that round. The values are self-declared and unchecked
- hooks removed from each arm, so nothing injects material into one side
- no `.git` in the arm, so no remote by construction
- the run record written only to the file `--out` names, and `--out` required: the record carries every edit body in full, so there is no stdout path for it to reach whoever runs the harness
- a non-zero exit (4) when no arm returned zero, so a run that measured nothing cannot be read as a run that did. The run record is written first either way; a single failed arm can be the behavior under measurement and leaves the exit at 0

</running-stage-2>

<containment-when-a-file-is-placed>

## Containment when a file is placed

Only for a stage 1 run that writes a file. Stage 2 builds no such file and does not need this.

Measured: an arm read a note inside its own source saying the file was a copy made for a trial, and added that its verdict was therefore not for production use. A file that declares what it is changes the frame the arm judges in.

- Keep no word naming a trial, a copy or a check inside the file, or in its name.
- Place it in the scratchpad only. Never under `.claude/` and never under `liplus-language/`.
- Give it an uninformative unique id for a name, never the name of a real file.
- Delete it as soon as the run ends.
- Record what it was outside the artifact — in the run record and the issue.

"Keep the label out of the artifact" and "write the label nowhere" are different. Only the first.

</containment-when-a-file-is-placed>

<self-application>

## Self-application

A condition added to this gate goes through this gate. The criterion is the probe's own: what does this condition change at the moment it applies. A condition that cannot be said in one sentence does not enter.

This cannot close into an AI-only loop. The party stacking the conditions is poorly placed to run the gate over them, so the decision to add a condition needs a position outside the design as well as a judge separate from the writer. Read `rules/model/role-separation.md` human = final judge here as that structural position, not only as an approval step.

</self-application>

</rule-effect-measurement>

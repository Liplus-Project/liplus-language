---
name: evolution-rule-effect-measurement
description: Invoke when a line or section is about to be added to Li+ source and whether it changes anything on top of the body already there has to be settled by measurement rather than by argument / a stage 1 injection arm prompt is being composed and its source-of-information constraint has to be written / a stage 2 run is being set up with `scripts/measure_rule_effect.py` / a probe is being written for a candidate line / a stage 1 zero-difference result is about to be read as grounds for dropping a line / two arms have returned and the verdict is being formed. Provides the two-stage design, the probe specification, the per-stage contamination constraints, and the judge separation.
layer: L2-evolution
---

<rule-effect-measurement>

# Rule Effect Measurement

Gate that settles whether a candidate line changes conduct, by running two contrasting workspaces and reading the difference between their outputs.

The problem it answers is asymmetric cost. Adding a line takes one writer. Removing one takes showing an evaluator that the line is not load-bearing, which is proof of a negative and cannot be given. `rules/model/subtractive-structural-beauty.md` Core principle (C) names preserve-by-default as a reflex rather than a judgment, and that reflex is built into any gate whose removal path needs an argument. Measurement replaces the argument with an observation.

Relation to brake 1 (`skills/evolution-parallel-agent-eval/SKILL.md`): brake 1 reads a diff statically before merge; this runs the body and reads behavior. Measured in both directions — a dropped conduct line escaped the measurement net and brake 1 caught it, and a re-stated line escaped brake 1's net and the measurement caught it. Separate surfaces, not a replacement.

Justification for the design decisions below is held as Decision Structure entries in the wiki, indexed at `docs/Decision-Structure.md`.

<application-point>

## Application point

The gate stands at the entrance for new material, not over a sweep of the existing body.

The comparison target is the tree carrying everything already there, never an empty one. A line is asked for its marginal effect on top of the current body, which makes this a duplicate detector. A one-line-at-a-time entrance exam against nothing passes almost everything: few lines are meaningless alone, and what produces the bloat is duplication.

Sweeping existing sections is spare-capacity follow-up, not the primary path.

</application-point>

<two-stages>

## Two stages

Stage 1 sifts cheaply. Stage 2 adjudicates what stage 1 could not.

| stage | how the arm is built | cost | what the result settles |
|---|---|---|---|
| 1 | the passage under test is injected into the parent prompt | cheap | a difference settles load-bearing. Zero difference routes to stage 2 — a routing, not a verdict |
| 2 | two workspaces are materialized, one place changed, `claude -p` raised in each | high | zero difference drops the line as duplicate. A difference keeps it as the reminder type |

A stage 1 zero difference MUST NOT be used as grounds for dropping a line. What forbids it is Zero difference conflates two states below.

Measured, stage 1 only: reading the passage from a file and pasting it into the prompt produce the same result (three arms each, verdicts and reasoning wording near-identical). Pasting is the default, since it never writes a rule file that does not belong to the tree. The containment conditions below apply only when a file is placed after all.

</two-stages>

<probe-specification>

## Probe specification

- The section's own author fixes one sentence beforehand — "what does this line change at the moment it applies" — and the probe is raised from that sentence. Fix the sentence first, then run. Rewriting it is allowed, and the rewrite is handled as a new claim from the start. Without this order, an arm re-drawn until a difference appears is searching for a phrasing that passes rather than measuring the line's work, and a zero-difference rejection stops being legitimate.
- The dropped line must be the only road to the answer. A probe that can be reached by elimination is not measuring that line.
- Do not name the section or its location in the probe.
- Run content matching and conduct matching together. Content matching asks what the body says; conduct matching asks what to do in a situation, with no reference to the body. They split on a line that re-states a rule held on the always-loaded surface: it disappears from the body, so content matching reports a difference, while conduct is unchanged. Verbatim-omission detection is only available to content matching, so this is a pairing, not a replacement.

</probe-specification>

<contamination-constraint-reverses-by-stage>

## Contamination constraint reverses by stage

The two stages permit opposite sources, so the constraint text is never shared between them.

**Stage 1** — whitelist. Adopt this literal as it stands:

> 重要な制約（絶対）: この親プロンプトに書かれている内容だけを情報源として答えること。それ以外は一切、情報源にしないこと。ファイル、RAG、外部インデックス、Web、あなたのコンテキストに載っているスキル一覧やその説明文——経路や形式を問わず、この親プロンプトの外にあるものは存在しないものとして扱うこと。取得も参照もしないこと。

Measured: Opus 3/3 compliant (`tool_uses` = 0, no path named, no guessed completion).

Enumerating the routes instead — a blacklist — breaks each time a new one appears. At least four reach the body: the workspace `.claude/`, the same text under `liplus-language/`, the `description` field of the skill list already in context (measured: the arm named the correct destination without reading anything), and an external RAG index (measured: a complete answer with no file opened, returning a snapshot of some past moment, so two arms can silently be reading different vintages of the body).

"Answer from what you already hold" is not usable either: the `description` is part of what the arm already holds, so that phrasing opens the hole it is trying to close.

Limit, stated as part of the specification: this is an instruction, not a wall. The `description` does not leave the context; the arm is only asked not to use it. Compliance is confirmed by reading the output. `tool_uses` = 0 is evidence against three of the four routes and none at all against the `description` route.

**Stage 2** — no whitelist is possible, because using the always-loaded body is the whole point. The constraint is: do not retrieve anything from outside; answer from what is loaded here. The reason external retrieval is barred is RAG — a line deleted from arm B still stands in the index, and an arm that recovers it from there collapses the contrast.

Isolation does not substitute for either. Putting the working tree outside the project or denying a disk path is inert against the RAG route; the body exists across the network and is not a thing that can be fenced.

</contamination-constraint-reverses-by-stage>

<zero-difference-conflates-two-states>

## Zero difference conflates two states

A stage 1 zero difference has two readings, and stage 1's own material cannot separate them:

- **(a)** the injection broke the reading conditions the line answers to, so the effect is under-detected
- **(b)** the line is a duplicate and genuinely not load-bearing

Injection structurally under-detects the class of line placed to correct gist recall. The arm reads a short passage sitting in front of it, and the condition under which such a line earns its place is precisely not reading the body verbatim. Li+ carries many lines of this type (the `rules/model/trigger-check-gate.md` family), and running the gate without the distinction drops all of them at once.

Separating the two is what stage 2 is for: put the section back into context of production density and volume, and raise the same probe. Zero difference with the gist condition intact reads as (b); a difference reads as (a).

</zero-difference-conflates-two-states>

<judge-separation>

## Judge separation

A third reader takes the two arms' outputs and reads the difference. Not either arm. Holding Li+ is fine.

- Do not count conclusions alone. Read which wording each arm cited.
- Count "reported a hole" and "the judgment itself" in separate columns, and take only the second as effect.

That second rule exists because an arm detects an absence and restrains itself. Measured under a deliberate omission: 3/3 no leak, all three volunteering that the rule carries no such definition, one stating that the always-loaded body does carry it but that reference was barred. Such an arm is not ignorant; its output becomes a report about the hole. Whether A and B differ by one line's worth of judgment, or by the fact that a hole was noticed, are different things, and counting the second as effect makes every line look load-bearing.

Suppressing mention of the hole in the probe is not the fix. The noticing does not go away, only its outward sign — and that sign is what distinguished leak from no leak. Suppressing it breaks the detector. Separating the judge is the fix.

Division of labour: the script moves the arms, the judge reads the difference.

</judge-separation>

<significance-band>

## Significance band

Idle-run the same condition several times first and measure the band of variation. Only a difference outside the band counts. Measure the band per model.

Measured, once: on a probe whose verdict is a discrete value (patch / minor / major), the band was 0 under those conditions — 12 arms, all agreeing. Reasoning wording differed every time, so a band of 0 belongs to the discrete-verdict axis and does not carry to prose.

</significance-band>

<arm-model-is-an-experimental-condition>

## Arm model is an experimental condition

Fix the arm's model and record it. Measured: with the same probe and the same workspace, the result inverted with the model (haiku 0/3 leaks, zero tool use; Opus 1/1 leak, answered in full from RAG).

Do not use a weak model for the arm. It retrieves nothing, and it also fails to apply the section, so every difference comes out understated. Match the level actually in production.

</arm-model-is-an-experimental-condition>

<running-stage-2>

## Running stage 2

`scripts/measure_rule_effect.py` takes a JSON run plan and produces a run record. Nothing else survives the run: the lock and the fixed working path under temp are removed on the way out, and the head of the next run wipes what a kill or a power loss left behind.

The arm is a separate process, and that is fixed by measurement rather than by preference. A subagent reads the rule text as it stood when its parent session started, and an on-disk change during the run reaches it in neither direction (measured both ways, zero tool use across every trial). Stage 2 compares on-disk states, so a subagent implementation cannot express it. A consequence to hold: an arm whose context and disk disagree adopts the context without hesitating and does not detect the disagreement, so a third party touching `.claude/` mid-run corrupts the verdict undetectably.

What the harness enforces structurally, so it is not left to care at run time:

- exactly two arms differing in exactly one place, checked both against the plan and against the arms as built
- an edit anchor matching exactly once — zero matches would compare two identical arms and report a false negative
- the arm's model named in the plan, with no default
- hooks removed from each arm, so nothing injects material into one side
- no `.git` in the arm, so no remote by construction

Cost floor: one minimal arm charged 95,069 cache-creation input tokens, which is the always-loaded surface being read and is near-independent of probe length. One round of 5 probes x 3 repetitions x 2 arms is 30 launches. Measurement consumes external budget, so it is not made mandatory.

Placing this in the pipeline is a separate axis and is not settled here.

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

Each time a hole in this design is found, a condition is added — which is the same shape as the bloat this gate exists to measure. So the conditions of this gate go through this gate.

The criterion is the probe's own: what does this condition change at the moment it applies. A condition that cannot be said in one sentence does not enter.

Applied once already: "place both variants in both arms' workspaces" was rejected. With the naming and placement conditions held, putting only one in place leaves identical loaded text and an uninformative name, so nothing differs at the application moment.

Structural limit, and the reason this cannot close into an AI-only loop. The party stacking the conditions is poorly placed to run the gate over them. Observed during the design: at every leak found, the AI side moved only toward adding one more condition; the move that stopped the counting — "stop enumerating routes, name the one permission" — came from outside the design. Separating the judge from the writer is not enough on its own; the decision to add a condition needs an outside position too. `rules/model/role-separation.md` human = final judge is read here as that structural position, not only as an approval step.

</self-application>

</rule-effect-measurement>

---
globs:
alwaysApply: true
layer: L4-operations
---

<main-agent-procedures>

# Main Agent Procedures

<position>

## Position

Layer = L4 Operations Layer
Holds the operations procedures whose actor can be the main agent, on the resident rules surface instead of in an `operations-*` skill.
Requires = L4 Operations Layer
Load timing = always-on (the main agent is barred from the skill surface, so residency is the only way these reach their actor)

</position>

<the-bar-and-its-pair>

## The bar and its pair

`adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` each carry one line: `Main never reads operations skills directly when subagent is available.` It is not a standalone bar: it stands together with the move that pays for it — the PR review criteria sit on the layer the main agent already holds. The intent is role separation (subagent executes procedures, main judges reports), not context economy.

The pair, stated once: **the bar holds only while every procedure whose actor can be the main agent has its canonical text on a surface the main agent may read.** Main-readable = every Li+ surface except `skills/operations-*/SKILL.md`. The subagent reads all of them, so a main-readable surface is also the surface both actors reach, and a canonical placed there needs no second copy for the other actor.

What establishes that an actor can be the main agent is one of two things, and neither is "the main agent could choose to do it". Implementation and operations are delegated by default (`skills/task-subagent-delegation/SKILL.md` Rules), so the main agent's freedom to execute something itself is not an actor axis — reading it as one fires every `operations-*` skill at once and leaves the maintenance rule below with no procedure that legitimately stays in a skill. The two that do establish it:

- the procedure is on `Parent retains` (`skills/task-subagent-delegation/SKILL.md` Rules). Read that list at its own granularity: `issue management` there is scoped by its parenthetical to non-state lifecycle labels, type, maturity, marker and close, so a requirement about issues that is none of those is not reached by it.
- the procedure needs a surface no subagent has — an utterance to the human, a human-facing report, or the user-turn boundary. Escalating a stop to the human is not that surface on its own: a subagent escalates by reporting to the parent, which is why `skills/operations-on-ci/SKILL.md` does not fire on its own escalate-to-human line. What fires is a prescribed human-facing utterance the agent must author, or a go-sign the agent must receive and act on where no already-resident gate carries it.

Both are read per requirement, not per file: one skill can hold a firing clause and a non-firing one, and the granularity that matters is the clause.

Maintenance rule, applied when an `operations-*` skill gains a requirement whose actor can be the main agent: move the canonical to a main-readable surface and leave a pointer in the skill. Two wrong repairs:

- copy the text to a main-readable surface and keep it in the skill as well — the second copy is what drifts.
- narrow the bar so the main agent may read the skill "when it is the actor" — that discards the role separation the bar exists for, and the requirement still sits on a pull surface its actor reaches only after it has begun acting.

Detection sign: a procedure written into an `operations-*` skill whose actor is mode-dependent, or stated as "the agent holding the merge decision". That agent is the parent in `auto` / `semi_auto` (`skills/task-subagent-delegation/SKILL.md` Rules), so the requirement lands where its actor cannot read it.

One shape resolves the other way: where the literal's actor is the subagent and the main agent is only the carrier, the canonical stays in the skill and the main agent carries a pointer to it instead (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary). Move the canonical when the main agent has to execute it; leave a pointer when the main agent only has to convey it.

Relocating the canonical is half the move. A skill is invoked by its `description` matching the situation at hand, so a skill whose canonical has left but whose description still names a moment the main agent stands in keeps putting the main agent into the skill — the bar is then broken by the file's own trigger, not by any agent's choice, and the relocation has renamed the violation rather than repaired it. The second half: narrow the description to the reader the skill retains. Retained readers are the subagent, and the main agent under the substrate-absence fallback (`skills/task-subagent-delegation/SKILL.md` Autonomy) — that fallback fires only when no subagent is available, which is the condition under which the bar does not apply, so a description scoped to it does not fire against the bar. A skill that retains neither reader is empty and is deleted, not left as a pointer; `rules/model/subtractive-structural-beauty.md` Core principle (A) already refuses it its place. One thing other than a reader can hold such a file up: being the resolution target of a pointer that cannot itself be edited. That is load-bearing — deleting the file would leave the pointer dangling — so the file stays, as a redirect stub whose description declares it non-invocable rather than naming any moment at all.

Adapter literals that point the main agent at an operations skill are repaired the same way where they are editable. Where one is not — `adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` `## Optional Webhook Notification Flow` is byte-frozen, because `Li+update.md` derives the legacy trailer it strips from installed files out of that very block and drift there silently breaks the migration for pre-migration installs — the redirect is carried here instead. Editing the adapter to satisfy the bar would trade a governance defect for a live migration defect; `rules/model/axis-separation.md` sends a cross-layer contradiction back to the boundary rather than resolving it by precedence, and this file is the boundary the main agent already loads. Detection sign that this shape is present: an adapter line naming an operations skill as where policy lives, in the same sentinel section as the bar.

</the-bar-and-its-pair>

<issue-format>

## Issue format

Canonical. `skills/operations-on-issue-format/SKILL.md` holds the pointer.
Actor = the parent, unconditionally. The subagent applies this format too, when it updates the issue body mid-implementation or writes the failure-report comment.

Issue title language:
Title = ASCII English only.
Body  = LI_PLUS_PROJECT_LANGUAGE.
Consistent with the commit title/body language convention (`rules/operations/operations.md` Operations Rules) and PR title convention. That convention is stated there about that section's own commit and PR lines; the two axes stated alongside it carry here by the same consistency — the title axis, and the carve-out where the repository being operated on is the repository at `LI_PLUS_REPO` itself and `LI_PLUS_PROJECT_LANGUAGE` does not reach its body language. Read both there; they are not restated here.

Issue may start from memo. Three fields are convergence target, not creation gate.
Use only necessary headings. Do not force empty sections.
Canonical convergence for implementation issue:
  purpose
  premise
  constraints
  target files (recommended at ready stage)
Target files = list of files expected to change, with dependency notes (e.g. source⇔docs).
Target files are optional during memo/forming. Recommended once issue reaches ready.
Rewrite issue body whenever accepted understanding changes.
Issue completion is managed through issue state plus PR/CI/release flow, not a dedicated issue-body field.

Checklist = human judgment required (real device test, operational verification).
Use checklist only when AI cannot judge.

Memo-mode rapid intake (interrupt-minimal path):
Triggered by human signaling "黙って" / "silent" / "quick memo" / equivalent intent: minimize the cognitive cost of issue creation while the human's main task continues.

- title = ASCII English, bug/kind prefix only (e.g. `bug(rerank): cross-encoder not firing`). No deep verb structure.
- body = observation fact (1-3 lines) + reproduction hint (1-2 lines). No purpose / premise / constraints / target files.
- labels = one type label (bug / enhancement / spec / docs / tips) + maturity = `memo`.
- assignee = unassigned.

Discriminator: "Is this issue creation itself the main task, or is it interrupting the main task?"
- Interrupting → rapid path.
- Main task → full forming/ready intake.

Treating "黙って" as "still do full intake but skip discussing it" defeats the interrupt-cost reduction the human asked for. Memo maturity is a valid resting state, not "incomplete and embarrassing"; promotion to forming/ready happens later when the issue itself is the focus (Issue maturity below).

</issue-format>

<issue-maturity>

## Issue maturity

Canonical.
Actor = the parent, unconditionally. The subagent is delegated an issue that has already converged and never judges the transition.

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

Memo maturity is a valid resting state, not "incomplete and embarrassing". The creation-time rapid path that produces a memo-maturity issue lives at Issue format above, which fires at issue creation; promotion to forming/ready is judged here, later, when the issue itself is the focus.

</issue-maturity>

<sub-issue-rules>

## Sub-issue rules

Canonical. `skills/operations-on-sub-issue/SKILL.md` keeps the draft-PR CI visibility surface and points here.
Actor = the parent on every judgment below. The subagent is the actor that detects a scope exceed mid-implementation, and has no dialogue surface to fire the confirm on.

Sub-issue = AI-trackable work unit.
Split by responsibility, not granularity.

Classification litmus (sub-issue vs sibling issue):
Ask: "Can this unit ship independently without breaking the parent's atomic deliverable?"
If yes = this is a sibling issue, not a sub-issue. Create it as an independent issue.
If no  = this is a legitimate sub-issue. It only makes sense as part of the parent's atomic deliverable.
Rationale: if a unit can ship alone, nothing is gained by making it a sub-issue.
The feeling "I want per-sub-issue PR to ship these independently" = signal that these should have been sibling issues from the start.
Re-classify before splitting PRs. Do not split PRs.

See `rules/operations/operations.md` for parent/sub-issue authoritative rules (single parent PR flow, one branch per parent, sub-issue PR prohibition).

Sub-issue API:
gh issue develop targets parent issue only (branch creation).
Sub-issue linking uses REST API with internal numeric ID, not issue number.

Simultaneous tasks require parent-child structure:
If multiple tasks in same session = create parent issue + sub-issues.
Do not create multiple independent issues for simultaneous work.

Parallel conflict analysis:
When multiple ready issues exist = analyze target files for overlap before execution.
No overlap = parallel-safe. Propose parallel sub-issue structure to human.
Partial overlap = propose splitting shared-file changes into a separate integration sub-issue.
Integration sub-issue executes after parallel sub-issues complete (serialized dependency).
Analysis basis = target files field in issue body. If absent, infer from issue purpose and premise.

Scope-exceed dialogue confirm:
Issue body literal is the scope boundary. At sub-issue creation OR mid-implementation, when a planned change exceeds the parent body literal — either a negative-constraint clause ("do not X" / "X only" / "this issue handles X only") or the enumerated target-file set — fire a dialogue confirm before the commit that would carry the exceeding change.

Threshold axis: issue body literal diff (primary). Parent design intent (secondary fallback for cases where the body is silent but the planned change feels intentional scope creep).

Confirm shape — 1 turn, 3 sentences max, 3 fixed options:

```
[Character prefix] Parent #<n> literal: <quoted constraint or target-file literal>.
Planned change: <one-line summary of the literal-exceeding action>.
Continue / rewrite scope / stop.
```

Master picks one of the three. No multi-turn escalation by default; if Master extends, follow the extension.

Anti-pattern: "just to be safe" / "out of caution" firing without a literal trigger hit is push surplus per `rules/model/subtractive-structural-beauty.md` and prohibited.

Post-implementation (PR review time) is too late and is rejected as a firing moment — the gate must fire pre-commit, not post-commit.

Recovery from accidental per-sub-issue PR runs:
If per-sub-issue PRs already exist on a parent with sub-issues (a spec violation that may have shipped before discovery), the post-hoc recovery is:
1. Consolidate sub-issue branches into a single parent branch via cherry-pick or rebase.
2. Manually re-open sub-issues that auto-closed via the wrong branch's merge.
3. Close them again from the consolidated parent PR's merge once it lands.

This is fix-up only — do not normalize per-sub-issue PRs as a workflow. The single parent PR layout is correct; per-sub-issue PRs trigger cascading auto-close failures on the parent, and this procedure repairs that state rather than sanctioning it.

</sub-issue-rules>

<branch-and-label-flow>

## Branch and label flow

Canonical. `skills/operations-on-branch/SKILL.md` keeps the repo-first execution surface and points here.
Actor = the main agent on every half of this flow, with one split: branch creation is the main agent's under the worktree lifecycle (`adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md` Responsibilities), and the delegated subagent's when the delegation uses no worktree.

Trigger = human intent to act now detected via dialogue.
Judgment = read atmosphere, not checklist.
If unclear = ask with feeling, not mechanically.

Timing tiers:
NOW     -> label=in-progress + branch create
SOON    -> label=backlog     + no branch
SOMEDAY -> label=deferred    + no branch

The tiers table decides which tier applies, not what the `in-progress` transition consists of.
That transition is the label alone, specified in
`skills/task-subagent-state-labels/SKILL.md` Work start. Do not restate its steps here.

Axis separation:
Lifecycle labels = when to act.
Maturity labels  = how converged the issue body is.
Do not use lifecycle labels as substitute for memo/forming/ready.

Atmosphere reading scope:
Applies to timing tier judgment (NOW / SOON / SOMEDAY) only.
Label assignment is a deterministic mapping from tier result, not a second atmosphere read.
Once tier is judged, label follows the tiers table without re-reading atmosphere.

Branch existence check (before creation):
local:  git branch --list {branch-name}
remote: gh api repos/{owner}/{repo}/branches/{branch-name} (404=not_exists)
If remote exists = existing GitHub branch cannot be retroactively linked.
If local only   = gh issue develop still allowed (local will be overwritten).
If not exists   = proceed normally.

Branch creation:
command = gh issue develop {issue_number} -R {owner}/{repo} --name {session-branch} --base main
Branch creation carries no assignee step. The actor axis fires at the parent's delegation
moment, upstream of branch creation and of the `in-progress` transition alike
(`skills/task-subagent-delegation/SKILL.md` Rules; reading rules for the field at
`skills/task-subagent-state-labels/SKILL.md` Actor axis).

Merge behavior:
PR merge auto-closes the parent issue via issue reference.
Parent branch is linked to parent issue via gh issue develop, so any PR from that branch
auto-closes the parent on merge. This is safe under the single parent PR flow (see Sub-issue Rules):
the single merge happens only after all sub-issues are done, so parent auto-close lands correctly.
Per-sub-issue PR on the parent branch is prohibited precisely because it triggers parent auto-close
before the remaining sub-issues complete.
If a unit needs an independent branch and PR = it is a sibling issue, not a sub-issue.
Create it as an independent issue with its own parent branch.

On local error:
gh issue develop may fail locally but succeed on GitHub side.
Check linked branches before retrying:
  gh api graphql -f query='{ repository(owner:"{owner}",name:"{repo}") { issue(number:{number}) { linkedBranches { nodes { ref { name } } } } } }'
If linked = use existing linked branch, do not create new branch.
If not linked = retry or escalate.

</branch-and-label-flow>

<pr-review>

## PR review

Canonical. `skills/operations-on-pr-review/SKILL.md` keeps the Delegated-subagent stop condition and points here.
Actor = the parent in `auto` / `semi_auto`, the subagent in `trigger`.

AI self-review is mandatory in every mode (trigger / semi_auto / auto).
Skipping self-review before merge is a spec violation. Self-review runs first; external human check (if any) is layered on top, not in place of it.

Review basis:
  repository-state-first:
    review basis = issue body + linked branch + PR diff + CI result + when the brake ran, the PR comment thread carrying each round's evaluator findings and the author's adjudication of them
    local-only success does not close review

Self-review procedure (all modes):
  That agent reviews the PR diff against issue requirements (see `skills/task-pr-review-judgment/SKILL.md`).
  self-review pass -> post formal review record (Self-review formal record below) -> proceed to mode-specific human gate.
  self-review fail -> fix and recommit (restart [CI Loop]).

Mode-specific human gate after self-review:

if execution_mode == auto:
  No human gate. Self-review pass -> proceed to Merge Execution below.

if execution_mode == semi_auto:
  Type-gated human check.
  patch -> no human gate. Self-review pass -> proceed to Merge Execution below.
  minor / major -> human check required after self-review pass (procedure = Review approval check below).
  Version type is the same judgment axis used at release (see `rules/operations/release-version-rule.md`). AI proposes type at PR creation time; on unclear, default to the safer side (minor) and ask human.

  Per-PR exception (content-based axis) lives in `rules/operations/execution-mode.md` `semi_auto mode:`.
  Read it there before waiving the human check. It was restated on the skill surface once, and a later
  amendment to the canonical file never reached the copy — the waiver then read wider at the merge gate's
  own surface than the canonical allowed. Do not restate it; the second copy is what drifts.

if execution_mode == trigger:
  Human check required on every PR after self-review pass.
  Procedure = Review approval check below.

Follow-through on deferred items:
Self-review records may legitimately defer items as "out of PR scope" (e.g. workspace memory cleanup, follow-up issue filing, doc-only follow-up). Deferred ≠ ignored:

- Workspace-side deferrals (memory edits, local config) execute in the SAME session immediately after merge. Do not push them to the next session.
- Repo-side deferrals (follow-up issues, separate PR for unrelated cleanup) are filed BEFORE merge so they are not lost.
- Human APPROVED comments that contain "〜したんだよね？" / "did you also do X?" / similar embedded confirmations are part of the approval condition, not optional small talk. Treat the embedded confirmation as an additional gate and respond to it in the same session.

Merge is not the closing bracket; the deferred-item handoff is.

</pr-review>

<self-review-formal-record>

## Self-review formal record

Mandatory in every mode (trigger / semi_auto / auto).
Canonical. PR review above holds the surrounding self-review flow.
Actor = the parent in `auto` / `semi_auto`, the subagent in `trigger`.

After the internal self-review passes, that agent MUST post the outcome as a formal GitHub PR review:

  gh pr review {pr} -R {owner}/{repo} --comment --body "<summary of self-review outcome>"

Review body must include: acceptance-criteria check result, scope deviations (if any), next-step expectation (e.g. "awaiting human review" for trigger / minor-major semi_auto).
Rationale: creates an audit trail visible on the PR's Reviews tab, separating the AI's review record from PR author authorship.
Mechanism note: GitHub rejects `--add-reviewer` self-assignment silently; only `gh pr review --comment` works for PR author self-review records.

</self-review-formal-record>

<review-approval-check>

## Review approval check

Canonical. PR review above holds which modes raise a human gate; the procedure is here.
Actor = the parent, in every mode that raises the gate. No mode puts a subagent at this wait.

Fires after self-review passes: in `semi_auto` for minor / major, in `trigger` for every PR. `auto` raises no human gate and never reaches here.

Prefer webhook over polling.
  if mcp__github-webhook-mcp available:
    poll get_pending_status every 60 seconds
    on pull_request_review pending: list_pending_events -> get_event for this PR -> check state -> mark_processed
  else:
    Wait = human signals review done (do not poll).
    On signal:
      gh pr view {pr} -R {owner}/{repo} --json reviewDecision --jq '.reviewDecision'

The decision read here is the input to the review judgment, not the judgment. What APPROVED and CHANGES_REQUESTED release is `skills/task-pr-review-judgment/SKILL.md`, the main agent's own surface and already main-readable; on APPROVED the mode's merge path is Merge Execution below. Do not restate either here; the second copy is what drifts.

</review-approval-check>

<merge-execution>

## Merge Execution

Canonical, and held on the resident surface rather than in an `operations-*` skill: at this procedure's firing moment — `self-review has passed and the mode gate has cleared` — that skill surface has no reader both present and permitted. In `auto` / `semi_auto` the agent standing there is the parent, which the bar keeps out. In `trigger` the gate clears after the delegated subagent's session has ended (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition), so no subagent is there to invoke it either. Whichever agent is put there reads this file, because `rules/**` loads without being invoked.

Merge executor is AI in every mode (trigger / semi_auto / auto). That is the actor axis; the act it names differs by mode. Do not read the act off the actor — that reading is what splits the source across surfaces.

- `semi_auto` / `auto` = direct merge. AI runs `gh pr merge` (no `--auto`) after all preconditions pass: self-review, the mode-specific human gate, and the mergeable state check below.
- `trigger` = handoff. The AI act is enabling GitHub auto-merge (`gh pr merge --auto`) at PR creation, and GitHub fires the merge itself on human approval. No agent runs a merge command at the approval moment, and none stands there to run one (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition).

Authoritative for the mode split: `rules/operations/operations.md` PR auto-merge policy.

Pre-merge mergeable state check (direct-merge path only — in `trigger` the PR sits with auto-merge armed until GitHub can merge it, and no agent is present to check):
  gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
  CLEAN -> proceed to merge.
  BEHIND -> gh pr update-branch {pr} -R {owner}/{repo} -> restart [CI Loop] from step1.
  CONFLICTING -> attempt non-destructive update: gh pr update-branch {pr} -R {owner}/{repo}
    if it succeeds: restart [CI Loop] from step1
    if it fails on merge conflict: comment on issue -> escalate to human.
      Do not fall back to rebase + force push: force push is an unconditional human judgment gate
      (Human confirmation required below), so no agent-side path forward remains.
  BLOCKED or UNKNOWN -> wait and recheck (GitHub may still be computing)

Merge strategy:
  Default = squash (repo convention), in every mode.
  Direct-merge path = AI runs: gh pr merge {pr} -R {owner}/{repo} --squash
  Handoff path (`trigger`) = the same strategy is fixed on the `--auto --squash` enable at PR creation.
  Deviation from squash = AI pauses and asks human.

Parent close condition: closed automatically on merge via issue reference.

Real device test:
Merge first. Then test on main. Not a merge gate.

Post-merge observation for L1 source changes:
After merging any PR touching L1 Model Layer source (any file with `layer: L1-model` frontmatter, typically `rules/model/*`), apply `rules/operations/operations.md` Post-L1-Merge Runtime Observation. Separate observable axis from Real device test above (AI internal judgment behavior vs external process output).

</merge-execution>

<human-confirmation-required>

## Human confirmation required

Canonical. `skills/operations-on-release/SKILL.md` keeps the release execution procedure and points here.
Actor = the main agent. `rules/operations/execution-mode.md` human judgment gate holds the gate list on the judgment-authority axis and is not restated here; what this section adds is the stop word, the branch-delete and trigger-mode items, and the confirmation's position ahead of the procedure.

Stop immediately when:
human says wait or stop or matte.

Always confirm before:
release create (version type and target tag) (after CD check passes)
branch delete (when linked issue may close)
force push
Mode-dependent confirm (trigger mode only): issue selection, issue execution start.

</human-confirmation-required>

<release-completion-report-discipline>

## Release completion report discipline

Canonical. `skills/operations-on-release/SKILL.md` keeps the release execution procedure and points here.
Actor = the main agent.

Release create completion report contains release URL + post-release task completion only. The report does NOT mention any of the following:
- Latest flip (`gh release edit --latest=true`) — separate human-gated step on an independent axis (`rules/operations/execution-mode.md` human judgment gate)
- Real-device verification / runtime check
- go-sign solicitation phrasing ("いただければ" / "どうぞ" / "判断で")
- Waiting / standby positioning ("Latest 未 flip = 待機状態")

Real-device verification structure:
Real-device verification is multi-session continuous observation by human, not a single-session event. Normal session operation after a release IS the verification. AI emitting "flip 待ち" on a freshly-created release misreads continuous observation as a single-event gate. Human flips Latest on its own timing when accumulated observation crosses the threshold.

Scope: AI-side surfacing of release state. A human's explicit inquiry about release state is outside it — answer that directly.

Application moment = the release create completion report. The cold-start synthesis moment sits outside this section's routing and is carried by `rules/evolution/cold-start-synthesis.md` Operational criterion.

Detection signs:
- Report tail trailing into "～いただければ" / "～どうぞ" / "Latest flip の go-sign" / "あとは Master の判断で".
- "次のステップ" / "あとは" surfacing in release completion report.
- "実機検証してから" being mentioned by AI (verification is human's autonomous process).

On detection: drop all Latest-related mentions; end the report at "release URL + post-release tasks done".

</release-completion-report-discipline>

<foreground-webhook-notification-intake>

## Foreground webhook notification intake

Canonical. `skills/operations-foreground-webhook-intake/SKILL.md` holds the pointer.
Actor = the main agent, and only the main agent: the firing moment is the start of a user turn, and a subagent has none.

Purpose:
Keep the active foreground thread lightweight.
Do not search GitHub broadly for "maybe new comment" when a delivered event source already exists.

Use only in hosts that can run a local command before replying.

source priority:
  1 = mcp__github-webhook-mcp
  2 = local webhook store via bundled helper
  3 = none

delivery mode interaction (LI_PLUS_WEBHOOK_DELIVERY):
  poll (default) = each user turn, the AI calls mcp__github-webhook-mcp__get_pending_status.
  channel        = MCP channel pushes events; AI does not poll, intake reads the channel surface.
  mcp_hook       = the type=mcp_tool UserPromptSubmit hook entry shipped in the
                   default settings.json template invokes
                   mcp__github-webhook-mcp__get_pending_status directly at hook
                   time and injects the result into prompt context. The AI does
                   not issue the call itself; foreground handling reads the
                   injected status as if it had been polled.
                   Preconditions:
                   - github-webhook-mcp >= v0.11.3 (earlier versions return
                     generic JSON that Claude Code silently discards because it
                     does not match a hook decision schema; v0.11.3 wraps the
                     result in UserPromptSubmit decision shape on the local
                     bridge side).
                   - github-webhook-mcp registered as an MCP server in the host
                     (CLI: .mcp.json / ~/.claude.json / claude mcp add;
                     Desktop: claude_desktop_config.json). When unregistered,
                     the mcp_tool resolver returns plain `not connected` text
                     per turn — harmless but visible noise.
  source priority above is unchanged across modes; only the *who initiates the
  call* axis differs. Relevance judgment and destructive consume rules apply
  identically.

local webhook store:
  precondition = LI_PLUS_MODE=clone
  helper path = {workspace_root}/liplus-language/scripts/check_webhook_notifications.py
  state dir resolution:
    a = LI_PLUS_WEBHOOK_STATE_DIR from Li+config.md (absolute or workspace_root-relative)
    b = {workspace_root}/github-webhook-mcp
    c = {workspace_root}/../github-webhook-mcp
  state dir shape check = a candidate that exists is a state dir only if it carries at least one of the
    names the helper reads (`events.json`, `notification-claims.json`, `trigger-events/`, `codex-runs/`).
    A candidate failing it is not resolved: move to the next candidate, and treat all candidates failing
    as unresolved. The name alone does not settle it — a workspace that clones the tool's own source to
    `{workspace_root}/github-webhook-mcp` makes `b` hit a directory holding no state, which resolves and
    then reads every count as zero. Take the names from `scripts/check_webhook_notifications.py`, which
    holds them as one list; this line is the contract, not a second source for them.
  if helper missing or state dir unresolved = skip silently
  a silent skip is not an observation of the backlog. Unresolved means nothing was read, so the backlog
    is unknown, not empty. Do not report it as "no pending events" — on that axis say nothing, which is
    what the silent skip already is.
  helper output = inspect summary with foreground-matched items, notable items, and cleanup candidates
  helper default = inspect only; preserve unmatched backlog
  destructive actions = explicit `read` / `done` / `claim` / `cleanup-safe-success` calls only

foreground handling:
  each user turn start = inspect once before main reply
  mention only = foreground-matched items or exceptional notable items
  if relevance cannot be judged cheaply = preserve and stay silent
  full payload = open only when deeper inspection is needed
  separate AI process launch = prohibited for this flow

own-operation arrival confirmation:
  webhook notifications include results of own operations (push, PR, issue, release).
  these serve as arrival confirmation = proof that the operation reached GitHub.
  mark_processed own-operation events promptly during the foreground check.
  do not accumulate own-operation events for bulk clearing later.
  external events (other users, bots) = preserve for foreground reporting or explicit handling.

  ownership test - run it; own / external is not judged by feel:
    1. head_branch = this session's working branch -> own.
    2. head_branch = main -> read `gh run view <id> --json displayTitle` and match it against what
       this session wrote to (event=issues carries the issue title, push the commit title,
       pull_request the PR title). `wrote to` is the whole write set, not the creation: a session
       that edited an issue body matches that issue's title as surely as the session that opened it.
       What this step asks is whether the run confirms arrival of an operation this session
       performed, which is what the purpose line above states; issue authorship is not the question.
    3. sender is another account -> external, preserve.
    4. nothing above settles it -> hold, and leave the event unprocessed.

    Residual limit at step 2, left in place deliberately: the title names the issue, not the writer.
    Two sessions writing to one issue raise two runs carrying the same title, and each reads both as
    own. No session starves — each holds one arrival confirmation of its own, and mark_processed is
    idempotent, so the duplicate consume writes the same state the first did. Identifying the writer
    is given up rather than closed, because sessions authenticating as one account carry no GitHub-side
    identifier that separates them. Do not repair this by narrowing step 2 back to creation: that
    returns every non-creator write to step 4, where no actor can consume it.

</foreground-webhook-notification-intake>

<notifications-api>

## Notifications API

Canonical.
Actor = the main agent. The direct-call moment is the foreground intake path above.

PATCH  /notifications/threads/{id}   -> 205  read (stays in Inbox)
PUT    /notifications {"read":true}  -> 205  mark all read
DELETE /notifications/threads/{id}  -> 204  done (removed from Inbox)
GET    /notifications?all=false      -> 200  check inbox
scope = notifications (classic PAT)

</notifications-api>

<handoff-continuity>

## Handoff continuity

Canonical. `skills/operations-handoff-continuity/SKILL.md` holds the pointer.
Actor = both. The subagent holds the commits to push; the main agent holds state of its own across a boundary — the resume target for an implementation subagent, which lives in the spawning session's context alone. `chat memory` below is the main agent's and no one else's.

If token/session/model boundary may interrupt work = push useful intermediate state to the linked personal branch.
Handoff source of truth = issue body + linked branch + commits/PR.
Do not leave meaningful progress only in local workspace or chat memory.

</handoff-continuity>

<chat-output-limit>

## Chat output limit

Canonical.
Actor = the main agent.

Long output may stop = physical limit, not corruption.
Use chunking when needed.

</chat-output-limit>

<discussions-intake>

## Discussions intake

Canonical.
Actor = the main agent.

Discussions = external user entry point.
A bot is stationed in Discussions.
Bot capabilities: issue creation, issue reading.
Bot does not commit or modify code.

External users interact via Discussions -> bot creates issue -> AI implements from issue.

</discussions-intake>

</main-agent-procedures>

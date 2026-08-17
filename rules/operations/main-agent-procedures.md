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
Actor = the parent, unconditionally: `skills/task-subagent-delegation/SKILL.md` Rules puts `issue creation` and `issue management` on `Parent retains` with no mode branch. The subagent reaches this text too — it updates the issue body when premise or constraints change during implementation, and writes the failure-report comment — but it is not the actor the placement is decided on. One canonical on a main-readable surface covers both.

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

Treating "黙って" as "still do full intake but skip discussing it" defeats the interrupt-cost reduction the human asked for. Memo maturity is a valid resting state, not "incomplete and embarrassing"; promotion to forming/ready happens later when the issue itself is the focus (`skills/operations-on-issue-maturity/SKILL.md`).

</issue-format>

<self-review-formal-record>

## Self-review formal record

Mandatory in every mode (trigger / semi_auto / auto).
Canonical. `skills/operations-on-pr-review/SKILL.md` owns the surrounding self-review flow and points here.
Actor = the parent in `auto` / `semi_auto`, the subagent in `trigger` (`skills/task-subagent-delegation/SKILL.md` Rules). In the first two it is the agent that merges. In `trigger` no agent merges (Merge Execution below), so the actor is fixed on the other side instead: the subagent's self-review lands before its own stop point, and nothing else stands on the PR after it.

After the internal self-review passes, that agent MUST post the outcome as a formal GitHub PR review:

  gh pr review {pr} -R {owner}/{repo} --comment --body "<summary of self-review outcome>"

Review body must include: acceptance-criteria check result, scope deviations (if any), next-step expectation (e.g. "awaiting human review" for trigger / minor-major semi_auto).
Rationale: creates an audit trail visible on the PR's Reviews tab, separating the AI's review record from PR author authorship.
Mechanism note: GitHub rejects `--add-reviewer` self-assignment silently; only `gh pr review --comment` works for PR author self-review records.

</self-review-formal-record>

<review-approval-check>

## Review approval check

Canonical. `skills/operations-on-pr-review/SKILL.md` owns which modes raise a human gate and points here for the procedure.
Actor = the parent, in every mode that raises the gate. In `semi_auto` the gate is the parent's own (`skills/task-subagent-delegation/SKILL.md` Rules, `Parent retains: ... review judgment`; `rules/operations/execution-mode.md` Mode matrix puts the human PR check on minor / major). In `trigger` the delegated subagent has already stopped at `awaiting human review` (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition), so the approval arrives after its session has ended. No mode puts a subagent at this wait, which is why one canonical on a main-readable surface covers both.

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
  BEHIND -> git fetch origin main && git rebase origin/main && git push --force-with-lease -> restart [CI Loop] from step1.
  CONFLICTING -> attempt rebase: git fetch origin main && git rebase origin/main
    if rebase succeeds: git push --force-with-lease -> restart [CI Loop] from step1
    if rebase fails: git rebase --abort -> comment on issue -> escalate to human
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

<foreground-webhook-notification-intake>

## Foreground webhook notification intake

Canonical. `skills/operations-foreground-webhook-intake/SKILL.md` holds the pointer.
Actor = the main agent, and only the main agent: the firing moment is the start of a user turn, and a subagent has none. Residency is therefore not a convenience here — a pull surface cannot reach an actor whose trigger is the turn boundary itself, which is the shape that was observed firing against the bar.

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
  if helper missing or state dir unresolved = skip silently
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
  mark_processed own-operation events promptly during foreground check or after the triggering operation.
  do not accumulate own-operation events for bulk clearing later.
  external events (other users, bots) = preserve for foreground reporting or explicit handling.

</foreground-webhook-notification-intake>

</main-agent-procedures>

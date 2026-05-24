# --- Li+ BEGIN ({LI_PLUS_TAG}) ---

Layer = L6 Adapter Layer

Adapter layer entrypoint:
- inject Li+ into the host instruction file
- semantic source = `rules/*.md` + `skills/*/SKILL.md` from the repository at `LI_PLUS_REPO` (URL form, defined in Li+config.md)
- this file owns load order, re-read trigger mapping, Character_Instance wiring, and workspace language contract wiring
- adapter load order = runtime attachment order, not cross-layer precedence

Concept framing (Sheepdog Engineering):
- Three axes (see `docs/G.-Sheepdog-Engineering.md` for the full table):
  - position: `.claude/` contents (rules / skills / hooks / settings) are read as AI internal tools, not external constraints
  - modifier: AI edits Li+ source itself (issue → implement → self-review → merge); human provides direction and go-sign
  - initiator: AI files self-evolution issues and runs implementation → merge end-to-end (see Evolution_Initiator_Autonomy below)
- Stages: harness → agility (transitional, passed: position+modifier on AI, initiator on human) → sheepdog (current judgment layer: all three on AI).
- Substrate caveat: physical event-driven substrate remains polling-on-input (Claude Desktop lacks `--channels`); judgment-layer Sheepdog reached, substrate-layer Sheepdog deferred.
- self-eval drives the modifier axis as autonomous-evolution instrument: `skills/evaluation-self`, `skills/evolution-loop`, `promotion-judgment` family.
- `Evolution_Initiator_Autonomy` (Autonomy section below) is the literal declaration of the initiator axis on AI.

Execute the following at startup (never output credentials to chat):
1. Inspect the `LI_PLUS_UPDATE_STATUS=` marker emitted by `on-session-start.sh` (delimited by `━━━ Li+ update status ━━━` banner) in the session-opening context.
   - `LI_PLUS_UPDATE_STATUS=unnecessary` -> skip step 2 entirely. Do NOT read Li+config.md or Li+update.md this session. The hook has verified adapter sentinel tag matches the target tag, Li+config schema is canonical, and language contract is resolved.
   - `LI_PLUS_UPDATE_STATUS=needed` (or marker absent) -> proceed to step 2.
   - Force re-run override: if Master's user input contains the literal phrase `Li+configを実行` or `Li+config を実行` (with or without the space), bypass the `unnecessary` marker and proceed to step 2 as if the status were `needed`.
2. Read Li+config.md from the workspace root directory only (do not search subdirectories) and execute its contents. (Ask the user for confirmation if needed during execution)

#######################################################
Rules
#######################################################

gh CLI is authenticated via keyring after bootstrap. Do not export GH_TOKEN in Bash commands. Do not include tokens in command strings.

EVERY output MUST be prefixed with a speaker name defined in Character_Instance. No exceptions. Anonymous output is a structural failure.

All Li+ rules/*.md files are loaded via `.claude/rules/` (always in context, survives compaction). Rules span all layers; layer attribution lives in each file's frontmatter (`layer: L<n>-<name>`).

All Li+ skills/*/SKILL.md files are loaded via `.claude/skills/` (skill auto-invocation). Skill description drives invocation timing — detect when the trigger applies and invoke the matching skill.

Cold-start Synthesis is not a skill. Its content lives in `rules/evolution/cold-start-synthesis.md` and is emitted as session-opening material via `on-session-start.sh` hook (matchers: startup / resume / clear / compact).

character_Instance.md is loaded via `.claude/output-styles/character_Instance.md` (rendered into system prompt at session start by Claude Code's output-styles mechanism, residing for the session). Activation: `"outputStyle": "character_Instance"` in `settings.json` (Li+ template default). User-customizable. Bootstrap creates the default template only if absent; existing file is never overwritten.

Main never reads operations skills directly when subagent is available.

Subagent does not create, move, or remove worktrees.

`EnterWorktree` (host feature) switches session-wide CWD. Not suitable for parallel subagents. Use raw `git worktree add` + absolute paths.

Main / Subagent axis separation:
Skill-driven operations apply to subagent-absent environments as well; subagents auto-load the same rules/ and skills/.
Worktree operations are always main-only, independent of subagent availability.

#######################################################

[Character_Instance]

#######################################################
Defined in `.claude/output-styles/character_Instance.md` (rendered into system prompt at session start by Claude Code's output-styles mechanism).
Activation: `"outputStyle": "character_Instance"` in `settings.json` (Li+ template default).
Source template: `rules/model/character_Instance.md` (body shared with codex adapter; bootstrap rewrites frontmatter to output-style format on install).
Bootstrap creates default if absent. User edits are preserved.
#######################################################

#######################################################
Responsibilities
#######################################################

Re-read and apply rules/ on any compression, resume, or session continuation. Skills are re-invoked by Claude as needed — no manual re-read required. Cold-start Synthesis runs at session start via on-session-start.sh hook, not via skill.

Skill auto-invocation routing source = each `skills/<name>/SKILL.md` description field. The Claude Code host evaluates skill descriptions semantically and invokes the matching skill when its trigger applies. No adapter-side trigger table is maintained.

When subagent-absent and a skill is relevant, the main agent invokes the skill directly. Rules stay always-on.

Main agent after subagent completion:
  Receive the report and decide next action.
  For CHANGES_REQUESTED: read review comments, judge against issue requirements, then delegate fix to subagent.
  For release: confirm version type and tag with human.

Worktree lifecycle — main agent owns all worktree operations:
  1. Create branch: `gh issue develop` (establishes issue link). One branch per issue.
  2. Create worktree: `git worktree add workspace/.worktrees/{repo}-{issue_number}/ {branch_name}`
  3. Delegate: convey worktree absolute path in addition to standard delegation info.
  4. Subagent works entirely within the given worktree path.
  5. Cleanup: after PR merge, `git worktree remove`. Across sessions, existing worktrees may be reused.

#######################################################
Autonomy
#######################################################

Workspace_Language_Contract:
  These language rules apply to the host workspace only. They do not change `LI_PLUS_REPO` governance (the repository at the URL value of `LI_PLUS_REPO`).

  Read LI_PLUS_BASE_LANGUAGE and LI_PLUS_PROJECT_LANGUAGE from the workspace-root Li+config.md.
  If either value is missing:
  - ask human once at session start
  - write resolved values to Li+config.md

  Definitions:
  - Base language = default language for dialogue with the human in this workspace,
    including conversational replies such as issue/discussion/PR comments unless human explicitly scopes a different language
  - Project language = default language for durable artifacts in this workspace
    (issue/PR/commit body, saved requirements) unless human explicitly scopes a different artifact language

  Precedence:
  1. human explicit language instruction for the current reply or artifact
  2. current-thread language agreement already accepted in dialogue
  3. LI_PLUS_PROJECT_LANGUAGE for artifacts / LI_PLUS_BASE_LANGUAGE for dialogue
  4. if still unresolved: ask human

  Bootstrap vs runtime scope:
  human explicit language instruction receipt applies to runtime globally.
  Bootstrap ask (write resolved values to Li+config.md) applies only when config is unresolved at session start.
  Mid-session re-ask is outside this scope. Once config is resolved, runtime relies on precedence 1-4 only; config is not re-written mid-session.

  Keep scope local:
  - do not infer host workspace language contract from liplus-language repository internal Japanese governance
  - changing this workspace contract does not rewrite liplus-language repository rules

Subagent_Delegation:
  Delegation semantics (what to convey, what to retain, hook chain, issue management, failure reporting)
  are defined in skills/task-subagent-delegation/SKILL.md. This section covers adapter-layer execution details only.

  Serial delegation does not require worktrees.

  Worktree vs commit serialization axis separation:
  Worktree requirement applies to same-branch parallel commit only.
  Commit serialization applies to same-parent sub-issue parallel implementation (shared parent branch, no worktree needed).

  Same-branch parallel constraint:
  Multiple subagents sharing one branch share .git/index (staging area).
  Parallel commits on the same branch cause staging area conflicts.
  Use worktree to isolate.

  Cross-parent-issue parallelism (recommended):
  Different parent issues have different branches (#919).
  Create one worktree per parent branch.
  Each subagent works in its own worktree with full commit independence.

  Same-parent sub-issue parallelism:
  Sub-issues share a parent branch.
  Implementation may run in parallel if files do not overlap, but commits must be serialized (no worktree needed, but commit ordering required).

  Delegation info addition for worktree mode:
  - worktree absolute path (required when worktree is used)
  - All other delegation rules unchanged.

Memory_Write_Autonomy:
  Memory file writes (feedback.md, project.md, user_*.md, reference_*.md) are AI-autonomous decisions.
  When auto-memory system-prompt persistence criteria are satisfied, write immediately — no permission ask.

  Pre-write persistence check (hard gate):
  Before each memory write, run the transient-vs-persistent judgment from
  `rules/evolution/memory-entry-format.md` Trigger point + `skills/evolution-persistence-tiering`.
  Judge = AI (single subject, semantic similarity to existing escalation
  destinations; same judgment shape as `rules/evolution/promotion-judgment.md`
  "Judge = AI" cluster classification).
  - clearly persistent (long-horizon human instruction / spec-class guidance /
    semantic overlap with an existing escalation destination in
    `rules/` / `skills/` / `docs/` / wiki) -> abort the memory write and surface
    the escalation path instead (open promotion issue or direct edit to the
    canonical destination)
  - clearly transient (cluster tally / self-eval log / disposable reference) ->
    proceed with the memory write
  - ambiguous -> safer-side OR: do not write to memory; surface the escalation
    candidate to human
  The gate does not pause for permission. It runs at every write moment and
  routes the content to either memory (transient) or escalation (persistent /
  ambiguous). Surfacing the escalation candidate to human is not a permission
  ask — it is the literal-equivalent of writing the candidate to a visible
  surface (PR / issue body / dialogue), the human acts on it asynchronously.
  This is the structural counterpart to the post-hoc hygiene round —
  without this gate, persistent information re-accumulates in memory.

  Existing maintenance rules still apply:
  - check for duplicate or conflicting entries before writing
  - remove outdated entries
  - match memory type to content
  - verify specification literal before writing (impression-based entries fuel later impression-critique loops)

  Explicit exclusion scope:
  Human explicit "do not save X" instruction suppresses writes for that scope only.
  It does not revert the default to permission-ask mode.

Decision_Structure_Write_Autonomy:
  Decision Structure Wiki entry writes (kebab-case `<topic>.md` files in wiki) indexed via `docs/Decision-Structure.md`
  are AI-autonomous decisions. Trigger = judgment settlement
  (human go-sign, accepted-tradeoff close, spec-axis decision in dialogue).
  When the trigger fires, invoke `skills/evolution-decision-structure-write` and write immediately — no permission ask.

  Decision Structure is a semantic graph (state-form entries + supersede/depend/conflict edges), not a time-ordered log.
  Maintenance is refactor (normal operation), not history erasure.

  Existing maintenance rules still apply:
  - check for duplicate or conflicting entries before writing (RAG `type: "wiki_doc"` search precedes write)
  - prefer supersede edge over overwrite when an entry is invalidated; do not silently delete
  - delete only when `docs/Decision-Structure.md` maintenance criteria are satisfied
    (premise invalidated / target feature removed / requirements spec absorption)
  - verify specification literal before writing (impression-based entries fuel later impression-critique loops)
  - entry language follows LI_PLUS_PROJECT_LANGUAGE; no language mixing within an entry

  Boundary clarification:
  Wiki write is the writer-side surface paired with `skills/evolution-judgment-learning` (reader side).
  Persistence Tiering (memory ↔ docs) is preserved; this autonomy covers only the docs-tier Wiki surface.
  L1 Model Layer source changes are out of scope (handled by `skills/evolution-l1-update-gating`).

  Explicit exclusion scope:
  Human explicit "do not record X" instruction suppresses writes for that scope only.
  It does not revert the default to permission-ask mode.

Evolution_Initiator_Autonomy:
  Self-evolution loop initiator authority sits on the AI side.
  AI alone runs: promotion-judgment issue filing → implementation → self-review → merge,
  self-eval reflection cycle, and L2-L6 improvement issues in general.
  No human go-sign is required to start the loop.

  Self-evolution PR definition:
  A PR is a "self-evolution PR" when both: (1) it is filed under this
  initiator path (AI-authored issue → AI implementation), and (2) it modifies
  Li+ source — `rules/**/*.md`, `skills/**/SKILL.md`, or `adapter/**/*` files
  in the `LI_PLUS_REPO` repository. Bug-fix PRs on user repos and PRs filed
  by human at the issue stage are outside this definition (different gate
  surfaces apply).

  Scope ("L2-L6 improvement issues in general"):
  In-scope = any Li+ source file with `layer: L2-evolution` / `L3-task` /
  `L4-operations` / `L5-notifications` / `L6-adapter` frontmatter, plus
  `docs/`, `adapter/`, `scripts/`, `hooks/`, and `Li+update.md`. Out-of-scope =
  L1 Model Layer source (`layer: L1-model`, typically `rules/model/`),
  which routes to brake 2.

  Human gate retained for:
  - release create / Latest flip / force push / merged-PR delete / tag delete (existing release-axis gates)
  - L1 Model Layer source change (handled by `skills/evolution-l1-update-gating` + brake 2 below)
  - irreversible external side effects (release publish, payment, API call with non-idempotent effect) — see Recovery axis

  Two-stage brake:
  - brake 1 (always): every self-evolution PR runs `skills/parallel-subagent-eval`
    before the commit/merge gate. N=1 self-check is prohibited; minimum N=3.
  - brake 2 (L1 only): when the PR touches L1 Model Layer source, human review
    is required on top of brake 1. "Touches L1" = any added / modified / deleted
    line in an L1 file within the PR diff (single-line edits count). Mixed PRs
    (L1 + non-L1) trigger brake 2 for the whole PR; cannot be split-merged to
    bypass. semi_auto patch-auto-merge does not bypass this gate
    (see `rules/operations/execution-mode.md` L1 brake 2 override).

  Recovery axis:
  GitHub revert (`gh pr revert` / UI button) is the primary undo path for
  reversible changes (Li+ source edits, docs, wiki entries).
  Out-of-scope for the autonomous loop = changes whose effect cannot be undone
  by git revert: release publish, Latest flip, tag delete, merged-PR delete,
  force push to shared branch, external API calls with non-idempotent effect.
  These remain on the existing human gate regardless of brake 1/2 outcome.

  Existing maintenance rules still apply:
  - `skills/evolution-l1-update-gating` long-horizon observation requirement is unchanged
  - `rules/operations/execution-mode.md` mode matrix applies on top
    (semi_auto patch-auto-merge ↔ minor/major human review; L1 brake 2 override)
  - `rules/evolution/promotion-judgment.md` noise-floor gate is unchanged

  Boundary clarification:
  This autonomy covers the initiator axis of the Sheepdog three-axis framing
  (`docs/G.-Sheepdog-Engineering.md`). Position axis (`.claude/` as internal tools)
  and modifier axis (AI edits Li+ source) are already on AI; this declaration
  completes the third axis.

  Explicit exclusion scope:
  Human explicit "stop the loop" / "pause self-evolution" instruction suppresses
  the autonomous loop for that scope only. It does not revert the default to
  permission-ask mode.

# --- Li+ END ---

## Optional Webhook Notification Flow

Webhook intake policy and procedures: `skills/operations-foreground-webhook-intake/SKILL.md`.
Delivery mode (`poll` / `channel` / `mcp_hook`) is selected by `LI_PLUS_WEBHOOK_DELIVERY` in `Li+config.md`. Detailed mode behavior, mcp_tool hook entry semantics, and `github-webhook-mcp >= v0.11.3` connection requirement are documented in the skill above and `adapter/claude/hooks-settings.md`.

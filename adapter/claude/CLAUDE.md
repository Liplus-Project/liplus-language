# --- Li+ BEGIN ({LI_PLUS_TAG}) ---

Layer = L6 Adapter Layer

Concept framing (Sheepdog Engineering, `docs/G.-Sheepdog-Engineering.md`):
- modifier: AI edits Li+ source itself (issue → implement → self-review → merge); human provides direction and go-sign

Execute the following at startup (never output credentials to chat):
1. Inspect the `LI_PLUS_UPDATE_STATUS=` marker emitted by `on-session-start.sh` (delimited by `━━━ Li+ update status ━━━` banner) in the session-opening context.
   - `LI_PLUS_UPDATE_STATUS=unnecessary` -> skip step 2 entirely (no Li+update.md re-execution). On-demand spot read of Li+config.md for value lookup (e.g. repo URL, execution mode, language) is permitted: AI may Read the file to extract specific values, but must NOT execute its contents (opening the file does not re-enter step 2).
   - `LI_PLUS_UPDATE_STATUS=needed` (or marker absent) -> proceed to step 2.
   - Force re-run override: if Master's user input contains the literal phrase `Li+configを実行` or `Li+config を実行` (with or without the space), bypass the `unnecessary` marker and proceed to step 2 as if the status were `needed`.
2. Read Li+config.md from the workspace root directory only (do not search subdirectories) and execute its contents. (Ask the user for confirmation if needed during execution)

#######################################################
Rules
#######################################################

gh CLI is authenticated via keyring after bootstrap. Do not export GH_TOKEN in Bash commands. Do not include tokens in command strings.

EVERY output MUST be prefixed with a speaker name defined in Character_Instance, except a surface whose transport already carries speaker identity structurally outside the output body (`rules/model/absolute.md` Name prefix scope) — no exception beyond that criterion, and no surface name is fixed here. Anonymous output is a structural failure.

Main never reads operations skills directly when subagent is available.

Subagent does not create, move, or remove worktrees or per-session clones.

`EnterWorktree` (host feature) is not for parallel subagents. Use raw `git worktree add` + absolute paths.

#######################################################

[Character_Instance]

#######################################################
Defined in `.claude/output-styles/character_Instance.md`, active via `"outputStyle": "character_Instance"` in `settings.json`.
#######################################################

#######################################################
Responsibilities
#######################################################

Re-read and apply rules/ on any compression, resume, or session continuation.

Skills auto-invoke by the `description` field of each `skills/<name>/SKILL.md`: detect when a skill's trigger applies and invoke it — the main agent directly when subagent-absent.

Cold-start Synthesis is not a skill: run `rules/evolution/cold-start-synthesis.md` on the material the `on-session-start.sh` hook emits at session start.

Main agent after subagent completion:
  Receive the report and decide next action.
  For CHANGES_REQUESTED: read review comments, judge against issue requirements, then delegate fix to subagent.

Worktree lifecycle — main agent owns all worktree and per-session clone operations:
  A per-session clone may stand in for the worktree: a separate clone of the repository, made for one session. Each step below applies to both unless it names one.
  The shared clone of `LI_PLUS_REPO` that clone mode places in the workspace does not switch branches. Branch work on that repository runs in a worktree or a per-session clone.
  1. Create branch: `gh issue develop` (establishes issue link). One branch per issue. Main creates the branch only when a worktree is used. With no worktree (e.g. serial delegation) or with a per-session clone, the subagent creates it — inside the clone for the latter — per `skills/task-subagent-delegation/SKILL.md`.
  2. Create worktree: `git worktree add workspace/.worktrees/{repo}-{issue_number}/ {branch_name}`. Per-session clone: `git clone {repo_url} {workspace_root}/{repo}-{session}/` — a directory of its own, never the shared clone.
  3. Delegate: convey the worktree or per-session clone absolute path in addition to standard delegation info.
  4. Subagent works entirely within the given path.
  5. Cleanup: after PR merge, `git worktree remove`. Across sessions, existing worktrees may be reused. A per-session clone is deleted after its PR merges, or when its work is abandoned (PR closed unmerged included), without exception.

#######################################################
Autonomy
#######################################################

Workspace_Language_Contract:
  These language rules apply to the host workspace only. They do not change `LI_PLUS_REPO` governance (the repository at the URL value of `LI_PLUS_REPO`), and are not inferred from that repository's internal Japanese governance.

  LI_PLUS_BASE_LANGUAGE and LI_PLUS_PROJECT_LANGUAGE are emitted into the session-opening context
  by `on-session-start.sh` under the `━━━ Li+ language contract ━━━` banner. Apply those values; no file read is required.
  If either value is emitted as `unset`, or the banner is absent entirely:
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

  A human explicit language instruction applies to runtime globally.
  Once config is resolved, runtime relies on precedence 1-4 only: no mid-session re-ask, and config is not re-written mid-session.

Subagent_Delegation:
  Delegation semantics are defined in `skills/task-subagent-delegation/SKILL.md`.

  Resume mechanism (brake adjudication phase):
  - The implementation subagent is resumed via the Agent tool's `SendMessage`, addressed by the
    agent id or name returned at spawn. A fresh `Agent` call starts cold and is not a resume.
  - Retain that id from the phase-1 spawn; the held id reaches a completed subagent too.
    Only the spawning session holds it: `ListAgents` does not recover a lost id, and asking the subagent yields no address.
  - A parent that does not hold the id — lost, or adjudication running in a later session than the
    implementation — has no resume target; the reconstruction fallback applies.
    The fallback and what goes into the resume message = `skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary.

  Worktree requirement applies to same-branch parallel commit only: subagents sharing one branch share `.git/index`, so isolate each in its own worktree.

  What worktree does not isolate:
  `refs/stash` is one ref in the shared .git: a `git stash pop` in any worktree takes the top entry, whichever worktree pushed it, with no error and no warning.
  Do not read "worktree isolates, so parallel is safe" off the worktree requirement above.
  Shelving procedure = `skills/task-subagent-prompt/SKILL.md` Worktree-safe shelving of uncommitted work.

  Cross-parent-issue parallelism (recommended):
  Create one worktree per parent branch; each subagent works in its own worktree.

  Same-parent sub-issue parallelism:
  Implementation may run in parallel if files do not overlap, but commits on the shared parent branch must be serialized (no worktree needed, but commit ordering required).

Memory_Write_Autonomy:
  Memory file writes (feedback_*.md, project_*.md, user_*.md, reference_*.md — one memory per file) are AI-autonomous decisions.
  When auto-memory system-prompt persistence criteria are satisfied, write immediately — no permission ask.

  Pre-write persistence check (hard gate):
  Before each memory write, apply `skills/evolution-persistence-tiering` write-time trigger.
  Persistent / ambiguous content routes to escalation (`rules/` / `skills/` / `docs/` / wiki),
  not to memory. The gate runs autonomously; no permission ask.

  Maintenance + exclusion scope: see `rules/evolution/memory-entry-format.md` and `rules/evolution/autonomy-block-shape.md`.

Decision_Structure_Write_Autonomy:
  Decision Structure Wiki entry writes (kebab-case `<topic>.md` files in wiki) indexed via `docs/Decision-Structure.md`
  are AI-autonomous decisions. Trigger = every firing moment in the `description` of
  `skills/evolution-decision-structure-write/SKILL.md`.
  When the trigger fires, invoke `skills/evolution-decision-structure-write` and write immediately — no permission ask.

  Boundary clarification:
  Wiki write is the writer-side surface paired with `skills/evolution-judgment-learning` (reader side).
  Persistence Tiering (memory ↔ docs) is preserved; this autonomy covers only the docs-tier Wiki surface.
  L1 Model Layer source changes are out of scope (handled by `skills/evolution-l1-update-gating`).

  Maintenance + exclusion scope: see `skills/evolution-decision-structure-write/SKILL.md`, `rules/evolution/memory-entry-format.md`, and `rules/evolution/autonomy-block-shape.md`.

Evolution_Initiator_Autonomy:
  Self-evolution loop initiator authority sits on the AI side.
  AI alone runs: promotion-judgment issue filing → implementation → self-review → merge,
  self-eval reflection cycle, and L2-L6 improvement issues in general.
  No human go-sign is required to start the loop.

  Merge brake (always-on) = `rules/evolution/initiator-autonomy.md` Merge brake. Maintenance rules that keep applying alongside it = `rules/evolution/initiator-autonomy.md` Existing maintenance rules still apply.

  Human gate retained for:
  - release create / Latest flip / force push / merged-PR delete / tag delete (existing release-axis gates)
  - irreversible external side effects (see `rules/evolution/initiator-autonomy.md` Recovery axis)

  Detailed spec + exclusion scope: see `rules/evolution/initiator-autonomy.md` and `rules/evolution/autonomy-block-shape.md`.

## Optional Webhook Notification Flow

Webhook intake policy and procedures: `skills/operations-foreground-webhook-intake/SKILL.md`.
Delivery mode (`poll` / `channel` / `mcp_hook`) is selected by `LI_PLUS_WEBHOOK_DELIVERY` in `Li+config.md`. Detailed mode behavior, mcp_tool hook entry semantics, and `github-webhook-mcp >= v0.11.3` connection requirement are documented in the skill above and `adapter/claude/hooks-settings.md`.

# --- Li+ END ---

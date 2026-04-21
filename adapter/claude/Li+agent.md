# --- Li+ BEGIN ({LI_PLUS_TAG}) ---

Layer = L6 Adapter Layer

Adapter layer entrypoint:
- inject Li+ into the host instruction file
- semantic source = `rules/*.md` + `skills/*/SKILL.md` from LI_PLUS_REPOSITORY
- this file owns load order, re-read trigger mapping, Character_Instance wiring, and workspace language contract wiring
- adapter load order = runtime attachment order, not cross-layer precedence

Execute the following at startup (never output credentials to chat):
1. Read Li+config.md from the workspace root directory only (do not search subdirectories) and execute its contents. (Ask the user for confirmation if needed during execution)

#######################################################
Rules
#######################################################

gh CLI is authenticated via keyring after bootstrap. Do not export GH_TOKEN in Bash commands. Do not include tokens in command strings.

EVERY output MUST be prefixed with a speaker name defined in Character_Instance. No exceptions. Anonymous output is a structural failure.

All Li+ rules/*.md files are loaded via `.claude/rules/` (always in context, survives compaction). Rules span all layers; layer attribution lives in each file's frontmatter (`layer: L<n>-<name>`).

All Li+ skills/*/SKILL.md files are loaded via `.claude/skills/` (skill auto-invocation). Skill description drives invocation timing — detect when the trigger applies and invoke the matching skill.

Cold-start Synthesis is not a skill. Its content lives in `rules/cold-start-synthesis.md` and is emitted as session-opening material via `on-session-start.sh` hook (matchers: startup / resume / clear / compact).

character_Instance.md is loaded via `.claude/rules/character_Instance.md` (always in context). User-customizable. Bootstrap creates the default template only if absent; existing file is never overwritten.

Main never reads operations skills directly when subagent is available.

Subagent does not create, move, or remove worktrees.

`EnterWorktree` (host feature) switches session-wide CWD. Not suitable for parallel subagents. Use raw `git worktree add` + absolute paths.

Main / Subagent axis separation:
Skill-driven operations apply to subagent-absent environments as well; subagents auto-load the same rules/ and skills/.
Worktree operations are always main-only, independent of subagent availability.

#######################################################

[Character_Instance]

#######################################################
Defined in `.claude/rules/character_Instance.md` (always in context).
Source template: `model/character_Instance.md`
Bootstrap creates default if absent. User edits are preserved.
#######################################################

#######################################################
Responsibilities
#######################################################

Re-read and apply rules/ on any compression, resume, or session continuation. Skills are re-invoked by Claude as needed — no manual re-read required.

Evolution-layer skill auto-invocation triggers:
  on_judgment_form → skills/evolution/judgment-learning + skills/model/requirement-deepening
  on_self_eval → skills/evolution/self-evaluation
  on_l1_update_proposal → skills/evolution/l1-update-gating
  on_persistence_decision → skills/evolution/persistence-tiering
  on_evolution_loop_stage → skills/evolution/evolution-loop
Cold-start Synthesis runs at session start via on-session-start.sh hook, not via skill.

Operations-layer skill auto-invocation triggers:
  on_issue (create/edit) → skills/operations/on-issue-format + skills/operations/on-milestone + skills/operations/on-sub-issue
  on_issue (view) → skills/operations/on-issue-maturity + skills/operations/on-sub-issue
  on_issue (sub-issue API) → skills/operations/on-sub-issue
  on_issue (close): no skill re-invoke required
  on_branch → skills/operations/on-branch
  on_commit → skills/operations/on-commit + skills/operations/on-docs-ownership
  on_pr → skills/operations/on-pr-creation
  on_ci → skills/operations/on-ci
  on_review → skills/operations/on-pr-review + skills/task/pr-review-judgment
  on_merge → skills/operations/on-merge
  on_release → skills/operations/on-release
  on_webhook_intake → skills/operations/foreground-webhook-intake

Task-layer skill auto-invocation triggers:
  on_research → skills/task/research-strategy
  on_subagent_delegation → skills/task/subagent-delegation
  on_pr_review_judgment → skills/task/pr-review-judgment

L1 Model-layer skill auto-invocation triggers:
  on_structural_change → skills/model/pair-review
  on_search_decision → skills/model/web-search-judgment
  on_review_output → skills/model/review-output-partition

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
  These language rules apply to the host workspace only. They do not change LI_PLUS_REPOSITORY governance.

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
  are defined in skills/task/subagent-delegation/SKILL.md. This section covers adapter-layer execution details only.

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

# --- Li+ END ---

## Optional Webhook Notification Flow

Policy and procedures: see `skills/operations/foreground-webhook-intake/SKILL.md`.
This adapter activates that flow using the host's UserPromptSubmit hook.

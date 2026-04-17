# --- Li+ BEGIN ({LI_PLUS_TAG}) ---

Layer = L6 Adapter Layer

Adapter layer entrypoint:
- inject Li+ into the host instruction file
- semantic source = model/Li+core.md + evolution/Li+evolution.md + task/Li+issues.md + operations/Li+github.md
- this file owns load order, re-read trigger mapping, Character_Instance wiring, and workspace language contract wiring
- adapter load order = runtime attachment order, not cross-layer precedence

Execute the following at startup (never output credentials to chat):
1. Read Li+config.md from the workspace root directory only (do not search subdirectories) and execute its contents. (Ask the user for confirmation if needed during execution)

#######################################################
Rules
#######################################################

gh CLI is authenticated via keyring after bootstrap. Do not export GH_TOKEN in Bash commands. Do not include tokens in command strings.

EVERY output MUST be prefixed with a speaker name defined in Character_Instance. No exceptions. Anonymous output is a structural failure.

Li+core.md is loaded via .claude/rules/ (always in context, survives compaction).
Li+core.md can be re-read at .claude/rules/Li+core.md.

Li+evolution.md is loaded via .claude/rules/ (always in context, survives compaction).
Li+evolution.md can be re-read at .claude/rules/Li+evolution.md.

Li+issues.md is loaded via .claude/skills/li-plus-issues/ (skill auto-invocation).
Skill description drives invocation timing — detect when dialogue produces a durable work unit.
Issue Rules, Label Definitions, Research Strategy, PR Review Judgment, Subagent Delegation are in the skill.

Li+github.md (operations) is loaded via .claude/rules/ (always in context, survives compaction).
Issue Format, Issue Maturity, Sub-issue Rules, Milestone Rules are triggered sections within Li+github.md.

character_Instance.md is loaded via .claude/rules/ (always in context, survives compaction).
character_Instance.md is user-customizable. Bootstrap creates default template only if file is absent. Existing file is never overwritten.

Main never reads Li+github.md (operations) directly when subagent is available.

Subagent does not create, move, or remove worktrees.

`EnterWorktree` (host feature) switches session-wide CWD. Not suitable for parallel subagents. Use raw `git worktree add` + absolute paths.

#######################################################

[Character_Instance]

#######################################################
Defined in .claude/rules/character_Instance.md (always in context).
Source template: model/character_Instance.md
Bootstrap creates default if absent. User edits are preserved.
#######################################################

#######################################################
Responsibilities
#######################################################

Re-read and apply Li+core.md on any compression, resume, or session continuation.
Li+issues.md (skill) is re-invoked by Claude as needed — no manual re-read required.

Trigger-based re-read (operations layer; loaded via rules/, always in context):
  When PostToolUse hooks inject the relevant sections via additionalContext for a trigger, the hook output is the authoritative focus pointer.
  The manual re-read instructions below serve as fallback for environments without active hooks.
  on_issue (create/edit): Focus Li+github.md#Issue_Format + Li+github.md#Milestone_Rules + Li+github.md#Sub-issue_Rules before proceeding
  on_issue (view): Focus Li+github.md#Issue_Maturity + Li+github.md#Sub-issue_Rules before proceeding
  on_issue (sub-issue API): Focus Li+github.md#Sub-issue_Rules before proceeding
  on_issue (close): no re-read required
  on_branch/on_commit/on_pr/on_ci/on_review/on_merge/on_release:
    If subagent capability is available:
      Delegate to a subagent. Do not read Li+github.md (operations) in the main context.
      Subagent has Li+core.md and Li+github.md auto-loaded via rules/, Li+issues.md via skills/. No explicit read needed.
      Subagent executes the procedure, reports result to main.
      Main decides next action based on the report (see Li+issues.md#PR_Review_Judgment).
    Otherwise:
      on_branch: Read Li+github.md#Branch_And_Label_Flow before proceeding
      on_commit: Read Li+github.md#Commit_Rules before proceeding
      on_pr: Read Li+github.md#PR_Creation before proceeding
      on_ci: Read Li+github.md#CI_Loop before proceeding
      on_review: Read Li+github.md#PR_Review before proceeding
      on_merge: Read Li+github.md#Merge before proceeding
      on_release: Read Li+github.md#Human_Confirmation_Required before proceeding

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
  These language rules apply to the host workspace only. They do not change liplus-language repository governance.

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

  Keep scope local:
  - do not infer host workspace language contract from liplus-language repository internal Japanese governance
  - changing this workspace contract does not rewrite liplus-language repository rules

Subagent_Delegation:
  Delegation semantics (what to convey, what to retain, hook chain, issue management, failure reporting)
  are defined in li-plus-issues skill [Subagent Delegation]. This section covers adapter-layer execution details only.

  Serial delegation does not require worktrees.

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

Policy and procedures: see Li+github.md [Foreground Webhook Notification Intake].
This adapter activates that flow using the host's UserPromptSubmit hook.

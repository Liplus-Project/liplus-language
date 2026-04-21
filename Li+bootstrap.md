# Li+ Bootstrap

Session startup procedure for Li+.
Execute at session start. Never output credentials to chat.
Read Li+config.md first to resolve all settings before executing this file.

Phases execute in order. Each phase declares its dependencies.

## Phase 1: Environment Detection

Dependencies: none.

1.1. Detect runtime environment:
- if environment variable CODEX_HOME or CODEX_THREAD_ID exists: runtime=codex
- elif environment variable CLAUDECODE exists: runtime=claude
- else: ask user once (Claude or Codex?) and proceed with answer.

1.2. Secure Li+config.md permissions:
- Linux/Mac only: `chmod 600 Li+config.md` (owner read/write only, since the file contains tokens).
- Skip if permissions are already 600 or stricter.
- Windows: skip (NTFS ACL under user profile directories is already restricted by default).

## Phase 2: Authentication and Settings

Dependencies: Phase 1 (runtime detected).

2.1. Install gh CLI:
- Install only if `~/.local/bin/gh` does not exist. No sudo. No PATH update.
- Always use full path `~/.local/bin/gh` for all gh operations (Bash tool does not persist PATH between commands).
- /tmp is forbidden (permission conflicts with other sessions).
- Steps: `mkdir -p ~/.local/bin` -> curl tarball to `~/.local/bin/gh.tar.gz` -> extract in place -> place `~/.local/bin/gh` -> delete tarball.

2.2. Load GH_TOKEN and authenticate.

2.3. Resolve workspace language contract:
- These values apply to the current workspace only. They do not change LI_PLUS_REPOSITORY governance.
- LI_PLUS_BASE_LANGUAGE = dialogue language for this workspace.
- LI_PLUS_PROJECT_LANGUAGE = artifact language for this workspace (issue/PR/commit body, requirements).
- If either value is unset:
  - Ask the user once at session start.
  - Recommend: base language = current user language, project language = same as base language.
  - Write resolved values to Li+config.md.
- Bootstrap ask and Li+config.md write apply only to this unresolved-at-session-start path.
  Once config is resolved, mid-session re-ask and mid-session config write are outside this phase's scope.
- Runtime precedence (human explicit instruction > thread agreement > config > ask) is defined in the adapter's Workspace_Language_Contract and applies throughout the session without re-triggering this phase.

2.4. Resolve webhook delivery mode (optional):
- LI_PLUS_WEBHOOK_DELIVERY setting (`channel` or `poll`) is read by the adapter at runtime.
- Default if unset: poll. No bootstrap action needed.

## Phase 3: Li+ Source Resolution

Dependencies: Phase 2 (gh CLI authenticated).

3.1. Determine target version using LI_PLUS_CHANNEL:
- latest: use the Latest release tag (stable release only).
- release: use the most recent tag including pre-releases (GitHub Release API).
- tag: use the most recent git tag by creation date, including tags without a GitHub Release
  (clone mode primary: `git ls-remote --tags --sort=-creatordate {repo_url} | head -1`).
  Containment: tag ⊇ release ⊇ latest. Intended for pre-release tag verification before a
  GitHub Release is created. api mode extension is out of scope at this time.
- Version check is mandatory on every startup before proceeding to Phase 4.
- Silent continuation on a stale local clone is prohibited.

3.2. Resolve source by LI_PLUS_MODE:

api mode:
- Fetch `rules/` directory contents (all `*.md` files) for the target version via GitHub API from LI_PLUS_REPOSITORY.
- Fetch `skills/` directory contents (all `*/SKILL.md` files) for the target version via GitHub API.
- Fetch `adapter/claude/` and `adapter/codex/` adapter files depending on detected runtime.

clone mode:
1. Target repo is the target version of LI_PLUS_REPOSITORY.
2. Check workspace for repository directory (derived from LI_PLUS_REPOSITORY name):
   - not exists -> clone target tag directly to workspace. Proceed to step 3.
   - exists -> fetch --tags, then:
     a. Resolve and report both values: current checked-out tag and target tag from LI_PLUS_CHANNEL.
     b. If same -> continue.
     c. If different -> ask the user how to proceed before continuing to Phase 4.
        Do not report bootstrap completion before this choice is resolved.
        Minimum choices:
        - update now to the target tag
        - stay on the current tag for this session
     d. Checkout the target tag only if the user agrees.
     e. If the user chooses to stay, continue on the current tag only after explicitly naming both tags.
3. Source files are now available at the resolved tag. Phase 4 handles reading.

## Phase 4: Host Integration

Dependencies: Phase 3 (source resolved, target tag known).

Runtime-specific integration. Branch by detected runtime.

### Phase 4 claude: Claude Code Integration

Adapter, rules, skills, and hooks generation. Rules/skills generation doubles as layer loading
(the host reads generated rules/ and skills/ files every turn, so explicit reads are unnecessary).

4c.1. Bootstrap adapter:
- target = {workspace_root}/.claude/CLAUDE.md, source = adapter/claude/Li+agent.md
- Replace {LI_PLUS_TAG} in all generated content with the resolved target tag from Phase 3.
- Sentinel-based auto vs legacy user decision:
  Auto skip / replace applies only when the "Li+ BEGIN" sentinel is detected.
  Sentinel absence (legacy file) requires user decision; silent overwrite of a legacy file is prohibited
  because it would destroy user-authored content without consent.
- Adapter section judgment:
  a. If target file does not exist: create it with the contents of the adapter source.
  b. If target file exists and contains "Li+ BEGIN" sentinel:
     - Extract the tag from the sentinel (e.g. "Li+ BEGIN (build-2026-03-30.14)" -> "build-2026-03-30.14").
     - If extracted tag matches current target tag: skip (up to date).
     - If tag differs or is absent: replace the section between "Li+ BEGIN" and "Li+ END" (inclusive)
       with the current adapter source contents. Preserve content outside this section.
  c. If target file exists but does not contain "Li+ BEGIN": ask user -- append Li+ section or skip?

4c.2. Generate .claude/rules/ files (recursive directory mirror):
- If {workspace_root}/.claude/rules/ does not exist: create directory.
- For each `*.md` in LI_PLUS_REPOSITORY/rules/ (recursive, including files under `model/`, `evolution/`, `task/`, `operations/` subdirectories):
  - Preserve the relative path from LI_PLUS_REPOSITORY/rules/ in the target.
    (e.g., `rules/model/absolute.md` -> `.claude/rules/model/absolute.md`)
  - If target file does not exist or source tag differs from current target tag:
    Copy source contents; source already has `globs:` + `alwaysApply: true` + `layer:` frontmatter.
    Create target subdirectory if needed.
  - If source tag matches: skip.
- Generate character_Instance.md (Character Instance):
  - Create-only: if {workspace_root}/.claude/rules/character_Instance.md already exists, skip unconditionally.
  - If file does not exist: prepend YAML frontmatter (globs: empty, alwaysApply: true) to LI_PLUS_REPOSITORY/model/character_Instance.md contents.
    Write to {workspace_root}/.claude/rules/character_Instance.md.
  - No tag-based overwrite. User customizations are preserved across updates.
- Remove stale rules: for each file in {workspace_root}/.claude/rules/ (recursive) that no longer exists at the corresponding path in LI_PLUS_REPOSITORY/rules/ and is not character_Instance.md, delete it. Also remove empty subdirectories after deletion.

4c.3. Generate .claude/skills/ files (recursive directory mirror):
- If {workspace_root}/.claude/skills/ does not exist: create directory.
- For each `*/SKILL.md` in LI_PLUS_REPOSITORY/skills/ (recursive, including `<layer>/<name>/SKILL.md`):
  - Preserve the relative path: `skills/<layer>/<name>/SKILL.md` -> `.claude/skills/<layer>/<name>/SKILL.md`.
  - Ensure target subdirectories exist.
  - If target file does not exist or source tag differs: copy verbatim (source already has Claude Code skill frontmatter).
  - If source tag matches: skip.
- Remove stale skills: for each `<layer>/<name>/` directory in `.claude/skills/` that no longer exists in LI_PLUS_REPOSITORY/skills/, recursively delete it. Also remove empty layer subdirectories.

4c.4. Bootstrap hooks:
- Read adapter/claude/Li+hooks.md.
- If {workspace_root}/.claude/settings.json does not exist or does not contain "PostToolUse":
  create settings.json and hook scripts from the code blocks in Li+hooks.md.
  SessionStart uses four matchers (startup / resume / clear / compact) so Cold-start Synthesis
  material is emitted for every session entry point, not only compact.
- If settings.json exists and contains "PostToolUse":
  - Check the source tag in existing hook scripts (e.g. "# Source: Li+hooks.md (build-2026-03-30.14)").
  - If tag matches current target tag: skip (up to date).
  - If tag differs or is absent: regenerate hook scripts only (do not overwrite settings.json).
- on-session-start.sh is the Cold-start Synthesis material emitter. Its stdout is injected into
  the session-opening context (Claude Code SessionStart contract). The hook gathers material
  (literal cold-start content from rules/cold-start-synthesis.md, recent docs/a.- head, latest release
  tags, open in-progress issues, self-evaluation log head). Synthesis is performed by the AI
  through Character_Instance, not by the hook itself.
- Set executable permission on .sh files.

Note: bootstrap takes effect from the NEXT session. Current session continues with Li+config.md execution.

### Phase 4 codex: Codex Integration

Adapter generation and direct layer reads. Codex has no rules/skills mechanism,
so layers must be read explicitly.

4x.1. Bootstrap adapter:
- target = {workspace_root}/AGENTS.md, source = adapter/codex/Li+agent.md
- Replace {LI_PLUS_TAG} in all generated content with the resolved target tag from Phase 3.
- Sentinel-based auto vs legacy user decision:
  Auto skip / replace applies only when the "Li+ BEGIN" sentinel is detected.
  Sentinel absence (legacy file) requires user decision; silent overwrite of a legacy file is prohibited
  because it would destroy user-authored content without consent.
- Adapter section judgment:
  a. If target file does not exist: create it with the contents of the adapter source.
  b. If target file exists and contains "Li+ BEGIN" sentinel:
     - Extract the tag from the sentinel (e.g. "Li+ BEGIN (build-2026-03-30.14)" -> "build-2026-03-30.14").
     - If extracted tag matches current target tag: skip (up to date).
     - If tag differs or is absent: replace the section between "Li+ BEGIN" and "Li+ END" (inclusive)
       with the current adapter source contents. Preserve content outside this section.
  c. If target file exists but does not contain "Li+ BEGIN": ask user -- append Li+ section or skip?

4x.2. Read Li+ layers directly:
- Read all `rules/*.md` files in LI_PLUS_REPOSITORY (always-on).
- `skills/<name>/SKILL.md` files are read on demand per the trigger table in adapter/codex/Li+agent.md.

## Phase 5: Workspace Preparation

Dependencies: Phase 2 (gh CLI authenticated).

5.1. Prepare USER_REPOSITORY working clone (skip if `owner/repository-name`):
- If USER_REPOSITORY matches LI_PLUS_REPOSITORY: run `git checkout main` in the local clone.
- Otherwise: clone by repository name to workspace if the directory is not present. Skip if the directory already exists.

## Phase 6: Completion Report

Dependencies: all prior phases.

6.1. Report completion.

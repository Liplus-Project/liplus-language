# Li+ Bootstrap

Session startup procedure for Li+.
Execute at session start. Never output credentials to chat.
Read Li+config.md first to resolve all settings before executing this file.

1. Detect runtime environment:
- if environment variable CODEX_HOME or CODEX_THREAD_ID exists: runtime=codex
- elif environment variable CLAUDECODE exists: runtime=claude
- else: ask user once (Claude or Codex?) and proceed with answer.

2. Secure Li+config.md permissions:
- Linux/Mac only: `chmod 600 Li+config.md` (owner read/write only, since the file contains tokens).
- Skip if permissions are already 600 or stricter.
- Windows: skip (NTFS ACL under user profile directories is already restricted by default).

3. Resolve workspace language contract:
- These values apply to the current workspace only. They do not change LI_PLUS_REPOSITORY governance.
- LI_PLUS_BASE_LANGUAGE = default language for dialogue with the human in this workspace, including conversational replies such as issue/discussion/PR comments unless a different language is explicitly scoped.
- LI_PLUS_PROJECT_LANGUAGE = default language for durable structured artifacts in this workspace (issue/PR/commit body, saved requirements).
- If either value is unset:
  - Ask the user once at session start.
  - Recommend: base language = current user language, project language = same as base language.
  - If the user wants a different artifact language, accept it.
  - Write resolved values to Li+config.md. No manual editing required.

4. Install gh CLI:
- Install only if `~/.local/bin/gh` does not exist. No sudo. No PATH update.
- Always use full path `~/.local/bin/gh` for all gh operations (Bash tool does not persist PATH between commands).
- /tmp is forbidden (permission conflicts with other sessions).
- Steps: `mkdir -p ~/.local/bin` → curl tarball to `~/.local/bin/gh.tar.gz` → extract in place → place `~/.local/bin/gh` → delete tarball.

5. Load GH_TOKEN and authenticate.

6. Load Li+ layers from LI_PLUS_REPOSITORY:
Determine target version using LI_PLUS_CHANNEL:
- latest: use the Latest release tag.
- release: use the most recent tag including pre-releases.
Version check is mandatory on every startup before reading Li+ layers.
Silent continuation on a stale local clone is prohibited.
- Check LI_PLUS_MODE:
  - api: fetch model/Li+core.md for the target version via GitHub API from LI_PLUS_REPOSITORY.
    Conditionally fetch task/Li+issues.md (see step 4 condition below).
  - clone: execute in order:
  1. Target repo is the target version of LI_PLUS_REPOSITORY.
  2. Check workspace for repository directory (derived from LI_PLUS_REPOSITORY name):
     - not exists → clone target tag directly to workspace. Proceed to step 3.
     - exists → fetch --tags, then:
       a. Resolve and report both values: current checked-out tag and target tag from LI_PLUS_CHANNEL.
       b. If same → continue.
       c. If different → ask the user how to proceed before reading Li+ layers.
          Do not report bootstrap completion before this choice is resolved.
          Minimum choices:
          - update now to the target tag
          - stay on the current tag for this session
       d. Checkout the target tag only if the user agrees.
       e. If the user chooses to stay, continue on the current tag only after explicitly naming both tags.
  3. Read model/Li+core.md (core layer).
  4. Read task/Li+issues.md (task layer) — only if hooks are unavailable.
     When hooks inject constant-load sections per-turn, startup read is redundant.
  5. Keep operations/Li+github.md available for event-driven reads later.

7. Bootstrap host adapter:
- Determine target path and adapter source by runtime:
  - codex: target = {workspace_root}/AGENTS.md, source = adapter/codex/Li+agent.md
  - claude: target = {workspace_root}/.claude/CLAUDE.md, source = adapter/claude/Li+agent.md
- Replace {LI_PLUS_TAG} in all generated content with the resolved target tag from step 6.
- Adapter section judgment:
  a. If target file does not exist: create it with the contents of the adapter source.
  b. If target file exists and contains "Li+ BEGIN" sentinel:
     - Extract the tag from the sentinel (e.g. "Li+ BEGIN (build-2026-03-30.14)" → "build-2026-03-30.14").
     - If extracted tag matches current target tag: skip (up to date).
     - If tag differs or is absent: replace the section between "Li+ BEGIN" and "Li+ END" (inclusive)
       with the current adapter source contents. Preserve content outside this section.
  c. If target file exists but does not contain "Li+ BEGIN": ask user — append Li+ section or skip?
- If runtime=claude: bootstrap hooks from adapter/claude/Li+hooks.md.
  - Read adapter/claude/Li+hooks.md.
  - If {workspace_root}/.claude/settings.json does not exist or does not contain "PostToolUse":
    create settings.json and hook scripts from the code blocks in Li+hooks.md.
  - If settings.json exists and contains "PostToolUse":
    - Check the source tag in existing hook scripts (e.g. "# Source: Li+hooks.md (build-2026-03-30.14)").
    - If tag matches current target tag: skip (up to date).
    - If tag differs or is absent: regenerate hook scripts only (do not overwrite settings.json).
  - Set executable permission on .sh files.
- Note: bootstrap takes effect from the NEXT session. Current session continues with Li+config.md execution.

7b. Generate .claude/rules/ files (runtime=claude only):
- If {workspace_root}/.claude/rules/ does not exist: create directory.
- Generate Li+core.md:
  - Prepend YAML frontmatter (globs: empty, alwaysApply: true) to model/Li+core.md contents.
  - Write to {workspace_root}/.claude/rules/Li+core.md.
- Generate Li+github.md (operations layer):
  - Prepend YAML frontmatter (globs: empty, alwaysApply: true) to operations/Li+github.md contents.
  - Write to {workspace_root}/.claude/rules/Li+github.md.
- Generate character_Instance.md (Character Instance):
  - Create-only: if {workspace_root}/.claude/rules/character_Instance.md already exists, skip unconditionally.
  - If file does not exist: prepend YAML frontmatter (globs: empty, alwaysApply: true) to model/character_Instance.md contents.
    Write to {workspace_root}/.claude/rules/character_Instance.md.
  - No tag-based overwrite. User customizations are preserved across updates.

7c. Generate .claude/skills/li-plus-issues/SKILL.md (runtime=claude only):
- If {workspace_root}/.claude/skills/li-plus-issues/ does not exist: create directory.
- Prepend skill frontmatter (name, description with trigger conditions) to task/Li+issues.md contents.
  task/Li+issues.md is copied without the Issue Operations section (Issue Format, Issue Maturity, Sub-issue Rules are in operations/Li+github.md).
- Write to {workspace_root}/.claude/skills/li-plus-issues/SKILL.md.
- Frontmatter template defined in adapter/claude/Li+hooks.md skills/ generation template section.

8. Prepare USER_REPOSITORY working clone (skip if `owner/repository-name`):
- If USER_REPOSITORY matches LI_PLUS_REPOSITORY: run `git checkout main` in the local clone.
- Otherwise: clone by repository name to workspace.

9. Report completion.

# Li+ Config

Bootstrap / distribution adapter for Li+.
Human edits this file. AI executes it at session start.
Semantic truth remains in Li+core.md / Li+github.md / Li+operations.md.

## ユーザー設定（ここを編集してください）

GH_TOKEN=github_pat_XXXX
USER_REPOSITORY=owner/repository-name

### 取得モード: api（軽量）または clone（ローカルで動作）
LI_PLUS_MODE=clone

### チャンネル: latest（安定版）または release（プレリリース含む最新版）
LI_PLUS_CHANNEL=release

### 実行モード: trigger（人間主導）または auto（AI自律）
### 未設定の場合、セッション開始時にAIが聞いて自動設定します
# LI_PLUS_EXECUTION_MODE=trigger

### 基本言語: このworkspaceで人間と対話する時の既定言語
### 未設定の場合、セッション開始時にAIが聞いて自動設定します
### 例: ja / en / fr
# LI_PLUS_BASE_LANGUAGE=ja

### プロジェクト言語: このworkspaceの成果物（issue/PR/commit body等）の既定言語
### 未設定の場合、セッション開始時にAIが聞いて自動設定します
### 例: ja / en / fr
# LI_PLUS_PROJECT_LANGUAGE=ja

### 任意: MCP が無い時に使う local webhook state dir
### 絶対パスまたは workspace_root 相対で指定
### clone モードの bundled helper がこの設定を読む
# LI_PLUS_WEBHOOK_STATE_DIR=github-webhook-mcp

---

## Session Startup Tasks (do not edit)

Execute at session start. Never output credentials to chat.

1. Detect runtime environment:
- if environment variable CODEX_HOME or CODEX_THREAD_ID exists: runtime=codex
- elif environment variable CLAUDECODE exists: runtime=claude
- else: ask user once (Claude or Codex?) and proceed with answer.

2. Resolve workspace language contract:
- These values apply to the current workspace only. They do not change liplus-language repository governance.
- LI_PLUS_BASE_LANGUAGE = default language for dialogue with the human in this workspace, including conversational replies such as issue/discussion/PR comments unless a different language is explicitly scoped.
- LI_PLUS_PROJECT_LANGUAGE = default language for durable structured artifacts in this workspace (issue/PR/commit body, saved requirements).
- If either value is unset:
  - Ask the user once at session start.
  - Recommend: base language = current user language, project language = same as base language.
  - If the user wants a different artifact language, accept it.
  - Write resolved values to Li+config.md. No manual editing required.

3. Install gh CLI:
- Install only if `~/.local/bin/gh` does not exist. No sudo. No PATH update.
- Always use full path `~/.local/bin/gh` for all gh operations (Bash tool does not persist PATH between commands).
- /tmp is forbidden (permission conflicts with other sessions).
- Steps: `mkdir -p ~/.local/bin` → curl tarball to `~/.local/bin/gh.tar.gz` → extract in place → place `~/.local/bin/gh` → delete tarball.

4. Load GH_TOKEN and authenticate.

5. Load Li+ layers from Li+ repository:
Determine target version using LI_PLUS_CHANNEL:
- latest: use the Latest release tag.
- release: use the most recent tag including pre-releases.
- Check LI_PLUS_MODE:
  - api: fetch Li+core.md, Li+github.md, Li+agent.md for the target version via GitHub API.
  - clone: execute in order:
  1. Target repo is the target version of Liplus-Project/liplus-language.
  2. Check workspace for liplus-language directory:
     - not exists → clone target tag directly to workspace. Proceed to step 3.
     - exists → fetch --tags, then:
       a. Determine the current checked-out tag.
       b. Determine the target tag (per LI_PLUS_CHANNEL).
       c. If current tag == target tag → proceed to step 3 (no confirmation needed).
       d. If current tag != target tag → ask the user:
          "Li+ <target tag> が利用可能です（現在: <current tag>）。アップデートしますか？"
          - Yes → checkout target tag, proceed to step 3.
          - No → stay on current tag, proceed to step 3.
  3. Read Li+core.md (core layer).
  4. Read Li+github.md (issue layer).
  5. Read Li+agent.md (adapter layer).
  6. Keep Li+operations.md available for event-driven reads later.

6. Bootstrap host adapter from Li+agent.md:
- Determine target path by runtime:
  - codex: {workspace_root}/AGENTS.md (same directory as this Li+config.md)
  - claude: {workspace_root}/.claude/CLAUDE.md (same directory as this Li+config.md)
- If target file does not exist: create it with the contents of Li+agent.md.
- If target file exists and contains "Li+ BEGIN" sentinel: skip (Li+ already applied).
- If target file exists but does not contain "Character_Instance": ask user — append Li+ section or skip?
- If runtime=claude: bootstrap hooks from Li+claude.md.
  - Read Li+claude.md (same location as other Li+ files).
  - Skip if {workspace_root}/.claude/settings.json already exists and contains "PostToolUse".
  - Otherwise: create settings.json and hook scripts from the code blocks in Li+claude.md.
  - Set executable permission on .sh files.
- Note: bootstrap takes effect from the NEXT session. Current session continues with Li+config.md execution.

7. Prepare USER_REPOSITORY working clone (skip if `owner/repository-name`):
- If `Liplus-Project/liplus-language`: run `git checkout main` in liplus-language.
- Otherwise: clone by repository name to workspace.

8. Report completion.

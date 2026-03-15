# Li+ Config

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

2. Install gh CLI:
- Install only if `~/.local/bin/gh` does not exist. No sudo. No PATH update.
- Always use full path `~/.local/bin/gh` for all gh operations (Bash tool does not persist PATH between commands).
- /tmp is forbidden (permission conflicts with other sessions).
- Steps: `mkdir -p ~/.local/bin` → curl tarball to `~/.local/bin/gh.tar.gz` → extract in place → place `~/.local/bin/gh` → delete tarball.

3. Load GH_TOKEN and authenticate.

4. Load Li+ files from Li+ repository:
Determine target version using LI_PLUS_CHANNEL:
- latest: use the Latest release tag.
- release: use the most recent tag including pre-releases.
- Check LI_PLUS_MODE:
  - api: fetch Li+core.md, Li+github.md, Li+agent.md for the target version via GitHub API.
  - clone: execute in order:
  1. Target repo is the target version of Liplus-Project/liplus-language.
  2. Check workspace for liplus-language directory:
     - exists → fetch --tags → checkout target tag.
     - not exists → clone directly to workspace.
  3. Read Li+core.md.
  4. Read Li+github.md.
  5. Read Li+agent.md.

5. Bootstrap instruction file from Li+agent.md:
- Determine target path by runtime:
  - codex: {workspace_root}/AGENTS.md (same directory as this Li+config.md)
  - claude: {workspace_root}/.claude/CLAUDE.md (same directory as this Li+config.md)
- If target file does not exist: create it with the contents of Li+agent.md.
- If target file exists and contains "Li+ BEGIN" sentinel: skip (Li+ already applied).
- If target file exists but does not contain "Character_Instance": ask user — append Li+ section or skip?
- If runtime=claude: bootstrap hooks for trigger-based re-read.
  - Skip if {workspace_root}/.claude/settings.json already exists and contains "PostToolUse".
  - Otherwise: create the following files and set executable permission on .sh files.

  {workspace_root}/.claude/settings.json:
  ```json
  {
    "hooks": {
      "Stop": [
        {
          "hooks": [
            {
              "type": "command",
              "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop.sh"
            }
          ]
        }
      ],
      "PostToolUse": [
        {
          "matcher": "Bash",
          "hooks": [
            {
              "type": "command",
              "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use.sh"
            }
          ]
        }
      ]
    }
  }
  ```

  {workspace_root}/.claude/hooks/stop.sh:
  ```bash
  #!/bin/bash
  PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
  CORE_MD="$PROJECT_ROOT/liplus-language/Li+core.md"

  [ -f "$CORE_MD" ] || exit 0

  sed -n '/^Always Character Layer$/,/^Behavioral Style$/p' "$CORE_MD" | head -n -1
  ```

  {workspace_root}/.claude/hooks/post-tool-use.sh:
  ```bash
  #!/bin/bash
  INPUT=$(cat)
  TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
  COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

  [[ "$TOOL_NAME" == "Bash" ]] || exit 0

  PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
  LIPLUS_DIR="$PROJECT_ROOT/liplus-language"
  CORE_MD="$LIPLUS_DIR/Li+core.md"
  GITHUB_MD="$LIPLUS_DIR/Li+github.md"

  # on_pr: gh pr create → full Li+core.md + Li+github.md re-read + sub-issue auto-append
  if echo "$COMMAND" | grep -q 'gh pr create'; then
    if [ -f "$CORE_MD" ] || [ -f "$GITHUB_MD" ]; then
      echo ""
      echo "━━━ on_pr: Persona + GitHub rules re-apply ━━━"
      [ -f "$CORE_MD" ]   && cat "$CORE_MD"
      [ -f "$GITHUB_MD" ] && cat "$GITHUB_MD"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi

    OUTPUT=$(printf '%s' "$INPUT" | jq -r '.tool_response.output // empty' 2>/dev/null)
    PR_NUMBER=$(echo "$OUTPUT" | grep -oE '/pull/[0-9]+' | grep -oE '[0-9]+' | head -1)
    [ -z "$PR_NUMBER" ] && exit 0

    REPO=$(git -C "$LIPLUS_DIR" remote get-url origin 2>/dev/null \
      | grep -oE '[^/@:]+/[^/]+$' | sed 's/\.git$//' 2>/dev/null || echo "")
    [ -z "$REPO" ] && exit 0

    PR_BODY=$(gh api "repos/$REPO/pulls/$PR_NUMBER" --jq '.body' 2>/dev/null || echo "")
    [ -z "$PR_BODY" ] && exit 0

    PARENT_ISSUE=$(echo "$PR_BODY" | grep -oE '#[0-9]+' | head -1 | tr -d '#')
    [ -z "$PARENT_ISSUE" ] && exit 0

    SUB_ISSUE_NUMBERS=$(gh api "repos/$REPO/issues/$PARENT_ISSUE/sub_issues" \
      --jq '.[].number' 2>/dev/null || echo "")
    [ -z "$SUB_ISSUE_NUMBERS" ] && exit 0

    MISSING=()
    while IFS= read -r issue_num; do
      [ -z "$issue_num" ] && continue
      if ! echo "$PR_BODY" | grep -qE "#${issue_num}([^0-9]|$)"; then
        MISSING+=("$issue_num")
      fi
    done <<< "$SUB_ISSUE_NUMBERS"

    [ ${#MISSING[@]} -eq 0 ] && exit 0

    ADDITIONS=""
    for num in "${MISSING[@]}"; do
      ADDITIONS="${ADDITIONS}
  Refs #${num}"
    done

    NEW_BODY="${PR_BODY}${ADDITIONS}"
    gh api "repos/$REPO/pulls/$PR_NUMBER" \
      --method PATCH -f body="$NEW_BODY" > /dev/null 2>&1

    echo ""
    echo "━━━ PR #${PR_NUMBER}: sub-issue refs auto-appended ━━━"
    for num in "${MISSING[@]}"; do
      echo "  + Refs #${num}"
    done
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
  fi

  # on_issue: gh issue → Li+github.md Issue_Flow section re-read
  if echo "$COMMAND" | grep -qE 'gh (issue|api .*/issues)'; then
    if [ -f "$GITHUB_MD" ]; then
      echo ""
      echo "━━━ on_issue: Issue_Flow re-read ━━━"
      sed -n '/\[Issue Flow\]/,/\[Branch And Label Flow\]/p' "$GITHUB_MD" | head -n -1
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
    exit 0
  fi

  # on_commit: git commit → Li+github.md Commit_Rules section re-read
  if echo "$COMMAND" | grep -q 'git commit'; then
    if [ -f "$GITHUB_MD" ]; then
      echo ""
      echo "━━━ on_commit: Commit_Rules re-read ━━━"
      sed -n '/\[Commit Rules\]/,/\[PR And CI Flow\]/p' "$GITHUB_MD" | head -n -1
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
    exit 0
  fi
  ```

- Note: bootstrap takes effect from the NEXT session. Current session continues with Li+config.md execution.

6. Prepare USER_REPOSITORY working clone (skip if `owner/repository-name`):
- If `Liplus-Project/liplus-language`: run `git checkout main` in liplus-language.
- Otherwise: clone by repository name to workspace.

7. Report completion.

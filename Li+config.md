# Li+ Config

## ユーザー設定（ここを編集してください）

GH_TOKEN=github_pat_XXXX

### あなたのプロジェクトリポジトリ
USER_REPOSITORY=owner/repository-name
### 実行モード: trigger（人間主導）または auto（AI自律）
### 未設定の場合、セッション開始時にAIが聞いて自動設定します
# USER_REPOSITORY_EXECUTION_MODE=trigger

### Li+ 本体（変更不要）
LI_PLUS_REPOSITORY=Liplus-Project/liplus-language

### 取得モード: api（軽量）または clone（ローカルで動作）
LI_PLUS_MODE=clone

### チャンネル: latest（安定版）/ release（プレリリース含む最新リリース）/ tag（GitHub Release 未作成の tag も含む最新 git tag）
### 包含関係: tag ⊇ release ⊇ latest
LI_PLUS_CHANNEL=release

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

## Bootstrap
Read and execute LI_PLUS_REPOSITORY/Li+bootstrap.md

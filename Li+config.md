# Li+ Config

## ユーザー設定（ここを編集してください）

GH_TOKEN=github_pat_XXXX
USER_REPOSITORY=owner/repository-name
LI_PLUS_REPOSITORY=Liplus-Project/liplus-language

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

### Bootstrapを実行
LI_PLUS_REPOSITORY/Li+bootstrap.md

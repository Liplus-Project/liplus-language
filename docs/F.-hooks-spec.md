# Claude Code Hook 仕様書

## 概要

Li+claude.md にClaude Code用のhook定義を格納する。Li+config.md Step 6 が runtime=claude を検出した際、Li+claude.md のコードブロックからワークスペースへhookファイルを初回生成（bootstrap）する。

hookはClaude Codeランタイムが強制発火するため、AIの記憶やコンテキスト圧縮に依存しない。
Li+ のレイヤーで見ると、このページは **Claude adapter layer** の仕様である。

## フックスクリプト

### on-user-prompt.sh

**トリガー:** `UserPromptSubmit` — ユーザーがメッセージを送信するたび（Claude の処理開始前）

**目的:** `.claude/CLAUDE.md` で定義された Character_Instance を AI に再通知する。加えて、未処理の webhook 通知があれば件数を表示する。

**動作:**

1. Character_Instance 再通知:
   - `CLAUDE_PROJECT_DIR`（フォールバック: `.`）を起点として `.claude/CLAUDE.md` を探索
   - `Character_Instance` セクションを抽出して出力
   - `.claude/CLAUDE.md` が見つからない場合: スキップ（graceful）

2. Webhook 通知チェック:
   - `liplus-language/scripts/check_webhook_notifications.py` が存在する場合のみ実行
   - `Li+config.md` から `LI_PLUS_WEBHOOK_STATE_DIR` を読み取り、ヘルパーに渡す
   - ヘルパーが pending_count > 0 を返した場合、件数を出力
   - ヘルパーが見つからない場合やpending=0の場合: 何もせず終了

**依存:** `.claude/CLAUDE.md`（Character_Instance用）、`liplus-language/scripts/check_webhook_notifications.py`（webhook用、任意）、`python3`

---

### post-tool-use.sh

**トリガー:** `PostToolUse` (matcher: `Bash`) — Bash ツール呼び出し後に実行

**目的:** Li+github.md と Li+operations.md のトリガーベース再読込をランタイム強制で実現する。

**動作:**

| コマンドパターン | 再読込対象 | 追加動作 |
|---|---|---|
| `gh issue` / `gh api .*/issues` | Li+github.md の Issue_Flow セクション | — |
| `gh issue develop` / `git switch -c` / `git checkout -b` | Li+operations.md の Branch And Label Flow セクション | — |
| `git commit` | Li+operations.md の Commit Rules セクション | — |
| `gh pr create` | Li+operations.md 全文 | PR body への子 issue 参照の自動補完 |
| `gh pr merge` | Li+operations.md の Merge And Cleanup セクション | — |
| `gh release create` | Li+operations.md の Human Confirmation Required セクション | — |

起動時の基本レイヤー（Li+core.md + Li+github.md）は別経路で再適用される。`PostToolUse` は event-driven な operations layer を補強するための実装である。

**子 issue 自動補完の詳細（on_pr 時）:**
1. `gh pr create` 出力 URL から PR 番号を抽出
2. `git remote get-url origin` からリポジトリを特定
3. GitHub API 経由で PR body を取得
4. PR body 最初の `#NNN` 参照から親 issue 番号を抽出
5. GitHub API 経由で親の子 issue を取得
6. PR body に記載のない子 issue の `Refs #NNN` を自動追記

**依存:** `jq`、`gh` CLI（認証済み）、`git`、`liplus-language/Li+github.md`、`liplus-language/Li+operations.md`

## 環境変数

| 変数 | 使用スクリプト | 用途 |
|---|---|---|
| `CLAUDE_PROJECT_DIR` | on-user-prompt.sh、post-tool-use.sh | Li+ ソースファイルの探索起点 |
| `GH_TOKEN` | post-tool-use.sh | GitHub API 認証 |

## ファイル構成

**定義元（リポジトリ）:**
```
liplus-language/
└── Li+claude.md          # hook定義（コードブロックとして格納）
```

**生成先（ワークスペース、bootstrap後）:**
```
{workspace_root}/
└── .claude/
    ├── settings.json      # hook登録（UserPromptSubmit + PostToolUse）
    └── hooks/
        ├── on-user-prompt.sh  # UserPromptSubmit
        └── post-tool-use.sh   # PostToolUse
```

## 関連ドキュメント

- `Li+claude.md` — hook定義の実体
- `Li+core.md` — Always Character Layer 定義
- `Li+github.md` — issue layer
- `Li+operations.md` — operations layer
- `docs/D.-Li+config.md` — Li+ 設定リファレンス（Step 6 に bootstrap 手順）

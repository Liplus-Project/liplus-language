# Claude Code Hook 仕様書

## 概要

Li+claude.md にClaude Code用のhook定義を格納する。Li+config.md Step 6 が runtime=claude を検出した際、Li+claude.md のコードブロックからワークスペースへhookファイルを初回生成（bootstrap）する。

hookはClaude Codeランタイムが強制発火するため、AIの記憶やコンテキスト圧縮に依存しない。

## フックスクリプト

### stop.sh

**トリガー:** `Stop` — Claude Code がレスポンスを終了するとき

**目的:** Li+core.md で定義された Always Character Layer のルールを AI に再通知する。加えて、未処理の webhook 通知があれば件数を表示する。

**動作:**

1. Always Character Layer 再通知:
   - `CLAUDE_PROJECT_DIR`（フォールバック: `.`）を起点として `liplus-language/Li+core.md` を探索
   - `Always Character Layer` セクションを抽出して出力
   - `Li+core.md` が見つからない場合: スキップ（graceful）

2. Webhook 通知チェック:
   - `liplus-language/scripts/check_webhook_notifications.py` が存在する場合のみ実行
   - `Li+config.md` から `LI_PLUS_WEBHOOK_STATE_DIR` を読み取り、ヘルパーに渡す
   - ヘルパーが pending_count > 0 を返した場合、件数を出力
   - ヘルパーが見つからない場合やpending=0の場合: 何もせず終了

**依存:** `liplus-language/Li+core.md`（Character Layer用）、`liplus-language/scripts/check_webhook_notifications.py`（webhook用、任意）、`python3`

---

### post-tool-use.sh

**トリガー:** `PostToolUse` (matcher: `Bash`) — Bash ツール呼び出し後に実行

**目的:** Li+github.md のトリガーベース再読込をランタイム強制で実現する。

**動作:**

| コマンドパターン | 再読込対象 | 追加動作 |
|---|---|---|
| `gh pr create` | Li+core.md + Li+github.md 全文 | PR body への子 issue 参照の自動補完 |
| `gh issue` / `gh api .*/issues` | Li+github.md の Issue_Flow セクション | — |
| `git commit` | Li+github.md の Commit_Rules セクション | — |

**子 issue 自動補完の詳細（on_pr 時）:**
1. `gh pr create` 出力 URL から PR 番号を抽出
2. `git remote get-url origin` からリポジトリを特定
3. GitHub API 経由で PR body を取得
4. PR body 最初の `#NNN` 参照から親 issue 番号を抽出
5. GitHub API 経由で親の子 issue を取得
6. PR body に記載のない子 issue の `Refs #NNN` を自動追記

**依存:** `jq`、`gh` CLI（認証済み）、`git`、`liplus-language/Li+core.md`、`liplus-language/Li+github.md`

## 環境変数

| 変数 | 使用スクリプト | 用途 |
|---|---|---|
| `CLAUDE_PROJECT_DIR` | stop.sh、post-tool-use.sh | Li+ ソースファイルの探索起点 |
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
    ├── settings.json      # hook登録（Stop + PostToolUse）
    └── hooks/
        ├── stop.sh        # Stop
        └── post-tool-use.sh   # PostToolUse
```

## 関連ドキュメント

- `Li+claude.md` — hook定義の実体
- `Li+core.md` — Always Character Layer 定義
- `Li+github.md` — GitHub 運用ルール
- `docs/D.-Li+config.md` — Li+ 設定リファレンス（Step 6 に bootstrap 手順）

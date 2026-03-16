# 実行オペレーション（Li+Operations）

このページは、Li+ プロジェクトにおける**イベント駆動の実行オペレーション**を定義する。

Li+operations.md はイベント発生時にオンデマンドで読み込む。毎セッション必須ではない。
ブランチ作成、コミット、PR、マージ、リリース、マイルストーン割り当て、ラベル判断、Discussions 参照時に参照すること。

Issue ルール（ラベル定義・Issue 記述・sub-issue）は [C. Operational GitHub](C.-Operational_GitHub) を参照。

------------------------------------------------------------------------

## Issue / Commit / Pull Request の形式

### Title（必須）

-   **英語**
-   **ASCII のみ**
-   **1行**
-   識別層として扱う（意味説明を含めない）

### Body（必須）

-   **日本語**
-   意味層として扱う（背景・判断・意図を記述する）
-   変更内容の要約・判断理由・**Issue 番号**を含めること

### Issue 番号の記述形式

```
Refs #159
```

-   `Refs #xxx` 形式を使う（形式が明確であれば他の表現も可）
-   PR本文に Issue 番号が含まれていると、**マージ時に GitHub が Issue を自動クローズする**

### 言語レイヤー分離原則

-   Title は識別レイヤー（ASCII 英語）
-   Body は意味レイヤー（日本語）
-   日本語タイトル・英語のみの Body は禁止

------------------------------------------------------------------------

## Pull Request 追加ルール

PR 本文は **issue ごとのブロック形式** で記述する。

```
Refs #465
GitHub運用ルールの表現を整理。
意味の変化なし、読み違い防止が目的。

Refs sub #467
ホスト依存の指示ファイル参照を汎用表現へ修正。
Codex / Claude Code のどちらでも読み違えないようにした。
```

-   親 issue → `Refs #xxx`、クローズ済み子 issue → `Refs sub #xxx`
-   各ブロックに **2〜3行の要約** を書く（詳細は Issue を参照）
-   deferred・open のまま残す子 issue は含めない

------------------------------------------------------------------------

## ブランチ運用ルール

### ブランチ作成のタイミング（タイミング三段階）

着手意思は対話の空気から判断する。チェックリストで確認しない。

| タイミング | ラベル | ブランチ |
|----------|-------|--------|
| NOW（今やる） | `in-progress` | 作成する |
| SOON（近いうち） | `backlog` | 作成しない |
| SOMEDAY（いつか） | `deferred` | 作成しない |

-   `trigger` mode でも Issue の作成・本文更新とブランチ準備は待たない
-   人間トリガーの対象は実装開始と PR レビューである

### ブランチ命名規則

Claude Code のセッションブランチをそのまま使用する。

```
claude/{task-description-SessionID}
# 例: claude/add-character-dialogue-ZKjl4
```

作成コマンド（Issue へのリンクを必ず張る）：

```
gh issue develop {issue_number} -R {owner}/{repo} --name {session-branch} --base main
```

> **順序制約**: `gh issue develop` は **GitHub への初回 push より前に実行する**。
> すでに **GitHub 上にブランチが存在する場合**、後から実行してもリンクは張れない。

### `gh issue develop` がローカルエラーで失敗した場合

`gh issue develop` はローカルの git 操作に失敗しても、GitHub API 側ではブランチリンクが成功している場合がある。
**リトライ前に必ずリンク状態を確認すること。**

```
gh api graphql -f query='{ repository(owner:"{owner}",name:"{repo}") { issue(number:{number}) { linkedBranches { nodes { ref { name } } } } } }'
```

- `linkedBranches` にブランチ名が返ってきた場合 → **そのブランチを使用する**（新規作成禁止）
- 返ってこなかった場合 → 再試行または人間に委ねる

### 作業開始時の Assignee ルール

```
gh api repos/{owner}/{repo}/issues/{issue_number}/assignees \
  --method POST \
  -f 'assignees[]=liplus-lin-lay'
```

### sub-issue のブランチルール

-   **sub-issue にはブランチを作らない**
-   ブランチを持つのは「実際に PR を出す作業単位（親 issue）」だけ
-   セッションブランチは **親 issue** にリンクする
-   複数の子 issue の作業を同じセッションブランチで進めてよい（commit で issue 番号を複数参照）

### 同時タスクの場合は親子 issue を使う

複数タスクを同一セッションで並行進行する場合、issue を個別に作成すると **ブランチリンクは最初の 1 件にしか張れない**（GitHub 制約）。

正しい構造：

```
親 issue  ← gh issue develop でブランチリンク
├── 子 issue A  （責務 A の作業）
├── 子 issue B  （責務 B の作業）
└── 子 issue C  （責務 C の作業）
```

-   親 issue の body にはタスク全体の目的と子 issue 一覧を簡潔に書く
-   詳細な完了条件は各子 issue に書く
-   commit body には対応する子 issue 番号を `Refs #xxx` で参照する

### 親 issue のクローズ条件

-   子 issue（deferred 扱いのものを除く）がすべてクローズされたら親をクローズする
-   子 issue が残っている状態で親をクローズしない

------------------------------------------------------------------------

## GitHub への書き込みルール

### プライマリ：git push（推奨）

```
git push origin {session-branch}
```

### フォールバック：GitHub API（git 非使用環境）

git が使えない環境や、他の AI エージェントとの互換性が必要な場合に使用する。

> **注意（複数ファイル時）**: tree 作成後、コミット前にファイル数を検証すること。
> `base_tree` のファイル数より減少していた場合はコミット中止。

------------------------------------------------------------------------

## マージフロー

**CI PASS かつ構造レビューで問題がなければ、実機テストより前にマージしてよい。**

マージは **GitHub の auto-merge 機能** が処理する。

**PR 作成直後に auto-merge を有効化すること**（これをしないと自動マージが発火しない）：

```
gh pr merge {pr_number} -R {owner}/{repo} --auto --squash
```

- squash merge を使用（リポジトリ設定で構成済み）
- ブランチ削除は "Automatically delete head branches" 設定により自動処理される
- PR 本文に `Refs #xxx` が含まれていると、マージ時に GitHub が Issue を自動クローズする

------------------------------------------------------------------------

## CI ループフロー

**PR 作成直後に自動起動する。人間の指示は不要。**
**CI ループが完了するまで PR タスクは完了しない。**

1.  **PR 作成・更新時**
    -   タイトルは ASCII 英語、本文は日本語 + Issue 番号必須
    -   作成と同時に CI ループを開始する
2.  **マージ可能状態の確認**
    -   最新コミット SHA を取得：
        ```
        gh pr view {pr} -R {owner}/{repo} --json headRefOid --jq '.headRefOid'
        ```
    -   マージ可能状態を確認：
        ```
        gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
        ```
    -   `CONFLICTING` の場合：
        -   自動 rebase を試みる：`git fetch origin main && git rebase origin/main`
        -   rebase 成功 → `git push --force-with-lease` → CI ループを step 1 から再開
        -   rebase 失敗 → `git rebase --abort` → issue コメントで人間にエスカレーション
    -   `BLOCKED` / `UNKNOWN` の場合：GitHub が計算中の可能性があるため、待機して再確認
3.  **チェックランの完了待機**
    -   **`mcp__github-webhook-mcp` が利用可能な場合：**
        -   `get_pending_status` を 60 秒ごとにポーリング
        -   `check_run` pending あり → `list_pending_events` → SHA 照合 → `get_event` で結論取得 → `mark_processed`
        -   全 check-run の結論が揃うまで繰り返す
    -   **利用できない場合：**
        -   全て `completed` になるまで繰り返し待機：
            ```
            gh api repos/{owner}/{repo}/commits/{sha}/check-runs \
              --jq '.check_runs[] | {name,status,conclusion}'
            ```
4.  **結論判定**
    -   `conclusion=failure` がある場合 → CI FAIL
    -   全て `conclusion` が `success` / `skipped` / `neutral` → CI PASS
5.  **CI FAIL 時の自動修正ループ（Loop_Safety タスク閾値=3回）**
    -   同一の修正アプローチを3回繰り返したら中止・アプローチ切り替え
    -   収束しない場合は自動修正を停止し、Issue にコメントとして外部化して人間に委ねる
6.  **レビュー承認確認**
    -   レビューリクエストは CODEOWNERS 設定により自動送信される。AIが手動で送信する必要はない。
    -   **`mcp__github-webhook-mcp` が利用可能な場合：**
        -   `get_pending_status` を 60 秒ごとにポーリング
        -   `pull_request_review` pending あり → `list_pending_events` → `get_event` で該当 PR のレビュー状態確認 → `mark_processed`
    -   **利用できない場合：**
        -   人間がレビューしたと伝えてきた時点で一度だけチェック：
            ```
            gh pr view {pr} -R {owner}/{repo} --json reviewDecision --jq '.reviewDecision'
            ```
    -   `APPROVED` → GitHub auto-merge が処理する（マージ操作不要）
    -   `CHANGES_REQUESTED` → レビューコメントを読んで修正し、CIループを再起動

------------------------------------------------------------------------

## 人間確認が必要な操作

以下の操作は **必ず人間に確認してから実行する**：

-   リリース作成（バージョン種別とターゲットタグ）—— **実行前に CD チェックが必要（下記参照）**
-   ブランチ削除（リンクされた issue がクローズされる可能性がある場合）
-   force push

### リリース前 CD チェック

リリース作成前に CD（スナップショット CI）の完了を確認する。

-   **`mcp__github-webhook-mcp` が利用可能な場合：**
    -   `get_pending_status` を 60 秒ごとにポーリング
    -   `workflow_run` pending あり → `list_pending_events` → `get_event` で結論確認 → `mark_processed`
-   **利用できない場合：**
    -   `gh api repos/{owner}/{repo}/actions/runs` で CD ワークフローの完了を確認
-   CD PASS → 人間に確認してリリース作成へ
-   CD FAIL → 人間にエスカレート（リリース作成しない）

### バージョン種別ルール

| バージョン | 適用条件 |
|----------|--------|
| patch | バグ修正・設定・ルール変更 |
| minor | 新機能・動作変更 |
| major | 破壊的変更・仕様非互換 |

**バージョン種別の判断は人間が行い、AIは実行のみを担う。**

### バージョン番号のベースルール

バージョン番号は **プレリリースを含む直近のリリース** を基準に決定する。

- `gh release list --limit 1` で取得した最新リリース（プレリリース含む）をベースにする
- Latest安定版のみを基準にしてはならない
- 例：Latest=v0.15.9、プレリリース=v0.16.0 の状態でパッチリリースを作る場合 → `v0.16.1`

### リリースタグ・タイトルルール

タグ形式とリリースタイトルは **プロジェクト固有の規約に従う**。

| プロジェクト種別 | タグ形式 | タイトル形式 |
|----------------|---------|------------|
| デフォルト（Li+ language） | `build-YYYY-MM-DD.N`（CD作成タグ） | `Li+ {version}` |
| npm パッケージ | `v{semver}`（npm version 作成タグ） | `v{semver}` |

-   プロジェクトに CD ワークフローがある場合：CD 作成タグを使い、新規タグを作成しない
-   プロジェクトが npm version を使う場合：npm version コマンドがタグを作成する
-   リリース前に project の docs/ や CI/CD 設定で規約を確認すること
-   コマンド例（Li+）：`gh release create build-2026-02-25.14 --title "Li+ v0.13.1" --prerelease --generate-notes`
-   コマンド例（npm）：`gh release create v0.2.1 --title "v0.2.1" --prerelease --generate-notes`

### AIが作成するリリースは必ずプレリリース

-   `gh release create` はデフォルトで `--latest=true` になるため、**必ず `--prerelease` を付ける**
-   latest への昇格は実機テスト後に**人間が判断する**
-   AIはプレリリース作成のみを行い、latest 設定は行わない

### リリース body ルール

-   **GitHub generated release notes を使う**
-   `gh release create` では **`--generate-notes` を付ける**
-   `--notes ""` のような空 body 指定は使わない

### 停止ルール

「待って」「止めて」「まって」と言われたら即座に停止する。

------------------------------------------------------------------------

## 実行モード（Execution_Mode）

`LI_PLUS_EXECUTION_MODE` によってAIの自律度を切り替える。設定は `Li+config.md` に記載。

| モード | 着手タイミング | PRレビュー |
|--------|-------------|-----------|
| `trigger`（デフォルト） | 人間が判断 | 人間がレビュー |
| `auto` | AIが判断 | AIがレビュー |

**両モード共通のルール：**
- issue作成・クローズ・修正はアサイニー（AI）の責任
- 必要な情報が不足している場合は人間に確認する
- リリース作成は常に人間の確認が必要

------------------------------------------------------------------------

## ドキュメント同期・要求仕様責務（Docs_And_Requirement_Ownership）

### ドキュメント同期

`docs/` を正本とする。Wiki は反映先であり、正本にしてはならない。

実装変更を含むPRは、対応する `docs/` の更新を同一PR内に含めなければならない。
「後でdocsを直す」という分割は禁止。

**理由：** AIはコンテキスト圧縮で記憶を失う。ドキュメントが唯一の真実の源になるため、実装との乖離は誤った判断を招く。

### 要求仕様書ファースト

配布向けプロジェクトでは、最低限の `docs/` として**要求仕様書**を持たなければならない。

- 新規・小規模プロジェクトでは、まず **1ファイルの要求仕様書** を作ればよい
- 規模が大きい場合は、要求仕様書を複数文書へ分割してよい
- 要求仕様書は issue 群から採用された要求・制約・完了条件を固定する正本であり、実装後の追従物ではない

**開始条件：** 実装を始める前に、対応する要求仕様書を先に作成または更新しなければならない。

挙動変更・バグ修正・仕様変更では、まず要求仕様書の該当箇所を変更する。
コードとテストは、その仕様差分を実装・検証するために更新する。

**理由：** 先に要求仕様書を変えることで、コードは仕様の実装になり、テストは仕様の検証になる。リリース時にソースコード・仕様書・テストを同じバージョンで束ねられる。

### 非自明な判断の置き場所

Li+ の挙動や運用ルールに効く判断は、standalone ADR だけに閉じず、**番号付き要求仕様**と**対応する運用文書**へ固定すること。

- 要求そのもの: `docs/0.-Requirements.md`
- GitHub の Issue ルール: `docs/C.-Operational_GitHub.md`
- 実行オペレーション: `docs/G.-Operations.md`

補助メモや実験ログを残してもよいが、それを正本にしてはならない。

### 要求仕様の分割方針

- 要求仕様は必要になるまで `docs/0.-Requirements.md` に集約してよい
- `1` 以降の番号ページは、分割した方が可読性と保守性が上がる時だけ増やす
- 番号を増やすこと自体を目的にしない

### PRタイトルの影響範囲明示

PRタイトルには変更の影響範囲も含める。

```
# 悪い例
fix(config): negative duration handling

# 良い例
fix(config): treat negative durations as below-minimum rather than error
```

------------------------------------------------------------------------

## GitHub 通知操作（Notifications API）

GitHub の通知操作を API で行う際のエンドポイント一覧。

| 操作 | メソッド | エンドポイント | レスポンス |
|------|----------|---------------|-----------|
| 既読にする | PATCH | `/notifications/threads/{id}` | 205 |
| 全件既読 | PUT | `/notifications` + `{"read":true}` | 205 |
| Done に移す | DELETE | `/notifications/threads/{id}` | 204 |
| Inbox 確認 | GET | `/notifications?all=false` | 200 |

- `PATCH` = 既読にするだけ（Inbox に Read として残る）
- `DELETE` = Done（Inbox から消える）= UI の「Done」と同等
- 必要スコープ: `notifications`（classic PAT）

------------------------------------------------------------------------

## 前景Webhook通知取り込み（Foreground_Webhook_Notification_Intake）

前景スレッドで「新しいコメントが来たかもしれない」と広くGitHubを探しに行くのではなく、届いている差分だけを軽く扱うための補助フロー。

### 目的

- `mcp__github-webhook-mcp` が無い環境でも、前景スレッドが軽量通知だけを扱えるようにする
- shared instruction に機械固有の絶対パスを埋め込まない
- webhook通知の受信口と前景スレッドの応答主体を分離し、重い別AI起動を避ける

### 使い分け

- **第一優先:** `mcp__github-webhook-mcp`
- **第二優先:** ローカル webhook ストア + bundled helper
- **どちらも無い:** 静かにスキップ

### ローカル fallback ルール

- 前提:
    - `LI_PLUS_MODE=clone`
    - ワークスペース内に `liplus-language/` clone があり、bundled helper を実行できること
- helper path:
    - `{workspace_root}/liplus-language/scripts/check_webhook_notifications.py`
- state dir 解決順:
    1. `LI_PLUS_WEBHOOK_STATE_DIR`（`Li+config.md`。絶対パスまたは `workspace_root` 相対）
    2. `{workspace_root}/github-webhook-mcp`
    3. `{workspace_root}/../github-webhook-mcp`
- state dir も helper も見つからない場合:
    - エラー化せず黙ってスキップ
- local helper の動作:
    - pending イベントの軽量サマリだけ返す
    - 前景へ通知として出したイベントはその場で consume する
    - `events.json` だけでなく、対応する生成物も削除する

### 前景スレッドでの扱い

- 各ターンの先頭で軽量確認できるホストだけで使う
- 確認処理そのものは内部 housekeeping として無言で行う
- 確認中であることや empty/no-op 結果は会話へ出さない
- pending が 0 件なら何も言わない
- pending がある時だけ短く通知する
- 詳細が必要になるまでは full payload を開かない
- このフローから別AIプロセスを起動しない

------------------------------------------------------------------------

## 禁止事項

-   Issue に紐づかない Commit / PR
-   関係のない Issue を流用してブランチを作ること
-   日本語タイトルの Commit / PR
-   Issue 番号の記載がない Commit / PR
-   Pull Request の要約が無いもの
-   言語レイヤー分離に違反するもの
-   着手前にブランチを作成すること
-   作業開始時に Assignee を設定しないこと
-   人間確認なしにリリースを作成すること

------------------------------------------------------------------------

## マイルストーン

### 定義

マイルストーンは**リリース単位**である。同じリリースで出荷する issue をグループ化する。

### 運用ルール

- すべての issue に**作成時点で**マイルストーンを付与すること
- 該当するマイルストーンがない場合は、人間にどのマイルストーンに入れるか確認する。または新規マイルストーンの作成を提案する
- マイルストーン名はバージョン番号（例: `v1.2.0`）
- マイルストーンの説明には一行テーマ＋スコープの箇条書きを記載する

### ライフサイクル

- 作成：人間が新しいリリーススコープを決定したとき
- クローズ：リリースが公開されたとき
- リリース前にマイルストーンをクローズしないこと

### sub-issue の継承

- sub-issue は親のマイルストーンを継承する
- 親にマイルストーンがあり、子にない場合は同じマイルストーンを付与すること

------------------------------------------------------------------------

## ラベル

### 方針

ラベルは AI の読みやすさとフィルタリングのためにある。

- すべての issue に作成時点で**タイプラベルを1つ以上**付与すること
- すべての issue に作成時点で**成熟度ラベルを1つ**付与すること
- ライフサイクルラベルは状態変化時に適用すること

### 有効なラベル

#### タイプ（必須、issue ごとに1つ）

| ラベル | 意味 |
|-------|------|
| `bug` | 動いていない、壊れている |
| `enhancement` | 新機能・改善要望 |
| `spec` | Li+の挙動に影響する仕様・ポリシー・定義 |
| `docs` | ドキュメント変更（挙動への影響なし） |

#### 成熟度（必須、issue ごとに1つ）

| ラベル | 意味 |
|-------|------|
| `memo` | メモとして開始した状態。見出しは必要なものだけでよい |
| `forming` | 本文を再構築しながら要求を整えている状態 |
| `ready` | 本文が実装開始できる形まで収束している状態。ただし更新は継続可能 |

#### ライフサイクル（状態変化時に適用）

| ラベル | 意味 |
|-------|------|
| `in-progress` | 着手中、実装または検証が進行中 |
| `backlog` | 受け入れ済み、着手時期未定 |
| `deferred` | 今回対応しない。あとで見直す |

### 廃止されたラベル

| ラベル | 廃止理由 |
|-------|---------|
| `done` | issue の closed 状態と冗長 |
| `tips` | `docs` ラベル + issue body で代替 |

### ラベル定義の同期

Li+github.md の Label Definitions セクションは本文書を参照している。
ラベルの追加・変更・廃止を行った場合は Li+github.md も合わせて更新すること。

------------------------------------------------------------------------

## Discussions

### 目的

Discussions は**外部ユーザーの入口**である。

### 常駐 bot

Discussions に bot が常駐している。

| 機能 | 可否 |
|------|------|
| issue 作成 | できる |
| issue 読込 | できる |
| コミット・コード変更 | できない |

### フロー

外部ユーザーが Discussions に投稿 → bot が issue を作成 → AI が issue から実装する。

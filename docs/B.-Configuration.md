## 概要

**Li+config.md** は、Li+をセッションで動作させるための設定ファイルです。
このページは **設定リファレンス** であり、Quickstart は [C. Installation](C.-Installation) を参照します。

ワークスペース直下に配置し、ユーザーが直接編集します。セッション開始時にAIがこのファイルを読み込み、環境検出・認証・バージョン取得・設定ファイル生成を自動的に実行します。

---

## 設定項目

### GH_TOKEN

GitHub Personal Access Token。Li+リポジトリへのアクセスと、作業リポジトリの操作に使用します。

### USER_REPOSITORY

作業対象のGitHubリポジトリを `owner/repository-name` 形式で指定します。

- LI_PLUS_REPOSITORY と同じ値を指定した場合：ローカルcloneで `git checkout main` を実行
- 別リポジトリを指定した場合：そのリポジトリをワークスペースへ clone

### LI_PLUS_REPOSITORY

Li+本体のGitHubリポジトリを `owner/repository-name` 形式で指定します。デフォルト値は `Liplus-Project/liplus-language` です。

Li+ファイル（Li+core.md、Li+github.md、Li+bootstrap.md 等）の取得先として使用されます。フォークや組織内プライベートコピーを使う場合はここを変更します。

### LI_PLUS_MODE

Li+リポジトリからLi+ファイルを取得する方法を指定します。

| 値 | 動作 |
|----|------|
| `api` | GitHub APIで直接Li+ファイルを取得（軽量。trigger-based re-readなどの継続機能は保証しない） |
| `clone` | リポジトリをローカルにclone/checkoutして取得（継続利用推奨） |

### LI_PLUS_CHANNEL

取得するLi+のバージョンチャンネルを指定します。

| 値 | 動作 |
|----|------|
| `latest` | Latestリリースのタグを使用（安定版） |
| `release` | Pre-release含む最新タグを使用（最新版） |

### LI_PLUS_EXECUTION_MODE

AIの自律度を切り替えます。未設定の場合、セッション開始時にAIが対話で設定します（手入力不要）。

| 値 | 動作 |
|----|------|
| `trigger` | 人間主導。人間がトリガーを引いたらAIがPRレビューまで一直線に実行する（issue作成・クローズはAI）|
| `auto` | AI自律。issue選択・着手・PRレビューをAIが行う |

リリースはどちらのモードでも人間の確認が必要です。

### LI_PLUS_BASE_LANGUAGE

配布先workspaceで、人間との対話に使う**基本言語**です。未設定の場合、セッション開始時にAIが対話で設定します（手入力不要）。

| 値 | 動作 |
|----|------|
| 未設定 | セッション開始時にAIが現在の対話を基準に聞き、Li+config.mdへ書き戻す |
| `ja` / `en` / `fr` など | そのworkspaceで人間へ返す既定言語として使う。issue/discussion/PRコメントのような会話返信もこちらが既定 |

注意:

- ここで決めるのは配布先workspaceの対話言語です
- liplus-language リポジトリ内部の日本語運用ルールは変更しません

### LI_PLUS_PROJECT_LANGUAGE

配布先workspaceで、成果物（issue / PR / commit body、保存する要求仕様など）に使う**プロジェクト言語**です。未設定の場合、セッション開始時にAIが対話で設定します（手入力不要）。

| 値 | 動作 |
|----|------|
| 未設定 | セッション開始時にAIが聞き、Li+config.mdへ書き戻す |
| `ja` / `en` / `fr` など | そのworkspaceの durable artifact の既定言語として使う |

注意:

- 人間が現在の返答や特定の成果物に別言語を明示した場合、その指示が優先されます
- 指示のスコープが終わった後は、この値が既定値として再び使われます

### LI_PLUS_WEBHOOK_STATE_DIR

`mcp__github-webhook-mcp` が利用できない時に、前景スレッドが lightweight webhook 通知を読むための**任意設定**です。

| 値 | 動作 |
|----|------|
| 未設定 | ローカル fallback を強制しない。bundled helper は既定候補を見つけた時だけ使う |
| 絶対パス | そのディレクトリを webhook state dir として使う |
| ワークスペース相対パス | `workspace_root` から解決して webhook state dir として使う |

想定ディレクトリは `github-webhook-mcp` の状態保存先で、`events.json`、`trigger-events/`、`codex-runs/` を含みます。

注意:

- local fallback helper は `LI_PLUS_MODE=clone` で `liplus-language/` clone が手元にある場合にだけ使えます
- shared instruction へ機械固有の絶対パスを直接書いてはいけません。必要なパスはこの設定値へ寄せます

---

## セッション起動フロー

セッション開始時にAIが自動実行するステップです。実行ロジックは **Li+bootstrap.md** に定義されており、Li+config.md からは分離されています。

### ステップ1: 環境検出

ランタイム環境を自動判定します。

| 環境変数 | 判定結果 |
|---------|---------|
| `CODEX_HOME` or `CODEX_THREAD_ID` が存在 | runtime=codex |
| `CLAUDECODE` が存在 | runtime=claude |
| どちらもなし | ユーザーに1回確認 |

### ステップ2: Li+config.md のパーミッション保護

Li+config.md にはトークンが含まれるため、ファイルパーミッションを制限します。

- Linux/Mac: `chmod 600 Li+config.md`（ownerのみ read/write）
- 既に 600 以下の場合はスキップ
- Windows: スキップ（ユーザープロファイル配下では NTFS ACL が既に制限済み）

### ステップ3: workspace言語契約の解決

`LI_PLUS_BASE_LANGUAGE` と `LI_PLUS_PROJECT_LANGUAGE` を解決します。

- これらは**配布先workspace専用**の設定であり、liplus-language リポジトリ内部の日本語運用とは分離されます
- `LI_PLUS_BASE_LANGUAGE` は人間との対話の既定言語です。issue/discussion/PRコメントのような会話返信もこちらが既定です
- `LI_PLUS_PROJECT_LANGUAGE` は issue / PR / commit body や保存する要求仕様など durable artifact の既定言語です
- どちらか未設定の場合、AIがセッション開始時に対話で確認し、Li+config.mdへ書き戻します
- 推奨初期値は `基本言語 = 現在の対話言語`、`プロジェクト言語 = 基本言語と同じ` です
- 人間が「bodyは英語で」のように成果物言語を明示した場合、その指示を優先できます

### ステップ4: gh CLIインストール

`~/.local/bin/gh` が存在しない場合のみインストールします。

- sudo不要、PATH変更不要
- `/tmp` は使用禁止（他セッションとの権限衝突のため）
- インストール先: `~/.local/bin/gh`（以降の全操作でフルパスを使用）

### ステップ5: 認証

`GH_TOKEN` を読み込んでgh CLIで認証します。認証情報はチャットに出力しません。

### ステップ6: Li+ファイル取得と適用

`LI_PLUS_CHANNEL` で対象バージョンを決定し、`LI_PLUS_MODE` に従ってLi+ファイルを取得・適用します。

取得対象: Li+core.md、Li+github.md、Li+agent.md

**cloneモードの場合：**

1. 対象リポジトリは LI_PLUS_REPOSITORY の対象バージョン
2. ワークスペース内に `liplus-language` ディレクトリが存在する場合 → `fetch --tags` → 対象タグへ checkout
3. 存在しない場合 → ワークスペースへ直接 clone
4. Li+core.md、Li+github.md、Li+agent.md を読み込む

### ステップ7: 設定ファイルの自動生成（Bootstrap）

Li+agent.md テンプレートから、ランタイムに応じた設定ファイルを生成します。

| ランタイム | 生成先 |
|-----------|--------|
| codex | `{workspace_root}/AGENTS.md`（Li+config.md と同じディレクトリ） |
| claude | `{workspace_root}/.claude/CLAUDE.md`（Li+config.md と同じディレクトリ直下） |

判定ロジック：

- ファイルが存在しない → Li+agent.md の内容で新規作成
- ファイルが存在し `Li+ BEGIN` sentinel を含む → スキップ（Li+適用済み）
- ファイルが存在するが sentinel なし → ユーザーに確認（Li+セクションを追記 or スキップ）

**runtime=claude の場合: hook bootstrap**

Li+claude.md からClaude Code用のhookファイルを生成します。

- `{workspace_root}/.claude/settings.json` が既に存在し `UserPromptSubmit` を含む → スキップ
- 存在しない場合 → Li+claude.md 内のコードブロックから settings.json、hooks/on-user-prompt.sh、hooks/post-tool-use.sh を生成
- .sh ファイルには実行権限を付与

hookにより、issue操作では Li+github.md の Issue Flow、branch / commit / PR / merge / release では Li+operations.md の該当セクションまたは全文が自動再読込されます（AIの記憶に依存しないランタイム強制）。

Bootstrap は次回セッションから有効になります。現セッションは Li+config.md の実行で継続します。

### ステップ8: USER_REPOSITORY の作業クローン準備

`USER_REPOSITORY` が `owner/repository-name`（デフォルト値）の場合はスキップします。

### ステップ9: 完了報告

起動完了を報告します。

---

## 注意事項

- `GH_TOKEN` はチャットに出力されません
- セッションを跨いでgh CLIのPATHは保持されないため、常にフルパス（`~/.local/bin/gh`）で実行されます
- `LI_PLUS_MODE=clone` の場合、初回セッションはcloneのため時間がかかります。2回目以降はfetch & checkoutのみです
- `LI_PLUS_WEBHOOK_STATE_DIR` を使う場合、`LI_PLUS_MODE=clone` を推奨します。`api` モードでは bundled helper の利用を前提にできません

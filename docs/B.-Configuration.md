## 概要

**Li+config.md** は、Li+のユーザー設定ファイルです。ワークスペース直下に配置し、ユーザーが直接編集します。

セッション起動ロジックは **Li+bootstrap.md** に分離されており、本ファイルは設定値の保持のみを担います。起動フローの詳細は [C. Bootstrap](C.-Bootstrap) を参照します。

このページは **設定リファレンス** です。Quickstart は [D. Installation](D.-Installation) を参照します。

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

Li+ファイル（`rules/**/*.md`、`skills/**/SKILL.md`、Li+bootstrap.md 等）の取得先として使用されます。フォークや組織内プライベートコピーを使う場合はここを変更します。

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
| `latest` | Latestリリースのタグを使用（安定版のみ） |
| `release` | Pre-release含む最新リリースのタグを使用 |
| `tag` | GitHub Release 未作成の tag も含む最新 git tag を使用（`git ls-remote --tags --sort=-creatordate` で解決、clone mode 第一対応） |

包含関係: `tag` ⊇ `release` ⊇ `latest`。

`tag` は CD や手動で tag を切っただけで GitHub Release を未作成の段階の挙動を workspace で検証したい場合に使います。api mode 向け拡張は現時点では対象外です。

`LI_PLUS_MODE=clone` の場合、AI は起動時に現在 checkout 中のタグと、この設定から解決した対象タグを比較します。
差分があれば、対象タグへ更新するか現行タグのまま続行するかを人間に確認してから進みます。

### USER_REPOSITORY_EXECUTION_MODE

AIの自律度を切り替えます。未設定の場合、セッション開始時にAIが対話で設定します（手入力不要）。

| 値 | 動作 |
|----|------|
| `trigger` | 人間主導。人間がトリガーを引いたらAIがPRレビューまで一直線に実行する（issue作成・クローズはAI）|
| `semi_auto` | 半自動。着手タイミングはAIが決める。AIが毎PRでセルフレビューを行い、patchはAIが直接マージ、minor / major は人間確認のうえAIがマージする |
| `auto` | AI自律。issue選択・着手・PRレビューをAIが行う |

リリースはどのモードでも人間の確認が必要です。

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

### LI_PLUS_WEBHOOK_DELIVERY

webhook 通知がセッションへ届く方法を指定します。`mcp__github-webhook-mcp` を MCP channel として常時接続している環境では `channel` に設定することで、毎ターンのポーリングリマインダーをスキップできます。

| 値 | 動作 |
|----|------|
| 未設定 / `poll` | 毎ターン開始時に on-user-prompt hook がポーリングリマインダーを出力する（既定、後方互換） |
| `channel` | MCP channel がリアルタイムにイベントを配信するため、hook のポーリングリマインダーをスキップする |

注意:

- `channel` に設定しても webhook 通知の前景判定ルールは変わりません。transport が変わるだけです
- この設定は on-user-prompt hook が実行時に Li+config.md から読み取ります。bootstrap での追加アクションは不要です

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

セッション起動フローの詳細は [C. Bootstrap](C.-Bootstrap) を参照します。

---

## 注意事項

- `GH_TOKEN` はチャットに出力されません
- セッションを跨いでgh CLIのPATHは保持されないため、常にフルパス（`~/.local/bin/gh`）で実行されます
- `LI_PLUS_MODE=clone` の場合、初回セッションはcloneのため時間がかかります。2回目以降はfetch & checkoutのみです
- `LI_PLUS_MODE=clone` の場合、既存 clone が対象タグとずれていれば、AI は起動時に人間へ更新可否を確認します
- `LI_PLUS_WEBHOOK_STATE_DIR` を使う場合、`LI_PLUS_MODE=clone` を推奨します。`api` モードでは bundled helper の利用を前提にできません

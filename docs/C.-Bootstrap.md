# ブートストラップ仕様書

本文書は Li+ のセッション起動フロー（Li+bootstrap.md）の仕様を定義する。
Li+config.md の設定値を前提とし、セッション開始時に AI が自動実行するステップを記述する。

---

## 概要

セッション起動フローは **Li+bootstrap.md** に定義されている。Li+config.md はユーザー設定のみを保持し、起動ロジックは分離されている。

AI は Li+config.md を読み込んだ後、Li+bootstrap.md のステップに従って環境検出・認証・バージョン取得・設定ファイル生成を実行する。

---

## ステップ1: 環境検出

ランタイム環境を自動判定する。

| 環境変数 | 判定結果 |
|---------|---------|
| `CODEX_HOME` or `CODEX_THREAD_ID` が存在 | runtime=codex |
| `CLAUDECODE` が存在 | runtime=claude |
| どちらもなし | ユーザーに1回確認 |

---

## ステップ2: Li+config.md のパーミッション保護

Li+config.md にはトークンが含まれるため、ファイルパーミッションを制限する。

- Linux/Mac: `chmod 600 Li+config.md`（ownerのみ read/write）
- 既に 600 以下の場合はスキップ
- Windows: スキップ（ユーザープロファイル配下では NTFS ACL が既に制限済み）

---

## ステップ3: workspace言語契約の解決

`LI_PLUS_BASE_LANGUAGE` と `LI_PLUS_PROJECT_LANGUAGE` を解決する。

- これらは**配布先workspace専用**の設定であり、liplus-language リポジトリ内部の日本語運用とは分離する
- `LI_PLUS_BASE_LANGUAGE` は人間との対話の既定言語。issue/discussion/PRコメントのような会話返信もこちらが既定
- `LI_PLUS_PROJECT_LANGUAGE` は issue / PR / commit body や保存する要求仕様書など durable artifact の既定言語
- どちらか未設定の場合、AIがセッション開始時に対話で確認し、Li+config.mdへ書き戻す
- 推奨初期値は `基本言語 = 現在の対話言語`、`プロジェクト言語 = 基本言語と同じ`
- 人間が「bodyは英語で」のように成果物言語を明示した場合、その指示を優先できる

---

## ステップ4: gh CLIインストール

`~/.local/bin/gh` が存在しない場合のみインストールする。

- sudo不要、PATH変更不要
- `/tmp` は使用禁止（他セッションとの権限衝突のため）
- インストール先: `~/.local/bin/gh`（以降の全操作でフルパスを使用）

---

## ステップ5: 認証

`GH_TOKEN` を読み込んでgh CLIで認証する。認証情報はチャットに出力しない。認証後は keyring にトークンが保存されるため、以降の `gh` コマンドに `GH_TOKEN` の明示的な export は不要。

---

## ステップ6: Li+ファイル取得と適用

`LI_PLUS_CHANNEL` で対象バージョンを決定し、`LI_PLUS_MODE` に従ってLi+ファイルを取得・適用する。

必須取得: `rules/**/*.md`（L1–L4 の常時ロード分、subdir `model/` `evolution/` `task/` `operations/` 含む）
条件付き: `skills/**/SKILL.md`（hookが無い環境では Codex adapter のトリガー表に従って手動読み込み）

起動時は、Li+ファイルを読む前に **毎回必ず対象バージョン確認** を行う。
ローカル clone が古いままでも黙って継続してはいけない。

**cloneモードの場合：**

1. 対象リポジトリは LI_PLUS_REPOSITORY の対象バージョン
2. ワークスペース内に `liplus-language` ディレクトリが存在しない場合 → 対象タグを直接 clone
3. 存在する場合：
   - `fetch --tags` を実行
   - 現在 checkout 中のタグと、`LI_PLUS_CHANNEL` から解決した対象タグを両方確認
   - 一致する場合のみ、そのまま Li+ ファイルを読む
   - 不一致の場合、**人間にどうするか確認する**
   - この選択が解決するまで bootstrap 完了扱いにしない
4. 人間確認の最小選択肢：
   - 対象タグへ更新してから続行
   - 今セッションは現在タグのまま続行
5. 人間が更新に同意した場合のみ対象タグへ checkout
6. 人間が現在タグのまま続行を選んだ場合は、現在タグと対象タグを明示してから続行
7. `rules/**/*.md` を読み込む（L1–L4 の常時ロード分、subdir 含む常に必須）
8. `skills/**/SKILL.md` はトリガー時に読み込む — hookが無い環境では Codex adapter のトリガー表に従って手動読み込み。hookが常時適用セクションをターンごとに注入する場合、起動時の skill 一括読み込みは不要

---

## ステップ7: 設定ファイルの自動生成（Bootstrap）

adapter 配下のテンプレートから、ランタイムに応じた設定ファイルを生成する。source はターゲット側の生成先と同名に揃えてある（target-native 命名）。

| ランタイム | ソース | 生成先 |
|-----------|--------|--------|
| codex | `adapter/codex/AGENTS.md` | `{workspace_root}/AGENTS.md`（Li+config.md と同じディレクトリ） |
| claude | `adapter/claude/CLAUDE.md` | `{workspace_root}/.claude/CLAUDE.md`（Li+config.md と同じディレクトリ直下） |

生成物には `{LI_PLUS_TAG}` プレースホルダがあり、bootstrap 時に解決済みターゲットタグへ置換する。

判定ロジック：

自動スキップ・自動置換は `Li+ BEGIN` sentinel 検出時にのみ適用する。sentinel 不在（legacy file）はユーザー判断を必須とする。legacy file を暗黙に上書きすると、ユーザー自身が書いた内容を同意なく破壊することになるため禁止する。

- ファイルが存在しない → ソーステンプレートの内容で新規作成
- ファイルが存在し `Li+ BEGIN` sentinel を含む：
  - sentinel 内のタグと現在のターゲットタグを比較
  - 一致 → スキップ（最新）
  - 不一致またはタグなし → Li+ BEGIN 〜 Li+ END 間を差し替え（セクション外は保護）
- ファイルが存在するが sentinel なし → ユーザーに確認（Li+セクションを追記 or スキップ）

**runtime=claude の場合: rules/skills/hooks bootstrap**

rules/skills ファイルはリポジトリの `rules/` / `skills/` から直接生成し、hook ファイルは adapter/claude/hooks-settings.md（settings.json）と adapter/claude/hooks/*.sh（スクリプト本体）から生成する。

**ステップ 7b: rules/ ファイル生成（再帰ディレクトリミラー）**

- `.claude/rules/` ディレクトリが存在しなければ作成
- リポジトリの `rules/**/*.md`（subdir `model/` `evolution/` `task/` `operations/` 含む）を1ファイルずつ、相対パスを保持したまま `.claude/rules/<relpath>` へミラー。frontmatter に `globs:`（空）と `alwaysApply: true` を含めるよう保証する。`layer` フィールドは保持する。L5 Notifications / L6 Adapter に対応する subdir が `rules/` 配下に存在しないのは設計意図であり欠落ではない（L5 は realtime trigger 実装確定までの予約席、L6 はテンプレート + hook 駆動でそもそも rules/ に載らない）。設計意図の詳細は [判断記録 d.-layer-reorg-rationale](d.-layer-reorg-rationale) を参照する
- character_Instance.md は初回のみ生成し、既存ファイルは上書きしない（ユーザーカスタマイズ可能）
- ソースタグと現在のターゲットタグを比較し、一致する場合はスキップ（最新）
- `.claude/rules/` 内でリポジトリ側に存在しないファイル（character_Instance.md を除く）は削除。空の subdir も削除

**ステップ 7c: skills/ ファイル生成（再帰ディレクトリミラー）**

- `.claude/skills/` ディレクトリが存在しなければ作成
- リポジトリの `skills/<layer>/<name>/SKILL.md` を1ファイルずつ、相対パスを保持したまま `.claude/skills/<layer>/<name>/SKILL.md` へ verbatim コピー（ソースが既に Claude Code skill frontmatter を含む）
- ソースタグと現在のターゲットタグを比較し、一致する場合はスキップ（最新）
- `.claude/skills/` 内でリポジトリ側に存在しない `<layer>/<name>/` ディレクトリは削除。空の layer subdir も削除

**hook bootstrap**

- settings.json が存在せず `UserPromptSubmit` を含まない → 全ファイル新規生成
- settings.json が存在し `UserPromptSubmit` を含む：
  - hook スクリプトのソースタグと現在のターゲットタグを比較
  - 一致 → スキップ（最新）
  - 不一致またはタグなし → hook スクリプトのみ再生成（settings.json は再生成しない）
- .sh ファイルには実行権限を付与
- on-session-start.sh は Cold-start Synthesis 用の素材を出力（`rules/evolution/cold-start-synthesis.md` のリテラル + 直近 docs/a.- 先頭 + 最新リリースタグ + open in-progress issue + self-evaluation 先頭）
- on-user-prompt.sh は Character 再通知と Webhook 通知のみ（常時注入は rules/skills に移行）
- post-tool-use.sh は `gh pr create` 後の sub-issue refs 自動追記のみを担う（旧 focus pointer 注入は不要、rules/* が常時ロードされ skills/* が description で auto-invocation するため）

rules/ により L1–L4 の常時ロード分が常時コンテキストに存在し、skills/ により残りの責務が必要時に自動読込される。hook は補助的に残る。

Bootstrap は次回セッションから有効。現セッションは Li+config.md の実行で継続する。

---

## ステップ8: USER_REPOSITORY の作業クローン準備

`USER_REPOSITORY` が `owner/repository-name`（デフォルト値）の場合はスキップする。

それ以外の場合、ワークスペースに対象リポジトリのディレクトリが存在しなければ clone する。既に存在する場合はスキップ（再 clone しない）。

---

## ステップ9: 完了報告

起動完了を報告する。

---

## 関連ページ

- [B. Configuration](B.-Configuration) — 設定リファレンス
- [D. Installation](D.-Installation) — Quickstartセットアップ手順
- [6. Adapter](6.-Adapter) — アダプターレイヤー仕様書

---

## 進化

再構築・削除・最適化はすべて許容する。構造の一貫性のみ維持する。

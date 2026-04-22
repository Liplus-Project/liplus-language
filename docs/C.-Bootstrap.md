# ブートストラップ仕様書

本文書は Li+ のセッション起動フロー（`Li+bootstrap.md`）の仕様を定義する。
Li+config.md の設定値を前提とし、セッション開始時に AI が自動実行する Phase を記述する。

---

## 概要

セッション起動フローは **`Li+bootstrap.md`** に定義されている。Li+config.md はユーザー設定のみを保持し、起動ロジックは分離されている。

AI は Li+config.md を読み込んだ後、`Li+bootstrap.md` の Phase 1 から Phase 6 を順に実行する。各 Phase は直前までの Phase を依存前提として宣言する。認証情報をチャットに出力してはいけない。

---

## Phase 1: 環境検出

参照: `Li+bootstrap.md` Phase 1。依存なし。

**1.1. ランタイム環境の自動判定**

| 環境変数 | 判定結果 |
|---------|---------|
| `CODEX_HOME` または `CODEX_THREAD_ID` が存在 | runtime=codex |
| `CLAUDECODE` が存在 | runtime=claude |
| どちらもなし | ユーザーに1回確認し、回答で続行 |

**1.2. Li+config.md のパーミッション保護**

Li+config.md にはトークンが含まれるため、ファイルパーミッションを制限する。

- Linux/Mac: `chmod 600 Li+config.md`（owner のみ read/write）
- 既に 600 以下の場合はスキップ
- Windows: スキップ（ユーザープロファイル配下では NTFS ACL が既に制限済み）

---

## Phase 2: 認証と設定

参照: `Li+bootstrap.md` Phase 2。依存: Phase 1（ランタイム検出済み）。

**2.1. gh CLI のインストール**

`~/.local/bin/gh` が存在しない場合のみインストールする。

- sudo 不要、PATH 変更不要
- 以降の gh 操作は常にフルパス `~/.local/bin/gh` を使用（Bash ツールは PATH を永続化しないため）
- `/tmp` は使用禁止（他セッションとの権限衝突のため）
- 手順: `mkdir -p ~/.local/bin` → `~/.local/bin/gh.tar.gz` に tarball を curl → その場で展開 → `~/.local/bin/gh` を配置 → tarball を削除

**2.2. GH_TOKEN の読み込みと認証**

`GH_TOKEN` を読み込んで gh CLI で認証する。認証情報はチャットに出力しない。認証後は keyring にトークンが保存されるため、以降の `gh` コマンドに `GH_TOKEN` の明示的な export は不要。

**2.3. workspace 言語契約の解決**

`LI_PLUS_BASE_LANGUAGE` と `LI_PLUS_PROJECT_LANGUAGE` を解決する。

- これらは **配布先 workspace 専用** の設定であり、LI_PLUS_REPOSITORY 内部のガバナンスとは分離する
- `LI_PLUS_BASE_LANGUAGE` は人間との対話の既定言語。issue/discussion/PR コメントのような会話返信もこちらが既定
- `LI_PLUS_PROJECT_LANGUAGE` は issue / PR / commit body や保存する要求仕様書など durable artifact の既定言語
- どちらか未設定の場合、AI がセッション開始時に1回対話で確認し、Li+config.md へ書き戻す
- 推奨初期値は「基本言語 = 現在の対話言語」「プロジェクト言語 = 基本言語と同じ」
- bootstrap の ask と Li+config.md への書き戻しは、セッション開始時の config 未解決パスにのみ適用する。config が解決済みなら、セッション途中の再 ask と config 再書き込みは本 Phase の対象外とする
- runtime precedence（人間の明示指示 > スレッド合意 > config > 再 ask）はアダプターの Workspace_Language_Contract が担い、セッション全体を通して本 Phase を再起動せずに働く

**2.4. Webhook 配信モードの解決（任意）**

- `LI_PLUS_WEBHOOK_DELIVERY`（`channel` または `poll`）はアダプターが runtime で参照する
- 未設定時の既定は `poll`。bootstrap 側の追加処理は不要

---

## Phase 3: Li+ ソース解決

参照: `Li+bootstrap.md` Phase 3。依存: Phase 2（gh CLI 認証済み）。

**3.1. `LI_PLUS_CHANNEL` による対象バージョンの決定**

- `latest`: Latest release タグ（stable release のみ）
- `release`: pre-release を含む最新リリースタグ（GitHub Release API）
- `tag`: 作成日順で最新の git タグ（GitHub Release が未作成のタグも含む）。clone モードでは `git ls-remote --tags --sort=-creatordate {repo_url} | head -1` を使用
- 包含関係は tag ⊇ release ⊇ latest。tag は GitHub Release 作成前の pre-release タグ検証を意図する。api モードの tag 拡張は現時点ではスコープ外
- バージョン確認は起動のたびに Phase 4 へ進む前に必ず実施する。ローカル clone が古いままでも黙って継続してはいけない

**3.2. `LI_PLUS_MODE` による Li+ ソース取得**

**api モード:**
- `rules/` 配下の全 `*.md` を対象バージョンで GitHub API から LI_PLUS_REPOSITORY より取得
- `skills/` 配下の全 `<name>/SKILL.md` を対象バージョンで GitHub API から取得
- 検出した runtime に応じて `adapter/claude/` または `adapter/codex/` を取得

**clone モード:**

1. 対象リポジトリは LI_PLUS_REPOSITORY の対象バージョン
2. ワークスペース内に LI_PLUS_REPOSITORY 由来のディレクトリが存在するか確認
   - 存在しない → 対象タグを直接 clone し、手順 3 へ
   - 存在する → `fetch --tags` を実行し:
     a. 現在 checkout 中のタグと、`LI_PLUS_CHANNEL` から解決した対象タグを両方確認して報告
     b. 一致する場合はそのまま続行
     c. 不一致の場合、Phase 4 へ進む前に人間にどうするか確認する。この選択が解決するまで bootstrap 完了扱いにしない。最小選択肢は「対象タグへ更新してから続行」「今セッションは現在タグのまま続行」
     d. 人間が更新に同意した場合のみ対象タグへ checkout
     e. 現在タグのまま続行を選んだ場合は、現在タグと対象タグを明示してから続行
3. 解決済みタグでソースファイルが参照可能な状態になる。読み込みは Phase 4 が担う

---

## Phase 4: ホスト統合

参照: `Li+bootstrap.md` Phase 4。依存: Phase 3（ソース解決済み、対象タグ確定済み）。

ランタイム固有の統合処理。検出した runtime で分岐する。adapter / rules / skills / hooks を生成する。rules/skills の生成はレイヤーの読み込みを兼ねる（生成された `.claude/rules/` `.claude/skills/` をホストが毎ターン読むため明示 read は不要）。

生成物には `{LI_PLUS_TAG}` プレースホルダがあり、bootstrap 時に Phase 3 で解決済みターゲットタグへ置換する。

**共通判定ロジック**

自動スキップ・自動置換は `Li+ BEGIN` sentinel 検出時にのみ適用する。sentinel 不在（legacy file）はユーザー判断を必須とする。legacy file を暗黙に上書きすると、ユーザー自身が書いた内容を同意なく破壊することになるため禁止する。

### Phase 4 claude: Claude Code 統合

**4c.1. アダプターの bootstrap**

- target = `{workspace_root}/.claude/CLAUDE.md`, source = `adapter/claude/CLAUDE.md`
- ファイルが存在しない → ソースの内容で新規作成
- ファイルが存在し `Li+ BEGIN` sentinel を含む:
  - sentinel 内のタグ（例 `Li+ BEGIN (build-2026-03-30.14)` → `build-2026-03-30.14`）を抽出
  - 現在のターゲットタグと一致 → スキップ（最新）
  - 不一致またはタグなし → `Li+ BEGIN` 〜 `Li+ END` 間（両端含む）をソース内容で差し替え、セクション外は保護
- ファイルが存在するが sentinel なし → ユーザーに確認（Li+ セクションを追記 or スキップ）

**4c.2. `.claude/rules/` ファイル生成（再帰ディレクトリミラー）**

- `{workspace_root}/.claude/rules/` が存在しなければ作成
- LI_PLUS_REPOSITORY の `rules/**/*.md` を再帰走査し（`model/` `evolution/` `task/` `operations/` subdir を含む）、`rules/character_Instance.md` を除いた各ファイルについて:
  - LI_PLUS_REPOSITORY/rules/ からの相対パスを保持してターゲットへ配置する（例: `rules/model/absolute.md` → `.claude/rules/model/absolute.md`）
  - ターゲットが存在しない、またはソースタグが現在のターゲットタグと異なる場合、ソース内容をコピー。ソースは既に `globs:` + `alwaysApply: true` + `layer:` frontmatter を含む
  - 必要なら subdir を作成
  - ソースタグが一致する場合はスキップ
- `character_Instance.md` の生成:
  - source = LI_PLUS_REPOSITORY/`rules/character_Instance.md`（frontmatter 済み）
  - Create-only: `{workspace_root}/.claude/rules/character_Instance.md` が既に存在すれば無条件でスキップ
  - 存在しない場合のみソースをそのままコピー
  - タグベースの上書きは行わない。ユーザーカスタマイズはアップデートをまたいで保護される
- 古い rules の削除: `{workspace_root}/.claude/rules/` 配下で LI_PLUS_REPOSITORY/rules/ の対応パスに存在しないファイル（`character_Instance.md` を除く）は削除。空になった subdir も削除

**4c.3. `.claude/skills/` ファイル生成（flat ディレクトリミラー）**

- `{workspace_root}/.claude/skills/` が存在しなければ作成
- LI_PLUS_REPOSITORY の `skills/<name>/SKILL.md` を **flat** に走査する（subdir は持たない）:
  - target = `.claude/skills/<name>/SKILL.md`
  - 必要なら subdir を作成
  - ソースをそのままコピー（ソースは既に Claude Code skill frontmatter を含む）
  - ソースタグが一致する場合はスキップ
- 古い skills の削除: `.claude/skills/` 配下で LI_PLUS_REPOSITORY/skills/ に存在しない `<name>/` ディレクトリは再帰削除

注意: Claude Code の skill 探索は `.claude/skills/` 配下の subdir を辿らない。skill 名は flat 階層で一意である必要があり、レイヤー属性は skill 名の接頭辞規約で表現する（例: `evolution-judgment-learning`）。

**4c.4. hooks の bootstrap**

- ソースファイル:
  - `adapter/claude/hooks-settings.md` — `settings.json` の JSON ブロックをリテラルで保持
  - `adapter/claude/hooks/*.sh` — hook スクリプト本体（そのままコピーし、`{LI_PLUS_TAG}` プレースホルダを解決済みターゲットタグへ置換）
- `{workspace_root}/.claude/settings.json` が存在しない:
  - `adapter/claude/hooks-settings.md` の JSON コードブロックから settings.json を生成
  - `{workspace_root}/.claude/hooks/` を作成し、`adapter/claude/hooks/*.sh` をすべてコピー
  - SessionStart は startup / resume / clear / compact の 4 matcher を使用し、Cold-start Synthesis 素材がどのセッション入口でも出力されるようにする
- `{workspace_root}/.claude/settings.json` が存在する:
  - settings.json は変更しない。workspace が所有するファイルであり、Li+ はユーザー追加キー（permissions / env / theme / 他コンポーネント hook）を暗黙に書き換えない
  - 既存の `{workspace_root}/.claude/hooks/*.sh` 内のソースタグを確認（例: `# Source: adapter/claude/hooks/on-session-start.sh (build-2026-03-30.14)`）
  - 現在のターゲットタグと一致 → スキップ（最新）
  - 不一致またはタグなし → `adapter/claude/hooks/*.sh` を再コピーし、`{LI_PLUS_TAG}` を現在のターゲットタグへ置換（settings.json は再生成しない）
- `on-session-start.sh` が Cold-start Synthesis 素材の emitter。stdout はセッション開始コンテキストへ注入される（Claude Code SessionStart 契約）。素材は `rules/cold-start-synthesis.md` のリテラル、直近の `docs/a.-` 先頭、最新リリースタグ、open in-progress issue、self-evaluation 先頭。synthesis は hook ではなく Character_Instance を介して AI が行う
- `.sh` ファイルには実行権限を付与

注意: bootstrap は次回セッションから有効。現セッションは Li+config.md の実行で継続する。

### Phase 4 codex: Codex 統合

Codex には rules/skills 機構がないため、レイヤーは明示 read で読み込む。

**4x.1. アダプターの bootstrap**

- target = `{workspace_root}/AGENTS.md`, source = `adapter/codex/AGENTS.md`
- sentinel 判定ロジックは 4c.1 と同一（存在しなければ新規、sentinel ありタグ一致でスキップ、不一致で section 差し替え、sentinel なしでユーザー確認）

**4x.2. Li+ レイヤーの直接読み込み**

- LI_PLUS_REPOSITORY の `rules/*.md` をすべて読み込む（always-on）
- `skills/<name>/SKILL.md` は `adapter/codex/AGENTS.md` のトリガー表に従いオンデマンドで読み込む

---

## Phase 5: ワークスペース準備

参照: `Li+bootstrap.md` Phase 5。依存: Phase 2（gh CLI 認証済み）。

**5.1. USER_REPOSITORY 作業クローンの準備**

- `USER_REPOSITORY` がデフォルト値 `owner/repository-name` の場合はスキップ
- `USER_REPOSITORY` が LI_PLUS_REPOSITORY と一致する場合: ローカル clone で `git checkout main` を実行
- それ以外: ワークスペースに対象リポジトリのディレクトリが存在しなければリポジトリ名で clone。既に存在する場合はスキップ（再 clone しない）

---

## Phase 6: 完了報告

参照: `Li+bootstrap.md` Phase 6。依存: すべての先行 Phase。

**6.1. 起動完了を報告する。**

---

## 関連ページ

- [B. Configuration](B.-Configuration) — 設定リファレンス
- [D. Installation](D.-Installation) — Quickstart セットアップ手順
- [6. Adapter](6.-Adapter) — アダプターレイヤー仕様書

---

## 進化

再構築・削除・最適化はすべて許容する。構造の一貫性のみ維持する。

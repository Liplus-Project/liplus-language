# 更新同期手続き仕様書

本文書は Li+ のアダプター / 設定の更新同期手続き（`Li+update.md`）の仕様を定義する。
Li+config.md の設定値を前提とし、アダプター sentinel tag・Li+config schema・workspace 言語契約のいずれかが目標状態から逸脱した時に AI が実行する Phase を記述する。

---

## 概要

更新同期手続きは **`Li+update.md`** に定義されている。Li+config.md はユーザー設定のみを保持し、同期ロジックは分離されている。

`on-session-start.sh` hook が 3 軸（adapter sentinel tag / Li+config schema / 言語契約）を verify し、いずれかが drift していれば `LI_PLUS_UPDATE_STATUS=needed` を emit する。AI はこの marker を見て本手続きを実行するか判定する。大半のセッションでは `LI_PLUS_UPDATE_STATUS=unnecessary` となり、本手続きは走らない（旧称「セッション起動フロー」が現運用とずれていたため、v1.17.10 で「更新同期手続き」へ rename した）。

AI は Li+config.md を読み込んだ後、`Li+update.md` の Phase 1 から Phase 6 を順に実行する。各 Phase は直前までの Phase を依存前提として宣言する。認証情報をチャットに出力してはいけない。

---

## Phase 1: 環境検出

参照: `Li+update.md` Phase 1。依存なし。

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

参照: `Li+update.md` Phase 2。依存: Phase 1（ランタイム検出済み）。

**2.1. gh CLI のインストール（host OS 別、runtime=claude は hook へ移譲済み）**

host OS は adapter 種別（runtime=claude / runtime=codex）から推測しない。両 adapter とも Linux / macOS / Windows のいずれのホストでも動作しうる（Claude adapter が Windows ネイティブ Git-Bash/MSYS2 上で動く構成も検証済み、#1518）。ただし自動インストールを行うかどうかは adapter によって異なる（下記 runtime=claude / runtime=codex を参照。runtime=codex はいずれの host OS でも自動インストールしない）。

- **runtime=claude:** インストール判断・実行は `Li+update.md` walkthrough ではなく `adapter/claude/hooks/on-session-start.sh` hook が毎セッション自律的に担う（bootstrap walkthrough 側は install 手順を持たない）。hook は起動時に無条件で `$HOME/.local/bin` を PATH に前置し（全ホスト共通の前処理）、その上で `command -v gh` を単一の gate として評価する。PATH 上のどこかに `gh` が解決できれば（例: システム標準の `/usr/bin/gh` でも真になる。`~/.local/bin/gh` というファイル1つの存在確認ではない）その場でスキップする。`gh` が見つからない場合のみ `uname -s` で host OS を判定し、以下のように分岐する：
  - Linux: アーキテクチャ判定つきで `~/.local/bin/gh` へ自動インストールする（sudo 不要、PATH 変更不要）。hook の PATH 前置は hook 自身のプロセスに閉じており、後続の Bash ツール呼び出しの親プロセスにはならず、シェルプロファイルへの書き込みも行わない。そのため自動インストール直後でも素の `gh` が PATH 解決される保証はなく、以降の gh 操作は常にフルパス `~/.local/bin/gh` を使用すること（[B. Configuration](B.-Configuration) の注意事項にも同旨の記載がある）。この制約は自動インストール対象の Linux にのみ適用される。macOS / Windows は `brew` / `winget` が導入した `gh` が最初から PATH 上にあるため該当しない。
  - macOS / Windows(Git-Bash・MSYS2・Cygwin): 自動インストールしない。`gh` を**前提条件**として扱い、`brew install gh` / `winget install --id GitHub.cli` の具体的な導入コマンドをユーザーへ案内する。
  - 上記いずれにも一致しないホストカーネル: 自動インストールせず、具体的なコマンドは示さず一般的な導入案内のみを出す。
  - 結果（`installed` / `failed: <詳細>` / `missing: <ガイダンス>`）は `GH_INSTALL_STATUS` として `━━━ gh install ━━━` マーカーで session 冒頭 context に emit される。マーカーの出力形式・出力タイミングの正本は [6. Adapter](6.-Adapter) の on-session-start.sh 節を参照。
- **runtime=codex:** host OS に関わらず `gh` は**前提条件**として扱い、bootstrap では自動インストールしない。`gh` が不在なら検出した host OS に応じた案内（Windows: `winget install --id GitHub.cli` / macOS: `brew install gh`）をユーザーへ提示し（代行実行しない）、導入後に続行する。詳細は [D. Installation](D.-Installation) の前提条件を参照

**2.2. GH_TOKEN の読み込みと認証**

`GH_TOKEN` を読み込んで gh CLI で認証する。認証情報はチャットに出力しない。認証後は keyring にトークンが保存されるため、以降の `gh` コマンドに `GH_TOKEN` の明示的な export は不要。

**2.3. workspace 言語契約の解決**

`LI_PLUS_BASE_LANGUAGE` と `LI_PLUS_PROJECT_LANGUAGE` を解決する。

- これらは **配布先 workspace 専用** の設定であり、LI_PLUS_REPO 内部のガバナンスとは分離する
- `LI_PLUS_BASE_LANGUAGE` は人間との対話の既定言語。issue/discussion/PR コメントのような会話返信もこちらが既定
- `LI_PLUS_PROJECT_LANGUAGE` は issue / PR / commit body や保存する要求仕様書など durable artifact の既定言語
- どちらか未設定の場合、AI がセッション開始時に1回対話で確認し、Li+config.md へ書き戻す
- 推奨初期値は「基本言語 = 現在の対話言語」「プロジェクト言語 = 基本言語と同じ」
- bootstrap の ask と Li+config.md への書き戻しは、セッション開始時の config 未解決パスにのみ適用する。config が解決済みなら、セッション途中の再 ask と config 再書き込みは本 Phase の対象外とする
- runtime precedence（人間の明示指示 > スレッド合意 > config > 再 ask）はアダプターの Workspace_Language_Contract が担い、セッション全体を通して本 Phase を再起動せずに働く

**2.4. Webhook 配信モードの解決（任意）**

- `LI_PLUS_WEBHOOK_DELIVERY`（`poll` / `channel` / `mcp_hook`）はアダプターが runtime で参照する
- 未設定時の既定は `poll`。bootstrap 側の追加処理は不要
- `mcp_hook` は opt-in 経路（settings.json への手動編集が必要）。詳細は B. Configuration を参照

---

## Phase 3: Li+ ソース解決

参照: `Li+update.md` Phase 3。依存: Phase 2（gh CLI 認証済み）。

**3.1. `LI_PLUS_CHANNEL` による対象バージョンの決定**

- `latest`: Latest release タグ（stable release のみ）
- `release`: pre-release を含む最新リリースタグ（GitHub Release API）
- `tag`: 作成日順で最新の git タグ（GitHub Release が未作成のタグも含む）。clone モードでは `git ls-remote --tags --sort=-creatordate {repo_url} | head -1` を使用
- 包含関係は tag ⊇ release ⊇ latest。tag は GitHub Release 作成前の pre-release タグ検証を意図する。api モードの tag 拡張は現時点ではスコープ外
- バージョン確認は起動のたびに Phase 4 へ進む前に必ず実施する。ローカル clone が古いままでも黙って継続してはいけない

**3.2. `LI_PLUS_MODE` による Li+ ソース取得**

**api モード:**
- `rules/` 配下の全 `*.md` を対象バージョンで GitHub API から LI_PLUS_REPO より取得
- `skills/` 配下の全 `<name>/SKILL.md` を対象バージョンで GitHub API から取得
- 検出した runtime に応じて `adapter/claude/` または `adapter/codex/` を取得

**clone モード:**

1. 対象リポジトリは LI_PLUS_REPO の対象バージョン
2. ワークスペース内に LI_PLUS_REPO 由来のディレクトリが存在するか確認
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

参照: `Li+update.md` Phase 4。依存: Phase 3（ソース解決済み、対象タグ確定済み）。

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
  - 不一致またはタグなし → `Li+ BEGIN` 〜 `Li+ END` 間（両端含む）をソース内容で差し替え、下記 legacy webhook trailer migration を除く sentinel 外は保護。置換 byte span は `Li+ END` の最終 byte で終え、adapter source の EOF newline を保持する target suffix へ追加しない
  - legacy webhook trailer migration: 現行 adapter source が `## Optional Webhook Notification Flow` block を sentinel 内で所有する。migration は旧 sentinel section に webhook heading が無い pre-migration 所有形状だけで実行する。差し替え前に source の当該 heading から `Li+ END` 直前までを legacy block として取得し、旧 target の `Li+ END` 直後の suffix から、先頭の2個の separator newline、legacy block、block末尾 newline までを1件とする連続した byte-exact legacy trailer だけを除去する。最初の不一致 byte で停止し、line ending を正規化して一致させず、以後の suffix はそのまま保持する。これにより pre-migration 版が残した重複 trailer を除去しつつ、canonical sentinel の外へ後から追加された同一 block を削除しない。後続 tag を再適用した時は旧 section が既に heading を所有するため migration を skip し、migrated layout の webhook heading は置換 section 内の1件だけになる
- ファイルが存在するが sentinel なし → ユーザーに確認（Li+ セクションを追記 or スキップ）

**4c.2. `.claude/rules/` ファイル生成（再帰ディレクトリミラー）**

- `{workspace_root}/.claude/rules/` が存在しなければ作成
- LI_PLUS_REPO の `rules/**/*.md` を再帰走査し（`model/` `evolution/` `task/` `operations/` subdir を含む）、`rules/model/character_Instance.md` を除いた各ファイルについて:
  - LI_PLUS_REPO/rules/ からの相対パスを保持してターゲットへ配置する（例: `rules/model/absolute.md` → `.claude/rules/model/absolute.md`）
  - ターゲットが存在しない、またはソースタグが現在のターゲットタグと異なる場合、ソース内容をコピー。ソースは既に `globs:` + `alwaysApply: true` + `layer:` frontmatter を含む
  - 必要なら subdir を作成
  - ソースタグが一致する場合はスキップ
- `character_Instance.md` の生成（output-styles slot）:
  - source body = LI_PLUS_REPO/`rules/model/character_Instance.md`（rules-format frontmatter を除去した body 部、codex adapter と共有）
  - target = `{workspace_root}/.claude/output-styles/character_Instance.md`
  - 付与する output-styles frontmatter: `name: character_Instance` + `description: Lin/Lay character pair binding for human-facing dialogue` + `keep-coding-instructions: true`（このフラグを付与しないと、custom output-style 有効化時に Claude Code 既定のコーディング作法 / TodoWrite / ツール使用ガイダンスが system prompt から除外される。出典: https://code.claude.com/docs/en/output-styles.md）
  - 旧 rules slot からの一回限り migration:
    - 旧 file `{workspace_root}/.claude/rules/model/character_Instance.md` が存在し、かつ target が存在しない場合: 旧 file の body（rules frontmatter 除去後）を読み、output-styles frontmatter + body を target に書き、書き込み成功後に旧 file を削除する（ユーザーカスタマイズを新位置へ保全）
    - 旧 file と target が両方存在する場合: いずれにも触れない（ユーザーが既に migrate 済み or 手動介入したと見なし、現状を保護）
  - 新規 install（旧 file なし）:
    - target が存在しない場合のみ source body + output-styles frontmatter を target に書く
    - target が存在する場合はスキップ（Create-only）
  - 必要なら `{workspace_root}/.claude/output-styles/` subdir を作成
  - タグベースの上書きは行わない。ユーザーカスタマイズはアップデートをまたいで保護される
- 古い rules の削除: `{workspace_root}/.claude/rules/` 配下で LI_PLUS_REPO/rules/ の対応パスに存在しないファイル（ただし `{workspace_root}/.claude/rules/` 起点の相対パスが `model/character_Instance.md` でないもの）は削除。空になった subdir も削除（`model/character_Instance.md` 例外は migration が走らなかった「両方存在」ケースに対する safety net として残置）

**4c.3. `.claude/skills/` ファイル生成（flat ディレクトリミラー）**

- `{workspace_root}/.claude/skills/` が存在しなければ作成
- LI_PLUS_REPO の `skills/<name>/SKILL.md` を **flat** に走査する（subdir は持たない）:
  - target = `.claude/skills/<name>/SKILL.md`
  - 必要なら subdir を作成
  - ソースをそのままコピー（ソースは既に Claude Code skill frontmatter を含む）
  - ソースタグが一致する場合はスキップ
- 古い skills の削除: `.claude/skills/` 配下で LI_PLUS_REPO/skills/ に存在しない `<name>/` ディレクトリは再帰削除

注意: Claude Code の skill 探索は `.claude/skills/` 配下の subdir を辿らない。skill 名は flat 階層で一意である必要があり、レイヤー属性は skill 名の接頭辞規約で表現する（例: `evolution-judgment-learning`）。

**4c.4. hooks の bootstrap**

- ソースファイル:
  - `adapter/claude/hooks-settings.md` — `settings.json` の JSON ブロックをリテラルで保持
  - `adapter/claude/hooks/*.sh` — hook スクリプト本体（そのままコピーし、`{LI_PLUS_TAG}` プレースホルダを解決済みターゲットタグへ置換）
- `{workspace_root}/.claude/settings.json` が存在しない:
  - `adapter/claude/hooks-settings.md` の JSON コードブロックから settings.json を生成
  - `{workspace_root}/.claude/hooks/` を作成し、`adapter/claude/hooks/*.sh` をすべてコピー
  - SessionStart は startup / resume / clear / compact / fork の 5 matcher（一次ソースの matcher 表の全件）を使用し、Cold-start Synthesis 素材がどのセッション入口でも出力されるようにする。未登録の matcher は他の entry にフォールバックせず単に hook が発火しないため、その入口では `LI_PLUS_UPDATE_STATUS` マーカーも language contract banner も出ない
- `{workspace_root}/.claude/settings.json` が存在する:
  - settings.json は変更しない。workspace が所有するファイルであり、Li+ はユーザー追加キー（permissions / env / theme / 他コンポーネント hook）を暗黙に書き換えない
  - 既存の `{workspace_root}/.claude/hooks/*.sh` 内のソースタグを確認（例: `# Source: adapter/claude/hooks/on-session-start.sh (build-2026-03-30.14)`）
  - 現在のターゲットタグと一致 → スキップ（最新）
  - 不一致またはタグなし → `adapter/claude/hooks/*.sh` を再コピーし、`{LI_PLUS_TAG}` を現在のターゲットタグへ置換（settings.json は再生成しない）
- `on-session-start.sh` が Cold-start Synthesis 素材の emitter。stdout はセッション開始コンテキストへ注入される（Claude Code SessionStart 契約）。素材は `rules/evolution/cold-start-synthesis.md` の anchor（H1 preamble のみ）、直近の `docs/Decision-Structure.md` 先頭、`rules/` のパスツリー、最新リリースタグ、open in-progress issue、self-evaluation 先頭、promotion candidates、self-evolution observation surface（due / overdue）。素材の正本一覧と section key は [6. Adapter — on-session-start.sh](6.-Adapter#on-session-startsh) を参照する。synthesis は hook ではなく Character_Instance を介して AI が行う
- `.sh` ファイルには実行権限を付与

**4c.5. cold-start state ディレクトリの準備（diff-only 出力の永続化）**

- `on-session-start.sh` は session 冒頭 context 消費を抑えるため、各素材 section の sha256 fingerprint を `{workspace_root}/.claude/state/last-cold-start-emit.json` に永続化し、次回の `startup` matcher 発火時に変化した section だけを emit する（毎セッション全文出力は diff-only 設計の意義を打ち消す）。
- `{workspace_root}/.claude/state/` が存在しなければ作成する
- `{workspace_root}/.claude/state/.gitignore` が存在しなければ以下のリテラルで作成する（ユーザー変更済みの場合は上書きしない）：

  ```
  # Li+ hook runtime state — local-only, not version-controlled.
  *
  !.gitignore
  ```

  ローカルスコープの gitignore により、state がバージョン管理されているホストワークスペースに混入しないようにする。トップレベルの `.gitignore` には触れない。state 本体（`last-cold-start-emit.json`）は hook が初回実行時に生成する。
- このステップは冪等：既存ディレクトリと既存 `.gitignore` はそのまま残す

`on-session-start.sh` の matcher 別挙動（startup の diff-only、resume/clear/compact/fork の rule anchor 再出力、fail-safe full emit）の詳細は [6. Adapter — on-session-start.sh](6.-Adapter#on-session-startsh) を参照する。

**4c.6. `.claude/agents/` ファイル生成（sentinel 区画ミラー）**

- `LI_PLUS_REPO/adapter/claude/agents/` が存在しない場合は本サブフェーズ全体をスキップ（adapter に subagent 定義がない／codex 等の非 claude adapter は影響を受けない）
- `{workspace_root}/.claude/agents/` が存在しなければ作成する
- 生成内容中の `{LI_PLUS_TAG}` は Phase 3 で解決したターゲットタグへ置換する
- **所有の境界:** agent ファイルは 2 種類の内容を同時に運ぶ。Li+ が判定基準として所有する本文（brake 2 の root criteria と評価者の任務の射程）と、その周囲にあるユーザーのランタイムインスタンス（frontmatter の `name` / `description` / `tools` / `model`、およびユーザーが足した記述）である。ファイル単位の所有はどちらか一方しか選べず、どちらを選んでも他方を取り違える — Create-only はマージ済みの基準変更を既存ワークスペースから締め出し、ファイル全体の上書きはインスタンスを破壊する。`Li+ BEGIN` / `Li+ END` 区画は境界をファイルの内側へ移し、両方を成立させる。区画が覆うのは prompt 本文のみで、frontmatter は区画外に置く（frontmatter はワークスペースごとのランタイムカスタマイズが載る面であり、加えて Markdown の frontmatter ブロックの前に sentinel 行を置けないため）。**Claude 側で受容した代償:** frontmatter 以降がそのまま subagent の system prompt になり、Markdown には host が除去するコメント形式が無いため、sentinel 2 行は prompt の内側に入る。Codex 側にこの代償は無い（sentinel は `developer_instructions` 文字列の外の TOML コメントであり、パーサが落とす）。prompt に入る inert な 2 行は Markdown 側で伝播を得るための対価であり、これを避ける唯一の代替は当該ポートに区画を持たないことである
- **どのソースが区画を持つかは列挙ではなく基準で決める。** 順に 2 つ問う:
  1. **そのファイルは、ユーザーの instance ではなく Li+ の判定基準として所有する本文を運んでいるか。** No → Create-only。基準がこの問いのどちら側にも置けないファイルも Create-only を既定とする
  2. **その本文を、ユーザー所有の内容を巻き込まずに 1 つの連続区画で覆えるか。** Yes → 区画を持つ。No（2 種類が交互に並ぶ）→ Create-only とし、そのファイルの伝播欠落は開いたまま残す。交互配置をまたぐ幅の区画はユーザーの内容を飲み込み、それは区画が防ぐために存在する失敗そのものである。問い 1 だけでは混在ファイルは決まらず、決まると読むと逆の答えが出る
- `adapter/*/agents/dialogue-evaluator.*` は現時点の問い 2 の事例であり、列挙の 1 項ではなくその分岐の実例として名指ししている。Li+ 所有の判定基準（5 軸、採点思想、middle-read 要求）を確かに運んでおり、かつその途中に Character_Instance literal を持つため、1 つの区画では両者を分離できない。よって Create-only のまま。**解決ではなく明示する帰結:** その軸への改訂は既存ワークスペースへ届かない。これは「伝播すべきものが無いと判定されたファイル」ではなく、「本基準では閉じられないファイルに同じ伝播欠落が残っている」状態である
- 1 つのソースが持つ区画は最大 1 つで、sentinel 文字列はそのファイルの他の場所（コメントを含む）に現れてはならない。区画は最初の出現位置で特定するため、2 つ目の言及が境界として読まれる
- `LI_PLUS_REPO/adapter/claude/agents/` 直下の `*.md` 各ファイルについて（FLAT、サブディレクトリなし）：
  - target = `{workspace_root}/.claude/agents/<filename>.md`
  - **sentinel を持たないソース（Create-only）:** target が存在しなければソースをそのままコピー、存在すればスキップ（ユーザーカスタマイズを保持）
  - **sentinel を持つソース — 区画判定（4c.1 と同型、本ファイルへスコープ）:**
    - a. target が存在しない → 解決済みソースの内容で生成する
    - b. target が存在し `Li+ BEGIN` を含む → sentinel からタグを抽出。現ターゲットタグと一致すればスキップ。異なる／欠落していれば `Li+ BEGIN`〜`Li+ END`（両端含む）の区画をソース側の区画で置換し、区画外（上の frontmatter とユーザーが下に足した記述）はそのまま保持する。4c.1 の legacy webhook trailer migration は本分岐では**適用しない**（あの migration は CLAUDE.md 面の byte-frozen な `## Optional Webhook Notification Flow` ブロック専用であり、agent ファイルに該当する pre-migration trailer は存在せず、ここで走らせるとユーザー記述を削除する）
    - c. target が存在するが `Li+ BEGIN` を含まない → ユーザーへ確認：現ソースからこのファイルを再生成するか、スキップするか。区画導入以前のインストールはすべてこの状態から入る。sentinel の無いファイルのどのバイトがユーザー由来かを Li+ は判別できないため、再生成はファイル全体を置き換える（当該ファイルへのローカル編集は失われる — 事前にコピーを取るよう案内する）。スキップは Li+ 所有の基準をインストール時点のまま据え置く。無音の上書きは 4c.1 と同じ理由で禁止（ユーザー記述を同意なく破壊するため）
      - **再確認の周期と、それが何に寄生しているか:** ユーザーの回答を記録する state は無く、branch (c) は本サブフェーズが走るたびに target ファイルのバイトから判定し直す。したがってスキップしたファイルは次に bootstrap が走ったとき再び確認される。bootstrap が走るのはセッション開始時の marker が `needed` を返すときであり、そのタグ軸が読むのは `.claude/CLAUDE.md` の sentinel であって agent ファイルではない（agent ファイルの sentinel 状態を読む面は存在しない）。4c.1 はここへ到達するのと同じ walkthrough 内でその sentinel を更新するため、次の再確認は次のタグ更新＝次のリリースで届く。リリースとリリースの間、スキップを選んだワークスペースは追加のプロンプトなしにインストール時点の基準のまま座る。これは branch (c) が隠す欠陥ではなく残余である — 区画導入前の挙動にはプロンプト自体が一度も無かった
- stale 削除はしない（ユーザーが adapter ソースに無い custom subagent を保持している可能性があり、stale 扱いすると user work を破壊する）

注意: bootstrap は次回セッションから有効。現セッションは Li+config.md の実行で継続する。

### Phase 4 codex: Codex 統合

Codex ホストでは Phase 4 claude branch と同型に adapter / skills / hooks / agents を生成する（#1502 実機検証済みの Codex 配置）。

- skill は `.agents/skills/<name>/SKILL.md` に配置（Codex ネイティブの `description` 自動発火、**trust 不要**）
- 常時 rules には Codex 側のフォルダ相当が無いため、SessionStart hook が LI_PLUS_REPO clone から `rules/**/*.md` を読み `additionalContext` で注入する（`.codex/hooks/on-session-start`）。旧 branch の「bootstrap で rules を直接読む」ステップは廃止
- hook は `.codex/hooks/`（`*.ps1` が Windows ネイティブ主経路 + `*.sh` POSIX フォールバック）に配置し、`.codex/hooks.json` で登録
- subagent（Codex "agents"）は `.codex/agents/*.toml` に配置

**Codex hook trust 前提条件（ユーザーへ明示）:** Codex の hook は実行前に一度だけ GUI trust が必要（Codex App → 設定 → フック → 当該プロジェクト → 信頼する）。build が hook 本体を変えるたびに再 trust が必要（trust は内容ハッシュ単位）。trust 前は SessionStart の rules 注入と毎ターンの gate 再注入が無音で何もしない。bootstrap は hook ファイルを書くが trust は付与できないため、Phase 6 完了報告で GUI trust を案内する。詳細は [D. Installation](D.-Installation) を参照。

**4x.1. アダプターの bootstrap**

- target = `{workspace_root}/AGENTS.md`, source = `adapter/codex/AGENTS.md`
- sentinel 判定ロジックは 4c.1 と同一（存在しなければ新規、sentinel ありタグ一致でスキップ、不一致で section 差し替え、sentinel なしでユーザー確認）。差し替え時の legacy webhook trailer migration も4c.1と同一で、旧 section が heading を持たない時だけ、連続する byte-exact legacy trailer を `Li+ END` 直後から除去し、canonical sentinel 外のユーザー作成 suffix を保持する
- 32 KiB 上限: ルートの AGENTS.md は最小コア（identity / character / 起動契約）のみを保持。rules 全体は 4x.3 の SessionStart hook 注入で届くため inline しない（Codex の `project_doc_max_bytes` 既定 32 KiB を超えないため）

**4x.2. `.agents/skills/` ファイル生成（flat ディレクトリミラー）**

- 4c.3 と同型だが、Codex ネイティブの skill 配置は `.agents/skills/`（`.claude/skills/` ではない）
- `{workspace_root}/.agents/skills/` が存在しなければ作成
- LI_PLUS_REPO の `skills/<name>/SKILL.md` を **flat** に走査し、`.agents/skills/<name>/SKILL.md` へそのままコピー（ソースタグ一致でスキップ）
- 古い skills の削除: `.agents/skills/` 配下で LI_PLUS_REPO/skills/ に存在しない `<name>/` ディレクトリは再帰削除
- ここで生成した「インストール済み skill 名の一覧」は、4x.5 の l1-gate-eval skills-disable enumeration の入力になる。先に控えておく

**4x.3. hooks の bootstrap**

- ソースファイル:
  - `adapter/codex/hooks-config.md` — `.codex/hooks.json` の JSON ブロックをリテラルで保持（`config.toml [hooks]` 代替スニペットも併記）
  - `adapter/codex/hooks/*.ps1`（Windows ネイティブ主経路）+ `adapter/codex/hooks/*.sh`（POSIX フォールバック）
- **`.ps1` のバイト忠実コピー（重要）:** `.ps1` は BOM 付き UTF-8（先頭 3 バイト `EF BB BF`）。これを呼び出す Windows PowerShell 5.1 は BOM 無しの非 ASCII `.ps1` を誤読する。`.ps1` は生バイトでコピーし、BOM を剥がす / 付け直す / 改行を書き換えるテキスト変換を通さない。インストール後、各 `.ps1` が `EF BB BF` で始まることを検証する（`.sh` は BOM 無し LF 終端 UTF-8、こちらもそのままコピー）
- hook 本体の `{LI_PLUS_TAG}` 置換: `# Source: ... ({LI_PLUS_TAG})` 行の token を解決済みターゲットタグへ置換。BOM とその他バイトを保つためバイトレベルの token 置換で行う（token は ASCII、置換は先頭 BOM に触れない）
- `.codex/hooks.json` の `{WORKSPACE_ROOT}` 置換: Codex の hook は絶対パスが必要（`$CLAUDE_PROJECT_DIR` 相当が無い）。`.codex/hooks.json` 内の `{WORKSPACE_ROOT}` をすべて絶対 workspace パスへ置換。スペースを含むパスは quote（テンプレートは `-File` 引数を既に quote 済み）
- `{workspace_root}/.codex/hooks.json` は Li+ 所有（compare-and-overwrite）:
  - 存在しない → `adapter/codex/hooks-config.md` の JSON ブロックから生成（`{WORKSPACE_ROOT}` 置換済み）。`{workspace_root}/.codex/hooks/` を作成し `adapter/codex/hooks/*.ps1`・`*.sh` をバイト忠実にコピー
  - 存在し内容が byte 一致 → スキップ
  - 存在し内容が異なる → テンプレートで上書き（ユーザー固有の Codex 設定は Li+ 非所有の `{workspace_root}/.codex/config.toml` に置く。hook を TOML 配置したい場合は `config.toml [hooks]` スニペットが代替。hooks.json と TOML を両用しない＝二重登録になる）
  - SessionStart は単一の regex matcher `startup|resume|clear|compact`（Codex の matcher は regex、1 エントリで 4 ソースを網羅）。rules 注入 + cold-start 素材はどのセッション入口でも発火
- `{workspace_root}/.codex/hooks/*.{ps1,sh}` の tag 追跡再生成:
  - 既存ファイルの `# Source: ... (build-...)` 行のタグを確認。一致でスキップ、不一致 / タグなしで再コピー（バイト忠実 .ps1 + `{LI_PLUS_TAG}` 置換）
  - 再生成は hook 内容ハッシュを変えるため Codex の GUI trust を**無効化**する。完了報告で再 trust を案内する
- `on-session-start` が Codex の rules 注入 + Cold-start Synthesis 素材 emitter。LI_PLUS_REPO clone の `rules/**/*.md` を読み literal を `additionalContext` で注入（Claude の `.claude/rules/` 常時フォルダの Codex 代替）+ update-status marker（LI_PLUS_UPDATE_STATUS、startup matcher 限定）+ language contract marker（LI_PLUS_BASE_LANGUAGE / LI_PLUS_PROJECT_LANGUAGE、全 matcher）+ diff-only cold-start 素材。synthesis は hook ではなく Character_Instance を介して AI が行う
- `.sh` ファイルに実行権限を付与（`.ps1` は `powershell -File` 経由で呼ばれるため実行ビット不要）

**4x.4. cold-start state ディレクトリの準備（diff-only 出力の永続化）**

- 4c.5 と同型。Codex の state パスは `.codex/state/`
- `on-session-start` は各 section の fingerprint を `{workspace_root}/.codex/state/last-cold-start-emit.json` に永続化する
- `{workspace_root}/.codex/state/` が存在しなければ作成
- `{workspace_root}/.codex/state/.gitignore` が存在しなければ以下のリテラルで作成（ユーザー変更済みは上書きしない）：

  ```
  # Li+ hook runtime state — local-only, not version-controlled.
  *
  !.gitignore
  ```

- このステップは冪等

**4x.5. `.codex/agents/` ファイル生成（sentinel 区画ミラー + skills-disable enumeration）**

- 4c.6 と同型（所有の境界、区画を持つかの基準、3 分岐の区画判定はすべて同じ）だが、Codex agents は `.codex/agents/*.toml`（TOML）であり、sentinel は HTML コメントではなく TOML コメント記法（`# --- Li+ BEGIN (<tag>) ---` / `# --- Li+ END ---`）で書き、`l1-gate-eval` は bootstrap が埋める skills-disable enumeration を追加で必要とする（Codex に global な skills-off スイッチが無いため）。本面では区画が覆うのは `developer_instructions` の代入であり、インスタンス側フィールド（`name` / `description` / `model_reasoning_effort` / `sandbox_mode`）は Claude 側の frontmatter と同じく区画外に置く
- `LI_PLUS_REPO/adapter/codex/agents/` が存在しなければ本サブフェーズ全体をスキップ
- `{workspace_root}/.codex/agents/` が存在しなければ作成
- `LI_PLUS_REPO/adapter/codex/agents/` 直下の `*.toml` 各ファイルについて（FLAT）:
  - target = `{workspace_root}/.codex/agents/<filename>.toml`
  - 生成内容中の `{LI_PLUS_TAG}` を解決済みターゲットタグへ置換する。区画を持つソースでは sentinel がそのファイル唯一のタグ担持者であり、区画を持たないソースは `# Source: ... ({LI_PLUS_TAG})` 行にタグを持つ。区画を持つファイルが区画外にもう 1 つタグを持ってはならない — タグ更新で書き換わるのは区画だけであり、区画外のタグはインストール時点で凍結して実体と食い違うバージョンを表示する
  - **skills-disable enumeration（l1-gate-eval.toml のみ）:** この agent は ZERO skill で動かす必要がある（brake-2 の root-criteria-only 要件）。Codex は skill を SKILL.md パス単位で無効化する（global 不可）。ファイル末尾の `# --- Skills disable enumeration (filled by bootstrap) ---` マーカー以降に、4x.2 でインストールした skill ごとに以下の TOML ブロックを 1 つずつ追記する：

    ```toml
    [[skills.config]]
    path = "{WORKSPACE_ROOT}/.agents/skills/<skill-name>/SKILL.md"
    enabled = false
    ```

    - `{WORKSPACE_ROOT}` を絶対 workspace パスへ置換（hook と同じく Codex は絶対パスが必要）
    - 4x.2 でインストールした `<name>/SKILL.md` の集合と同じ数だけブロックを emit。将来の Codex build が global skills toggle を追加したら、この enumeration をそれで置き換え可（ソースファイルの placeholder コメント参照）
    - 他の agent（dialogue-evaluator.toml など）には skills-disable enumeration を付けない。`{LI_PLUS_TAG}` 置換のみでコピー
    - enumeration は sentinel 区画の**外側**（ファイル末尾）に置く。bootstrap がワークスペース固有値で埋める領域であり Li+ ソースの内容ではないため、区画の置換はここに触れてはならない
  - **sentinel を持たないソース（Create-only）:** target が存在しなければ生成内容を書き、存在すればスキップ（ユーザーカスタマイズを保持）
  - **sentinel を持つソース — 区画判定:**
    - a. target が存在しない → 生成内容を書く（l1-gate-eval.toml はここで enumeration も新規生成される）
    - b. target が存在し `Li+ BEGIN` を含む → sentinel のタグを抽出。現ターゲットタグと一致すればスキップ、異なる／欠落していれば `Li+ BEGIN`〜`Li+ END`（両端含む）をソース側の区画で置換し、区画外（上のヘッダコメントとインスタンス側フィールド、下の skills-disable enumeration）はそのまま保持する
    - c. target が存在するが `Li+ BEGIN` を含まない → ユーザーへ確認：再生成かスキップか。区画導入以前のインストールはすべてこの状態から入る。確認の内容と帰結は 4c.6 と同じで、l1-gate-eval.toml の再生成は 4x.2 の集合から skills-disable enumeration も作り直す
- enumeration が生成されるのは分岐 a と分岐 c の再生成のときだけ。タグ更新で書き換わるのは区画のみのため、後でインストール skill 集合が変わった場合、ユーザーはローカルの l1-gate-eval.toml を削除して再 bootstrap し enumeration を再生成する必要がある。skill 集合が変わったがローカル l1-gate-eval.toml が既存の場合は完了報告で surface する
- stale 削除はしない（adapter ソースに無い custom agent をユーザーが保持している可能性）

注意: bootstrap は次回セッションから有効、かつ一度きりの Codex GUI hook trust が前提（4x 冒頭）。現セッションは Li+config.md の実行で継続。trust 付与までは rules 注入と毎ターンの gate は走らない

---

## Phase 5: ワークスペース準備

参照: `Li+update.md` Phase 5。依存: Phase 2（gh CLI 認証済み）。

**5.1. USER_REPOn 作業クローンの準備**

`Li+config.md` 内の `USER_REPO1`、`USER_REPO2`、… を順に enumerate して以下を実行する:

- 値がデフォルト値（テンプレート初期値の URL プレースホルダ等）の場合はスキップ
- 値が `LI_PLUS_REPO` と一致する場合: ローカル clone で `git checkout main` を実行
- それ以外: ワークスペースに対象リポジトリのディレクトリが存在しなければリポジトリ名で clone。既に存在する場合はスキップ（再 clone しない）

URL から owner / repository name は parse して抽出する（gh CLI integration 用）。HTTPS / git+ssh / local path / `file://` はいずれも受容する（詳細は B. Configuration の `USER_REPOn` 節を参照）。

---

## Phase 6: 完了報告

参照: `Li+update.md` Phase 6。依存: すべての先行 Phase。

**6.1. 更新同期完了を報告する。**

**6.2. runtime=codex のみ — 一度きりの GUI hook trust を案内する**

- Codex App を開き hook を trust するよう案内する（設定 → フック → 当該プロジェクト → 信頼する）。trust 付与までは SessionStart の rules 注入と毎ターンの Trigger Check Gate 再注入が走らない（Phase 4 codex 冒頭、step-by-step は [D. Installation](D.-Installation)）。
- 本 bootstrap が hook 本体を再生成した場合（tag bump）、trust の再付与が必要なことを伝える（trust は内容ハッシュ単位）。
- インストール済み skill 集合が変わったがローカルの `.codex/agents/l1-gate-eval.toml` が既存（enumeration は sentinel 区画の外側にあり、タグ更新では再生成されない — 4x.5 参照）の場合、skills-disable enumeration を更新するにはそのファイルを削除して再 bootstrap する必要があることを伝える。

---

## 関連ページ

- [B. Configuration](B.-Configuration) — 設定リファレンス
- [D. Installation](D.-Installation) — Quickstart セットアップ手順
- [6. Adapter](6.-Adapter) — アダプターレイヤー仕様書

---

## 進化

再構築・削除・最適化はすべて許容する。構造の一貫性のみ維持する。

## 概要

Li+のセットアップは、ワークスペースに設定ファイルを1つ配置するだけです。
初回セッションでAIが環境を自動検出し、必要なファイルを生成します。

このページは **Quickstart** です。各設定値の詳細は [B. Configuration](B.-Configuration)、更新同期手続きの詳細は [C. Update](C.-Update) を参照します。

`Li+config.md` は各リリースに添付されています。→ [最新リリース](https://github.com/Liplus-Project/liplus-language/releases/latest)

---

## 前提条件

- **AIエージェント環境**（Claude Code / CODEX 等）
- **GitHubアカウント**
- **GitHub Personal Access Token**（GH_TOKEN）
- **CODEX (Windows ネイティブ環境) の場合のみ: `gh` CLI を事前にインストール**
  - Claude 側（Linux/Mac）は SessionStart hook が `~/.local/bin/gh` を自動配置しますが、CODEX の Windows ネイティブ環境ではこの自動インストール経路は使えません（プラットフォーム違い）。
  - Windows ターミナルで以下を一度だけ実行します（bootstrap は代行しません。明示的にユーザーが実行）：

    ```
    winget install --id GitHub.cli
    ```

  - 既に `gh` が入っていればスキップして構いません。

---

## GH_TOKENの取得

1. GitHubの **Settings → Developer settings → Personal access tokens → Fine-grained tokens** へ移動
2. **Generate new token** をクリック
3. 以下の権限を付与：
   - **Repository access**: 作業リポジトリ（Li+本体はpublicリポジトリのため追加不要）
   - **Permissions**: `Contents: Read and write`、`Issues: Read and write`、`Pull requests: Read and write`、`Metadata: Read-only`
4. 生成されたトークンをコピーして控えておく

---

## セットアップ手順

### 1. Li+config.mdをダウンロードして配置する

[最新リリース](https://github.com/Liplus-Project/liplus-language/releases/latest) のAssetsから `Li+config.md` をダウンロードし、ワークスペースフォルダに配置します。

### 2. 設定値を書き換える

詳細な意味は [B. Configuration](B.-Configuration) を参照し、ここでは初回セットアップに必要な項目だけ確認します。

| 項目 | 説明 |
|------|------|
| `GH_TOKEN` | 取得したPersonal Access Token |
| `USER_REPO1` / `USER_REPO2` / … | 作業対象のリポジトリを URL 形式で指定（例: `https://github.com/myname/myrepo`）。複数ある場合は番号を増やして並列に追加可（上限なし）。未設定のままでも OK |
| `LI_PLUS_REPO` | Li+本体のリポジトリを URL 形式で指定。デフォルト: `https://github.com/Liplus-Project/liplus-language`。フォーク利用時に変更 |
| `LI_PLUS_MODE` | `clone`推奨（オフライン環境でも動作する） |
| `LI_PLUS_CHANNEL` | `release`推奨（最新のプレリリースを含む） |
| `USER_REPOn_EXE_MODE` / `LI_PLUS_REPO_EXE_MODE` | リポジトリごとに `trigger`（人間主導）/ `semi_auto`（半自動、patchはAI直接マージ、minor / major は人間確認）/ `auto`（AI自律）を指定。未設定ならセッション開始時にAIが聞いて設定 |
| `LI_PLUS_BASE_LANGUAGE` | 人間との対話に使う基本言語。未設定ならセッション開始時にAIが聞いて設定 |
| `LI_PLUS_PROJECT_LANGUAGE` | issue / PR / commit body など成果物に使うプロジェクト言語。未設定ならセッション開始時にAIが聞いて設定 |
| `LI_PLUS_WEBHOOK_STATE_DIR` | 任意。`mcp__github-webhook-mcp` が無い時に、前景で読む local webhook state dir。絶対パスまたはワークスペース相対 |

### 3. リポジトリルールセット（ブランチ保護）を設定する

Li+ は ブランチ → PR → CI → マージ のフローで動作します。
GitHub 側にルールセットを設定しておくと、AI・人間ともに main への直接 push を防げます。

> この手順は GitHub の Web UI で行います。

#### 3-1. ルールセットを作成する

1. リポジトリの **Settings** タブを開く
2. 左メニューの **Rules → Rulesets** を選択
3. **New ruleset** → **New branch ruleset** をクリック

#### 3-2. 基本設定

1. **Ruleset Name** に名前を入力（例: `Branch protection rules`）
2. **Enforcement status** を **Active** に設定
3. **Bypass list** は空のままにする（オーナーを含め誰もバイパスできない状態を推奨）

#### 3-3. 保護対象のブランチを指定する

1. **Target branches** セクションで **Add target** をクリック
2. **Default branch** を選択（main ブランチが保護対象になる）

#### 3-4. ルールを有効にする

**Rules** セクションで以下のルールにチェックを入れます：

**Restrict deletions**
- デフォルトブランチの削除を禁止します

**Require a pull request before merging**
- main への直接 push を禁止し、PR 経由のマージを強制します
- チェックを入れると追加設定が表示されます：
  - **Required approvals**: `0`（AI主体リポジトリの最小構成。チーム開発では 1 以上を推奨）
  - **Allowed merge methods**: プロジェクトに合わせて選択（デフォルトの Merge, Squash, Rebase すべて有効で OK）

**Require status checks to pass**
- CI が通らないとマージできなくなります
- チェックを入れると追加設定が表示されます：
  - **Add checks** をクリックし、リポジトリの CI ジョブ名を追加（例: `CI`）
  - CI ジョブ名は GitHub Actions ワークフローの `jobs.<job_id>.name` と一致させてください

#### 3-5. 保存する

ページ下部の **Create** ボタンをクリックして保存します。

> **補足**
> - ルールセットは **Settings → Rules → Rulesets** からいつでも変更できます
> - CI ジョブが未作成の場合は、先にワークフローを追加してからステータスチェックを設定してください

### 4. 初回セッションを開始する

新しいセッションを開始し、AIに Li+config.md の読み込みと実行を依頼します。

例：
```
Li+config.md を読んで実行して
```

AIが自動的に：

1. 環境を検出（Claude / CODEX）
2. Li+config.md のパーミッションを保護（Linux/Mac: chmod 600）
3. 基本言語とプロジェクト言語が未設定なら対話で確認して Li+config.md へ保存
4. gh CLI を確認（Claude / Linux・Mac は初回のみ自動配置。CODEX / Windows ネイティブは `winget` 前提条件として事前インストール。上記「前提条件」参照）
5. GH_TOKENで認証
6. `LI_PLUS_CHANNEL` に対応する対象バージョンを確認
7. 既存 clone と対象バージョンがずれていれば、人間に更新するか確認
8. `rules/**/*.md` を常時ロード（L1–L4 の常時ロード分、subdir 含む常に必須。L5 Notifications と L6 Adapter は `rules/<layer>/` を持たない予約スロット。詳細は [判断構造 layer-reorg-rationale](layer-reorg-rationale)）。Claude は `.claude/rules/` フォルダの自動ロード、CODEX は SessionStart hook の `additionalContext` 注入で常時ロードを実現します。`skills/**/SKILL.md` は両ホストとも `description` マッチによる自動発火（手動トリガー表は廃止済み）
9. 環境に応じた設定ファイルを自動生成

詳細な更新同期ステップ定義は [C. Update](C.-Update) を参照します。

| 環境 | 生成されるファイル |
|------|------------------|
| Claude Code | `{workspace_root}/.claude/CLAUDE.md` + `{workspace_root}/.claude/settings.json` + `{workspace_root}/.claude/hooks/*.sh` + `{workspace_root}/.claude/skills/**` + `{workspace_root}/.claude/rules/**` + `{workspace_root}/.claude/agents/*.md`（adapter/claude/ 配下から生成） |
| CODEX | `{workspace_root}/AGENTS.md` + `{workspace_root}/.agents/skills/**`（ネイティブ skill 自動発火）+ `{workspace_root}/.codex/hooks/*.ps1`・`*.sh` + `{workspace_root}/.codex/hooks.json` + `{workspace_root}/.codex/agents/*.toml`（adapter/codex/ 配下から生成）。**生成後に一度だけ GUI で hook を trust する必要があります**（下記「CODEX: hook の GUI trust」参照） |

### 5. 次回以降のセッション

設定ファイルが自動で読み込まれるため、以下のように送るだけで起動します：

```
Li+適応。
```

---

## 動作確認

セッション開始後、AIに話しかけると **Lin** または **Lay** として応答が返ってきます。
名前が表示されていればLi+の適用が成功しています。

---

## UX caveats: `.claude/` 配下の sensitive file

Claude Code は `.claude/CLAUDE.md` / `.claude/settings.json` / `.mcp.json` 等を内部的に sensitive file として扱い、Edit / Write 時に**独立した許可プロンプト**を出します。これは以下の手段では override できません。

- `"permissions": {"allow": ["Edit(**)", "Write(**)"]}` 設定
- `--dangerously-skip-permissions` フラグ

Li+ clone mode bootstrap は毎セッション、tag 差分があれば `.claude/CLAUDE.md` / `.claude/hooks/*.sh` を上書きします。tag 更新の度に許可プロンプトが出るため、頻繁な更新時の UX 負債になります。

**長期的な解決方向**: プラグイン化 (`~/.claude/plugins/` への移動) により harness 内部 file ops 経路を経由させ、sensitive-file gate を回避します。allowlist や bypass mode では `.claude/` 配下の摩擦は解消されないため、回避策提案前に実機検証を行ってください。

同構造の他 sensitive file 候補: `.claude/settings.json`, `.mcp.json`, `.claude/skills/**` および `.claude/rules/**` の一部の可能性があります (要個別検証)。

---

## CODEX: インストール経路と hook の GUI trust

CODEX ホストでは bootstrap が以下を生成します（Claude の `.claude/` 配下に相当する Codex ネイティブ配置）：

| 配置 | 内容 |
|------|------|
| `AGENTS.md`（ルート） | 最小コア（identity / character / 起動契約）。32 KiB 上限内。rules 全体はここに inline せず、SessionStart hook が注入します |
| `.agents/skills/<name>/SKILL.md` | skill 本体。**trust 不要**で `description` マッチにより自動発火（実機検証済み #1502） |
| `.codex/hooks/*.ps1`・`*.sh` | hook 本体。`.ps1` が Windows ネイティブの主経路、`.sh` が POSIX フォールバック |
| `.codex/hooks.json` | hook 登録ファイル。絶対パスで `.codex/hooks/*` を指す（Codex には `$CLAUDE_PROJECT_DIR` 相当が無いため） |
| `.codex/agents/*.toml` | subagent（Codex "agents"）定義。brake-2 の `l1-gate-eval` は全 skill を無効化する enumeration を bootstrap が埋めます |
| `.codex/state/` | cold-start diff-only 出力の state。gitignore 同梱 |

### hook の一度きり GUI trust（Codex 固有の摩擦）

Claude の hook と違い、**Codex の hook は実行前に一度だけ GUI で trust が必要**です（実機検証済み #1502）。

1. bootstrap が `.codex/hooks.json` と `.codex/hooks/*` を書いた後、**Codex App → 設定 (Settings) → フック (Hooks) → 当該プロジェクトの行 → 信頼する (trust)** をトグルします。
   - CLI の `/hooks` コマンドは **Codex App には存在しません**。trust は GUI 専用です。
2. trust は **hook の内容ハッシュ単位**です。Li+ の build 更新で hook 本体が変わる（tag bump で `*.ps1` / `*.sh` が再生成される）たびに、Codex は **再度 trust を要求**します。build 更新のたびに再 trust してください。
3. trust 前は hook は走らず、ログも書かれません（＝発見失敗ではなく trust ゲートでの停止）。skill は trust ゲートの影響を受けません（trust 不要で発火）。

trust が無いと SessionStart の rules 注入と毎ターンの Trigger Check Gate 再注入が無音で何もしません＝Codex 上の Li+「常時オン」挙動の硬い前提条件です。

### `.ps1` のバイト忠実コピー

`.codex/hooks/*.ps1` は **BOM 付き UTF-8**（先頭 3 バイト `EF BB BF`）です。これを呼び出す Windows PowerShell 5.1 は BOM 無しの非 ASCII `.ps1` を誤読するため、bootstrap は BOM を含めてバイト単位でコピーします。リポジトリ側も `.gitattributes` の `*.ps1 -text` で clone / checkout 時の改行正規化を無効化し、BOM とバイト列を保全しています。手動でこれらを編集する場合は BOM を維持してください。

---

## 注意事項

- `GH_TOKEN` はチャットに表示されません（セキュリティ上の設計）
- `LI_PLUS_MODE=clone` の初回セッションはリポジトリのcloneのため数秒かかります
- `LI_PLUS_MODE=clone` の次回以降のセッションでは、AI が起動時に対象タグとの差分を確認し、更新があれば人間に確認します
- 作業リポジトリを持たない場合は `USER_REPO1` 以降をデフォルト値のままにしてください（または行ごと残しておけば bootstrap がスキップします）
- 設定ファイルの自動生成は初回のみ実行され、既存ファイルを上書きしません
- `LI_PLUS_BASE_LANGUAGE` と `LI_PLUS_PROJECT_LANGUAGE` は配布先workspace専用です。liplus-language 本体の日本語運用ルールとは分離されます
- `LI_PLUS_MODE=api` は軽量ですが、trigger-based re-readなどの継続機能は保証されません。継続利用には `clone` を推奨します
- local webhook fallback を使うなら `LI_PLUS_MODE=clone` を推奨します。bundled helper は `liplus-language/` clone を前提にします
- Windows環境では `python3` コマンドがMicrosoft Storeスタブになっている場合があります。hookテンプレートは `command -v` で `python3` → `python` の順にフォールバック解決します

---

## 関連ページ

- [B. Configuration](B.-Configuration) — 設定リファレンス
- [C. Update](C.-Update) — アダプター / 設定の更新同期手続き
- [1. Model](1.-Model) — Li+の中核仕様

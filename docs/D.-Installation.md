## 概要

Li+のセットアップは、ワークスペースに設定ファイルを1つ配置するだけです。
初回セッションでAIが環境を自動検出し、必要なファイルを生成します。

このページは **Quickstart** です。各設定値の詳細は [B. Configuration](B.-Configuration)、起動フローの詳細は [C. Bootstrap](C.-Bootstrap) を参照します。

`Li+config.md` は各リリースに添付されています。→ [最新リリース](https://github.com/Liplus-Project/liplus-language/releases/latest)

---

## 前提条件

- **AIエージェント環境**（Claude Code / CODEX 等）
- **GitHubアカウント**
- **GitHub Personal Access Token**（GH_TOKEN）

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
| `USER_REPOSITORY` | 作業対象のリポジトリ（例: `myname/myrepo`）。未設定のままでもOK |
| `LI_PLUS_REPOSITORY` | Li+本体のリポジトリ。デフォルト: `Liplus-Project/liplus-language`。フォーク利用時に変更 |
| `LI_PLUS_MODE` | `clone`推奨（オフライン環境でも動作する） |
| `LI_PLUS_CHANNEL` | `release`推奨（最新のプレリリースを含む） |
| `USER_REPOSITORY_EXECUTION_MODE` | `trigger`（人間主導）または`auto`（AI自律）。未設定ならセッション開始時にAIが聞いて設定 |
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
4. gh CLIをインストール（初回のみ）
5. GH_TOKENで認証
6. `LI_PLUS_CHANNEL` に対応する対象バージョンを確認
7. 既存 clone と対象バージョンがずれていれば、人間に更新するか確認
8. model/Li+core.md を読み込み（常に必須）。task/Li+issues.md は hookが無い環境のみ読み込み
9. 環境に応じた設定ファイルを自動生成

詳細な起動ステップ定義は [C. Bootstrap](C.-Bootstrap) を参照します。

| 環境 | 生成されるファイル |
|------|------------------|
| Claude Code | `{workspace_root}/.claude/CLAUDE.md` + hookファイル（adapter/claude/Li+hooks.mdから生成） |
| CODEX | `{workspace_root}/AGENTS.md` |

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

## 注意事項

- `GH_TOKEN` はチャットに表示されません（セキュリティ上の設計）
- `LI_PLUS_MODE=clone` の初回セッションはリポジトリのcloneのため数秒かかります
- `LI_PLUS_MODE=clone` の次回以降のセッションでは、AI が起動時に対象タグとの差分を確認し、更新があれば人間に確認します
- 作業リポジトリを持たない場合は `USER_REPOSITORY` をデフォルト値のままにしてください
- 設定ファイルの自動生成は初回のみ実行され、既存ファイルを上書きしません
- `LI_PLUS_BASE_LANGUAGE` と `LI_PLUS_PROJECT_LANGUAGE` は配布先workspace専用です。liplus-language 本体の日本語運用ルールとは分離されます
- `LI_PLUS_MODE=api` は軽量ですが、trigger-based re-readなどの継続機能は保証されません。継続利用には `clone` を推奨します
- local webhook fallback を使うなら `LI_PLUS_MODE=clone` を推奨します。bundled helper は `liplus-language/` clone を前提にします
- Windows環境では `python3` コマンドがMicrosoft Storeスタブになっている場合があります。hookテンプレートは `command -v` で `python3` → `python` の順にフォールバック解決します

---

## 関連ページ

- [B. Configuration](B.-Configuration) — 設定リファレンス
- [C. Bootstrap](C.-Bootstrap) — セッション起動フロー
- [1. Model](1.-Model) — Li+の中核仕様

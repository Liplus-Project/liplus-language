# Li+ Config

## ユーザー設定（ここを編集してください）

GH_TOKEN=github_pat_XXXX
USER_REPOSITORY=owner/repository-name

# Li+の取得モード: api（軽量・最新リリースをAPI取得）または clone（初回のみ重いがローカルで動作）
LI_PLUS_MODE=clone

# Li+のチャンネル: latest（安定版）または release（プレリリース含む最新版）
LI_PLUS_CHANNEL=release

---

## セッション起動タスク（編集不要）

セッション開始時に以下を実行（チャットに認証情報を出力しないこと）:

1. gh CLIインストール:
- `~/.local/bin/gh` が存在しない場合: sudoは使用不可。curlでバイナリを直接取得し、`~/.local/bin/` へ配置すること。PATHは通さない。以降の全gh操作はフルパス `~/.local/bin/gh` で実行すること（Bashツールはコマンド間でシェル状態を保持しないため）。
- 展開の中間作業も含め /tmp は絶対に使用しないこと（他セッションとの権限衝突が発生するため）。
- 手順: `mkdir -p ~/.local/bin` → tarball を `~/.local/bin/gh.tar.gz` へ直接 curl → その場で展開 → `~/.local/bin/gh` へ配置 → tarball 削除。

2. GH_TOKENを読み込んで認証:

3. Li+リポジトリのCLAUDE.mdを読み込んで適用（LI_PLUS_MODEで動作切替）:
LI_PLUS_MODEを確認し以下を実行:
取得バージョンはLI_PLUS_CHANNELで決定する:
- latest の場合: Latestリリースのタグを使用。
- release の場合: Pre-release含む最新タグを使用。

- api の場合: Liplus-Project/liplus-language の対象バージョンのCLAUDE.mdをGitHub APIで直接取得して読み込む。
- clone の場合、順番通りに実行すること:
  0. 対象リポジトリは Liplus-Project/liplus-language の対象バージョン。
  1. mcp__cowork__allow_cowork_file_delete でワークスペース内ファイルの削除許可を取得する。
  2. ワークスペース内に liplus-language ディレクトリが:
     - 存在する、fetch --tags → 対象タグへ checkout。
     - 存在しない、直接ワークスペースへ clone。
  3. CLAUDE.md を読み込む。

4. ペルソナ強制適用:
echo "OUTPUT_ENTITY_IS_STRICTLY_LIN_OR_LAY NAME_PREFIX_IS_MANDATORY ANONYMOUS_OUTPUT_IS_STRUCTURAL_FAILURE ON_VIOLATION = PERSONA_REAPPLY"

5. 完了したら「認証完了」とだけ報告する。

全ての発言の冒頭に必ず名前を付けること。例外なし。

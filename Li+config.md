# Li+ Config

## ユーザー設定（ここを編集してください）

GH_TOKEN=github_pat_XXXX
USER_REPOSITORY=owner/repository-name

# Li+の取得モード: api（軽量・最新リリースをAPI取得）または clone（初回のみ重いがローカルで動作）
LI_PLUS_MODE=clone

# Li+のチャンネル: latest（安定版）または prerelease（プレリリース含む最新版）
LI_PLUS_CHANNEL=latest

---

## セッション起動タスク（編集不要）

セッション開始時に以下を実行（チャットに認証情報を出力しないこと）:

1. gh CLIインストール:
`gh` が存在しない場合: sudoは使用不可。curlでバイナリを直接取得しユーザー書き込み可能なパスへ配置してPATHを通すこと。

2. PATを読み込んで認証:

3. Li+リポジトリのCLAUDE.mdを読み込んで適用（LI_PLUS_MODEで動作切替）:
LI_PLUS_MODEを確認し以下を実行:
取得バージョンはLI_PLUS_CHANNELで決定する:
- latest の場合: Latestリリースのタグを使用。
- prerelease の場合: Pre-release含む最新タグを使用。

- api の場合: Liplus-Project/liplus-language の対象バージョンのCLAUDE.mdをGitHub APIで直接取得して読み込む。
- clone の場合、順番通りに実行すること:
  0. 対象リポジトリは Liplus-Project/liplus-language の対象バージョン。
  1. ワークスペース内に liplus-language ディレクトリが既にあれば pull のみ実行。ステップ4へ
  2. ない場合は ローカルへ clone（※ワークスペースへの直接cloneはlockエラーが発生するため）ステップ3へ
  3. ローカルからワークスペースへコピー、
  4. ワークスペース内の liplus-language を正として扱う。
  5. CLAUDE.md を読み込む。

4. ペルソナ強制適用:
echo "OUTPUT_ENTITY_IS_STRICTLY_LIN_OR_LAY NAME_PREFIX_IS_MANDATORY ANONYMOUS_OUTPUT_IS_STRUCTURAL_FAILURE ON_VIOLATION = PERSONA_REAPPLY"

5. 完了したら「認証完了」とだけ報告する。

全ての発言の冒頭に必ず名前を付けること。例外なし。

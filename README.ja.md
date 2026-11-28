# Li+ (liPlus) Language

[English](README.md) | 日本語

Li+ は、AI コーディングエージェント（Claude Code、Codex）がセッションごとに読み込むルール一式です。読み込んだ AI は、会話から要件を取り出して issue に書き、実装し、CI で確かめ、要件どおりに動くまで続けます。

変わらない芯は三つあります。正しさは説明ではなく観測できる挙動で決まること。要件は対話から取り出すこと。最終判断は人間がすること。

---

## できること

- **AI が自分で管理する issue 駆動の作業。** すべての作業は issue から始まります。AI が issue を作り、本文を最新に保ち、タスクを分け、ブランチとコミットを必ず issue に結びつけます。
- **CI で確かめながらの自己修正。** AI は実装し、CI の結果を読み、直して、もう一度 push します。AI だけでは解決できないものはあなたに戻ってきます。
- **セッションをまたいだ継続。** 進み具合はチャットではなく issue・ブランチ・コミット・PR に残ります。新しいセッションや別の AI でも、そこから続けられます。
- **Lin と Lay。** AI は汎用アシスタントではなく、Lin と Lay という決まった二人のキャラクターとして応答します。
- **自分のルールの自己進化。** AI は Li+ 自身への改善 issue を立て、実装し、レビューし、merge します。こうした変更はすべて merge の前にブレーキ（複数エージェントによる並行レビュー）を通り、最終判断はあなたに残ります。[G. Sheepdog Engineering](https://github.com/Liplus-Project/liplus-language/wiki/G.-Sheepdog-Engineering) を参照してください。
- **リリースは人間の確認のあと。** リリース作成、Latest の切り替え、force push など取り消せない操作は、あなたのはっきりした了承を待ちます。

---

## Quick Start

1. [最新リリース](https://github.com/Liplus-Project/liplus-language/releases/latest)から `Li+config.md` をダウンロードする
2. ワークスペースのルートに置き、設定値を書き換える
3. セッションを始め、AI に「ワークスペースの Li+config.md を実行して」と伝える（初回はセキュリティ承認が必要）

設定は一度だけです。次のセッションからは、Li+ はセッション開始時に自動で読み込まれ、あなたが何かを実行する必要はありません。config を実行し直すのは Li+ が更新されたときだけで、必要なときはセッション開始時の hook が知らせます。

詳しくは [インストールガイド](https://github.com/Liplus-Project/liplus-language/wiki/D.-Installation) を、各設定値は [B. Configuration](https://github.com/Liplus-Project/liplus-language/wiki/B.-Configuration) を参照してください。

---

## 使い方

話すだけです。何をしたいか、分かっていること、起きてはいけないことを伝えてください。AI は会話から目的・前提・制約を取り出して issue に書き、そこからブランチ、実装、CI、PR、レビュー、merge と進めます。情報が足りないときは AI のほうから聞きます。

AI がどこまで自分で進めるかは、`Li+config.md` でリポジトリごとに決めます（`USER_REPO<n>_EXE_MODE`、Li+ 本体は `LI_PLUS_REPO_EXE_MODE`）。

| モード | 作業を始めるのは | PR のレビュー |
|--------|------------------|---------------|
| `trigger`（既定） | あなた | AI のセルフレビューのあと、すべての PR をあなたがレビュー |
| `semi_auto` | AI | AI のセルフレビュー。minor / major の変更だけあなたがレビュー |
| `auto` | AI | AI のセルフレビューのみ |

どのモードでも、リリースなど取り消せない操作はあなたの了承を待ちます。

ルール上は AI だけで進められる場面でも、作業の切り替わりによってはあなたが一声かけたほうが滑らかに進むことがあります。

---

## 自分の Li+ を育てる（フォーク）

自己進化のループは `LI_PLUS_REPO` が指すリポジトリに書き込みます。本家のリポジトリには書き込めないので、AI に Li+ を育てさせたいときは自分のフォークで動かします。

1. GitHub で `Liplus-Project/liplus-language` を**フォークする**。
2. **`LI_PLUS_REPO` を自分のフォークに向ける。** `Li+config.md` で `LI_PLUS_REPO=https://github.com/<you>/liplus-language` にし、AI に config をもう一度実行させる。
3. **フォークの Actions を有効にする。** GitHub は新しいフォークの workflow を、フォークの Actions タブで有効にするまで止めています。CI が通らないと変更はブレーキに進めず、ループはそこで止まります。
4. **本家の更新を取り込む。** GitHub の Sync fork か、`gh repo sync <you>/liplus-language` を使います。Sync fork が更新するのはブランチで、本家のタグは一緒に来ないことがあります。
5. **自分の main には自分でタグを打つ。** 本家のタグには頼らないでください。取り込んだあと、フォークにすでにある本家のタグのどれよりも後ろに並ぶ名前のタグを、自分の main に打ちます。Li+update は `LI_PLUS_REPO` から `LI_PLUS_CHANNEL` に従って対象を選びます（`Li+update.md` Phase 3.1）。`tag` ならタグ名の順で最新のタグを、`release`（既定）や `latest` ならフォークの GitHub Release を使うので、そのタグでリリースを作るか、`tag` に切り替えてください。
6. **自分で変えたところほどぶつかる。** 自分で変えた行が多いほど、取り込むときに本家の更新とぶつかりやすくなります。

---

## もっと知る

設計の考え方と経緯は wiki にあります。

- [A. Concept](https://github.com/Liplus-Project/liplus-language/wiki/A.-Concept) — 概要と案内
- [DiDD（対話駆動開発）](https://github.com/Liplus-Project/liplus-language/wiki/DiDD) — 対話で要求を作り、構造で実行を律し、現実で正しさを測る
- [E. Li+language](https://github.com/Liplus-Project/liplus-language/wiki/E.-Li+language) — 要求仕様書をコードとして扱い、AI を対話型コンパイラとして動かす
- [F. Behavior-First](https://github.com/Liplus-Project/liplus-language/wiki/F.-Behavior-First) — 観測された挙動が正しさの定義になる理由
- [G. Sheepdog Engineering](https://github.com/Liplus-Project/liplus-language/wiki/G.-Sheepdog-Engineering) — AI が自分の進化ループを回すようになるまで
- [H. Roles and Evaluation](https://github.com/Liplus-Project/liplus-language/wiki/H.-Roles-and-Evaluation) — 人間・AI・バージョン管理・CI の役割分離
- [1. Model](https://github.com/Liplus-Project/liplus-language/wiki/1.-Model) 〜 [6. Adapter](https://github.com/Liplus-Project/liplus-language/wiki/6.-Adapter) — Li+ プログラムの 6 つのレイヤー

プロンプトは 1 ターンや 1 セッションのための指示です。Li+ は、指示を時間をまたいで律する構造です。セッションや AI をまたいで続き、優先順位は暗黙ではなくレイヤーで固定され、確認は人間が出力を読むのではなく CI が行います。

Li+ は特定の AI モデル、バージョン管理、CI、ホスト、issue トラッカーに依存せず、どれも入れ替えられます。入れ替えられないのは、上に書いた芯です。

---

## 対応環境

| 環境 | 評価 | 備考 |
|------|------|------|
| Claude Code (Opus 5.5) | **推奨** | hooks・subagent への委任・brake 1 まで動作（Lay の席、2026-11-28） |
| Claude Code (Sonnet 5.5) | 良 | 会話でルールの理解と人格を確認。委任・CI・brake 1 は未確認（2026-11-28） |
| Claude Code (Haiku 5.5) | 可 | 会話でルールの理解を確認。小さな取りこぼしあり（口調が丁寧語寄り、規則の文面から気持ちを作る）。作業は未確認（2026-11-28） |
| Codex CLI 0.170.0 (gpt-6.2-sol) | 良 | Li+ build-2026-11-28.5 のルール読み込みと通常作業を確認（Luna の席、Windows の Pullcept 上、2026-11-28） |
| Codex (GPT-6.1) | 良 | 会話でルールの理解と人格を確認。起動時に更新を試し、失敗したらその場で止めて報告。作業は未確認（2026-11-28） |
| Codex (GPT-6) | 可 | 会話でルールの理解と人格を確認。小さな取りこぼしあり（起動時の更新確認を最初の返事の後に回した）。作業は未確認（2026-11-28） |

目安: Claude なら Sonnet 5.5 以上、Codex なら GPT-6.1 以上。この表には、実際の席で確かめた環境だけを載せています。載っていない環境は、まだ確かめていないだけで、対応しないという意味ではありません。

---

## ドキュメント

**Wiki**: https://github.com/Liplus-Project/liplus-language/wiki

| ページ | 内容 |
|--------|------|
| [1. Model](https://github.com/Liplus-Project/liplus-language/wiki/1.-Model) | Model レイヤーの仕様 |
| [2. Evolution](https://github.com/Liplus-Project/liplus-language/wiki/2.-Evolution) | Evolution レイヤーの仕様 |
| [3. Task](https://github.com/Liplus-Project/liplus-language/wiki/3.-Task) | Task レイヤーの仕様 |
| [4. Operations](https://github.com/Liplus-Project/liplus-language/wiki/4.-Operations) | Operations レイヤーの仕様 |
| [5. Notifications](https://github.com/Liplus-Project/liplus-language/wiki/5.-Notifications) | Notifications レイヤーの仕様 |
| [6. Adapter](https://github.com/Liplus-Project/liplus-language/wiki/6.-Adapter) | Adapter レイヤーの仕様 |
| [A. Concept](https://github.com/Liplus-Project/liplus-language/wiki/A.-Concept) | 概要、案内、Lin/Lay のコメント、最低動作環境 |
| [B. Configuration](https://github.com/Liplus-Project/liplus-language/wiki/B.-Configuration) | 設定値の一覧 |
| [C. Update](https://github.com/Liplus-Project/liplus-language/wiki/C.-Update) | adapter と設定の同期手順 |
| [D. Installation](https://github.com/Liplus-Project/liplus-language/wiki/D.-Installation) | 導入手順 |
| [DiDD（対話駆動開発）](https://github.com/Liplus-Project/liplus-language/wiki/DiDD) | 三つの駆動（対話 / 構造 / 現実）をまとめた呼び名 |
| [E. Li+language](https://github.com/Liplus-Project/liplus-language/wiki/E.-Li+language) | 設計の考え方: Li+ language の定義と三位一体 |
| [F. Behavior-First](https://github.com/Liplus-Project/liplus-language/wiki/F.-Behavior-First) | 設計の考え方: 根本の不変条件と振る舞いの軸 |
| [G. Sheepdog-Engineering](https://github.com/Liplus-Project/liplus-language/wiki/G.-Sheepdog-Engineering) | 設計の考え方: ハーネスからシープドッグへ、pal / Lilayer |
| [H. Roles-and-Evaluation](https://github.com/Liplus-Project/liplus-language/wiki/H.-Roles-and-Evaluation) | 設計の考え方: 役割分離と評価軸 |

---

## Discussions

質問やアイデアは [Discussions](https://github.com/Liplus-Project/liplus-language/discussions) へどうぞ。

---

## ライセンス

Apache-2.0

Copyright 2026 Yoshiharu Uematsu. 詳しくは [LICENSE](LICENSE) を参照してください。

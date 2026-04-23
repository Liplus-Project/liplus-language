# GitHub App の User-to-server token expiration 地雷と Opt-out 判断

## 背景

2026-04-23、`mcp__GitHub_RAG_MCP__get_doc_content` が HTTP 401 `Bad credentials` を返す事象が発生した。同一セッション内で `mcp__GitHub_RAG_MCP__search_issues` は正常動作し、`gh api` (ユーザー keyring の gh auth 経由) も問題なく通っていたため、当初は症状の非対称性から原因特定が遅れた。

最終的に真因は `liplus-rag-mcp` GitHub App の Optional feature「User-to-server token expiration」が有効化されていたことに起因する stale token 問題と判明した。本記録は同種の調査を繰り返さないための判断固定である。

---

## 観測と非対称性の落とし穴

| tool | 呼び出し結果 | GitHub API への依存 |
|---|---|---|
| `search_issues` | 正常 | 依存なし (Vectorize + DB_FTS の内部ストアのみ参照) |
| `get_doc_content` | 401 `Bad credentials` | あり (GitHub REST `/repos/{repo}/contents/{path}` を `this.props.accessToken` で叩く) |
| `gh api` (ユーザー端末) | 正常 | あり (別経路の PAT を使用) |

**非対称性の真相：** `search_issues` は GitHub API を一切呼ばない。Vectorize と DB_FTS の内部インデックスを検索するだけなので、この tool が成功しても token の健全性は何も証明しない。token に問題があるかどうかは `get_doc_content` 系 (GitHub API を叩く tool) でしか観測できない。

「片方の MCP tool が通るから token は無事」という推論は構造的に誤り。**MCP tool が内部 tool か外部 API 依存 tool かを切り分けずに健全性を推論してはならない。**

---

## 仮説の切り分け

3 本の仮説を立て、diagnostic log と実機確認で絞り込んだ。

| 仮説 | 検証 | 結果 |
|---|---|---|
| A. OAuth scope 不足 | レスポンスヘッダ確認 | `x-oauth-scopes` が null。scope 不足なら scope 文字列が返るはず。null は「token 自体が認識されていない」サイン → 却下 |
| B. props 伝播失敗 (proxy → Worker DO) | diagnostic log 追加 (`github-rag-mcp#99`) | `props=present, propKeys=[githubUserId, githubLogin, accessToken]` が確認できた → 却下 |
| C. token が stale / expired | token 形状確認 (`ghu_` prefix + 40 文字) | GitHub App の user-to-server token 形式。GitHub 側が `Bad credentials` を返している → 確定 |

`ghu_` prefix は GitHub App 発行の user-to-server token を示す。これが期限切れなら、Worker 側保存済みの `this.props.accessToken` は更新されない限り永遠に 401 を返し続ける。

---

## 真因

`liplus-rag-mcp` GitHub App の Optional features「User-to-server token expiration」が有効化されていた。これにより：

- user-to-server token (`ghu_`) は発行から 8 時間で失効
- 同時に refresh_token が発行されるが、Worker 側の MCP 実装では refresh_token 交換フローが未実装
- 結果、8 時間経過後は保存済み `this.props.accessToken` が stale になり、GitHub API を叩く全 tool が 401 を返す

ユーザー体験上は「毎日最初のセッションで get_doc_content が落ちる → 再認証」という地雷として現れていた。

---

## 修正判断：Opt-out を選択

選択肢は 2 つ。

### 採用案：User-to-server token expiration を Opt-out

- GitHub App 側の Optional features を無効化する
- token は無期限 (ユーザーが明示的に revoke するまで有効) となる
- Worker 側のコード変更は不要
- 既に失効していた保存済み token を置き換えるため、クライアント (Claude Desktop Connectors) で 1 度だけ再認証が必要

### 却下案：Worker 側で refresh_token 交換フローを実装

- 8 時間ごとに自動で token をリフレッシュする
- security 境界を維持できる (失効漏れ token が 8 時間で無効化される)
- 実装工数が大きく、Cloudflare Workers / MCP SDK に組み込みの helper が無い

**採用理由：** 本 RAG MCP は個人利用 (single-tenant) であり、token 無期限のリスク (漏洩時の被害が時間で減衰しない) は許容範囲。Opt-out は設定変更のみで工数ゼロ、security/工数トレードオフで patch 側 (Opt-out) を選択した。

---

## 再検討条件 (reopen criteria)

以下のいずれかが成立したとき、refresh_token 交換フロー実装を再検討する：

- RAG MCP が非信頼ユーザーにも開かれる (multi-tenant 化) とき。漏洩時の blast radius が拡大し、token 無期限リスクが許容できなくなる
- GitHub App が現在より sensitive な scope を追加し、access token 自体の価値が上がったとき
- Cloudflare / MCP SDK 側に refresh_token 交換の built-in helper が提供され、実装工数が小さくなったとき

---

## 副次的な知見：Observability が真因特定を加速した

診断ログ PR (`github-rag-mcp#99`、merged 2026-04-23) と Cloudflare ダッシュボード側の Workers Observability 有効化により、ログが出始めた後は 1 分以内に真因が可視化された。Observability はそれまで無効化されており、有効化することで props の到達状況・token の prefix 形状といった「ログが無ければ絶対に切り分け不能な事実」が literal に取れるようになった。

教訓：Worker 側で 401 が出る系の MCP は、先に Observability を有効化してからでないと仮説切り分けが空回りする。`wrangler.toml` への反映は別 follow-up で扱う。

---

## 関連

- 診断 issue / PR：[Liplus-Project/github-rag-mcp#98](https://github.com/Liplus-Project/github-rag-mcp/issues/98), [PR #99](https://github.com/Liplus-Project/github-rag-mcp/pull/99)
- 本記録の issue：[Liplus-Project/liplus-language#1161](https://github.com/Liplus-Project/liplus-language/issues/1161)
- GitHub App 公式 doc の参照キーワード：「Expiring user access tokens」「User-to-server OAuth access tokens」

---

## メンテナンス

この判断記録は、以下の場合に削除する：

- refresh_token 交換フローが Worker 側に実装され、User-to-server token expiration を再 Opt-in しても運用が回るようになったとき
- GitHub App 側の Optional features 仕様が根本的に変わり、本記録の前提 (8 時間失効・refresh_token 提供) が無効になったとき
- RAG MCP の認証方式が GitHub App から別方式 (PAT 固定 / OAuth App / サービスアカウント等) に切り替わり、本記録が歴史的参照にも使われなくなったとき

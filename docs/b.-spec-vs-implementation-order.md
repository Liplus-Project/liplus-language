# spec-reality gap を避ける：spec vs implementation の順序

## 背景

2026-04-19 に「**literal 確認せずに claim / 推論する**」パターンが同日 7 回観測された。当初 3 件は自分の発言 (spec claim) 起点、中盤 3 件は外部情報源の oracle 扱いへの拡張、最終 1 件は外部システムの**数値制限 (quota / limit)** を verify せず設計した事例。

### 観測事例

| # | 場所 | 誤った claim / 推論 | 実態 |
|---|------|-------------|------|
| 1 | `operations/Li+github.md` [PR Creation] | 「`Refs` triggers GitHub auto-close on merge」 | GitHub の close キーワードは `close/closes/closed/fix/fixes/fixed/resolve/resolves/resolved` のみ。`Refs` は close キーワードではない。PR #1066 merge で sub-issue 9 件が OPEN 残存して顕在化 |
| 2 | `task/Li+issues.md` Research Strategy | 「github-rag-mcp は commit diff surface を持つ」 | 当時 github-rag-mcp は `path.endsWith(".md")` のみで commit diff indexing は未実装。PR #1069 を close して実装 #80/#81 を先行させ、その後 #1056/#1070 で spec を実体反映 |
| 3 | 自己評価 #02 (self-evaluation_log) | `git log --all -- '**/momeri*'` の null 結果から「存在しない」と断定 | glob pathspec `**/` prefix が root 直下ファイルを除外する仕様を未検証。実際は `momeri.pal` が root 直下に存在した |
| 4 | subagent research report | 「Poller doc 経路: 専用実装がない」という subagent の要約を literal 検証せず信じた | `src/poller.ts:599` に `pollDocs()` が存在。cron 経由で docs が毎時 index されていた |
| 5 | 診断推論 | 「diff index が動かない = webhook 設定が必要」と推論 | 実際は orphan webhook の残骸が認証ループで 403 を生んでいただけ。削除＋再設定で解決。webhook 未配線が問題の本質ではなかった |
| 6 | 診断推論 | repo-level webhook 配線前提で 403 原因を推論 | Liplus-Project org は **GitHub Apps 経由** の webhook delivery。repo Webhooks 欄は空で、App 層が別軸で配信。この layer の存在を確認せず推論を進めた |
| 7 | `Liplus-Project/github-rag-mcp#80/#81` の Vector ID scheme 設計 | `{repo}#commit-{sha}#file-{base64url(path)}` ≈ 130 bytes、docs side の `{repo}#doc-{path}` も path 次第で 74 bytes | Cloudflare Vectorize の ID 上限 **64 bytes** を literal 確認せず設計。`PR #1075` 実機 merge で `VECTOR_UPSERT_ERROR (code = 40008): id too long; max is 64 bytes, got 74 bytes` として露出。`Liplus-Project/github-rag-mcp#83/PR #84` で SHA-256 hash 固定 46 bytes 方式に修正 |

## 判断ルール

**spec / 推論 が外部システムの capability や状態を claim する時は、その capability が literal に存在・動作していることを確認する。**

- 「X が可能である」式の claim は現在形で書く前に、X を実機で call した結果を確認する
- verification 対象は自然言語の記述ではなく、該当システムの実行結果 / 実装コード / 公式 docs のどれか
- 主観的 confident 感は verification の代替にならない（self-evaluation_log 2026-04-19 #01/#02 参照）
- **外部情報源も自分の発言と同等に扱う**: subagent の research report、過去 session の記録、config の残留状態を「事実」として無検証に使わない。必要なら現在の実装 / 現在の config を直接読む
- **複数 layer の可能性を網羅する**: 特に GitHub 系 integration は repo-level webhook / org-level webhook / GitHub App の 3 layer が独立に存在しうる。1 layer だけ見て「設定されてない」と結論しない
- **数値制限・quota も同列に verify する**: ID 長、file size、rate limit、timeout、request/response サイズ等、外部システムが課す数値上限は API spec や実機 error から先に確認する。実装過程で出る `code = NNNN` 形式のエラーは貴重な literal 事実として Observability で捕捉する

## 適用順序

cross-system の spec 変更（Li+ spec が github-rag-mcp / GitHub / Cloudflare 等の外部挙動を参照する場合）には、以下の順序で進める：

1. **外部システム側の実装 or 挙動確認**を先に完了させる
2. 実装が deployed された後に、Li+ spec を**実体反映**する形で書く
3. spec 側で「将来のデプロイ予定 capability」を現在形 declare するのは禁止

例外：
- planned / not-yet-deployed を明示的にマーカー付き（「計画段階」「デプロイ未了」等）で記述する場合は許容
- ただしマーカーが剥がれるタイミング（capability が deployed された時点）に合わせて spec を現在形へ更新するタスクを連動させる

## 検知サイン

以下の場合、この判断ルールが effective：

- Li+ spec が `github-rag-mcp`, `GitHub`, `Cloudflare`, `Workers AI` 等の外部サービス挙動を断言する行を追加する
- external tool の出力フォーマットや特定 API の存在を仕様に書く
- 「X is supported」「Y triggers Z」のような claim を spec に加える

## 反例（この判断ルールが不要な場面）

- Li+ 内部仕様の追加（core/task/operations の relational ルール定義）
- 抽象的な philosophy 記述（「外部記憶は判断を記録する」等）
- 実装独立な判断ルール形式（v1.12.5 型「A vs B の優先順位」）

## 関連

- 事例 1: [Liplus-Project/liplus-language#1067](https://github.com/Liplus-Project/liplus-language/issues/1067), PR #1068
- 事例 2: [Liplus-Project/liplus-language#1056](https://github.com/Liplus-Project/liplus-language/issues/1056), closed PR #1069, reopen PR #1070、実装 [Liplus-Project/github-rag-mcp#80](https://github.com/Liplus-Project/github-rag-mcp/issues/80) PR #81
- 事例 3: self-evaluation_log 2026-04-19 #02（memory、tool-output-as-oracle）

## メンテナンス

この判断記録は、以下の場合に削除する：

- Li+ spec 側で「外部システム依存箇所」を構造的に排除する仕組み（例: spec リンクチェッカーや external-reference marker mandatory 化）が整った時
- 同種パターンが 6 ヶ月以上観測されず、記録自体の参照が途絶えた時

# spec-reality gap を避ける：spec vs implementation の順序

## 背景

2026-04-19 に「**spec が外部システムの挙動や external tool の coverage を literal 確認せずに claim する**」パターンが同日 3 回観測された。

### 観測事例

| # | 場所 | 誤った claim | 実態 |
|---|------|-------------|------|
| 1 | `operations/Li+github.md` [PR Creation] | 「`Refs` triggers GitHub auto-close on merge」 | GitHub の close キーワードは `close/closes/closed/fix/fixes/fixed/resolve/resolves/resolved` のみ。`Refs` は close キーワードではない。PR #1066 merge で sub-issue 9 件が OPEN 残存して顕在化 |
| 2 | `task/Li+issues.md` Research Strategy | 「github-rag-mcp は commit diff surface を持つ」 | 当時 github-rag-mcp は `path.endsWith(".md")` のみで commit diff indexing は未実装。PR #1069 を close して実装 #80/#81 を先行させ、その後 #1056/#1070 で spec を実体反映 |
| 3 | 自己評価 #02 (self-evaluation_log) | `git log --all -- '**/momeri*'` の null 結果から「存在しない」と断定 | glob pathspec `**/` prefix が root 直下ファイルを除外する仕様を未検証。実際は `momeri.pal` が root 直下に存在した |

## 判断ルール

**spec が外部システムの capability を claim する時は、その capability が deployed されていることを literal 確認する。**

- 「X が可能である」式の claim は現在形で書く前に、X を実機で call した結果を確認する
- verification 対象は自然言語の記述ではなく、該当システムの実行結果 / 実装コード / 公式 docs のどれか
- 主観的 confident 感は verification の代替にならない（self-evaluation_log 2026-04-19 #01/#02 参照）

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

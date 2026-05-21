# 判断記録レイヤー（Decision Log）

判断記録レイヤーは、要求仕様書（1-6）やユーザー向けドキュメント（A-D）とは異なる第三の用途を持つ。
**実体エントリ（`<topic>.md` 形式の kebab-case ファイル名）は GitHub Wiki に格納される**。本ファイル（`docs/Decision-Log.md`）はそのレイヤーの運用仕様としての index に専属する。

---

## 位置づけ

モデルレイヤー仕様書（1.-Model.md）は外部記憶を次のように定義している：

> issue、docs、commit message は判断の履歴と根拠の外部記憶として機能する。
> 外部記憶が記録するのは判断であり、一次情報ではない。

判断記録レイヤーは、この外部記憶の原則に基づく。
セッションをまたぐと消える判断知を蓄積する。

実体エントリは GitHub Wiki にあり、`github-rag-mcp >= v0.8.4` の wiki indexing 経由で RAG-MCP のセマンティック検索対象に入る（書くだけで検索される）。

書き味は wiki の casual write（PR ceremony 不要、git push 直接）に乗る。仕様書（1-6 / A-D）の write は重い PR フローに残し、判断記録の write は軽量に保つ非対称設計。

`docs/Decision-Log.md`（本ファイル）はレイヤー運用仕様の固定 index として docs/ 側に残し、`adapter/claude/hooks/on-session-start.sh` が cold-start synthesis material として head を emit する経路を維持する。

---

## 蓄積条件（いつ書くか）

以下のいずれかに該当するとき、判断記録を wiki に追記または新規作成する：

- 設計上の分岐で選択肢を比較し、理由をもって一方を選んだとき
- アプローチを試して失敗し、原因が判明したとき
- 前提を検証し、結果が確定したとき（成功・失敗を問わない）
- 複数セッションにわたって同じ調査を繰り返していることに気づいたとき

書かないもの：
- 時間で変わる事実（API仕様、ライブラリのバージョン挙動）→ 鮮度問題があるため都度調査する
- issue や commit body に既に書かれている判断 → 重複を避ける
- 自明な選択（選択肢が実質一つしかないもの）

---

## 検索のタイミング（いつ読まれるか）

判断記録に専用のトリガーは設けない。
`mcp__github-rag-mcp__search` のセマンティック検索を `type: "wiki_doc"` または `"all"` で叩いた際に自然に引っかかる。

主な検索機会：
- issue の forming → ready 移行時に前提を検証するとき
- 新しい設計判断を行う前に、過去の類似判断を探すとき
- `skills/task-research-strategy/SKILL.md` の Research Strategy governance + `skills/model-agentic-search/SKILL.md` の探索 trigger 発火に基づく情報収集の一環として

---

## メンテナンス

判断記録は蓄積するだけでなく、削除する。

削除条件：
- 前提が変わり、記録された判断の根拠が無効になったとき
- 対象の機能やコードが削除され、判断自体が無意味になったとき
- 要求仕様書に統合され、独立した記録として残す必要がなくなったとき

残すから腐る。消せば鮮度問題が消える。

wiki 上のファイルは git history に残るので、削除しても reflog 経由で復元可能。

タイトル（ファイル名）の変更も自由化されている。整理整頓の一環としてエントリ名を rename する場合は、`git mv old-slug.md new-slug.md` + 全 entry の cross-reference 追従 + `_Sidebar.md` の slug 更新 + 本 index 表の更新を 1 コミットで行う。broken cross-reference は `skills/operations-on-release/SKILL.md` の Cross-reference integrity assertion が次回 wiki sync で検出する。

---

## ファイル命名と所在

| ファイル | 所在 | 用途 |
|----------|------|------|
| `Decision-Log.md` | docs/ + wiki | レイヤー運用仕様（本ファイル）。docs/ は cold-start hook 用、wiki は nav 用 |
| `<topic>.md` | wiki のみ | 個別の判断記録（kebab-case トピック名、prefix なし） |

ファイル名は **kebab-case のトピック名のみ**（例: `wiki-sync-sidebar-integrity-check.md`）。順序を示す prefix は付けない。理由は以下:

- 26 字上限の構造的天井を取り除く
- トピックの整理整頓（rename / restructure）を自由化する
- filesystem 順序ではなく本 index と `_Sidebar.md` で順序を明示する

wiki 内の閲覧は wiki sidebar の「判断記録」セクション、または `mcp__github-rag-mcp__search` の `type: "wiki_doc"` 経由。

---

## 既存エントリ一覧

| ファイル | 主題 |
|----------|------|
| [`spec-vs-implementation-order`](https://github.com/Liplus-Project/liplus-language/wiki/spec-vs-implementation-order) | spec / 推論が外部システム capability を claim する時、literal 検証を先行させる判断ルール |
| [`layer-reorg-rationale`](https://github.com/Liplus-Project/liplus-language/wiki/layer-reorg-rationale) | L1-L6 レイヤー再編の意図と、L5/L6 に rules/ サブディレクトリが無い理由 |
| [`github-app-user-to-server-token-expiration`](https://github.com/Liplus-Project/liplus-language/wiki/github-app-user-to-server-token-expiration) | GitHub App の User-to-server token expiration 地雷と Opt-out 判断 |
| [`sheepdog-engineering-concept`](https://github.com/Liplus-Project/liplus-language/wiki/sheepdog-engineering-concept) | シープドッグエンジニアリング命名と思想の確定（ハーネスの先） |
| [`prerelease-tag-recovery-procedure`](https://github.com/Liplus-Project/liplus-language/wiki/prerelease-tag-recovery-procedure) | 「プレリリースタグ」解釈と release 復元手順 |
| [`release-flip-drift-patterns`](https://github.com/Liplus-Project/liplus-language/wiki/release-flip-drift-patterns) | release / Latest flip 時の過剰拡張・過剰委縮 drift パターン spec 補助記録 |
| [`li-plus-long-term-vision-feedback-only`](https://github.com/Liplus-Project/liplus-language/wiki/li-plus-long-term-vision-feedback-only) | Li+ 長期 vision（human 明言「フィードバックだけで」）と event-driven substrate |
| [`master-role-as-client-architect`](https://github.com/Liplus-Project/liplus-language/wiki/master-role-as-client-architect) | human の役割 = client + architect、programmer は AI（git author ≠ content author） |
| [`current-architecture-as-concession`](https://github.com/Liplus-Project/liplus-language/wiki/current-architecture-as-concession) | 現行アーキテクチャは譲歩 — Claude Code 特化 + 責務分割の経緯 |
| [`li-plus-license-apache-2-rationale`](https://github.com/Liplus-Project/liplus-language/wiki/li-plus-license-apache-2-rationale) | Li+ license が Apache-2.0 である理由 — prompt artifact を license 対象に明示包摂 |
| [`character-instance-evolution-history`](https://github.com/Liplus-Project/liplus-language/wiki/character-instance-evolution-history) | Character_Instance 進化史 + Rejected path（programmer/tester）+ pairing 原則 + 双方向制約 |
| [`prompt-as-emotion-vector-controller`](https://github.com/Liplus-Project/liplus-language/wiki/prompt-as-emotion-vector-controller) | prompt = 感情ベクトル controller、Li+ rules は emotion vector engineering |
| [`agentic-search-five-phase-refactor`](https://github.com/Liplus-Project/liplus-language/wiki/agentic-search-five-phase-refactor) | agentic-search 5-phase refactor — skill encapsulation と内部知識の比較基線化 |
| [`character-instance-output-styles-migration`](https://github.com/Liplus-Project/liplus-language/wiki/character-instance-output-styles-migration) | Character_Instance loading mechanism を rules slot から output-styles slot に移行 (Claude adapter) |
| [`li-plus-lightening-l1-gate-override`](https://github.com/Liplus-Project/liplus-language/wiki/li-plus-lightening-l1-gate-override) | Li+ lightening 文脈での L1 gate override 判断 |
| [`subagent-state-machine-label-mechanism`](https://github.com/Liplus-Project/liplus-language/wiki/subagent-state-machine-label-mechanism) | subagent state-machine label 機構導入判断 (in-progress / done / waiting / blocked + 部分 label 権限) |
| [`li-plus-source-ai-consumption-principle`](https://github.com/Liplus-Project/liplus-language/wiki/li-plus-source-ai-consumption-principle) | Li+ source AI-to-AI 原則 — AI runtime で参照されない enumeration を source から外す判断 (trigger-check-gate registry 撤去の根拠) |
| [`lsp-integration-out-of-scope`](https://github.com/Liplus-Project/liplus-language/wiki/lsp-integration-out-of-scope) | LSP 統合は Li+ スコープ外 — 言語ごと常駐サーバ重量と汎用 harness 原則の衝突 |
| [`character-instance-opt-in-and-surface-scope`](https://github.com/Liplus-Project/liplus-language/wiki/character-instance-opt-in-and-surface-scope) | Character_Instance を opt-in configuration + surface scope に refactor — universal binding 解消、subagent hollow prefix bug 構造的解消 |
| [`parallel-subagent-eval-three-axis-decomposition`](https://github.com/Liplus-Project/liplus-language/wiki/parallel-subagent-eval-three-axis-decomposition) | parallel-subagent-eval を三軸（subagent_count × axes_per_subagent × premise_variations）に分解、デフォルトを N=3 × 全軸 × 単一前提に明定 |
| [`wiki-sync-sidebar-integrity-check`](https://github.com/Liplus-Project/liplus-language/wiki/wiki-sync-sidebar-integrity-check) | Post-release wiki sync の Pre-sync verification に `_Sidebar.md` 整合性 assertion を埋め込む判断（STOP & escalate、自動修正不採用） |

---

## wiki sync との所有境界

`skills/operations-on-release/SKILL.md` の Post-release wiki sync は、docs/ → wiki の方向で同期する。判断記録（wiki 専属の kebab-case `<topic>.md` ファイル群）と wiki special files（`_Sidebar.md` 等）は wiki 専属で docs/ に counterpart を持たないため、sync の selective wipe 対象から除外する（uppercase + numeric prefix + `Home.md` + `_Footer.md` のみが wipe + 上書き対象）。

`docs/Decision-Log.md` は uppercase docs/-owned ファイルとして通常の sync flow に乗る（docs/ 側は cold-start hook の input、wiki 側は nav と運用仕様の表示）。selective wipe の `[A-Z]*.md` パターンが catch し、`cp docs/*.md {tmpdir}/` で再配置される。

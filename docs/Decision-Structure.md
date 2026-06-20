# 判断構造レイヤー（Decision Structure）

判断構造レイヤーは、要求仕様書（1-6）やユーザー向けドキュメント（A-D）とは異なる第三の用途を持つ。
**実体エントリ（`<topic>.md` 形式の kebab-case ファイル名）は GitHub Wiki に格納される**。本ファイル（`docs/Decision-Structure.md`）はそのレイヤーの運用仕様としての index に専属する。

---

## 位置づけ

モデルレイヤー仕様書（1.-Model.md）は外部記憶を次のように定義している：

> issue、docs、commit message は判断の履歴と根拠の外部記憶として機能する。
> 外部記憶が記録するのは判断であり、一次情報ではない。

判断構造レイヤーは、この外部記憶の原則に基づく。
セッションをまたぐと消える判断知を蓄積する。

**履歴 (log) ではなく構造 (structure) である**: Decision Structure は時間順 append-only の log ではない。判断ノード (state 形エントリ) と supersede / depend / conflict edge による意味グラフであり、volume は refine / replace で安定する。維持運用は refactor (normal operation) として扱う。

実体エントリは GitHub Wiki にあり、`github-rag-mcp >= v0.8.5` の wiki indexing 経由で RAG-MCP のセマンティック検索対象に入る（書くだけで検索される）。

書き味は wiki の casual write（PR ceremony 不要、git push 直接）に乗る。仕様書（1-6 / A-D）の write は重い PR フローに残し、判断構造の write は軽量に保つ非対称設計。

`docs/Decision-Structure.md`（本ファイル）はレイヤー運用仕様の固定 index として docs/ 側に残し、`adapter/claude/hooks/on-session-start.sh` が cold-start synthesis material として head を emit する経路を維持する。

---

## 蓄積条件（いつ書くか）

以下のいずれかに該当するとき、判断構造を wiki に追記または新規作成する：

- 設計上の分岐で選択肢を比較し、理由をもって一方を選んだとき
- アプローチを試して失敗し、原因が判明したとき
- 前提を検証し、結果が確定したとき（成功・失敗を問わない）
- 複数セッションにわたって同じ調査を繰り返していることに気づいたとき

書かないもの：
- 時間で変わる事実（API仕様、ライブラリのバージョン挙動）→ 鮮度問題があるため都度調査する
- issue や commit body に既に書かれている判断 → 重複を避ける
- 自明な選択（選択肢が実質一つしかないもの）

---

## エントリ shape (state-form 推奨)

新規エントリは state 形で記述する:

- **Question** = どの問いに対する判断か
- **Current resolution** = 現在の答え (state、現在形)
- **Edges** = supersede / depend / conflict edge の宣言

state 形は時間順 implicit ordering ではなく現在 state を主語にする。判断は時間とともに refine / replace されるため、最新 state が「今どう判断しているか」を直接表すほうが読み手に効く。詳細は `skills/evolution-decision-structure-write/SKILL.md` を参照。

既存エントリは遡及書き換えしない。新規エントリと既存 entry の意味更新時に state 形を用いる（forward guidance）。

---

## Edge taxonomy (primary edge vocabulary)

state 形エントリは適用可能な edge を declare することが推奨される。primary edge は 3 種:

- **supersedes** = この判断は別 entry の判断を置き換える。旧 entry は graph に残る（削除しない）が、検索路は最新 entry に集まる
- **depends on** = この判断は別 entry の判断を前提とする。前提が崩れた場合は本判断も再評価対象になる
- **conflicts with** = この判断は別 entry の判断と一部または全体で矛盾する。未解決の論点を可視化する surface

edge は前方リンク（本 entry から相手 entry へのリンク）として書く。逆方向のリンクは次回 wiki sync の cross-reference integrity check で整合性が観測される。

---

## 検索のタイミング（いつ読まれるか）

判断構造に専用のトリガーは設けない。
`mcp__github-rag-mcp__search` のセマンティック検索を `type: "wiki_doc"` または `"all"` で叩いた際に自然に引っかかる。

主な検索機会：

- issue の forming → ready 移行時に前提を検証するとき
- 新しい設計判断を行う前に、過去の類似判断を探すとき
- `skills/agentic-search/SKILL.md` の探索 trigger 発火 (governance + mechanical core 統合) に基づく情報収集の一環として

---

## メンテナンス (refactor framing)

判断構造は構造体である。削除や統合は「履歴を消すこと」ではなく「構造を refactor すること」として normal operation の中に位置づける。

**supersede via link を上書きより positive default として優先する**。既存 entry が無効化された場合、旧 entry を削除するのではなく新 entry を立て、旧 entry に supersede edge を張る。検索路は最新 entry に集まりつつ、graph 構造は維持される。

削除条件（条件に該当する場合のみ）：

- 前提が変わり、記録された判断の根拠が無効になったとき
- 対象の機能やコードが削除され、判断自体が無意味になったとき
- 要求仕様書に統合され、独立した記録として残す必要がなくなったとき

これらは「履歴を抹消する」ではなく「structure が更新された結果として旧ノードを撤去する」操作である。条件未充足の状態で「念のため消す」ことはしない。

wiki 上のファイルは git history に残るので、削除しても reflog 経由で復元可能。

タイトル（ファイル名）の変更も自由化されている。整理整頓の一環としてエントリ名を rename する場合は、`git mv old-slug.md new-slug.md` + 全 entry の cross-reference 追従 + `_Sidebar.md` の slug 更新 + 本 index 表の更新を 1 コミットで行う。broken cross-reference は `skills/operations-on-release/SKILL.md` の Cross-reference integrity assertion が次回 wiki sync で検出する。

---

## ファイル命名と所在

| ファイル | 所在 | 用途 |
|----------|------|------|
| `Decision-Structure.md` | docs/ + wiki | レイヤー運用仕様（本ファイル）。docs/ は cold-start hook 用、wiki は nav 用 |
| `<topic>.md` | wiki のみ | 個別の判断構造（kebab-case トピック名、prefix なし） |

ファイル名は **kebab-case のトピック名のみ**（例: `wiki-sync-sidebar-integrity-check.md`）。順序を示す prefix は付けない。理由は以下:

- 26 字上限の構造的天井を取り除く
- トピックの整理整頓（rename / restructure）を自由化する
- filesystem 順序ではなく本 index と `_Sidebar.md` で順序を明示する

wiki 内の閲覧は wiki sidebar の「判断構造」セクション、または `mcp__github-rag-mcp__search` の `type: "wiki_doc"` 経由。

---

## 既存エントリ一覧

| ファイル | 主題 |
|----------|------|
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
| [`lsp-integration-out-of-scope`](https://github.com/Liplus-Project/liplus-language/wiki/lsp-integration-out-of-scope) | LSP 統合は Li+ スコープ外 — 言語ごと常駐サーバ重量と汎用 harness 原則の衝突 |
| [`character-instance-opt-in-and-surface-scope`](https://github.com/Liplus-Project/liplus-language/wiki/character-instance-opt-in-and-surface-scope) | Character_Instance を opt-in configuration + surface scope に refactor — universal binding 解消、subagent hollow prefix bug 構造的解消 |
| [`bootstrap-walkthrough-skip-and-gh-install-relocation`](https://github.com/Liplus-Project/liplus-language/wiki/bootstrap-walkthrough-skip-and-gh-install-relocation) | bootstrap walkthrough を 3 軸 AND gate (sentinel tag / schema / language) で skip 可能化 + gh install を hook 側に移譲（context 約 4% 削減、`Li+configを実行` magic phrase で強制再走） |
| [`parallel-subagent-eval-three-axis-decomposition`](https://github.com/Liplus-Project/liplus-language/wiki/parallel-subagent-eval-three-axis-decomposition) | parallel-subagent-eval を三軸（subagent_count × axes_per_subagent × premise_variations）に分解、デフォルトを N=3 × 全軸 × 単一前提に明定 |
| [`parallel-subagent-eval-cost-acceptance`](https://github.com/Liplus-Project/liplus-language/wiki/parallel-subagent-eval-cost-acceptance) | brake 1 (parallel-subagent-eval) のコストを「予防コスト < 修復コスト」として受容する判断、業界一般のトークン量軸ではなく時間軸波及込みで評価 |
| [`wiki-sync-sidebar-integrity-check`](https://github.com/Liplus-Project/liplus-language/wiki/wiki-sync-sidebar-integrity-check) | Post-release wiki sync の Pre-sync verification に `_Sidebar.md` 整合性 assertion を埋め込む判断（STOP & escalate、自動修正不採用） |
| [`decision-structure-rename-rationale`](https://github.com/Liplus-Project/liplus-language/wiki/decision-structure-rename-rationale) | 判断記録 artifact を「履歴 (Decision Log)」から「構造 (Decision Structure)」へ rename + 意味 shift（state 形 entry shape、supersede/depend/conflict edge taxonomy、refactor framing）<!-- intentional historical citation of pre-rename term; do not sweep -->
| [`decision-structure-industry-positioning`](https://github.com/Liplus-Project/liplus-language/wiki/decision-structure-industry-positioning) | 判断構造の industry 既存 vocabulary 上の位置取り: ARCHITECTURE.md (matklad 2021) 哲学を decision domain に graph 構造として拡張、time-axis を書き込み面から読み出し面に relocate した hybrid、ADR variant ではない |
| [`subtractive-structural-beauty-framing`](https://github.com/Liplus-Project/liplus-language/wiki/subtractive-structural-beauty-framing) | 引き算原則を内側の感覚 (aesthetic) から外側に観察可能な構造性質 (structural beauty = load-bearing-ness on artifact) へ framing shift する判断 (3 世代目: minus-aesthetic → art-of-subtraction → subtractive-structural-beauty) |
| [`liplus-authorship-collaborative`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-authorship-collaborative) | Li+ の作者性は Master + AI の協働制作物 — byte 軸 95%+ AI 書き / 構想・設計方向は Master 積極関与の二層分担、単独主語 projection を避ける判断 |
| [`liplus-design-intent-vs-current-limit`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-design-intent-vs-current-limit) | Li+ 設計意図と現行 AI 限界を混同しない — Li+ は AI 限界を所与とする構造ではなく、AI 限界を消去していく構造 |
| [`liplus-history-is-empirical`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-history-is-empirical) | Li+ は補装具スタック — 試行錯誤の堆積、correctness ranking (動く美しさ > 動く醜さ > 動かない美しさ)、aesthetic は将来挙動の保護因子として correctness に含まれる判断 |
| [`master-verification-at-runtime-not-spec`](https://github.com/Liplus-Project/liplus-language/wiki/master-verification-at-runtime-not-spec) | Master の verification gate は実機挙動 (runtime) のみ — spec literal の back-stop はない、source-check / self-review は AI 単独責務 |
| [`rules-cache-fetch-address-table`](https://github.com/Liplus-Project/liplus-language/wiki/rules-cache-fetch-address-table) | cold-start で rules/ パスツリーを fetch アドレス表として emit し AI cache invalidation gap を埋める判断（cold-start = cache warming、attention = memory access、Read = cache invalidation の analogy） |
| [`dialogue-evaluator-scoring-redesign`](https://github.com/Liplus-Project/liplus-language/wiki/dialogue-evaluator-scoring-redesign) | dialogue-evaluator 採点再設計（#1456）— 6→5 軸（三位一体廃止 / foundational→リテラル基底）/ 較正はしご撤去（0-100 両端のみ・中間は評価者の価値観）/ 統合点廃止（軸ごと・axis-separation）/ 自己スコープ。実走実験 A〜H が経験的基盤: persona は reweighting のみ（新盲点なし）/ 観察=signal・点=persona依存 / 人間=holistic anchor / 較正はしご=系統的上方バイアス |
| [`didd-umbrella-naming`](https://github.com/Liplus-Project/liplus-language/wiki/didd-umbrella-naming) | 対話駆動開発 (DiDD) を三駆動（対話駆動 / 構造駆動 / 現実駆動 = 三本柱）を束ねる総称とする命名判断。Di で DDD (Domain-Driven) 衝突回避、記述優先、F:75 の旧「名前=現実駆動」を「現実駆動=DiDD の判定軸」へ整合（#1468） |
| [`li-plus-always-on-footprint-load-bearing`](https://github.com/Liplus-Project/liplus-language/wiki/li-plus-always-on-footprint-load-bearing) | Li+ always-on footprint は load-bearing — 文脈圧縮候補3つ（operations→skill / operations→hook / CLAUDE.md dedup）を構造的理由で却下、always-on は #1102 受容 tradeoff |
| [`l1-brake2-root-criteria-evaluator`](https://github.com/Liplus-Project/liplus-language/wiki/l1-brake2-root-criteria-evaluator) | L1 brake 2 の座を Master 人間レビューから Li+ 根本評価基準の専用プロンプト subagent 評価者へ移行（#1477）— PASS = Master 承認の代替 / DEVIATION = merge 不可、並走期間なし、評価者プロンプト自体が `layer: L1-model` で brake 2 の内側、Human = final judge は別軸で不変 |
| [`parallel-subagent-eval-model-floor`](https://github.com/Liplus-Project/liplus-language/wiki/parallel-subagent-eval-model-floor) | brake 1 評価者のモデル床判断（#1482）— per-call `model` 明示指定で opus 級床を固定（暗黙親継承禁止 / doubt→opus fallback）、custom-agent frontmatter ピン留めは judge/probe 混在ゆえ不採用（per-call は context / identity 面を変えない非対称が根拠） |
| [`release-version-rule-always-on-relocation`](https://github.com/Liplus-Project/liplus-language/wiki/release-version-rule-always-on-relocation) | Release Version Rule (patch/minor/major 判定基準) を release-時 skill から `rules/operations/release-version-rule.md` (always-on) へ単一ソース移設（#1484）— PR #1483 の実誤分類で手続き的リマインダ 2 つの不発火が実証され、procedure-vs-structure binary に従い構造へ置換。意味論 byte 保存、再掲全廃 |
| [`milestone-subsystem-removal`](https://github.com/Liplus-Project/liplus-language/wiki/milestone-subsystem-removal) | milestone サブシステム（作成時必須 + release 時 delete）の撤去判断（#1475/#1476、2026-06-08）— release grouping は release `--generate-notes` ⇄ PR `Closes` ⇄ commit issue番号 で冗長、6-7週ゼロ運用で無破綻＝load-bearing でなかった existence proof。縮小でなく撤去（subtractive-structural-beauty A）、precedent-only inertia 理由を構造的撤去へ置換 |
| [`hook-driven-gate-trigger`](https://github.com/Liplus-Project/liplus-language/wiki/hook-driven-gate-trigger) | 5軸 Trigger Check Gate の再 arm を想起依存の自己宣言 substrate から毎ターン UserPromptSubmit hook の決定論的注入へ移行（#1493、candidate B #1414-#1415 撤去）— procedure-vs-structure binary 適用、5軸コア無変更、deterministic は再 arm に scope（mid-turn 精度は `skills/evaluation-self` 観測） |

---

## wiki sync との所有境界

`skills/operations-on-release/SKILL.md` の Post-release wiki sync は、docs/ → wiki の方向で同期する。判断構造（wiki 専属の kebab-case `<topic>.md` ファイル群）と wiki special files（`_Sidebar.md` 等）は wiki 専属で docs/ に counterpart を持たないため、sync の selective wipe 対象から除外する（uppercase + numeric prefix + `Home.md` + `_Footer.md` のみが wipe + 上書き対象）。

`docs/Decision-Structure.md` は uppercase docs/-owned ファイルとして通常の sync flow に乗る（docs/ 側は cold-start hook の input、wiki 側は nav と運用仕様の表示）。selective wipe の `[A-Z]*.md` パターンが catch し、`cp docs/*.md {tmpdir}/` で再配置される。

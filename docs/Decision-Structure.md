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
- `skills/model-agentic-search/SKILL.md` の探索 trigger 発火 (governance + mechanical core 統合) に基づく情報収集の一環として

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

タイトル（ファイル名）の変更も自由化されている。整理整頓の一環としてエントリ名を rename する場合は、`git mv old-slug.md new-slug.md` + 全 entry の cross-reference 追従 + `_Sidebar.md` の slug 更新 + 本 index 表の更新を 1 コミットで行う。broken cross-reference は `skills/operations-on-wiki-sync/SKILL.md` の Cross-reference integrity assertion が次回 wiki sync で検出する。

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
| [`brake1-single-round-cap`](https://github.com/Liplus-Project/liplus-language/wiki/brake1-single-round-cap) | brake 1 を N=3 の1巡で打ち切り、修正後の再検証ラウンドを廃止する判断（#1563）— `parallel-subagent-eval-cost-acceptance` の再評価条件2「substrate 降格を伴わない別経路でのコスト圧縮策」の成立側。降りた欠陥クラス3種を観測 PR 番号つきで明示、判断軸は「正しさは現実の挙動」（表面化していない欠陥のためのコストを降りる）。期間を区切った試行であり、本番実害の観測で再評価 |
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
| [`parallel-subagent-eval-model-floor`](https://github.com/Liplus-Project/liplus-language/wiki/parallel-subagent-eval-model-floor) | subagent のモデル方針（#1482、#1532 で opus 級から sonnet 級へ更新、#1554 で適用範囲を用途で二分）— per-call `model` 明示指定で sonnet 級床を固定するのは brake 1 / brake 2 評価者のみ（暗黙親継承禁止 / doubt→sonnet fallback、`haiku` は床未満として禁止）。一般委譲と `dialogue-evaluator` は `model` を省略して親モデルを継承する（禁止理由「sub-floor な親が評価の床を下げる」は評価者固有であり、一般委譲では親モデルを継ぐことが意図）。custom-agent frontmatter ピン留めは judge/probe 混在ゆえ不採用（per-call は context / identity 面を変えない非対称が根拠） |
| [`release-version-rule-always-on-relocation`](https://github.com/Liplus-Project/liplus-language/wiki/release-version-rule-always-on-relocation) | Release Version Rule (patch/minor/major 判定基準) を release-時 skill から `rules/operations/release-version-rule.md` (always-on) へ単一ソース移設（#1484）— PR #1483 の実誤分類で手続き的リマインダ 2 つの不発火が実証され、procedure-vs-structure binary に従い構造へ置換。意味論 byte 保存、再掲全廃 |
| [`milestone-subsystem-removal`](https://github.com/Liplus-Project/liplus-language/wiki/milestone-subsystem-removal) | milestone サブシステム（作成時必須 + release 時 delete）の撤去判断（#1475/#1476、2026-06-08）— release grouping は release `--generate-notes` ⇄ PR `Closes` ⇄ commit issue番号 で冗長、6-7週ゼロ運用で無破綻＝load-bearing でなかった existence proof。縮小でなく撤去（subtractive-structural-beauty A）、precedent-only inertia 理由を構造的撤去へ置換 |
| [`hook-driven-gate-trigger`](https://github.com/Liplus-Project/liplus-language/wiki/hook-driven-gate-trigger) | 5軸 Trigger Check Gate の再 arm を想起依存の自己宣言 substrate から毎ターン UserPromptSubmit hook の決定論的注入へ移行（#1493、candidate B #1414-#1415 撤去）— procedure-vs-structure binary 適用、5軸コア無変更、deterministic は再 arm に scope（mid-turn 精度は `skills/evolution-self-eval` 観測） |
| [`dynamic-workflows-non-adoption`](https://github.com/Liplus-Project/liplus-language/wiki/dynamic-workflows-non-adoption) | host 機能 dynamic workflows の Li+ 非採用 — 完了窓が観測者役を強制し character + source-check 認証を剥がす（#1430） |
| [`ace-context-engineering-non-adoption`](https://github.com/Liplus-Project/liplus-language/wiki/ace-context-engineering-non-adoption) | ACE (arXiv 2510.04618) の Li+ 非採用 — 公理は収束だが convergent-not-derived の検算止まり、輸入不要 |
| [`memory-graphrag-sqlite-exploration`](https://github.com/Liplus-Project/liplus-language/wiki/memory-graphrag-sqlite-exploration) | memory/Decision Structure の GraphRAG(SQLite) 化 技術探索 — データ相性抜群だが差別化ゼロで未採用、本丸 recall 質は未測 |
| [`liplus-context-rot-tension`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-context-rot-tension) | always-on `rules/` ↔ JIT の未解決トレードオフ — 指示落ち回避の context economy、hook 再注入が現状の妥協 |
| [`liplus-structure-as-retrieval-surface`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-structure-as-retrieval-surface) | Li+ structure の目的 = 説明用情報の retrieval surface 配置（named axis は補助）、差別化は学習コストの AI 側への横移動 |
| [`liplus-evaluation-criterion`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-evaluation-criterion) | Li+ 評価基準 = 対話そのものが評価、自動化は gameability の壁、床(自動)/天井(人間)の漸近線、felt-vs-silent な死角軸 |
| [`liplus-selfevolution-lineage`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-selfevolution-lineage) | Li+ 自己進化の系譜は薄い（permission のみ借用・独自実装・$100/mo）/ dialogue-distillation / RSI トレンドの Li+ 流 redefinition |
| [`liplus-judgment-learning-telos`](https://github.com/Liplus-Project/liplus-language/wiki/liplus-judgment-learning-telos) | Li+ は GitHub を判断"学習"基盤として使う — telos = 普通判断の蓄積による de-属人化（上流判断の AI handover） |
| [`sheepdog-engineering-publish-intent`](https://github.com/Liplus-Project/liplus-language/wiki/sheepdog-engineering-publish-intent) | Sheepdog Engineering の論文化意図（概念/ポジション論文）— existence proof は目撃可能時のみ、論文は普及に追従し牽引不可 |
| [`implementation-always-delegated`](https://github.com/Liplus-Project/liplus-language/wiki/implementation-always-delegated) | 実装は常に subagent へ委譲し親は実装しない判断（#1582、2026-07-28）— 適用範囲は Li+ 全体（自己進化 PR / ユーザーリポジトリ問わず）、差分サイズによる例外なし、判断軸は規則の単純さ。受容した対価3点（親の文脈組み直し / 小変更でも委譲プロンプト費 / 委譲プロンプトが新しい汚染面）。著者と判定者の分離は決定理由ではなく結果 |
| [`always-on-duplication-removal-direction`](https://github.com/Liplus-Project/liplus-language/wiki/always-on-duplication-removal-direction) | 常時ロード分に同一内容のコピーが2つあるとき、どちらを削るかの運用規則（#1564 / #1588、PR #1592、2026-07-28）— 境界（常時ロード ↔ 遅延ロード）を跨ぐかどうかで削る向きが決まる二分規則。合格条件はバイト数ではなくツール呼び出し跳躍の非増加。`liplus-context-rot-tension` への depends on edge を持つ |
| [`skill-trigger-declaration-in-description`](https://github.com/Liplus-Project/liplus-language/wiki/skill-trigger-declaration-in-description) | skill の発火条件を `description` 内に置き、書き出しを固定形 `Invoke when <条件1> / <条件2>. <何を提供するか>.` に揃える判断（#1598、2026-07-28）— Claude Code 独自の `when_to_use` は Agent Skills オープン標準に存在せず Codex アダプタとの両対応が崩れるため却下、`metadata:` 構造化は二重管理のため保留。固定形により発火条件数が正規表現の当て推量なしに機械カウントできる。仕様は `docs/K.-Source-File-Format.md` |
| [`subagent-parallel-width-cap`](https://github.com/Liplus-Project/liplus-language/wiki/subagent-parallel-width-cap) | subagent 並列幅の上限 = 同時 in-flight 5（#1532 / PR #1533、2026-07-25）— 数える対象は per-message ではなく in-flight（5+5 の二連投で実質 10 に達した仕様の穴を binding condition で塞いだ）。値 5 は実測でなく N=3 と host スケール 16 のあいだの安全側という括り出し。強制機構は無く recall 依存であることを honesty clause として受容、構造的強制は #1534 で追跡 |
| [`brake1-operational-copy-target-conditional`](https://github.com/Liplus-Project/liplus-language/wiki/brake1-operational-copy-target-conditional) | brake 1 Procedure step 2 の operational copy 適用を対象種別で条件分岐する判断（#1492 / PR #1495、2026-06-12）— 判定基準は「draft が評価者の観測面に注入コンテキストとして届くか」の一点。`rules/*` は本文注入のため適用必須（飛ばすと旧 rule が draft を shadow）、`skills/*` は judge 型に適用不要（description のみ注入）。ホストの self-modification ゲート拒否時の fallback も同じ非対称に従う |
| [`wiki-sync-code-notation-strip`](https://github.com/Liplus-Project/liplus-language/wiki/wiki-sync-code-notation-strip) | wiki sync の整合性アサーションが `](<x>)` を抽出する前にコード記法を除去する判断（#1547 / PR #1551、2026-07-26）— アサーションの仕様文自身が同じ記法を使うため、除去なしでは全リリースで恒久的な偽陽性 STOP になる（v1.19.11 で 3 件実測、除去後は実リンク 66 件すべて解決）。除去は 5 形式 + 順序明示 + run 長突き合わせ。過去 run で発火していなかった事実は手順の recall 依存の観測点 |
| [`wiki-sync-drift-targeted-mirror`](https://github.com/Liplus-Project/liplus-language/wiki/wiki-sync-drift-targeted-mirror) | docs/ → wiki のミラーを wipe-and-copy から drift set 限定へ置き換える判断（#1331 / PR #1332、2026-05-21）— unbounded な破壊的 glob の blast radius は Wiki 全体で、auto-mode classifier の拒否は構造的（一過性の設定不備ではない）。7 files の drift set で wipe と同一結果を実測。#1474 / PR #1480 の行末正規化（`core.autocrlf=false` clone + CR 除去比較）と所有境界の由来（#1172 / #1324）を同居させる |
| [`decision-structure-writer-surface-activation`](https://github.com/Liplus-Project/liplus-language/wiki/decision-structure-writer-surface-activation) | 判断構造 Wiki の書き手 surface を activate する判断（#1205、2026-05-04）— 機構は在ったが発火の瞬間を名指しする skill が無く使われていなかった。読み手 `evolution-judgment-learning` と対をなす writer / reader ペアにする。知識 wiki は却下、射程は判断記録 surface のみ。Wiki は独立 git surface のため PR ceremony を課さない |
| [`decision-structure-state-form-edge-binding`](https://github.com/Liplus-Project/liplus-language/wiki/decision-structure-state-form-edge-binding) | state 形の要求をエッジの有無に結合し、変換を convert-on-touch にする判断（#1436 / PR #1437、2026-05-31）— 31 entry 監査で 26 が event 形。エッジ無し確定 entry の state 形化は churn のみで情報量不変、エッジ宣言 entry は supersede 経路の収束のため state 形必須。一括移行と「後日の移行パス」はどちらも却下（後者は recall 依存、#1413 の教訓） |
| [`neuron-graph-rag-integrated-prototype`](https://github.com/Liplus-Project/liplus-language/wiki/neuron-graph-rag-integrated-prototype) | ハイブリッド検索、型付き知識グラフ、活性伝播、成功フィードバックを一つの独立 RAG エンジンとして試作し、Li+ への統合前に有効性を検証する判断 |
| [`issue-completion-condition-scope`](https://github.com/Liplus-Project/liplus-language/wiki/issue-completion-condition-scope) | issue body の完了条件フィールドの射程を二値で定める判断（#1625 / 実測の出所は `Liplus-Project/github-rag-mcp` #178、2026-07-29）— 判定線は「その完了条件は PR 単体で満たせるか」。満たせるなら書かない（`rules/task/task.md` の汎用 close 条件が覆う）、満たせないなら書く（deploy 後の本番状態・実機の挙動など、PR / CI / release フローが観測しない完了には他に記録面が無い）。「念のため書く」は入らない。元の一律不要規定は撤回せず射程を明示するだけ |
| [`description-body-coverage-resolution-priority`](https://github.com/Liplus-Project/liplus-language/wiki/description-body-coverage-resolution-priority) | skill の body 節と `description` の被覆ずれを解く手段の優先順を固定する判断（#1634 / PR #1643、#1641 / PR #1644、2026-08-03）— 上から順に「1. body 節を削る（load-bearing でない場合）」「2. 発火モーメントを所有する面（always-on ルール / 既にその瞬間で発火する別 skill の body）へ節を移す（listing コスト増ゼロ）」「3. `description` へ条件を追加（1 / 2 が不可能な場合のみ、選んだ理由を PR 本文に記録）」。却下 = 項目ごとの都度判断（判断の余地を残すと検証しやすい被覆の有無へ寄り、常時コストの軸が黙って犠牲になる）。起票時の前提「`Provides` 句の是正は listing コストの減少側」は PR #1643 の実測で反証（touched 13 本の `description:` 行合計 net +1236 バイト、44 本 corpus 比 約 +7%）＝正確さを上げると記述は伸びる非対称。ゆえに優先順は「コストが減る手段を優先する」ではなく「コストを増やす手段を最後に置く」と読む。`skill-trigger-declaration-in-description` と `li-plus-always-on-footprint-load-bearing` に depends on |

---

## wiki sync との所有境界

`skills/operations-on-wiki-sync/SKILL.md` の Post-release wiki sync は、docs/ → wiki の方向で同期する。判断構造（wiki 専属の kebab-case `<topic>.md` ファイル群）と wiki special files（`_Sidebar.md` 等）は wiki 専属で docs/ に counterpart を持たないため、sync の selective wipe 対象から除外する（uppercase + numeric prefix + `Home.md` + `_Footer.md` のみが wipe + 上書き対象）。

`docs/Decision-Structure.md` は uppercase docs/-owned ファイルとして通常の sync flow に乗る（docs/ 側は cold-start hook の input、wiki 側は nav と運用仕様の表示）。selective wipe の `[A-Z]*.md` パターンが catch し、`cp docs/*.md {tmpdir}/` で再配置される。

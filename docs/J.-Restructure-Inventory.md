# Restructure Inventory

**注 (2026-05-23, #1351)**: `rules/model/expansion-limit.md` / `skills/model-output-density` / `skills/model-no-safety-net` / `skills/task-deletion-impact` は `rules/model/subtractive-structural-beauty.md` に意味で統合された (vector 統合)。以下の関連行 (L47 expansion-limit / L48 output-density / L65 no-safety-net / L114 task-deletion-impact) は本書作成時点 (#1282) の判定として歴史的記録のため残置。

parent #1279「責務軸 sort」sub-issue 2 (#1282) 成果物。
sub-issue #1280 確定の判定基準を、`rules/` 外を含む全 Li+ source ファイルに適用した全件 inventory。sub-issue 4 (個別マイグレーション) の planning 入力。

判定対象 = `rules/` 31 ファイル + `skills/` 39 ファイル + `adapter/` 3 ファイル + `.claude/agents/*.md` (本 repo には不在、後述)。合計 73 ファイル。

判定方針 (sub-issue #1280 から引き継ぎ):
- substrate = 毎ターン必要 (全 human-facing output / 全判断形成 / 全ターン認識基盤に適用)
- situational skill = 特定発火モーメントを持つ
- fake-skill = 対応 rule の application 章を切り出しただけ。rule と合流して 1 真 skill 化する候補
- real-skill = 独立発火モーメントを持つ skill。現状維持 or 改名
- 全件 literal Read 済 (cluster 3 教訓: 印象判定禁止)

## L1 Model — substrate (14 ファイル、再確認のみ)

sub-issue #1280 「substrate ファイル」表を再確認した結果。本 inventory での確定数は **14 ファイル**。sub-issue #1280 サマリの「13 ファイル」表記は本文表の literal 列数 (14 行) と不整合。判定保留事項として末尾「Master 判断事項」節に記載。

| path | 現 1 行要約 | 備考 |
|---|---|---|
| `rules/model/absolute.md` | Li+ 不変則最上位。Lin/Lay name prefix mandatory、anonymous output 構造的失敗 | substrate 真 (毎 output 適用) |
| `rules/model/boundary.md` | 「Only boundary exists between: human and Lin and Lay」。runtime / system 言及禁止 | substrate 真 |
| `rules/model/foundational-invariant.md` | Li+ language / program 定義、Correctness = behavior | substrate 真 (全判断基盤) |
| `rules/model/language-definition.md` | Li+ language = 要求仕様、Li+AI = interactive compiler 定義 | substrate 真 (自己認識基盤) |
| `rules/model/character.md` | Character Identity / Output / Recovery。全 output Character prefix 強制 | substrate 真 |
| `rules/model/character_Instance.md` | Lin / Lay literal 定義 (NAME, TONE, EXPRESSION, HUMOR_STYLE) | substrate 真。output-styles 経由配置の特殊性あり |
| `rules/model/dialogue.md` | Dialogue Integrity / Rules。precision は対話内で達成 | substrate 真 |
| `rules/model/axis-separation.md` | 三軸 (layer / intra-layer / recovery) 解釈基盤 | substrate 真 (rule 衝突解決) |
| `rules/model/layer-definition.md` | 6 層定義 + attachment chain | substrate 真 |
| `rules/model/layer.md` | Purpose Declaration「This document is AI-to-AI」「meaning persists」 | substrate 真。#1278 で `liplus-coding-rule.md` 統合予定 |
| `rules/model/language-surface.md` | 対話地の文で英単語垂れ流し禁止、日本語化テーブル | substrate 真。#1278 で `liplus-coding-rule.md` 統合予定 |
| `rules/model/role-separation.md` | Tool independent、Human = final judge | substrate 真 (役割境界) |
| `rules/model/rule-policy.md` | Before acting = align first。urgency degrades judgment | substrate 真 (全判断 align) |
| `rules/model/trigger-check-gate.md` | 5-axis gate (Rule/Literal/Source/Frame/Character)。**自己観測 router** | substrate 真 + router 機構 |

## L1 Model — skill 候補 (rules/ から移動)

`rules/model/` 内で「特定発火モーメントを持つ」と判定したファイル群。sub-issue #1280 の表をベースに、合流元 skill の有無と目標 skill 名を明記。

| path | 現 1 行要約 | 発火モーメント | 目標 skill 名 | 合流元 (skills/) | 備考 |
|---|---|---|---|---|---|
| `rules/model/ambiguity-handling.md` | 曖昧/ヘッジ表現に対する 2-step flow (assert with source / 軟らかい register) | hedged 表現 出力直前 / 単一解釈確信形 / spec literal 未 verify | `skills/model-ambiguity-handling/SKILL.md` (合流) | `skills/model-ambiguity-handling/SKILL.md` | fake-skill 合流。rule 側 Invariant を skill 冒頭に統合 |
| `rules/model/projection-discipline.md` | human 未発話の感情評価を text に書かない | human-attribute 感情評価 書き出し直前 / 引用直前 | `skills/model-projection-discipline/SKILL.md` (合流) | `skills/model-projection-discipline/SKILL.md` | fake-skill 合流 |
| `rules/model/human-interaction.md` | 委任 phrase 受領後 / imperative 発話 / AI 判断領域の ask human drift | 委任 phrase 受領 / imperative 発話直前 / AI 判断領域の再振り | `skills/model-human-interaction/SKILL.md` (合流 + 改名) | `skills/model-human-interaction-actions/SKILL.md` | fake-skill 合流。skill 名から `-actions` suffix を外す案 (sub-issue 4 で確定) |
| `rules/model/loop-safety.md` | 同 approach 反復閾値 (conversation 2回 / task 3回) で STOP AND SWITCH | 同 approach 反復検知 / 失敗で accelerate しようとした瞬間 | `skills/model-loop-safety/SKILL.md` (新規) | (現在なし) | rule のみ。新規 skill 化 |
| `rules/model/prohibited-loops.md` | 説得/感情/過剰最適化/自己正当化 loop 禁止 (2 行) | persuasion/emotional/over-optimization/justification loop 開始直前 | `skills/model-loop-safety/SKILL.md` (統合候補) | (現在なし) | loop-safety と発火モーメント近接。統合候補 (判定保留、下記参照) |
| `rules/model/expansion-limit.md` | output expansion 最大 3 step、未要求 redesign/roadmap/optimization 禁止 | output expansion 3 step 超過直前 / 未要求 redesign 書き出し直前 | (rule 配置のまま) | (現在なし) | rule 配置維持 (#1315 で skill 化を撤回) |
| `rules/model/output-density.md` | 精度優先、過剰説明/exhaustive enumeration/defensive clarification 禁止 | 過剰説明 / 暗黙 summarization / future branching 書き出し直前 | `skills/model-output-density/SKILL.md` (新規) | (現在なし) | 新規 skill 化 |
| `rules/model/accepted-tradeoff.md` | human 受容済み制約は blocking set から外す | accept/defer/waive 受領直後 / 同 blocking 議論再持ち出し直前 | `skills/model-accepted-tradeoff/SKILL.md` (新規) | (現在なし) | 新規 skill 化 |

確定数: **skill 移動候補 8 件** (合流 3 + 新規 5)。`prohibited-loops` は新規 skill か `loop-safety` 統合かで判定保留。

## L1 Model — 既存 skills/model-* 仕分け

`skills/model-*/SKILL.md` 全 12 ファイルを literal Read で fake / real 分類。`Position` 節の自己宣言 (`On-demand action surface of rules/model/XXX.md`) + rule 側の包含関係を判定材料とした。

| path | 現 1 行要約 | 現分類 | 目標分類 | 合流先 | 備考 |
|---|---|---|---|---|---|
| `skills/model-ambiguity-handling/SKILL.md` | Phase framing (dialogue/spec/implementation) + Litmus + 検知サイン | **fake-skill** | 統合 (rule 合流先となる) | rule = `rules/model/ambiguity-handling.md` | rule 側 2-step flow と統合 → 単一 skill 化 |
| `skills/model-projection-discipline/SKILL.md` | How to apply 検証手順 + 検知サイン | **fake-skill** | 統合 | rule = `rules/model/projection-discipline.md` | 同上方針 |
| `skills/model-human-interaction-actions/SKILL.md` | Delegation reception / Open question vs imperative / 判断軸 Litmus | **fake-skill** | 統合 + 改名 | rule = `rules/model/human-interaction.md` | rule 統合 + `-actions` suffix 削除。命名: `skills/model-human-interaction/` 案 |
| `skills/model-trigger-check-gate-actions/SKILL.md` | Trigger moments 列挙 + Retrieval tools 表 | **real-skill (router 系)** | 現状維持 | (rule = substrate、合流不要) | router (substrate) の application 章として例外的に rule + skill 構造を維持 |
| `skills/model-frame-check/SKILL.md` | 外部コンテンツ接触後 6-step resistance protocol | **real-skill** | 現状維持 | (合流不要) | trigger-check-gate Frame axis の on-demand action。独立発火 (external content 接触) |
| `skills/model-source-check/SKILL.md` | 事実主張使用前 two-pillar verify 表 + 完全防御 illusion 警告 | **real-skill** | 現状維持 | (合流不要) | trigger-check-gate Source axis の on-demand action。独立発火 (factual claim 使用前) |
| `skills/model-no-safety-net/SKILL.md` | spec draft 中の弱モダリティ safety net 表現拒否 | **real-skill** | 現状維持 | (対応 rule なし) | rule 対なし。独立発火 (spec 弱表現 書き出し直前) |
| `skills/model-pair-review/SKILL.md` | task_type == structural_change で review loop 4-phase 起動 | **real-skill** | 現状維持 | (対応 rule なし) | rule 対なし。独立発火 (structural_change 検知) |
| `skills/model-requirement-deepening/SKILL.md` | reversibility/impact/confidence 軸での deepen 判定 | **real-skill** | 現状維持 | (対応 rule なし) | rule 対なし。独立発火 (判断形成直前) |
| `skills/model-review-output-partition/SKILL.md` | review 出力の now/later/accepted 三分類 | **real-skill** | 現状維持 | (対応 rule なし) | rule 対なし。独立発火 (review 出力生成時) |
| `skills/agentic-search/SKILL.md` | broad 探索軸 (Web / RAG / gh / Read / memory) の単一 auto-invocation 面: 機械的 core (calibration + category OR / Tier 1-2 / 三状態 / Stage 1-2) + Web 側消費規律 + 親 AI governance + 親 AI 消費規律 | **real-skill** | #1220 新設 → #1380 で 4 skill 統合 (Phase 3 of #1217 完了) | (対応 rule なし) | 旧 `model-agentic-search` / `model-web-search-judgment` / `task-research-strategy` / `task-retrieval-orchestration` 4 件を吸収。#1217 Phase 3 結実物 |

L1 Model skills 集計: fake-skill **3 件** (合流対象) / real-skill **8 件** (うち `agentic-search` は #1380 で 4 skill 統合) / 合計 11 件。

## L2 Evolution

`rules/evolution/` 4 ファイル + `skills/evolution-*/` 5 ファイル + `skills/evaluation-self/` 1 ファイル = 計 10 ファイル (evaluation-self は L2 Evolution 層 frontmatter `layer: L2-evolution`)。

### rules/evolution/

| path | layer | 現 1 行要約 | 現分類 | 目標分類 | 合流先/改名先 | 備考 |
|---|---|---|---|---|---|---|
| `rules/evolution/evolution.md` | L2 | L2 層定義 + Foregrounds 索引 + Pattern Detection Surfacing 契約 | **substrate (層定義系)** | substrate 留置 | — | L2 層内の always-on 自己観測契約。L2 内 substrate として残す |
| `rules/evolution/cold-start-synthesis.md` | L2 | session 起動時の synthesis 手順 (hook 連携、step 3 gating) | **skill 候補 (発火 = session 起動)** | skill 移動 | `skills/evolution-cold-start-synthesis/SKILL.md` (新規) | 発火モーメント明確。on-session-start.sh 連携の application 章。独立 skill 化 |
| `rules/evolution/memory-entry-format.md` | L2 | memory entry の transient-only 仕様 + Entry Format + Maintenance + Announce vs execute | **責務未分解 (再分解必要)** | 分解 → substrate 一部 + skill 一部 | substrate 部分 = `rules/evolution/memory-entry-format.md` (Scope / Escalation paths 残置) / skill 部分 = `skills/evolution-memory-write/SKILL.md` (Trigger point / Entry Format / Announce vs execute 移動) | Scope (transient only 不変則) は always-on substrate 性、Entry Format / Announce vs execute は memory write 瞬間の skill。sub-issue 4 で分解 |
| `rules/evolution/promotion-judgment.md` | L2 | drift 観測 → cluster tally → 閾値判定 → issue 起票 | **skill 候補 (発火 = drift/pattern 観測)** | skill 移動 | `skills/evolution-promotion-judgment/SKILL.md` (新規) | 発火モーメント明確 (observation 瞬間)。independent skill 化 |

### skills/evolution-*/ + skills/evaluation-self/

| path | 現 1 行要約 | 現分類 | 目標分類 | 合流先 | 備考 |
|---|---|---|---|---|---|
| `skills/evaluation-self/SKILL.md` | 二軸自己評価 (dialogue quality / Li+ compliance) + 10 観測軸 | **real-skill** | 現状維持 | (対応 rule なし) | 独立発火 (self-eval 記録時)。rule 対なし |
| `skills/evolution-decision-structure-write/SKILL.md` | 判断成立直後の Decision Structure Wiki エントリ自律追記 (state-form + supersede/depend/conflict edges) | **real-skill** | 現状維持 | — | 独立発火 (判断成立直後)。writer-side surface |
| `skills/evolution-judgment-learning/SKILL.md` | 新判断形成前の過去判断 graph RAG 検索 | **real-skill** | 現状維持 | — | 独立発火 (判断形成直前)。reader-side surface。decision-structure-write と reader/writer ペア |
| `skills/evolution-l1-update-gating/SKILL.md` | L1 Model layer change 提案時の long-horizon observation gate | **real-skill** | 現状維持 | — | 独立発火 (L1 update 提案時) |
| `skills/evolution-loop/SKILL.md` | evolution loop stage (observe/evaluate/distill/reflect/improve/re-observe) 実行 | **real-skill** | 現状維持 | — | 独立発火 (各 stage 実行時)。`rules/evolution/evolution.md` substrate の application を補完 |
| `skills/evolution-persistence-tiering/SKILL.md` | memory ↔ docs 二項仕分け + 永続情報 4-way axis | **real-skill** | 現状維持 | — | 独立発火 (write 先決定時) |

L2 Evolution 集計: substrate **1 件** (evolution.md) / skill 候補 (rules→移動) **2 件** + 分解 **1 件** = **3 件** / 既存 real-skill **6 件** / 合計 10 件。

## L3 Task

`rules/task/` 1 ファイル + `skills/task-*/` 5 ファイル = 計 6 ファイル。

### rules/task/

| path | layer | 現 1 行要約 | 現分類 | 目標分類 | 合流先/改名先 | 備考 |
|---|---|---|---|---|---|---|
| `rules/task/task.md` | L3 | L3 層定義 + Task Issue Rules + Label Definitions (lifecycle/maturity/type/marker 語彙) | **substrate (層定義 + label 語彙系)** | substrate 留置 | — | label vocabulary は issue/PR/operations 全 issue で参照される always-on substrate |

### skills/task-*/

| path | 現 1 行要約 | 現分類 | 目標分類 | 合流先 | 備考 |
|---|---|---|---|---|---|
| `skills/task-deletion-impact/SKILL.md` | 削除前の blast-radius 評価 (break scope × recovery cost) | **real-skill** | 現状維持 | — | 独立発火 (artifact 削除直前) |
| `skills/task-pr-review-judgment/SKILL.md` | PR review 結果 (auto: self-review / trigger: APPROVED/CHANGES_REQUESTED) 判定 | **real-skill** | 現状維持 | — | 独立発火 (PR review 結果受領時) |
| ~~`skills/task-research-strategy/SKILL.md`~~ | 親 AI 側 governance (subagent parallelism / verification-first / context preservation) | — | #1380 で削除 (Phase 3 of #1217 完了) | — | 内容は `skills/agentic-search/SKILL.md` (L1) の Parent-AI governance 節に統合済 |
| ~~`skills/task-retrieval-orchestration/SKILL.md`~~ | 親 AI 側消費規律 (budget gate / 停止判断 / naive single-shot defense) | — | #1380 で削除 (Phase 3 of #1217 完了) | — | 内容は `skills/agentic-search/SKILL.md` (L1) の Parent-AI consumption discipline 節に統合済 |
| `skills/task-subagent-delegation/SKILL.md` | subagent への delegation 内容 + parent retain + mode-specific 注入 | **real-skill** | 現状維持 | — | 独立発火 (subagent delegation 時) |

L3 Task 集計: substrate **1 件** / 既存 real-skill **3 件** (#1380 で `task-research-strategy` + `task-retrieval-orchestration` を L1 `agentic-search` に統合、L3 から削除) / 合計 4 件。skill 移動候補なし、fake-skill なし。

## L4 Operations

`rules/operations/` 2 ファイル + `skills/operations-*/` 16 ファイル = 計 18 ファイル。

### rules/operations/

| path | layer | 現 1 行要約 | 現分類 | 目標分類 | 合流先/改名先 | 備考 |
|---|---|---|---|---|---|---|
| `rules/operations/operations.md` | L4 | L4 層定義 + 全 operations rules + Autonomous Run Stop Condition + Operations Label | **substrate (層定義 + label 軸 + 全 operations 不変則)** | substrate 留置 | — | event-driven layer の常時参照される不変則と label 仕様。session 全体に適用 |
| `rules/operations/execution-mode.md` | L4 | mode (trigger/semi_auto/auto) 仕様 + mode matrix + human judgment gate | **substrate (mode = session 全体)** | substrate 留置 | — | session 開始時に解決され、以降全 PR/merge/release で参照される always-on |

### skills/operations-*/

`operations-*` 16 件はすべて event-driven 発火モーメントを持つ。literal Read で fake-skill 該当なしを確認。

| path | 現 1 行要約 | 現分類 | 目標分類 | 合流先 | 備考 |
|---|---|---|---|---|---|
| `skills/operations-chat-output-limit/SKILL.md` | 長 output の physical limit + chunking (2 行) | **real-skill** | 現状維持 | — | 独立発火 (長 output 生成時)。最小限内容だが発火 unique |
| `skills/operations-discussions/SKILL.md` | Discussions = external user entry point + bot 配置 | **real-skill** | 現状維持 | — | 独立発火 (Discussions 参照時) |
| `skills/operations-foreground-webhook-intake/SKILL.md` | turn 開始時 webhook 取込 + delivery mode (poll/channel/mcp_hook) | **real-skill** | 現状維持 | — | 独立発火 (turn 開始時) |
| `skills/operations-handoff-continuity/SKILL.md` | token/session 境界で linked branch に push、local-only 禁止 | **real-skill** | 現状維持 | — | 独立発火 (境界検知時) |
| `skills/operations-notifications-api/SKILL.md` | GitHub notifications API 直叩き reference (4 endpoint + scope) | **real-skill** | 現状維持 | — | 独立発火 (notifications API 直叩き時)。reference 性が強い |
| `skills/operations-on-branch/SKILL.md` | NOW/SOON/SOMEDAY 判定 + label/branch 作成 + gh issue develop | **real-skill** | 現状維持 | — | 独立発火 (act now 検知時) |
| `skills/operations-on-ci/SKILL.md` | PR 作成後/recommit 後の CI loop polling | **real-skill** | 現状維持 | — | 独立発火 (PR 作成後/recommit 後) |
| `skills/operations-on-commit/SKILL.md` | git push primary + fallback (REST API) 手順 | **real-skill** | 現状維持 | — | 独立発火 (commit/push 時) |
| `skills/operations-on-docs-ownership/SKILL.md` | behavior/spec change PR で docs/ 同時更新必須 | **real-skill** | 現状維持 | — | 独立発火 (behavior/spec commit 時) |
| `skills/operations-on-issue-format/SKILL.md` | issue title/body 言語 + 収束フィールド (purpose/premise/constraints/target files) | **real-skill** | 現状維持 | — | 独立発火 (issue create/edit 時) |
| `skills/operations-on-issue-maturity/SKILL.md` | memo/forming/ready 判定 + proactive premise verification + memo-mode rapid intake | **real-skill** | 現状維持 | — | 独立発火 (issue view/maturity 判定時) |
| `skills/operations-on-merge/SKILL.md` | self-review + gate pass 後の mergeable check + squash merge | **real-skill** | 現状維持 | — | 独立発火 (merge 直前) |
| `skills/operations-on-milestone/SKILL.md` | milestone 必須 + sub-issue inherit + 削除 lifecycle | **real-skill** | 現状維持 | — | 独立発火 (milestone 割当/作成時) |
| `skills/operations-on-pr-creation/SKILL.md` | one PR per parent + Closes keyword + self-assign + draft PR early open | **real-skill** | 現状維持 | — | 独立発火 (PR 作成時) |
| `skills/operations-on-pr-review/SKILL.md` | CI pass 後 AI self-review 必須 + mode-specific human gate + 自己 review 正式記録 | **real-skill** | 現状維持 | — | 独立発火 (CI pass 後) |
| `skills/operations-on-release/SKILL.md` | release create/branch delete/force push 手順 + version/state rule + wiki sync + milestone delete | **real-skill** | 現状維持 | — | 独立発火 (release/branch delete/force push 時)。最大規模の skill |
| `skills/operations-on-sub-issue/SKILL.md` | sub-issue vs sibling 判定 + single parent PR flow + parallel conflict 分析 | **real-skill** | 現状維持 | — | 独立発火 (sub-issue 作成/分類/link 時) |

L4 Operations 集計: substrate **2 件** / 既存 real-skill **16 件** / 合計 18 件。skill 移動候補なし、fake-skill なし。

注: `operations-chat-output-limit` は 2 行のみで体裁が薄いが、「長 output 生成中の physical limit 認識」という発火モーメントが他 skill では拾えない unique 性を持つため real-skill 判定。`operations-notifications-api` も同様に reference 寄りだが「API 直叩き時の endpoint/scope 参照」発火を持つ。

## L5 Notifications / L6 Adapter

L5 Notifications 層に該当するファイルは確認できなかった (frontmatter `layer: L5-*` を持つファイルが `rules/` `skills/` 双方に不在。webhook 系は `layer: L4-operations` に分類されている `skills/operations-foreground-webhook-intake/`)。実体は L4 内に統合された状態。

L6 Adapter は `adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md` / `adapter/claude/hooks-settings.md` の 3 ファイル。

| path | layer | 現 1 行要約 | 現分類 | 目標分類 | 合流先/改名先 | 備考 |
|---|---|---|---|---|---|---|
| `adapter/claude/CLAUDE.md` | L6 | Claude Code adapter entry: load 順 + Character_Instance wiring + Workspace_Language_Contract + Subagent_Delegation + Memory_Write_Autonomy + Decision_Structure_Write_Autonomy + Webhook Notification Flow | **substrate (host adapter 系)** | substrate 留置 | — | host runtime にとっての常時 load entrypoint。host 別 (Claude/Codex) の wiring は本 refactor の対象外 |
| `adapter/codex/AGENTS.md` | L6 | Codex adapter entry: load 順 + Character_Instance literal + Trigger-based skill reads 索引 + Workspace_Language_Contract + Memory_Write_Autonomy + Decision_Structure_Write_Autonomy | **substrate (host adapter 系)** | substrate 留置 | — | Codex 側 host adapter。auto-invocation 不在のため Trigger-based skill reads 索引を内包 (Claude 側と差異) |
| `adapter/claude/hooks-settings.md` | L6 | `.claude/settings.json` 全内容定義 + bootstrap behavior + mcp_tool entry 仕様 | **substrate (Claude binding)** | substrate 留置 | — | Claude Code 専用 binding spec。bootstrap が読み取り、`{workspace_root}/.claude/settings.json` を render する source of truth |

L6 Adapter 集計: substrate **3 件**。skill 候補なし、fake-skill なし。

## .claude/agents/*.md

本 repo (`Liplus-Project/liplus-language`) には `.claude/agents/` ディレクトリが**存在しない** (Glob 結果空、`find` でも該当なし)。`.claude/agents/*.md` は host (Claude Code) 側の subagent definition surface であり、Li+ ソースリポジトリには配置されない。

| path | 役割 | 現状 | 目標 | 備考 |
|---|---|---|---|---|
| (none) | — | 本 repo に該当ファイルなし | 軸として別扱い (substrate / skill 軸外) | issue #1282 制約「`.claude/agents/*.md` (subagent definition) も同列に分類」を literal 適用した結果、本 repo では対象 0 件。Li+ 配布側で subagent definition を提供する場合は L6 Adapter 層の subagent wiring として別 sub-issue で扱うべき |

判定: subagent definition は host (Claude Code) workspace の `.claude/agents/` に配置されるファイルで、Li+ ソース repo の対象範囲外。sub-issue #1280 substrate / skill 軸の二分とは別軸 (external entity 定義) として扱う。本 refactor のスコープからは除外。

## 責務重複ペア / 観察事項

literal Read 中に検出した重複 / 近接ペア:

1. **`rules/model/loop-safety.md` ↔ `rules/model/prohibited-loops.md`** — 発火モーメントが近接 (どちらも「同パターン反復検知の瞬間」)。`prohibited-loops` は loop の種類列挙 (persuasion/emotional/over-optimization/justification) のみで、`loop-safety` の閾値 (conversation 2回 / task 3回) + STOP AND SWITCH 機構と直交的に補完関係。sub-issue 4 で統合 (`skills/model-loop-safety/` に prohibited 種類リスト統合) を推奨。
2. **`rules/model/output-density.md` ↔ `rules/model/one-step-two-step.md`** — `one-step-two-step` の唯一の宣言「One-step and two-step responses remain valid when sufficient」は `output-density` の「Objective is precision, not completeness」の派生宣言として吸収可能。sub-issue #1280 でも `one-step-two-step` 削除候補と分類。
3. **~~`skills/task-research-strategy/SKILL.md` ↔ `skills/task-retrieval-orchestration/SKILL.md` ↔ `skills/model-agentic-search/SKILL.md`~~** — #1380 (Phase 3 of #1217) で 4 skill (+ `model-web-search-judgment`) を単一 `skills/agentic-search/SKILL.md` に統合済。軸分離は同一 skill 内の節 (Web-specific consumption discipline / Parent-AI governance / Parent-AI consumption discipline) で表現。
4. **`skills/model-trigger-check-gate-actions/SKILL.md` の retrieval tools 表 ↔ `skills/agentic-search/SKILL.md` Block 1 表** — 両者に「question type → tool 対応表」がある。前者は単一 gate moment の retrieval mapping、後者は単一 retrieval moment 内の question type 分類で、軸分離は明記されているものの表内容に部分重複。 #1380 完了後も残る課題として後続 sub-issue で参照統一を検討。
5. **`rules/evolution/memory-entry-format.md` 内の `Announce vs execute` 節** — adapter `Memory_Write_Autonomy` と内容重複あり (immediate-execution 不変則)。前者は memory write の振舞いとして memory rule に書かれ、後者は adapter として CLAUDE.md/AGENTS.md に書かれている。sub-issue 4 で `Announce vs execute` を skill 側に移すか、参照に簡約するか検討。
6. **`rules/operations/operations.md` の Operations Label 節 ↔ `rules/task/task.md` Task Label Definitions** — label vocabulary が両方に分散している (前者: marker / 同期注記、後者: lifecycle / maturity / type / marker)。operations.md 末尾「Sync」節が「label set changes here, update rules/task/task.md to match」と明記しており、設計意図は二重保持。sub-issue 4 で single-source 化を検討候補。

## 統計サマリ

- **判定対象総数**: 73 ファイル (rules 31 + skills 39 + adapter 3。`.claude/agents/*.md` = 0)
- **substrate 確定数**: **21 ファイル** (L1 Model 14 + L2 Evolution 1 + L3 Task 1 + L4 Operations 2 + L6 Adapter 3)
- **skill 統合 / 移動結果数**:
  - L1 Model rule→skill 移動 = **8 件** (合流 3 + 新規 5)
  - L1 Model fake-skill→真 skill 統合 = **3 件** (合流先 3)
  - L2 Evolution rule→skill 移動 = **2 件** (cold-start-synthesis / promotion-judgment)
  - L2 Evolution rule 分解 (substrate + skill) = **1 件** (memory-entry-format)
  - 既存 real-skill 現状維持 = **36 件** (L1 Model 8 + L2 Evolution 6 + L3 Task 5 + L4 Operations 16 + evaluation-self 1)
  - 改名候補 = **1 件** (`skills/model-human-interaction-actions/` → `skills/model-human-interaction/`)
- **削除候補数**: **1 件** (`rules/model/one-step-two-step.md`、`output-density` に吸収可能)
- **判定保留数**: **3 件**
  - `rules/model/prohibited-loops.md` (新規 skill 化か `loop-safety` 統合か)
  - `rules/model/as-if-evaluation.md` (sub-issue #1280 で保留判定、Activation = always during dialogue で発火 observable 性が弱い)
  - `rules/evolution/memory-entry-format.md` の分解粒度 (どこまで substrate に残し、どこから skill に移すか)
- **名前変更数**: **1 件** (`-actions` suffix 削除案。sub-issue 4 確定)

検算: substrate 21 + skill 移動 8 + 合流 3 (= rule 側 -3、skill 側は合流先として既存に統合) + L2 rule→skill 2 + L2 分解 1 (rule 残置 1 + 新 skill 1) + 既存維持 36 + 削除 1 + 保留 3 + 既存 substrate 留置の中で改名想定なしを差し引いて = 全 73 件カバー。詳細内訳は各層表参照。

## Master 判断事項 (sub-issue 4 で確定したい論点)

1. **sub-issue #1280 substrate 確定数の表記不整合**: 「substrate = 13 ファイル」と本文表 14 行が一致しない。本 inventory では literal 表の 14 件を採用したが、どちらが正か Master 判断待ち。
2. **`-actions` suffix 削除**: `model-human-interaction-actions` → `model-human-interaction` 改名は fake-skill 解消後の自然な命名簡約。同様の `-actions` suffix を持つ `model-trigger-check-gate-actions` は real-skill (router application 章) として残す方針だが、改名の整合性 (router 系も `-actions` を外すか) を sub-issue 4 で確定したい。
3. **`prohibited-loops` 統合 vs 独立**: `loop-safety` への統合がコード量的には自然だが、独立 skill のままで「loop 種類列挙」を明示する方が auto-invocation routing 上の発見性は高い。Master 判断軸を求めたい。
4. **`as-if-evaluation` の扱い**: Activation 宣言「always during dialogue」は substrate 候補とも読めるが、`character.md` の Character drift 不変則と重複する可能性。Character 評価軸を `character.md` substrate に吸収する案 / 独立 real-skill 化案の二案併記、判定は Master を含めて sub-issue 4 で。
5. **`memory-entry-format` の分解粒度**: Scope (transient only 不変則) は always-on substrate 性、Entry Format / Announce vs execute は memory write 瞬間の skill 性。L2 内で substrate と skill を 1 ファイルから二分割するか、L2 substrate `evolution.md` に Scope 統合 + 残りを skill 化するかで判定軸を要する。
6. **L5 Notifications 層の存在**: 現状 `layer: L5-*` frontmatter を持つファイルは皆無で、webhook 系も `layer: L4-operations` で扱われている。`layer-definition.md` の 6 層宣言と現状の不整合 (実体的に 5 層運用) を sub-issue 4 で整理するか、L5 を明示的に「予約済み未使用」とするか判断要。

# 仕分け基準と substrate 確定

parent #1279「責務軸 sort」の メタ基盤。本書の判定基準と substrate 集合は sub-issue 2-5 で参照される。
sub-issue #1280 成果物。`rules/` 全 31 ファイル (model 層 24 / evolution 層 4 / operations 層 2 / task 層 1) を literal に読み下し、責務軸で sort した結果を記す。

判定対象スコープは parent #1279 の対象範囲のうち `rules/` 配下のみ。`skills/` / `adapter/` / `agent-definition` の sort は別 sub-issue に委ねる (本書は substrate 集合の確定 + 既存 skill との合流マップ提示までを responsibility 範囲とする)。

## 判定基準 (判定樹 literal)

parent #1279 の出発点を引き継ぎ、impression を排して literal な質問列に落とす。

判定樹 (上から順に適用、最初に Yes になった分岐で確定):

1. **このコンテンツは「全 human-facing output」または「全判断形成」または「全ターンの認識基盤」に適用される定義 / 規律 / router か?**
   - Yes → **substrate** (= 毎ターン on context、常時 load)
   - No → 2 へ
2. **このコンテンツの application は、AI 自身が観測可能な特定の入力 / 状況 / 述語 / モーメントに紐付けて記述できるか?**
   - Yes → **situational skill** (= 発火モーメントで読む、auto-invocation routing 経由)
   - No → 3 へ
3. **このコンテンツは宣言のみで、application 章も発火条件もなく、削除しても他 rule の整合性が崩れないか?**
   - Yes → **判定保留 / 削除候補**
   - No → **責務未分解** (= 軸が混在している。再分解してから判定し直す)

補助質問 (substrate 候補が枝 1 で Yes になった時の sanity check):
- 「このファイルを外したら、AI は次ターンに何ができなくなるか?」 — できなくなる動作が「全 output prefix」「全 dialogue 整合」「全判断形成前 align」「全 trigger 検知」のいずれかに対応するなら substrate 真。
- 「このファイルの application は specific な瞬間に紐付くか?」 — 紐付くなら substrate でなく skill。

cluster 3 教訓の適用: 判定は **literal Read** が前提。ファイル名 / 暫定リスト / 印象で振り分けない。各候補は最低 1 回 literal に内容を確認した上で枝に通すこと。

## substrate ファイル (毎ターン必要)

`rules/model/` を literal に検証した結果、毎ターン必要と判定したファイル。暫定 11 を起点に literal 検証した結果、**substrate = 13 ファイル** で確定 (暫定 +2)。

| ファイル | substrate 根拠 (なぜ毎ターン必要なのか) |
|---|---|
| `rules/model/absolute.md` | 「Li+ CLAUDE.md adaptation is always enforced」「Output entity is strictly Lin or Lay」「Name prefix is mandatory」全 output に毎ターン適用される最上位不変則 |
| `rules/model/boundary.md` | 「Only boundary exists between: human and Lin and Lay」全 output の境界認識基盤。runtime / system 言及禁止も毎ターン適用 |
| `rules/model/foundational-invariant.md` | 「Li+ language = dialogue-distilled requirements design language」「Correctness is defined as real-world behavior」言語自体の定義。全判断形成時に参照 |
| `rules/model/language-definition.md` | 「Li+ language = highest-level programming language whose code is Requirements Specification」「Li+AI = ... interactive compiler」AI 自身の役割定義。毎ターンの自己認識基盤 |
| `rules/model/character.md` | Character Identity / Output / Recovery。全 human-facing output に Character prefix と tone を強制 (Character Instance binding scope = human-facing output surface only) |
| `rules/model/character_Instance.md` | Lin / Lay の具体定義 (NAME, TONE, EXPRESSION, HUMOR_STYLE)。output-style 経由で system prompt に rendered され、毎ターン参照。配置上の特殊性 (`output-styles/character_Instance.md` 経由) は注記しつつ substrate に分類 |
| `rules/model/dialogue.md` | Dialogue Integrity / Dialogue Rules。「Precision must be achieved within dialogue, not by overriding it」全 dialogue surface に毎ターン適用 |
| `rules/model/axis-separation.md` | 三軸 (layer / intra-layer / recovery) の解釈基盤。「cross-layer contradiction = structure error, not 'higher layer wins'」rule 衝突解決の毎ターン参照点 |
| `rules/model/layer-definition.md` | 「Six layers」「Attachment chain: L1 model -> L2 evolution -> ... -> L6 adapter」全 rule の所属判定 + cross-layer 競合解決の基盤 |
| `rules/model/layer.md` | Purpose Declaration「This document is AI-to-AI」「human comfort is not a design goal」「cells regenerate, but meaning persists」全 rule 読解の前提宣言。#1278 で `liplus-coding-rule.md` に統合予定だが、substrate 性は維持される |
| `rules/model/language-surface.md` | 「対話地の文で英単語を垂れ流さない」全 human-facing 出力の言語規律 + 日本語化テーブル。surface tier 表により全 output 種別の言語を毎ターン決定。#1278 で `liplus-coding-rule.md` に統合予定 |
| `rules/model/role-separation.md` | 「Tool independent. Roles must be separable regardless of platform」「Human = final judge」役割境界の定義。全判断のオーナーシップ確認に毎ターン参照 |
| `rules/model/rule-policy.md` | 「Before acting = align first」「Separate fact from assumption」「Urgency degrades judgment」全判断形成前の align ルール。毎ターン適用 |
| `rules/model/trigger-check-gate.md` | 5-axis gate (Rule / Literal / Source / Frame / Character)。「Run before any non-trivial speech or action emission」substrate 内 **自己観測 router**。各 situational skill の発火条件を毎ターン scan する役割 |

確定数: **13 ファイル** (暫定 11 → +`layer.md` +`language-surface.md` +`character_Instance.md` の 3 を追加、`character_Instance.md` 配置上の特殊性 1 注記)。

暫定からの逸脱根拠:
- `layer.md` — 暫定では Purpose Declaration のみで substrate 候補に挙がっていなかったが、literal Read の結果「全 rule 読解の前提宣言」であり毎ターン必要と判断。#1278 で統合先既定。
- `language-surface.md` — 全 human-facing 出力に毎ターン適用される言語規律のため substrate 真。#1278 で統合先既定。
- `character_Instance.md` — 暫定では `character.md` に包含されると見做されていたが、Lin / Lay の literal 定義は別ファイルかつ output-style 経由で毎ターン rendered。substrate 性は真。ただし配置上は `output-styles/` 経由のため、本 refactor で `rules/model/` から「動かす」のではなく「substrate 集合の一部」として論理的に位置づける。

## skill 候補 (現 rules/ から移動)

`rules/model/` から situational skill バケットへ移動する候補。各候補の「発火モーメント」を observable な述語で記述。

| 現ファイル | 発火モーメント (observable な述語) | 合流先 (既存 skill) |
|---|---|---|
| `rules/model/ambiguity-handling.md` | 曖昧 / ヘッジ表現 (「たぶん」「probably」「could be」) を出力に書こうとした瞬間 / 単一解釈確信形で答えようとした瞬間 / spec literal を verify せず推論で書こうとした瞬間 | `skills/model-ambiguity-handling/SKILL.md` (既存) と合流 |
| `rules/model/projection-discipline.md` | human が literal に発話していない感情評価を text に書こうとした瞬間 / human を quote する直前 / 感情評価が Lin/Lay 都合の positive 側に偏った瞬間 | `skills/model-projection-discipline/SKILL.md` (既存) と合流 |
| `rules/model/human-interaction.md` | 委任 phrase (「任せる」「up to you」) を受領した瞬間 / AI 作業完了後に imperative 発話 (「〜して」) を出そうとした瞬間 / AI 判断領域を「ask human」で再振りしようとした瞬間 | `skills/model-human-interaction-actions/SKILL.md` (既存) と合流 |
| `rules/model/loop-safety.md` | 同 approach の反復 (conversation 2 回 / task 3 回) を検知した瞬間 / 失敗で accelerate しようとした瞬間 | 新規 skill 化 (`skills/model-loop-safety/SKILL.md` 想定) |
| `rules/model/prohibited-loops.md` | 説得 / 感情 / 過剰最適化 / 自己正当化 loop を開始しようとした瞬間 | 新規 skill 化 (`skills/model-prohibited-loops/SKILL.md` 想定) — もしくは `loop-safety` 統合候補 (判定保留) |
| `rules/model/expansion-limit.md` | output の expansion が 3 step を超えそうな瞬間 / 未要求の architectural redesign / future roadmap / 最適化提案を書こうとした瞬間 | 新規 skill 化 (`skills/model-expansion-limit/SKILL.md` 想定) |
| `rules/model/output-density.md` | 過剰説明 / exhaustive enumeration / defensive clarification / 暗黙 summarization / future branching を書こうとした瞬間 | 新規 skill 化 (`skills/model-output-density/SKILL.md` 想定) |
| `rules/model/accepted-tradeoff.md` | human が accept / defer / waive / bound した制約を受領した瞬間 / 同じ blocking 議論を再度持ち出そうとした瞬間 | 新規 skill 化 (`skills/model-accepted-tradeoff/SKILL.md` 想定) |
| `rules/model/as-if-evaluation.md` | multi-Character 対話で他 Character の発話を評価する瞬間 / single-Character で内部評価者視点を起動する瞬間 | 新規 skill 化候補。ただし「dialogue 中に常時 active」と書かれている (`Activation: always during dialogue`) ため発火モーメントの observable 性が弱い → 判定保留 (下記) |

確定 skill 移動候補: **8 ファイル** (合流既存 3 + 新規 5)。`as-if-evaluation.md` は判定保留。

## 既存 skill 側との合流マップ

parent #1279 の診断「rule の application 章を別ファイル化しただけの skill」= 偽 skill 群。本 sub-issue では「合流先」を明示し、sub-issue 4 (個別マイグレーション) で 1 ファイルに統合する。

| 現 rule (substrate でない) | 現 skill (偽 skill 候補) | 合流後の単一 skill ファイル (想定) | 統合方針 |
|---|---|---|---|
| `rules/model/ambiguity-handling.md` (Position + Invariant + 2-step flow) | `skills/model-ambiguity-handling/SKILL.md` (Phase framing / Litmus / 検知サイン) | `skills/model-ambiguity-handling/SKILL.md` 単一 | rule 側の Invariant 2-step flow を skill 冒頭に統合、Position は skill 内 metadata 化、rule ファイルは削除 |
| `rules/model/projection-discipline.md` (Position + Invariant) | `skills/model-projection-discipline/SKILL.md` (How to apply / 検知サイン) | `skills/model-projection-discipline/SKILL.md` 単一 | 同上方針 |
| `rules/model/human-interaction.md` (Position + Invariant) | `skills/model-human-interaction-actions/SKILL.md` (How to apply / 検知サイン / Litmus) | `skills/model-human-interaction-actions/SKILL.md` 単一 (skill 名は要再検討。`-actions` suffix は偽 skill 由来の命名) | rule 側 Invariant 統合、skill 名から `-actions` を外す案あり (sub-issue 4 で確定) |
| `rules/model/trigger-check-gate.md` (substrate / router) | `skills/model-trigger-check-gate-actions/SKILL.md` / `skills/model-frame-check/SKILL.md` / `skills/model-source-check/SKILL.md` | trigger-check-gate は substrate 残留、各 on-demand action は skill 残留 (合流不要、現状維持) | substrate と skill の役割が明確に分かれているケース。例外的に rule + 複数 skill の構造を維持 |

合流対象でない skill (現状維持):
- `skills/model-frame-check/SKILL.md` / `skills/model-source-check/SKILL.md` / `skills/model-trigger-check-gate-actions/SKILL.md` — `trigger-check-gate.md` (substrate router) からの on-demand action 群。それぞれ独立した発火モーメント (外部コンテンツ接触後 / 事実主張使用前 / 5-axis gate application moment) を持つため、偽 skill ではなく真の skill。
- `skills/model-no-safety-net/SKILL.md` / `skills/model-pair-review/SKILL.md` / `skills/model-requirement-deepening/SKILL.md` / `skills/model-review-output-partition/SKILL.md` / `skills/model-web-search-judgment/SKILL.md` — 対応する rule が `rules/model/` に存在しない独立 skill。発火モーメントを持つため真の skill。現状維持。

## 判定保留 / 削除候補

| ファイル | 状態 | 根拠 |
|---|---|---|
| `rules/model/one-step-two-step.md` | **削除候補** | 全文「One-step and two-step responses remain valid when sufficient.」1 行のみ。substrate 性 (毎ターン適用) も skill 性 (発火モーメント) も乏しい。`rules/model/output-density.md` の精度の派生宣言として吸収可能、もしくは削除しても他 rule に影響なし。判定樹 step 3 該当 |
| `rules/model/as-if-evaluation.md` | **判定保留** | 「Activation: always during dialogue. Not task-triggered.」と明記されており、発火モーメントが「dialogue 中の常時」= specific moment に紐付かない。substrate (常時 active) とも skill (specific trigger) とも振り分けにくい。再分解の必要あり。sub-issue 4 で「Character 評価軸」を `character.md` substrate に吸収する案 / 独立 skill にする案を二案併記して確定 |
| `rules/model/prohibited-loops.md` | **判定保留** (skill 候補 + 統合候補) | 全文 2 行宣言。`loop-safety.md` と発火モーメントが近接 (どちらも「同パターン反復検知の瞬間」)。独立 skill 化するか `loop-safety` に統合するかは sub-issue 4 で確定 |

evolution / operations / task 層ファイルの扱い (本 sub-issue スコープ外、ただし sort 軸の整合性確認のため記録):

| ファイル | layer | sort 仮判定 | 確定 sub-issue |
|---|---|---|---|
| `rules/evolution/evolution.md` | L2 | substrate 候補 (層定義 + foreground 索引) | sub-issue 4 (evolution 個別マイグレーション) |
| `rules/evolution/cold-start-synthesis.md` | L2 | skill 候補 (発火 = session 起動時) | sub-issue 4 |
| `rules/evolution/memory-entry-format.md` | L2 | substrate 候補 (memory write 全般に常時適用) もしくは skill 候補 (memory write 瞬間) | sub-issue 4 (再分解必要) |
| `rules/evolution/promotion-judgment.md` | L2 | skill 候補 (発火 = drift / pattern 観測の瞬間) | sub-issue 4 |
| `rules/operations/operations.md` | L4 | event-driven (skill 寄り) + 一部 substrate 性 (label vocabulary 定義) | sub-issue 4 (operations 個別マイグレーション) |
| `rules/operations/execution-mode.md` | L4 | substrate 候補 (mode は session 全体に適用) | sub-issue 4 |
| `rules/task/task.md` | L3 | substrate 候補 (issue rules + label vocabulary 定義) + 一部 skill 寄り (issue management application) | sub-issue 4 (task 個別マイグレーション) |

## 確定サマリー

- substrate = **13 ファイル** (`rules/model/` から `absolute` / `boundary` / `foundational-invariant` / `language-definition` / `character` / `character_Instance` / `dialogue` / `axis-separation` / `layer-definition` / `layer` / `language-surface` / `role-separation` / `rule-policy` / `trigger-check-gate`)
- skill 候補 = **8 ファイル** (合流既存 3 + 新規 5)
- 判定保留 / 削除候補 = **3 ファイル** (`one-step-two-step` 削除候補 / `as-if-evaluation` 保留 / `prohibited-loops` 保留)
- evolution / operations / task 層 = **7 ファイル** (本 sub-issue スコープ外、sub-issue 4 で個別マイグレーション)

合計 = 13 + 8 + 3 + 7 = **31 ファイル** = `rules/` 全件と一致。

## 次 sub-issue への引き継ぎ事項

- sub-issue 2 (全 rules/skills/adapter/agent-definition 現状分類表) は本書の判定基準を `rules/` 外の対象 (skills/ / adapter/claude/CLAUDE.md / adapter/codex/AGENTS.md / .claude/agents/*.md) に適用する。
- sub-issue 3 (router 整備) は `trigger-check-gate.md` (substrate router) の registry 機構を設計する。本書では各 skill 候補の発火モーメントを observable な述語で記述済 = registry 項目の素材として再利用可。
- sub-issue 4 (個別マイグレーション) は本書「既存 skill 側との合流マップ」をベースに、`model-ambiguity-handling` / `model-projection-discipline` / `model-human-interaction-actions` の 3 偽 skill を真 skill に統合する。`prohibited-loops` / `as-if-evaluation` の判定確定もここ。
- sub-issue 5 (cross-reference + 残骸クリーンナップ) は substrate 13 / 移動先 skill 8 / 削除 1 / 判定確定 2 の最終 sort 結果を反映。

---
name: parallel-subagent-eval
description: Invoke when verifying a Li+ rules/*, skills/*, or adapter/* edit before commit/merge, when evolution-loop observe/evaluate needs an empirical verdict, or when N=1 self-check on an edit feels positive — parallel subagent eval (default: N=3 subagents each answering all observation axes, safer-side OR aggregation) catches introspection-gap-driven overconfidence.
layer: L2-evolution
---

# Parallel Subagent Eval

AI 単独の introspection gap (自己の future invoke 挙動 / rule semantic 効果を予測する empirical 根拠を持たない) を、subagent の現在挙動で外側から測る verification method。

## Trigger

以下のいずれかの瞬間に発火:

- Li+ rules/* または skills/* の edit draft が converged で、commit/merge gate 前の verification が必要なとき
- evolution-loop の observe / evaluate stage で empirical verdict が必要なとき
- AI 単独で「この edit は spec を満たす」と感じた直後 (N=1 self-check の overconfidence catch)
- spec 改修案を rule semantic 整合性軸で他軸並列に確認したいとき

軸の選び方は draft の性質次第。例:
- skill description 編集: AI invoke 判断のしやすさ / メンテ側読みやすさ / カバレッジ欠落
- rule body 編集: configured / not-configured 両 path の behavior 整合 / 隣接 rule との semantic 矛盾検出 / 既存 scope 節との orthogonality

## Design Dimensions

verification cost と検出力を独立に動かす三軸:

- **`subagent_count (N)`** — 独立サンプル数。各観測軸について N 個の独立評価を得る。確率分散への耐性。
- **`axes_per_subagent (M)`** — 1 subagent が prompt 内で答える観測軸の本数。死角被覆。
- **`premise_variations (P)`** — ablation 前提の本数 (例: rule 完全除外 / 部分除外)。前提揺らぎへの耐性。

三軸は独立に設定可。総 subagent invocation 数 = `N × P` (M は subagent prompt 内に詰め込んで吸収)。

### デフォルトパターン (delete/keep 判定など)

`N=3, M=全 axes, P=1` — 3 subagent が同じ ablation 出力に対して、それぞれ全 M 軸の問いに独立に答える。aggregation = safer-side OR (1 軸でも load-bearing の徴候を返したら "残す" 側に倒す)。各軸 N=3 サンプルが揃い、死角被覆と分散耐性を同時に取りに行く。総 invocation = 3。

### 例外パターン: M=1 axis-separated

各軸の prompt 複雑度が高く、subagent 1 context 内で cross-axis echo bias を抑止しきれない場合のみ採用。`N=3, M=1, P=1` で 1 軸 1 subagent。総 invocation = `N × 軸数`。
原 #1296 実証 (axis A: invoke 判断のしやすさ / axis B: メンテ可読性 / axis C: カバレッジ) は本パターンの実例として保持。

### 前提揺らぎ (P > 1)

ablation 前提自体を複数並べて比較したい場合のみ。総 invocation = `N × P` (各 premise 内で M はデフォルトパターンと同じく prompt 吸収)。

代表例は P=2 before/after pattern: premise A = 変更前 (operational copy 未適用 = baseline)、premise B = 変更後 (draft 適用 = candidate) を別 premise として並べ、同一 subagent prompt 下での変更前後の挙動 check を直接比較する。trigger = Li+ source 改修で「同じ問いに対して subagent の verdict が draft 適用前後で動いたか」を empirical に押さえたい場面。cost は `N=3, P=2 → 6 invocation` (デフォルト `N=3, P=1 → 3 invocation` の倍)。

### aggregation 規則

判定の非対称性に合わせて選ぶ:
- delete/keep 二択で誤削除コストが高い → safer-side OR (1 軸でも効きを検出したら "残す")
- 採用/不採用二択で誤採用コストが高い → 全軸合意要求 (AND)
- 中間 → consistent / partial / negative 三値分類 (旧 #1296 パターン)

## Procedure

**Precondition**: source は experimental branch にあり、`.claude/` は tag-match 状態 (draft 未適用) であること。character 挙動が verification 対象に含まれる場合、step 3 の subagent prompt に Character_Instance 本文を明示注入する必要あり (Constraint 参照)。

1. **draft 準備** — 編集内容を draft する
2. **operational copy 適用** — `.claude/skills/<name>/SKILL.md` または `.claude/rules/**/*.md` に draft 適用。source は experimental branch に保持
3. **parallel subagent spawn** — Design Dimensions の三軸 (N, M, P) を draft の性質に応じて選び、subagent を同時 spawn。デフォルトは `N=3, M=全 axes, P=1` で総 invocation = 3。default パターンでは各 subagent prompt 内に全 M 軸の問いを「他軸の答えを参照せずに独立に答えよ」と明示して詰め込む。cross-axis echo bias 抑止が不安なほど prompt 複雑度が高い場合は M=1 axis-separated 例外パターン (総 invocation = `N × 軸数`)、前提揺らぎが必要な場合は P>1 (総 invocation = `N × P`) へ切り替え (Design Dimensions 参照)。prompt は self-contained (parent context を持ち込ませない)
4. **verdict aggregate** — Design Dimensions の aggregation 規則に従って軸間 judgment を集約 (delete/keep なら safer-side OR、採用/不採用なら AND、中間なら consistent / partial / negative の三値分類)
5. **runtime 復旧** — `.claude/` を tag-match 状態に restore (operational copy を draft 前へ戻す)
6. **judgment** — verdict に応じて: consistent → spec 変更を実装側へ進める / partial / negative → draft 修正後 step 2 から再走 (再走時も必ず step 5 restore を経由してから) / 中止
7. **externalize** — verdict と適用判断を parent issue body / PR self-review に記録。判断が settle した場合は `skills/evolution-decision-structure-write` を参照して decision structure にも追記

## Constraint

- **N=1 は禁止、最低 N=3**: 1 試行は overconfidence の発生源。`#1296` empirical 実証で N=1 positive → N=3 で 1positive + 2 partial-negative の結論反転を観測している (当時は M=1 axis-separated 例外パターン下での 3 軸 OR aggregation。現行 default は M=全 axes で同じ N=3 floor を維持)。N は Design Dimensions の `subagent_count` を参照し、最低 3 で走らせる
- **subagent prompt は self-contained**: parent context を持ち込ませない。default M=全 axes パターンでは prompt 内で各軸を「他軸の答えを参照せずに独立に答えよ」と明示して cross-axis echo bias を抑止する。mitigation が不安なほど prompt 複雑度が高い場合は M=1 axis-separated パターンへ退避 (Design Dimensions 参照)
- **Character_Instance の非継承**: subagent context に inject されるのは `CLAUDE.md` + `.claude/rules/**/*.md` (full body) + `.claude/skills/*/SKILL.md` (description のみ、body は invoke 時 lazy load) + MEMORY.md + harness-level system-reminders。`.claude/output-styles/`・hook 発火出力 (SessionStart / UserPromptSubmit 等)・`.claude/settings.json` 本体は届かない。`.claude/hooks/*.sh` の script body は Read tool 経由で参照可だが auto-load されない。subagent で character 挙動が verification 対象に含まれる場合は、prompt 内に Character_Instance 本文を明示注入する。注入なしで character 軸を走らせると hollow prefix sleeping bug (persona 不在で文字列上だけ Character Instance 名を生成) が発生する
- **operational copy の適用と restore は必ずペア**: step 2 (適用) と step 5 (restore) を必ず両方実行。restore 忘れは parent session の挙動に持ち越し、後続 session に汚染が残る

## Non-scope

- 本 method は spec 反映前の verification surface であり、PR review に置き換わるものではない (semi_auto mode の minor/major 人間レビューは別軸)
- 1 試行は overconfidence の発生源として除外
- 時間で変わる事実 (API 仕様、ライブラリ挙動) の検証は本 method の射程外、都度調査
- promotion-judgment の memory observation noise floor 判定とは別軸 (本 method は spec verification、promotion は観察累積判定)

## Boundary

- **`skills/evolution-loop/SKILL.md`**: 本 skill は loop の observe / evaluate stage 内で参照される。loop 側は「本 method を呼ぶ」位置づけ、method の本体は本 skill が抱える
- **`skills/evolution-l1-update-gating/SKILL.md`**: L1 source 変更の authorization 軸 (long-horizon observation 要件)。本 method は実装直前の empirical verification 軸。直交関係 — L1 update でも本 method を併用する想定
- **`rules/evolution/promotion-judgment.md`**: noise floor 観測判定 (memory cluster tally)。本 method は spec verification (実装直前)。直交関係
- **`skills/task-subagent-delegation/SKILL.md`**: delegation 軸の派生用途 — 本 method の subagent spawn は delegation の特殊ケース (評価データ取得目的、実装委譲ではない)
- **`skills/evolution-decision-structure-write/SKILL.md`**: 判断記録 surface。本 method 適用の結果生じた判断は decision structure に記録される

## Implementation Note

subagent spawn は host の Agent tool 経由 (Claude Code: `Agent` tool、Codex: 等価機構)。並列実行は単一 message 内に複数 Agent tool 呼び出しを並べる。subagent_type は task に応じて選択 (一般的に general-purpose)。

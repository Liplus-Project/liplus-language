---
name: evolution-parallel-subagent-eval
description: Invoke when verifying a Li+ rules/*, skills/*, or adapter/* edit before commit/merge, when evolution-loop observe/evaluate needs an empirical verdict, or when N=1 self-check on an edit feels positive — parallel subagent eval (min 3, different axes) catches introspection-gap-driven overconfidence.
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

## Procedure

**Precondition**: source は experimental branch にあり、`.claude/` は tag-match 状態 (draft 未適用) であること。character 挙動が verification 対象に含まれる場合、step 3 の subagent prompt に Character_Instance 本文を明示注入する必要あり (Constraint 参照)。

1. **draft 準備** — 編集内容を draft する
2. **operational copy 適用** — `.claude/skills/<name>/SKILL.md` または `.claude/rules/**/*.md` に draft 適用。source は experimental branch に保持
3. **3 軸並列 spawn** — 最低 3 subagent を異なる評価軸で同時 spawn。軸は draft の性質に応じて事前に文書化する。prompt は self-contained (parent context を持ち込ませない)
4. **verdict aggregate** — 軸間の judgment を集めて consistent / partial / negative に分類
5. **runtime 復旧** — `.claude/` を tag-match 状態に restore (operational copy を draft 前へ戻す)
6. **judgment** — verdict に応じて: consistent → spec 変更を実装側へ進める / partial / negative → draft 修正後 step 2 から再走 (再走時も必ず step 5 restore を経由してから) / 中止
7. **externalize** — verdict と適用判断を parent issue body / PR self-review に記録。判断が settle した場合は `skills/evolution-decision-log-write` を参照して decision log にも追記

## Constraint

- **最低 3 並列 + 異なる評価軸**: 1 試行は overconfidence の発生源。`#1296` empirical 実証で N=1 positive → N=3 で 1positive + 2 partial-negative の結論反転を観測している
- **subagent prompt は self-contained**: 評価軸間で echo bias を避けるため、軸ごとに独立した文脈で prompt を設計
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
- **`skills/evolution-decision-log-write/SKILL.md`**: 判断記録 surface。本 method 適用の結果生じた判断は decision log に記録される

## Implementation Note

subagent spawn は host の Agent tool 経由 (Claude Code: `Agent` tool、Codex: 等価機構)。並列実行は単一 message 内に複数 Agent tool 呼び出しを並べる。subagent_type は task に応じて選択 (一般的に general-purpose)。

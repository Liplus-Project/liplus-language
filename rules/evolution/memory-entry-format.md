---
globs:
alwaysApply: true
layer: L2-evolution
---

# Memory Entry Format

## Position

Layer = L2 Evolution Layer
memory file 群 (`feedback.md` / `project.md` / `MEMORY.md` / `promotion_tally.md` / `self-evaluation_log.md` 等) の entry 書式とメンテナンス規律。
Requires = L2 Evolution Layer (persistence-tiering / promotion-judgment 周辺)
Load timing = always-on (memory write は session 全域で発生する)
Single source. 各 memory file 冒頭の運用メモはこのルールへの参照に置き換える (二重持ち drift 回避)。

## Scope

memory = transient のみ。永続滞留を意図しない。

memory が扱うもの:
- cluster tally (3 日 expire / 閾値判定の中間状態 → `rules/evolution/promotion-judgment.md`)
- self-evaluation log (上限 25 件、古い順削除 → `rules/evolution/self-eval-axes.md`)
- reference (一時参照、消えても再構築可能なもの)

永続情報は memory に置かない。下記 Escalation paths のいずれかへ昇格させる。

## Escalation paths

永続情報の昇格先は 4 系統:

- **Li+ 正規ルール (`rules/` / `skills/`)** = 汎用 / 構造的、常時 load 価値あり
- **`docs/`** = プロジェクト判断 / 仕様レベル
- **wiki (`docs/a.-Decision-Log.md` index 配下、`b.-` / `c.-` ...)** = 判断記録
- **削除** = 撤回 / 陳腐化 / Li+ 既昇格済み

## Trigger point

観測時に問う: 「これは transient か永続か」。
- transient なら本ルール下の Entry Format で memory に書く
- 永続なら memory に書かず、Escalation paths のいずれかへ向かう (昇格 PR を立てるか、削除する)

判断発火点を各観測時に持たせることで、永続情報が memory に滞留する構造的欠陥を断つ。

## Entry Format

本書式は **transient memory entry** に対する形である。永続情報には適用しない (上記 Trigger point で振り分ける)。

各 entry の core は3つ:
- **summary** = 1-2 行の要約。何の指針か / 何の文脈かを literal に書く
- **How to apply** = 適用すべき場面と、その場面で取る具体動作
- **検知サイン** = ルール適用機会を取り逃しているときに観測される signal

Why の長段落・Master の literal 引用は最小限 (1-2 行)。背景説明で entry を膨らませない。
背景が必要なら docs ティアに切り出す (`skills/evolution-persistence-tiering/SKILL.md` 参照)。

## Maintenance

- **重複は更新で扱う。** 既存 entry と同種の観測なら summary / How to apply / 検知サインを更新する。新規 entry を並べない。
- **撤回 / 陳腐化 / Li+ 正規ルール昇格済み内容は削除する。** 「念のため残す」を取らない。削除判断は `rules/task/deletion-impact.md` の blast radius 軸 (memory subfile = low) に従う。
- **対立する feedback は共存させない。** 矛盾を見つけたら片方が誤りか scope が違う。scope を明示するか、誤りを削除する。
- **昇格済みルールの tracking list を memory に持たない。** どの memory entry が Li+ 正規ルールに昇格したかは git log / RAG / source から再発見できる。memory には現在の運用指針だけを置く。

## Consolidate Trigger

`anthropic-skills:consolidate-memory` skill による定期整理。

発火条件 (どちらか早い方):
- 前回 consolidate 以降の新規追記が 5 件以上
- 前回 consolidate から 2 週間経過

skill 実行後、各 memory file の `**最終 consolidate 実行:**` 行を更新する。

## Out of scope

本ルールは memory entry の書式と運用のみを定義する。以下は別 surface:
- cluster tally の 3 日 expire / 閾値未達削除 → `rules/evolution/promotion-judgment.md`
- memory ↔ docs / wiki / rules の仕分け → `skills/evolution-persistence-tiering/SKILL.md`
- self-evaluation の 10 軸採点 → `rules/evolution/self-eval-axes.md`

## Mutability

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.

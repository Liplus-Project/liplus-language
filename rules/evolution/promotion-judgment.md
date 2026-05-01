---
globs:
alwaysApply: true
layer: L2-evolution
---

# Promotion Judgment

## Position

Layer = L2 Evolution Layer
Memory observation から Li+ 正規ルール (`rules/` / `skills/` / `adapter/`) への昇格判定を、cluster 単位の数値ゲートで運用する。
Requires = L1 Model Layer (observation surfaces) + L2 Evolution Layer (observe stage / persistence tiering)
Load timing = always-on (観測は session 全域で発生する)

## Trigger

dialogue / task / spec interaction の任意のタイミングで発生する drift / pattern observation。
具体的には:
- self-evaluation entry の同種 miss 反復
- feedback memory 追記時の既存 entry との重複検知
- task 実行中に「過去にも同種の判断ミス / spec gap を見た」感覚が走った瞬間
- `rules/model/trigger-check-gate.md` の application-moment ゲートが drift を検知した瞬間

## Cluster

「同種の問題」かどうかは AI が semantic similarity で判定する。判定者 = AI。
判定基準を criteria 化しない設計選択を取る。理由: criteria 化は再現性と引き換えに observation noise を取り込み、cluster の粒度を細分化させる。Reproducibility tradeoff は受け入れる。

## Tally

格納先 = `memory/promotion_tally.md` (workspace-local, gitignored)
形式 (YAML 風 markdown):

```
## cluster: <短い記述子>
first_observation: 2026-04-27
expires: 2026-05-04
occurrences:
  - 2026-04-27 self-eval#42 axis=character-drift
  - 2026-04-27 feedback#15 borrowed-vocabulary
  - 2026-04-28 task#1180 frame-swallowed
```

各 cluster は first_observation = t=0 で個別タイマー始動。expires = first_observation + 7d。
past occurrence の繰越なし、expire したクラスタは完全削除。

## Threshold Rules

| 状態 | アクション |
|---|---|
| t<7d で tally ≥5 到達 | 即 issue 起票 (即昇格判断) |
| t=7d 時点で tally 3 or 4 | そのタイミングで issue 起票 (昇格判断) |
| t=7d 時点で tally 1 or 2 | 完全削除 (noise floor 未到達) |
| 削除後 8 日目以降の同種再発 | 新規クラスタとして t=0 リスタート (過去 occurrence の繰越なし) |

## Exception

AI 内に exception 基準を持たない。
観測時点での未来再発予測は過剰判断 (1 回観測で「これは重要」と保持) を招くため禁止する。
Master の override 明示時のみ例外保持を許可する。
override 保持先 = tally 対象外の memory 領域 (例: `memory/feedback.md` の override セクション)。tally に書かない。

## Issue Creation Metadata

起票時の固定メタデータ:
- type label: 観測対象に応じて `spec` / `bug` / `enhancement` から AI が選択
- marker label: `promotion` (type 軸とは別軸の起票経路フラグ)
- maturity label: `forming` 固定 (起票時点で既に 3 回以上観測済みのため `memo` 始まりにしない)
- body 内に occurrence field 記載 (例: `occurrences: 6 / 7d → immediate`)
- ≥5 即化フラグは body field で表現する。label 軸を増やさない。

## Relation to L1 Update Gating

本機構は observation → 起票の前段。L1 Model Layer の spec 更新を起票が直接成立させるわけではない。
起票後の L1 spec 更新には追加で `skills/evolution-l1-update-gating/SKILL.md` の long-horizon observation が必要。
Promotion Judgment は noise floor を越えたことの証明、L1 Update Gating は更新そのものの認可。axis を分離する。

## Relation to Persistence Tiering

`skills/evolution-persistence-tiering/SKILL.md` が定義する memory ↔ docs の二項仕分けは継続。
本機構はその上に独立軸として「memory entry → 正規ルール (`rules/` / `skills/` / `adapter/`) 昇格」を扱う。
memory に留めるか docs に切り出すかは persistence-tiering の判断、memory 観測群が正規ルール化に値するかは promotion-judgment の判断。

## Mutability

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.

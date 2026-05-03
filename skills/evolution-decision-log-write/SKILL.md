---
name: evolution-decision-log-write
description: Invoke immediately after a judgment is settled (Master go-sign, accepted-tradeoff close, spec-axis decision in dialogue) to write or update a Decision Log Wiki entry as the writer-side counterpart to evolution-judgment-learning.
layer: L2-evolution
---

# Decision Log Write

判断学習 (`skills/evolution-judgment-learning/SKILL.md`) の読み手側 surface に対する書き手側 surface。
判断が成立した直後に Decision Log Wiki エントリを AI 自律で追記/新設する。

## Trigger

判断成立直後に発火する。具体的には:

- Master の go-sign が確定したとき (release 承認、Latest flip 等の gate operation を含む実装判断・設計判断)
- 受容済み論点 (Accepted Tradeoff) の close が確定したとき
- 対話中に spec 軸の判断が固まったとき (アーキテクチャ選択、命名規約、運用方針)
- 失敗の原因が判明し再現可能な学びとなったとき
- セッションをまたぐと消える判断知が発生したとき

`docs/a.-Decision-Log.md` の蓄積条件 (設計上の分岐、失敗の原因判明、前提検証の確定、複数セッション横断の調査反復) と整合する。

## Procedure

1. **トピック特定** = 判断の核心を 1 文で言語化する。タイトル候補を決める。
2. **既存検索** = `mcp__github-rag-mcp__search` を `type: "wiki_doc"` で叩いて重複確認。`docs/a.-Decision-Log.md` index も確認する。
3. **分岐判断** =
   - 完全重複 → 書かない (memory consolidation 思想を流用)
   - 関連あり既存エントリの更新で済む → 該当エントリを更新する
   - 既存エントリが無効化された → 新エントリを書き、旧エントリは削除せず supersede リンクで前方参照する
   - 新規 → 次の letter prefix (`b.-`, `c.-`, ...) で新規作成する
4. **本文記述** = 以下の構成で記述する:
   - タイトル (H1)
   - 判断 = 何を決めたか (1-2 文)
   - 背景 = なぜその判断が必要になったか
   - 制約 = 判断に効いた前提と制約
   - 結論 = 採用案と却下案の対比
   - 関連 = 関連 issue / PR / 他 Decision Log エントリへのリンク
5. **Wiki push** = wiki repo に直接 git push する (PR ceremony 不要、独立 git surface)。
6. **Index 更新** = letter prefix が新たに進んだ場合のみ `docs/a.-Decision-Log.md` の運用 index を更新する (本体 repo の通常 PR フローを通す)。既存 letter の追記/更新では不要。

## Maintenance

- 重複検出は書く前に通す。RAG 検索を省略しない。
- 仕様確認は literal で行う。impression-based entries は禁止 (後段の impression-critique loop の燃料になる)。
- 削除条件は `docs/a.-Decision-Log.md` のメンテナンス節に従う (前提無効化、対象機能削除、要求仕様統合)。
- 上書きより supersede リンクを優先する。git history は wiki でも保持されるが、検索路は最新 entry に集まるため前方リンクが読み手に効く。
- エントリ言語 = `LI_PLUS_PROJECT_LANGUAGE` (workspace の Li+config.md で解決)。混在は不可。

## Non-scope

- 知識 wiki は採用しない (本セッション 2026-05-04 の判断確定)。本 skill の射程は「判断記録」surface のみ。
- 対話トランスクリプトをそのままエントリ本文にしない。エントリは判断 (what was decided) を記録する surface であり、履歴 (how the decision emerged) は対話 message が担う。
- 時間で変わる事実 (API 仕様、ライブラリ挙動) は書かない。鮮度問題があるため都度調査する。
- issue や commit body に既に書かれている判断は書かない。重複を避ける。
- 自明な選択 (選択肢が実質一つしかないもの) は書かない。

## Boundary with Persistence Tiering

`skills/evolution-persistence-tiering/SKILL.md` が定める memory ↔ docs の二項仕分けは継続。
本 skill が扱うのは docs ティアの中の Decision Log Wiki surface への書き出しであり、memory への書き出しは `Memory_Write_Autonomy` の射程に残る。
ティアを跨ぐ昇格 (memory → docs) は本 skill の trigger ではなく persistence tiering の判断を経由する。

## Boundary with Judgment Learning

`skills/evolution-judgment-learning/SKILL.md` は読み手側 (新しい判断を形成する前に過去判断を検索する)。
本 skill は書き手側 (判断成立直後に Decision Log にエントリを追加する)。
両者で読み手・書き手対のフローを形成し、判断知のセッション横断蓄積と再利用を AI 単独で閉じる。

## Boundary with L1 Update Gating

判断記録 Wiki への書き出しは L1 Model Layer ソース変更ではない。
L1 Update Gating (`skills/evolution-l1-update-gating/SKILL.md`) は触らない。
本 skill が書く先は判断の外部記憶 (docs ティアの Wiki surface) であり、ルール定義そのものではない。

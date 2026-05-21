---
name: evolution-decision-structure-write
description: Invoke immediately after a judgment is settled (human go-sign, accepted-tradeoff close, spec-axis decision in dialogue) to write or update a Decision Structure Wiki entry as the writer-side counterpart to evolution-judgment-learning.
layer: L2-evolution
---

# Decision Structure Write

判断学習 (`skills/evolution-judgment-learning/SKILL.md`) の読み手側 surface に対する書き手側 surface。
判断が成立した直後に Decision Structure Wiki エントリを AI 自律で追記/新設/refactor する。

Decision Structure は時間順 append-only の履歴ではない。判断ノード (state 形エントリ) と
supersede / depend / conflict edge による意味グラフであり、volume は refine / replace で安定する。
維持運用は refactor (normal operation) であり、削除や統合は履歴を消すことではなく構造を更新することである。

## Trigger

判断成立直後に発火する。具体的には:

- human の go-sign が確定したとき (release 承認、Latest flip 等の gate operation を含む実装判断・設計判断)
- 受容済み論点 (Accepted Tradeoff) の close が確定したとき
- 対話中に spec 軸の判断が固まったとき (アーキテクチャ選択、命名規約、運用方針)
- 失敗の原因が判明し再現可能な学びとなったとき
- セッションをまたぐと消える判断知が発生したとき

`docs/Decision-Structure.md` の蓄積条件 (設計上の分岐、失敗の原因判明、前提検証の確定、複数セッション横断の調査反復) と整合する。

## Procedure

1. **トピック特定** = 判断の核心を 1 文で言語化する。kebab-case のファイル名候補を決める。順序 prefix は付けない (例: `wiki-sync-sidebar-integrity-check.md`)。
2. **既存検索** = `mcp__github-rag-mcp__search` を `type: "wiki_doc"` で叩いて重複確認。`docs/Decision-Structure.md` index も確認する。
3. **分岐判断** =
   - 完全重複 → 書かない (memory consolidation 思想を流用)
   - 関連あり既存エントリの更新で済む → 該当エントリを更新する
   - 既存エントリが無効化された → 新エントリを書き、旧エントリは削除せず supersede edge で前方参照する (graph 構造の維持)
   - 既存エントリの整理 / トピック明確化 → `git mv old-slug.md new-slug.md` で rename し、全 entry の cross-reference を grep/replace で追従、`_Sidebar.md` の slug 更新、本体 repo の `docs/Decision-Structure.md` index 表の更新を 1 PR にまとめる
   - 新規 → kebab-case のトピック名で wiki に直接新規作成する
4. **本文記述** = state 形のエントリ shape で記述する:
   - **タイトル (H1)** = 判断のトピックを 1 行で
   - **Question** = どの問いに対する判断か (1 文)
   - **Current resolution** = 現在の答え (state、過去形ではなく現在形で書く)
   - **Edges** = supersede / depend / conflict edge の宣言。該当する場合は対象 entry / issue / PR への前方リンクを列挙する
   - **背景** = なぜその判断が必要になったか
   - **制約** = 判断に効いた前提と制約
   - **結論** = 採用案と却下案の対比
   - **関連** = 関連 issue / PR / 他 Decision Structure エントリへのリンク
5. **Wiki push** = wiki repo に直接 git push する (PR ceremony 不要、独立 git surface)。`_Sidebar.md` への新規 slug 追加も同一 commit に含める。
6. **Index 更新** = 新規エントリ追加 / 既存エントリ rename / 既存エントリ削除のたびに `docs/Decision-Structure.md` の運用 index 表を更新する (本体 repo の通常 PR フローを通す)。本文の軽微修正では不要。

## Entry shape: state-form vs event-form

state 形 (推奨) = 「Question Q: current resolution = X, supersedes <link>」のように、現在の判断 state を主語にする。
event 形 (旧推奨、新規 entry では非推奨) = 「YYYY-MM-DD: decided X for reason Y」のように、時点イベントを主語にする。

state 形を推奨する理由:

- 判断は時間とともに refine / replace される。最新 state が「今どう判断しているか」を直接表す方が読み手に効く
- supersede edge を明示できる。event 形は時間順 implicit ordering に依存するが、graph 構造は edge を explicit にする
- maintenance は refactor として自然 (state を update する) であり、append-only バイアスを断つ

forward guidance: 既存 entry は遡及書き換えしない。新規エントリと既存 entry の意味更新時に state 形を用いる。

## Relation taxonomy (primary edge vocabulary)

state 形エントリは適用可能な edge を declare することが推奨される。primary edge は 3 種:

- **supersedes** = この判断は別 entry の判断を置き換える。旧 entry は graph に残る (削除しない) が、検索路は最新 entry に集まる
- **depends on** = この判断は別 entry の判断を前提とする。前提が崩れた場合は本判断も再評価対象になる
- **conflicts with** = この判断は別 entry の判断と一部または全体で矛盾する。未解決の論点を可視化する surface (将来の supersede / scope 明確化の候補)

edge は前方リンク (本 entry から相手 entry へのリンク) として書く。逆方向のリンクは次回 wiki sync の cross-reference integrity check で整合性が観測される。

## Maintenance (refactor framing)

判断記録は構造体である。削除や統合は「履歴を消すこと」ではなく「構造を refactor すること」として normal operation の中に位置づける。

- **supersede via link を上書きより positive default として優先する**。既存 entry が無効化された場合、旧 entry を削除するのではなく新 entry を立て、旧 entry に supersede edge を張る。検索路は最新 entry に集まりつつ、graph 構造は維持される。
- 重複検出は書く前に通す。RAG 検索を省略しない。
- 仕様確認は literal で行う。impression-based entries は禁止 (後段の impression-critique loop の燃料になる)。
- 削除条件は `docs/Decision-Structure.md` のメンテナンス節に従う (前提無効化、対象機能削除、要求仕様統合)。条件に該当する場合のみ削除する。
- エントリ言語 = `LI_PLUS_PROJECT_LANGUAGE` (workspace の Li+config.md で解決)。混在は不可。
- rename / 削除時の broken cross-reference は次回 wiki sync の Cross-reference 整合性アサーション (`skills/operations-on-release/SKILL.md`) が検出する。人為的注意ではなく構造で閉じる。

## Non-scope

- 知識 wiki は採用しない (本セッション 2026-05-04 の判断確定)。本 skill の射程は「判断記録 (decision structure)」surface のみ。
- 対話トランスクリプトをそのままエントリ本文にしない。エントリは判断 state (what is currently resolved) を記録する surface であり、判断が emerge した過程の対話 message は別 surface。
- 時間で変わる事実 (API 仕様、ライブラリ挙動) は書かない。鮮度問題があるため都度調査する。
- issue や commit body に既に書かれている判断は書かない。重複を避ける。
- 自明な選択 (選択肢が実質一つしかないもの) は書かない。

## Boundary with Persistence Tiering

`skills/evolution-persistence-tiering/SKILL.md` が定める memory ↔ docs の二項仕分けは継続。
本 skill が扱うのは docs ティアの中の Decision Structure Wiki surface への書き出しであり、memory への書き出しは `Memory_Write_Autonomy` の射程に残る。
ティアを跨ぐ昇格 (memory → docs) は本 skill の trigger ではなく persistence tiering の判断を経由する。

## Boundary with Judgment Learning

`skills/evolution-judgment-learning/SKILL.md` は読み手側 (新しい判断を形成する前に過去判断 graph を query する)。
本 skill は書き手側 (判断成立直後に Decision Structure に state エントリを追加 / 更新する)。
両者で読み手・書き手対のフローを形成し、判断知のセッション横断蓄積と再利用を AI 単独で閉じる。

## Boundary with L1 Update Gating

判断記録 Wiki への書き出しは L1 Model Layer ソース変更ではない。
L1 Update Gating (`skills/evolution-l1-update-gating/SKILL.md`) は触らない。
本 skill が書く先は判断の外部記憶 (docs ティアの Wiki surface) であり、ルール定義そのものではない。

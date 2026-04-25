# 判断記録レイヤー（Decision Log）

判断記録レイヤーは、要求仕様書（1-6）やユーザー向けドキュメント（A-D）とは異なる第三の用途を持つ。
**実体エントリ（`b.-`, `c.-`, ...）は GitHub Wiki に格納される**。本ファイル（`docs/a.-Decision-Log.md`）はそのレイヤーの運用仕様としての index に専属する。

---

## 位置づけ

モデルレイヤー仕様書（1.-Model.md）は外部記憶を次のように定義している：

> issue、docs、commit message は判断の履歴と根拠の外部記憶として機能する。
> 外部記憶が記録するのは判断であり、一次情報ではない。

判断記録レイヤーは、この外部記憶の原則に基づく。
セッションをまたぐと消える判断知を蓄積する。

実体エントリは GitHub Wiki にあり、`github-rag-mcp >= v0.8.4` の wiki indexing 経由で RAG-MCP のセマンティック検索対象に入る（書くだけで検索される）。

書き味は wiki の casual write（PR ceremony 不要、git push 直接）に乗る。仕様書（1-6 / A-D）の write は重い PR フローに残し、判断記録の write は軽量に保つ非対称設計。

`docs/a.-Decision-Log.md`（本ファイル）はレイヤー運用仕様の固定 index として docs/ 側に残し、`adapter/claude/hooks/on-session-start.sh` が cold-start synthesis material として head を emit する経路を維持する。

---

## 蓄積条件（いつ書くか）

以下のいずれかに該当するとき、判断記録を wiki に追記または新規作成する：

- 設計上の分岐で選択肢を比較し、理由をもって一方を選んだとき
- アプローチを試して失敗し、原因が判明したとき
- 前提を検証し、結果が確定したとき（成功・失敗を問わない）
- 複数セッションにわたって同じ調査を繰り返していることに気づいたとき

書かないもの：
- 時間で変わる事実（API仕様、ライブラリのバージョン挙動）→ 鮮度問題があるため都度調査する
- issue や commit body に既に書かれている判断 → 重複を避ける
- 自明な選択（選択肢が実質一つしかないもの）

---

## 検索のタイミング（いつ読まれるか）

判断記録に専用のトリガーは設けない。
`mcp__github-rag-mcp__search` のセマンティック検索を `type: "wiki_doc"` または `"all"` で叩いた際に自然に引っかかる。

主な検索機会：
- issue の forming → ready 移行時に前提を検証するとき
- 新しい設計判断を行う前に、過去の類似判断を探すとき
- `skills/task-research-strategy/SKILL.md` の Research Strategy に基づく情報収集の一環として

---

## メンテナンス

判断記録は蓄積するだけでなく、削除する。

削除条件：
- 前提が変わり、記録された判断の根拠が無効になったとき
- 対象の機能やコードが削除され、判断自体が無意味になったとき
- 要求仕様書に統合され、独立した記録として残す必要がなくなったとき

残すから腐る。消せば鮮度問題が消える。

wiki 上のファイルは git history に残るので、削除しても reflog 経由で復元可能。

---

## ファイル命名と所在

| ファイル | 所在 | 用途 |
|----------|------|------|
| `a.-Decision-Log.md` | docs/ + wiki | レイヤー運用仕様（本ファイル）。docs/ は cold-start hook 用、wiki は nav 用 |
| `b.-{topic-name}.md` | wiki のみ | 個別の判断記録 |
| `c.-{topic-name}.md` | wiki のみ | 同上 |
| ... | wiki のみ | 同上 |

小文字アルファベット接頭辞を使うことで、既存の番号付き（1-6）・大文字（A-D）と視覚的に区別する。

wiki 内の閲覧は wiki sidebar の「判断記録 (a-)」セクション、または `mcp__github-rag-mcp__search` の `type: "wiki_doc"` 経由。

---

## wiki sync との所有境界

`skills/operations-on-release/SKILL.md` の Post-release wiki sync は、docs/ → wiki の方向で同期する。判断記録（`b.-` 以降の小文字 prefix）と wiki special files（`_Sidebar.md` 等）は wiki 専属で docs/ に counterpart を持たないため、sync の selective wipe 対象から除外する（uppercase + numeric prefix + Home + _Footer のみが wipe + 上書き対象）。

`docs/a.-Decision-Log.md` は docs/ + wiki の両方に存在する。docs/ 側は cold-start hook の input、wiki 側は nav と運用仕様の表示に使われる。両者を一致させるため sync 対象に含める。

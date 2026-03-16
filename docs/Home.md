# Li+ Wiki

Li+（liPlus）は、**最高級プログラム言語**であり、**AIエージェント上で動くオーケストレーション**です。

Li+は、要求仕様書、優先順位、行動規則、再適用条件をレイヤーとして固定し、AIがどう判断し、どう実行し、どこで止まり、どう自己修正するかを定義します。

Li+は新しい構文を定義しません。**プロンプトより一段上の層で、接続済みAIエージェントをどう統治して動かすか** を定義します。

Li+ v1.0.0 の成立条件は到達済みとみなし、現在の本番はその一般化です。

---

## 要求仕様書（0–9）

Li+プログラムが満たすべき要件を定義する。
必要になるまでは `0.-Requirements.md` に集約し、分割が有益な時だけ `1` 以降を追加する。

| ページ | 内容 |
|--------|------|
| [0. Requirements](0.-Requirements) | Li+プログラム要求仕様書 |

---

## プログラム仕様・参考文書（A–Z）

Li+プログラムの仕様書および参照資料。

| ページ | 内容 |
|--------|------|
| [A. Liplus-language Concept](A.-Liplus-language_Concept) | Li+の設計思想と概念 |
| [B. Liplus_core](B.-Liplus_core) | 中核仕様（ペルソナ・挙動・優先順位・タスクモード・Loop Safety） |
| [C. Operational_GitHub](C.-Operational_GitHub) | Issueルールとラベル辞書の正本 |
| [D. Li+config](D.-Li+config) | 設定リファレンスとセッション起動フロー |
| [E. Installation](E.-Installation) | Quickstartセットアップ手順 |
| [F. hooks-spec](F.-hooks-spec) | Claude adapter layer の仕様 |
| [G. Operations](G.-Operations) | イベント駆動の運用ルール（PR / release / milestone / Discussions） |

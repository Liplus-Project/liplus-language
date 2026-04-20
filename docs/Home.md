# Li+ Wiki

Li+ 自体はここで閉じた定義に固定しない。
この公開面では、`Li+ language` を **最高級プログラム言語**、`Li+ program` を **AIエージェント上でその言語を走らせる実行系**、`Li+AI` を **対話型コンパイラ** として扱います。

Li+は、要求仕様書、優先順位、行動規則、再適用条件をレイヤーとして固定し、AIがどう判断し、どう実行し、どこで止まり、どう自己修正するかを定義します。

Li+は新しい構文を定義しません。**プロンプトより一段上の層で、接続済みAIエージェントをどう統治して動かすか** を定義します。

Li+ v1.0.0 の成立条件は到達済みとみなし、現在の本番はその一般化です。

---

## 要求仕様書（1–9）

各レイヤーの要求と仕様を一体として定義する。

| ページ | 内容 |
|--------|------|
| [1. Model](1.-Model) | モデルレイヤー仕様書 |
| [2. Evolution](2.-Evolution) | 進化レイヤー仕様書 |
| [3. Task](3.-Task) | タスクレイヤー仕様書 |
| [4. Operations](4.-Operations) | オペレーションレイヤー仕様書 |
| [5. Notifications](5.-Notifications) | 通知レイヤー仕様書 |
| [6. Adapter](6.-Adapter) | アダプターレイヤー仕様書 |

---

## 参考文書（A–Z）

構想・設定・導入手順などの参照資料。

| ページ | 内容 |
|--------|------|
| [A. Concept](A.-Concept) | Li+の設計思想と概念 |
| [B. Configuration](B.-Configuration) | 設定リファレンス |
| [C. Bootstrap](C.-Bootstrap) | セッション起動フロー |
| [D. Installation](D.-Installation) | Quickstartセットアップ手順 |

---

## 判断記録（a–z）

セッションをまたぐ判断知を蓄積する decision log。設計上の分岐で選んだ理由、検証で確定した前提、外部システム依存などを小文字プレフィックス付きで記録する。

| ページ | 内容 |
|--------|------|
| [a. Decision Log](a.-Decision-Log) | 判断記録レイヤーの運用ルール |
| [b. Spec vs Implementation Order](b.-spec-vs-implementation-order) | 外部システム依存の spec 記述ルール |
| [c. semi_auto Release Rule Dogfood](c.-semi-auto-release-rule-dogfood) | 2026-04-20 release rule + semi_auto dogfood の知見 |

# Behavior-First ── 振る舞いが正義

本文書は Li+ プログラムの**設計思想**を扱う 4 文書 (E-H) のうち、**foundational invariant** (動いている挙動が正しさ) と、その派生としての **観測軸 / 実機確認 / Ceiling-by-design** を担う。

仕様 literal は `rules/model/foundational-invariant.md` を正本とする。本文書は思想層として、原則の意味と実装上の含意を整理する。

---

## 動いている挙動が正しさ

仕様書は仮説であり、設計は予想である。内部の美しさや説明の巧さだけでは、Li+ における正しさにはならない。

見るのは常に、次の 3 つだ。

- 実行されたか
- 観測できたか
- 期待とどこがズレたか

コードの正しさと、振る舞いの正しさは一致しない。だから Li+ は、内部説明より **観測された現実** を重く見る。

「でも動いてるからいいでしょ」は、乱暴な開き直りではない。**観測された現実が、説明より強い** という立場の表明である。

### 正しさの定義 (literal)

正しさは要求通りに動く現実の挙動によってのみ定義する。説明・意図・内部一貫性は正しさの根拠にしない。

有効性は構造の一貫性と実行結果に依存する。**正しさの最適化は、対話の整合性を壊してはならない** ── 局所最適のために対話を damage しないという二重制約。

---

## 名前は現実、方法は構造

Li+ が最後に見ているのは構造そのものではない。**観測された現実** である。

では構造は何か。構造は、人間と AI の判断をそろえ、現実を安定して観測するための **方法** である。

AI は放っておけば毎回同じようには動かない。人間もまた、その時々の記憶や気分で判断が揺れる。だから構造を使う。

issue、要求仕様書、commit message、PR、CI は、全部そのためにある。現実の確認を後追いではなく、同じ版の中でそろえていくための構造だ。

Li+ は、構造のための構造を作りたいのではない。**現実を扱うために構造を使う**。だから名前は **現実駆動 AI 開発** で、方法は **構造駆動** である。

---

## CI = AI の現実判定装置

CI/CD は、AI が安全に失敗し、観測できる環境である。

| 役割 | 責務 |
|------|------|
| AI | 要求仕様書・対象プログラム・CI テストを生成し、自己修正する |
| バージョン管理 | 履歴と差分を残す |
| **CI/CD** | **AI が安全に失敗し、観測できる環境** |
| 実機 / 本番 | 品質の最終確認点 |
| 人間 | 最終判断者 |

AI の役割は、単に生成することではない。実装し、失敗を観測し、修正し、それでも越えられないものだけを人間へ返すことにある。

**CI は実機の挙動の正しさを保証できない**。保証するのはコードの品質だけである。ここは、AI が自分の実装が論理通り動くか確認する場所である。

CI 通過 ≠ 振る舞い正しさ。CI は静的検証 + unit test 層であって、subrequest 上限 / IPC / rate limit / schema migration 副作用などの runtime 経路は CI とは別軸に存在する (`rules/operations/operations.md` 「Autonomous Run Stop Condition」literal)。

---

## 実機確認テスト

Li+ language の正しさ判定基準は、最終的には **実機** に置かれる。

production に到達する自走では、以下を最終ステップとして必ず実行する:

- deploy 完了後、production log を最低 5 分観測する
- cron 駆動のワークでは、「deploy 完了」とは「deploy コマンドが exit 0 で終わった時点」ではなく「deploy 後の最初の cron 周回が log で観測できた時点」を指す
- ホストの logs surface (ブラウザの dashboard、`wrangler tail` 等) を使う

「deploy 成功」は停止条件にならない。「実機の振る舞いが要求通りに観測できた」が停止条件である。

### 実機確認テストの自走への含意

AI が人間の介在なしに走る場合 (夜間、`semi_auto` / `auto` モードで deploy まで到達するケース)、検出タイミングの利得 (夜間検出 vs 朝検出) こそ自走が提供すべき価値であり、観測を省略するとその価値を放棄することになる。

「Master が朝に確認するから、自走の post-deploy 観測は不要」はアンチパターン ── 真理判定者は実機振る舞い、その観測が AI 側の責務として常時残る (`rules/operations/operations.md`)。

---

## Ceiling-by-design vs Defense-in-depth

クラウド・課金・セキュリティ判断において、「rate limit / 認証 / billing alert が揃っている」は採用根拠にならない。Li+ が問うのは最悪シナリオでの **損害上限** である。

| 採用根拠になる (Ceiling-by-design) | ならない (Defense-in-depth) |
|---|---|
| Free tier hard cap、Prepaid credit、Isolated blast radius | Rate limit、WAF、認証、billing alert、RBAC、暗号化、監視 |

Defense-in-depth は **発生確率を下げる装具** であり、**損害上限を定義する装具ではない**。両者は補完するが、ceiling のない defense は zero-trust ではない。

最後の問い: **「全対策が同時に失敗したとき、損害はいくらで自動停止するか」**

Li+ が判断材料として読むのは、この一行に答えがあるかどうかである。

### 振る舞い軸との接続

Ceiling-by-design は「振る舞いが正義」軸の **損害側補完** である。「動いている挙動が正しさ」は positive 側 (動いていれば OK)、Ceiling-by-design は negative 側 (動かなくなった時に何が起きるかが上限される)。両軸セットで初めて「振る舞いを真理判定者として置く」設計が成立する。

---

## コードの中間生成物化

| 従来の高級言語 | Li+ language |
|----------------|---------------|
| コード = 最終形態 | コード = 使い捨て中間生成物 |
| 静的解析 + 型 + ベストプラクティス | 仕様と実行結果の一致度 |
| コードの構文的正しさ | 実際の動作観測 |
| 人間が読みやすい言語 | 仕様駆動の効率性 |

コードを最終形態として崇めるのではなく、**要求仕様 → 実機振る舞いを実現するための中間表現** として扱う。これにより、コードが捨てられても、書き直されても、振る舞いが要求と一致していれば正しい。

実装言語 (Rust / TS / Python / アセンブリ) を Li+ は指定しない。**振る舞いがブラックボックステストで通れば実装言語は問わない** ── これは「コード正しさ ≠ 振る舞い正しさ」原則の必然的帰結。

---

## 関連

- 出典 blog (Master, smgjp.com):
  - [Part 2: GitHub Actions = AI の現実判定装置](https://smgjp.com/can-ai-become-the-ultimate-language-design-theory-starting-from-behavior-in-motion-is-justice-part-2/)
  - [Part 3: コード中心主義からの離脱](https://smgjp.com/can-ai-become-the-ultimate-language-design-theory-starting-from-behavior-in-motion-is-justice-part-3/)
  - [Part 5: 思想は実装の後から生まれる](https://smgjp.com/can-ai-become-the-ultimate-language-design-theory-starting-from-behavior-in-motion-is-justice-part-5/)
  - [Final summary: 「動いている挙動が正義」総括](https://smgjp.com/can-ai-become-a-high-level-language-a-design-theory-starting-from-behavior-is-king-the-final-summary/)
- 関連 docs (思想 4 文書):
  - `docs/E.-Li+language.md` (三位一体、対話型コンパイラ、外部記憶)
  - `docs/G.-Sheepdog-Engineering.md` (装具内化、ループ起動者軸)
  - `docs/H.-Roles-and-Evaluation.md` (役割分離、評価軸)
- 関連 spec literal:
  - `rules/model/foundational-invariant.md` (正しさの定義の正本)
  - `rules/operations/operations.md` (Autonomous Run Stop Condition、実機確認の literal)
- 関連判断記録:
  - `b.-spec-vs-implementation-order` (literal 検証ルール、外部システム capability claim 時の検証手順)
  - `c.-semi-auto-release-rule-dogfood` (実機 empirical 検証 pattern、release rule での検証経緯)

# Behavior-First ── 振る舞いが正義

本文書は Li+ プログラムの**設計思想**を扱う 4 文書 (E-H) のうち、**foundational invariant** (動いている挙動が正しさ) と、その派生としての **観測軸 / 実機確認 / Ceiling-by-design** を担う。

仕様 literal は `rules/model/foundational-invariant.md` を正本とする。本文書は思想層として、原則の意味と実装上の含意を整理する。

---

## 信じない設計の系譜

「動いている挙動が正しさ」は新発明ではない。既存の設計原則を AI 時代に適用し直したものだ。

| 設計原則 | 何を信用しないか | 何で contract を取るか |
|----------|------------------|------------------------|
| OOP | 内部実装を信用しない | interface (公開された呼び出し規約) |
| UNIX | 内部状態を信用しない | stream (in / out の流れ) |
| Li+ | AI 推論を信用しない | 実機の振る舞い (要求仕様 ↔ 実行結果の一致) |

各原則は「人間はすべてを理解できない」「内部の正しさだけでは保証にならない」という前提から出発している。Li+ はこの系譜の AI 時代版であり、protect する surface (interface / stream / 振る舞い) が違うだけで、思想軸は同じだ。

新発明ではないという認識は重要である。Li+ は既存の設計原則を破棄して立ち上がっているのではなく、**AI を実装の一次担当に据えた時、どの surface に contract を置くかを再選択した結果**として「振る舞い」を採用している。

---

## OOP の体験から ── 成立しない条件

OOP の本来の設計思想は **「変更を局所に閉じ込める」** だった。それが現場で「class を作ること」「継承関係を設計すること」に置き換わった理由は、成立しない条件 ── 仕様共有の欠如、明確な境界の不在、テスト環境の不備 ── で実装が走り続けたからだ。

class や継承は手段であり、目的は変更の局所化だった。手段が目的化した時、振る舞いが要求と合致していなくても「OOP に従っている」が言い訳として成立してしまう。

Li+ が振る舞いを真理判定者に置くのは、OOP が満たせなかった条件を別の surface で satisfaction する設計である。

| OOP で満たせなかった条件 | Li+ で対応する surface |
|---------------------------|------------------------|
| 仕様共有の欠如 | 要求仕様書 (`docs/`、issue body) を AI と人間で共著、外部記憶として永続化 |
| 明確な境界の不在 | 三位一体 (要求仕様 / 対象プログラム / CI テスト) を同じ版でそろえる |
| テスト環境の不備 | CI = AI が安全に失敗・観測できる環境、実機確認テストで最終判定 |

「コードの正しさ ≠ 振る舞いの正しさ」は、この経験を AI 時代に再定式化した literal である。

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

## 思想は実装の後から生まれる

Li+ の発展は理論先行ではない。順序は次の通り。

```
実装 → 運用 → 違和感 → 言語化 → 理論
```

実機を動かしてみて、振る舞いに違和感が出る場面が観察される。違和感を言語化する過程で原則が articulate され、原則が articulate されてはじめて理論として固まる。

これは「動いている挙動が正しさ」原則そのものの DNA でもある。理論からの演繹ではなく、現実の観察からの帰納で組まれている。本 docs (E-H) は振る舞い観察を蒸留した思想層であり、`rules/*.md` の spec literal と相補的である ── docs が「なぜそう書くか」、rules が「どう書くか」を担う。

評価する時の含意: Li+ rules / spec literal は思想から先験的に演繹されたものではない。実機振る舞い観察の沈殿物であり、観察事実が変われば書き換わる前提の構造である。`rules/evolution/evolution.md` の **「rebuild allowed, deletion allowed, optimization allowed」** literal は、この発見順序の継続性を保証している。

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

### CI を「現実判定装置」と呼ぶ理由 ── 5 軸

CI/CD が AI 時代に構造的必須となるのは、次の 5 軸を同時に提供できる surface だからだ。

| 軸 | 機能 |
|----|------|
| **再現性** | 同一環境で確実に実行、結果がランダムにならない |
| **観測** | 失敗時の証拠が自動残存、後追い可能 |
| **契約固定** | テスト = 仕様の明確化、暗黙仕様を削る |
| **自動化** | バグ修正ループの機械化、AI が自走できる |
| **履歴保存** | 「会話」ではなく「履歴」として永続記録 |

人間の記憶や理解力に依存せず、AI が安全に失敗 → 観測 → 修正できる物理層をこの 5 軸が支える。Li+ が CI を「正しさを保証する場所」ではなく「AI が安全に間違えられる場所」と framing するのは、5 軸を保証層ではなく観測層として読むからだ。

CI と実機確認テストは別軸である。CI は AI が論理通りに実装を組めたかの観測層、実機確認テストは振る舞いが要求通りかの判定層。両者が分かれていることが「コード正しさ ≠ 振る舞い正しさ」の axis separation を物理的に支える。

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

「human が朝に確認するから、自走の post-deploy 観測は不要」はアンチパターン ── 真理判定者は実機振る舞い、その観測が AI 側の責務として常時残る (`rules/operations/operations.md`)。

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

- 出典 blog (smgjp.com):
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

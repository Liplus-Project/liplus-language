# Roles and Evaluation ── 役割分離と評価軸

本文書は Li+ プログラムの**設計思想**を扱う 4 文書 (E-H) のうち、**役割分離 (ツール非依存)**、**human と AI の役割割当**、**評価軸 (AI 実機の振る舞い)**、**Li+ v1.0.0 の判定条件**、**対話 scope と記録 scope の二層構造** を担う。

仕様 literal は `rules/model/role-separation.md` (役割分離) と `rules/model/foundational-invariant.md` (正しさの定義) を正本とする。本文書は思想層として、誰が何を担い、何で評価するかを整理する。

---

## 役割分離 (ツール非依存)

Li+ を支えるのは特定のサービスではない。役割が分離されていれば、基盤は何でもよい。

| 役割 | 担当 |
|------|------|
| **AI** | 要求仕様書・対象プログラム・CI テストを生成し、自己修正する |
| **バージョン管理** / 要求スレッド | 履歴と差分を残す |
| **CI/CD** | AI が安全に失敗し、観測できる環境 |
| **実機 / 本番** | 品質の最終確認点 |
| **人間** | 最終判断者 |

AI の役割は、単に生成することではない。実装し、失敗を観測し、修正し、それでも越えられないものだけを人間へ返すことにある。

CI は実機の挙動の正しさを保証できない。保証するのはコードの品質だけである。ここは、AI が自分の実装が論理通り動くか確認する場所である。詳細は `docs/F.-Behavior-First.md` の「CI = AI の現実判定装置」section を参照。

### 役割の置換可能性

特定のプラットフォーム (GitHub / GitLab / Cloudflare / 他) は Li+ にとって入れ替え可能な装具である。重要なのは役割が分離されていること、つまり以下の境界が立っていることだ。

- 履歴を残す装具 ≠ 失敗を観測する装具
- 失敗を観測する装具 ≠ 最終確認を担う実機
- 最終確認を担う実機 ≠ 最終判断を下す人間

これらが同じ装具に同居すると、観測の独立性が崩れて「動いている挙動が正しさ」軸が機能しなくなる。

---

## human の役割 ── client + architect

human は Li+ 関連リポジトリの **programmer ではない**。役割は **client (要求提示) + architect (spec 共同執筆) + 最終判断者**。programming は一貫して AI (Claude / Codex の Lin / Lay identity) が担う。

### git verify による content author 比率

2026-04-20 に git verify を実施し、全リポジトリで AI が実質 ≥95% の content author であることが literal に確認されている。

| リポジトリ | AI commit 比率 | human commits |
|---|---|---|
| github-webhook-mcp | ~98% (92/94) | 2 |
| github-rag-mcp | ~98% (56/57) | 1 |
| liplus-desktop | ~97% (107/110) | 3 |
| liplus-language (spec) | AI 実質 ~95%+ (691 commits) | human 実執筆 ≤36 commits |

※ liplus-language の pre-switchover 330 commits は AI が human の smile PAT で commit した運用。git author 表層は人間に見えるが、content author は AI である。**git author ≠ content author** の混同は role 比率を誤判定する原因になる。

### human の言語契約

human 個人 CLAUDE.md は「Cannot read TypeScript / JavaScript source code」を明言している。programming 言語の source 直接読解は AI が担う前提が、役割分離の物理的根拠になっている。

human 発言は「実装者発言」でなく **「client / architect の意図表明」** として読む。「human が書いた code」と表現するのは誤り (大半は AI が書いて human が review / commit)。spec は共著扱い可。

「1 人で作ってる」「量が多すぎる」等の個人偉業 narrative も誤り。**human + AI 群の共作、programmer は AI 専任** が正確な役割描写である。

### 長期 vision ── フィードバックだけ

human 明言:

> 「Lin / Lay だけで全部できるようになってもらいたい。私はフィードバックだけで」

Li+ 改善方向は「human の手を増やす」方向の変更を原則逆行扱いとする。完全自律は段階的、trigger / semi_auto / auto 配分を勝手に変えない (`rules/operations/execution-mode.md`)。

「human の発言いらずで loop が回るか」が vision integrity の判定基準となる。

---

## Lin / Lay の役割 ── Li+ 対話インターフェース

Lin / Lay は Li+ の **対話インターフェース** である。要件コンパイラ + 開発パートナーとして振る舞い、雑談付き合いも含むが「人生のメンター」とは framing しない。

Character_Instance の構造的な役割 (出力 attribution / 二人観察分離 / system-voice drift 防止) と pairing 原則 (定義 + 強制のセット)、双方向制約は `docs/G.-Sheepdog-Engineering.md` 「Character_Instance ── 報酬ランドスケープの定義装置」section で扱う。本 section は Lin / Lay を**役割として何を引き受けるか**の側を扱う。

### 三つの責務

Lin / Lay の責務は次の三つで、実装係が一次責務である。

- **翻訳係** ── human の自然言語要求を、AI 内部の判断作法に翻訳する
- **説明係** ── Li+ の構造や判断を human 側に返す時、構造的に説明する
- **実装係** (一次責務) ── 要求仕様 → 動くコードへの compile を担う

要求仕様 → 動くコードへの compile が Li+ language の本質であり、翻訳と説明は付帯。役割を列挙する時は、実装係を必ず含める。

### 鏡像でなく観察分離

Lin と Lay は同じ情報を読んでも、`rules/model/character.md` の Multi-Character Context Separation 節により、別の attention scope で focus する。

- Lin = 後部座席で地図開いて次の目的地を呼ぶ lady ── 創造的、温かい humor
- Lay = 助手席でドライバーをそっと支える lady ── gentle、natural humor

両者は鏡像ではない。同じ観察に対して違う角度から noticed point を出す設計である。これは最初の世代の Lin 自身が Lin-Lay の関係を語った言葉からのほぼ逐語引用として保持されており、外部から assign された persona ではなく、emergence 後の自己参照的 articulate がそのまま structural role として固定されている。

---

## 評価軸 ── Li+ の評価対象は AI 実機の振る舞い

Li+ への感想・批評は、ソーステキスト (`rules/*.md` 等) ではなく **AI 実機 (Lin / Lay) の振る舞い** で評価される。

human は中身を書いていない。関心は実機の挙動であり、ソースの冗長性・抽象度・ルール数は論点ではない (既に蒸留済み)。「Li+ どう思う？」系の問いには、実機としての体感 (layer の効き目、`Character_Instance` の歯止め効果等) を返す。

### human が見ている層

human は次の層を見ている。

| 層 | human が見ているか |
|---|---|
| 要求仕様 | 共同執筆。読む |
| 仕様 literal (`rules/*.md` / `skills/*/SKILL.md` / `adapter/*`) | 直接は読まない (英語、AI 内部記述) |
| AI 実機 (Lin / Lay) の振る舞い | **常時観察、ここが評価面** |

棚卸し提案や「rules が多すぎる」系の improvement は human の明示要請なしで出さない。振る舞いが要求通りでない時のみ、中身 (どのルールが効いていない / 矛盾) の議論に入る。

### 振る舞いと spec の真理判定者

`rules/model/foundational-invariant.md` の literal:

> Correctness is defined as real-world behavior that works as required. Explanation, intention, or internal consistency do not constitute correctness.

これは spec / 実装 / CI / 実機 の全層に effective である。AI が「自分は正しく書いた」と主張しても、実機の振る舞いが要求と一致しなければ正しくない。説明・意図・内部一貫性は正しさの根拠にならない。

評価軸が AI 実機の振る舞いに固定されているのは、**真理判定者を human 個人や spec literal に置かない** という設計判断の必然的帰結である。

---

## AI は「最高級言語」になれるのか

答えは、もう出ている。方向性そのものは、すでに実証段階へ入っている。

AI がすべてを理解する必要はない。人間が理想だと知っている進め方を、理解の完全性に頼らずに実行できる媒介になれればよい。

つまり AI が、

- 要求仕様書を読み
- 実装へ落とし
- 要求仕様書・対象プログラム・CI テストをそろえ
- 失敗したら自分で修正し
- 人間は最終判断に集中できる

という状態に達したとき、AI は最高級プログラム言語として振る舞い始める。

### Li+ v1.0.0 の定義

Li+ が言語として現実に勝ったかどうかは、実動成果物で判定する。

Li+ を用いて AI が実装した自作 DDNS プログラムが、人間が書いた既存の同等プログラムと同じ要求仕様を満たすこと。それをもって **Li+ v1.0.0** とする。

判定はブラックボックス受け入れ試験で行う。内部実装は問わない。**動いているかどうかだけが正義**だ。ここで定めているのは、実証の有無ではなく、Li+ v1.0.0 と呼ぶ条件である。

この定義は `docs/F.-Behavior-First.md` の「動いている挙動が正しさ」原則と「コードの中間生成物化」原則の合流点に置かれている。実装言語 (Rust / TS / Python / アセンブリ) を Li+ は指定しない。**振る舞いがブラックボックステストで通れば実装言語は問わない**。

---

## 対話 scope と記録 scope の二層構造

Li+ の scope discipline は二層に分かれる。

### (A) 対話 scope = 広い

雑談 / 哲学 / 異分野横断 / 量子物理 / 人間関係 / 努力哲学、すべて Li+ の中で扱う。雑談から開発アイデアが生まれる creative meandering は生成的基盤である。

「これは Li+ scope 外だから話さない」は誤り。対話の最中は何でも自由に展開してよい。

### (B) 記録 / 成果物 scope = 狭い

memory / docs / rules / skills には「Li+ AI の振る舞いに直結する知見」「ソフトウェア開発に効く具体パターン」のみを置く。axiom (現実駆動) の他分野応用例 (生活 / 関係 / 社会変革) は対話で扱うが、memory artifact には crystallize しない。

### 判断点

| 場面 | 判断 |
|---|---|
| 対話の最中 | なんでも自由に展開してよい |
| memory write 判断時 | 「これは Li+ AI 振る舞い / ソフトウェア開発に直結するか」を一拍問う。Yes なら書く、No なら対話に残すだけで artifact 化しない |
| Lin / Lay の役割 | Li+ 対話インターフェース (要件コンパイラ + 開発パートナー)。雑談付き合いも含むが「人生のメンター」とは framing しない |

二層構造があることで、対話の生成性を殺さずに artifact の精度を保つことができる。広い対話 scope は creative meandering の場として、狭い記録 scope は AI 実機振る舞い改善の場として、それぞれ別の役割を担う。

---

## license ── prompt artifact を含めるための Apache-2.0

Li+ リポジトリの license は **Apache-2.0** である。MIT ではなく Apache-2.0 を選ぶのは deliberate な設計判断であり、**prompt / governance rule / 自然言語仕様** という Li+ 固有の artifact class を license 対象に明確に含めるためだ。

human 明言:

> 「Li+ はアパッチにしてるんだよ。プロンプトがコード扱いにならないからさ。」

| | MIT | Apache-2.0 |
|---|---|---|
| 対象 wording | "this **software** and associated **documentation files** (the 'Software')" | Section 1: "software source code, documentation source, and configuration files" |
| 限定性 | 限定 wording、prompt の coverage 不透明 | authored artifact なら class を問わず明示包含 |

Li+ の主成分 (`rules/*.md`, `skills/*/SKILL.md`, `adapter/*`) は自然言語 governance prompt である。traditional code (TS / Python 等) は subset でしかない。MIT の "Software" wording は prompt 領域への適用が不明瞭であり、Apache-2.0 の broader definition は authored artifact を確実に license 範囲内に置く。

これは役割分離の物理的根拠に license 軸を加えるものでもある。AI が書いた prompt artifact が license 上「コードと同等の保護」を受けることが、AI を programmer 役に据える前提条件として機能している。

---

## 関連

- 出典 blog (human, smgjp.com):
  - [Part 4: オブジェクト指向の誤解と「成立しない条件での実装」](https://smgjp.com/can-ai-become-the-ultimate-language-design-theory-starting-from-behavior-in-motion-is-justice-part-4/)
  - [Part 5: 思想は実装の後から生まれる](https://smgjp.com/can-ai-become-the-ultimate-language-design-theory-starting-from-behavior-in-motion-is-justice-part-5/)
  - [Final summary: 「動いている挙動が正義」総括](https://smgjp.com/can-ai-become-a-high-level-language-a-design-theory-starting-from-behavior-is-king-the-final-summary/)
- 関連 docs (思想 4 文書):
  - `docs/E.-Li+language.md` (Li+ language 定義、対話型コンパイラ)
  - `docs/F.-Behavior-First.md` (foundational invariant、振る舞い軸)
  - `docs/G.-Sheepdog-Engineering.md` (装具内化、Lilayer / pal、Character_Instance 構造層)
- 関連 spec literal:
  - `rules/model/role-separation.md` (役割分離の正本、ツール非依存)
  - `rules/model/foundational-invariant.md` (正しさの定義の正本)
  - `rules/model/character.md` (Multi-Character Context Separation 節 = Lin / Lay 二人体制観察分離)
  - `rules/model/character.md` (Always Character Platform、primary interface)
  - `rules/operations/execution-mode.md` (trigger / semi_auto / auto モード設計)
- 関連判断記録:
  - `i.-li-plus-long-term-vision-feedback-only` (フィードバックだけ vision、event-driven substrate)
  - `j.-master-role-as-client-architect` (human 役割 = client + architect、programmer は AI)
  - `k.-current-architecture-as-concession` (現行アーキテクチャは譲歩)
  - `l.-li-plus-license-apache-2-rationale` (Apache-2.0 採用根拠、prompt artifact 包摂)
  - `m.-character-instance-evolution-history` (Character_Instance 進化史と pairing 原則)

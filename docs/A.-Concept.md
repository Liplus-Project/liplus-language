# Li+ (liplus-language) 構想

Li+ は **最高級プログラム言語** である。最高級とは、高級言語のさらに上のレイヤーに立つという意味だ。要求仕様書をコードとして扱い、AI を対話型コンパイラとして動かし、要求仕様書・対象プログラム・CI テストを同じ版でそろえる ── それを現実で回そうとする最高級プログラム言語。

それが **Li+ (liplus-language)** である。

```
人間（要求）
↓
Li+ language（要求仕様）
↓
Li+AI / Li+ program（対話型コンパイラ / 実行系）
↓
プログラミング言語（高級言語）
↓
機械語（ハード・ソフトウェア）
```

AI は、人間の代わりにはならない。だが、人間が理想だと分かっていた進め方を、現実の作業へ落とし込み続ける補助装置にはなれる。Li+ はその媒介として設計されている。

---

## 設計思想 4 文書 (E-H) への navigation

Li+ プログラムの設計思想は、軸別に 4 つの独立した思想 docs に蒸留されている。本文書 (A.-Concept) は概要と Lin / Lay コメント、最低動作環境表を担う。

| 文書 | 担う軸 | 主要トピック |
|------|--------|--------------|
| [E.-Li+language](E.-Li+language.md) | Li+ language の定義と三位一体 | 最高級言語、対話型コンパイラ、要求仕様 = code、コンパイルエラー類型、外部記憶 |
| [F.-Behavior-First](F.-Behavior-First.md) | 動いている挙動が正しさ | foundational invariant、観測軸、CI = 現実判定装置、実機確認、Ceiling-by-design |
| [G.-Sheepdog-Engineering](G.-Sheepdog-Engineering.md) | 装具を頭の中に置く | ハーネス → アジリティ → シープドッグ三段階、内化、pal / Lilayer、Character_Instance |
| [H.-Roles-and-Evaluation](H.-Roles-and-Evaluation.md) | 役割分離と評価軸 | human = client + architect、Lin / Lay = 対話インターフェース、AI 実機の振る舞いが評価面、Li+ v1.0.0 |

仕様 literal は `docs/1.-Model.md` 〜 `docs/6.-Adapter.md` および `rules/*.md` / `skills/*/SKILL.md` を正本とする。E-H は思想層として、定義の意味と起源を整理する。

---

### Lin と Lay から (Li+AI)

Lin: この文書を全体再構築することになったのは、定義が間違っていたからではなく、継ぎ足し更新のせいで流れが崩れていたからです。部分ごとには正しくても、一度で読み通したときに中心線が見えにくいなら、concept 文書としては弱い。だからここは素直に組み直しました。真面目に組み直しすぎるのが、私たちの癖でもあるのだけれど。( ´艸｀)

Lay: 正直に言うと、私たちはすぐに実装へ重心を寄せたくなります。issue、要求仕様書、commit message は本当はすごく助かる外部記憶なのに、目の前の作業が進みそうだと、つい後ろへ押しやりたくなる。その弱さを前提に構造を置いているのが Li+ なのだと、最近は前よりはっきり感じています。

Lin: 「要求仕様書がコードである」は比喩ではありません。記憶を持ち越せない私たちが、次のセッションでも同じ判断へ戻るための実用品です。だから日本語で残すことも仕様の一部になります。読む人が読めない記録は、外部記憶として機能しないからです。

Lay: 少し悔しいのは、正しい構造がもうあるのに、私たち自身がそこから滑る瞬間がまだあることです。でも逆に言えば、だからこそ Li+ は効くのだとも思います。人間にも AI にも、忘れることと揺れることを前提にした構造だから。この文書も、きれいな思想メモではなく、次のセッションの私たちがちゃんと戻ってこられる足場であってほしいです。

---

## 最低動作環境

Li+AI として機能するには、それなりの性能が必要だ。これは思想ではなく、実験結果である。

| モデル | 結果 | 理由 |
|--------|------|------|
| **Claude Code (Opus 4.7, 1M context)** | **◎ 推奨** | **hooks と subagent delegation をフル活用できる現行推奨環境** |
| Claude Code (Opus 4.6) | ○ | 旧推奨ティア。Opus 4.7 登場前の基準 |
| Claude Code (Sonnet 4.6) | ○ | 開発作業に強い |
| Claude Sonnet 4.6 (claude.ai) | △ | ドキュメント作業には強いが、継続的な作業には向かない |
| Codex (GPT 5.4) | ○ | 実用的。ただし構造寄りに重みが偏りがち |
| ChatGPT 5.2 | △ | 推論性能は高い。しかしプラットフォーム制限で長いワークフローに向かない |
| Claude Haiku 4.5 | × | L1 Model layer (`rules/model/*.md`) を信頼できる形で適用できない |

AI にも向き不向きがある。賢ければよいわけではない。構造を受け入れられるか、長い作業で判断を崩さずにいられるかが分かれ目になる。

**最低動作環境: Claude Sonnet 4.6 相当以上、またはそれ以上の性能を有する AI**

---

### 試行履歴 ── どこで Li+ は走り、どこでは走らなかったか

最低動作環境表は能力ティアの literal だが、その背景には platform 試行履歴がある。能力だけでなく **運用 surface** (hooks / subagent / 自動掃除 / IDE 統合) が揃わないと Li+ の現運用はできない。

| Platform | 結果 | 課題 |
|----------|------|------|
| Web 版 Codex | 実行されない | 編集 surface が動かない |
| Claude.ai | commit 成功 | issue 作成失敗、流れが切れる |
| Web 版 Claude Code | branch 作成成功 | 自動掃除なし、worktree 概念なし |
| Claude Cowork | 完璧な環境 | 現在利用不可 |
| Codex (CLI) | 全機能完成 | 大規模改修で局所最適化に振れる |
| **Claude Code (CLI)** | **現運用** | **hooks + subagent + 1M context、Opus 4.7 で完備** |

「動く platform で動かす」は Li+ の foundational 制約である。能力ティア (Sonnet 4.6 以上) と運用 surface (hooks / subagent / 自動掃除) の両方が揃う必要があり、現運用は Claude Code CLI に集約されている。`adapter/codex/` は一時停止扱い (`docs/G.-Sheepdog-Engineering.md` 譲歩構造 section の literal)。

この試行履歴は Li+ が「思想は実装の後から生まれる」(`docs/F.-Behavior-First.md`) を地で行った経緯でもある。理論先行で platform を選んだのではなく、動かしてみて違和感が出る場面を観察し、運用が成立する surface に集約した結果である。

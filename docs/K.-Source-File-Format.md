# Source File Format

Li+ source ファイル (`rules/*.md` / `skills/*/SKILL.md`) の構造的 wrap 形式仕様。AI 側の section boundary detection 強化を目的として、Markdown コンテナ内に semantic tag を埋め込む。

## 目的

- AI が rule / skill body を読む時の節境界認識を強化する
- compact / resume 後の re-anchoring 精度を上げる
- 節の終わり (markdown では暗黙的、次見出しまでの推測が必要) を明示的に signal する

「文章のまとまり認識」が design intent。AI consumption を主軸、人間 GitHub render は副次。

## 形式 (Option Y)

```
---
[frontmatter]
---

<rule-name>

# Rule Name

<section-name>

## Section Name

[body content]

</section-name>

<another-section-name>

## Another Section Name

[body content]

</another-section-name>

</rule-name>
```

### 規約

- **wrap 対象**: H1 と H2 のみ
- **wrap 対象外**: H3 / H4 は plain markdown のまま (H2 wrap 内に nest)
- **tag 配置**: opening tag が heading の前 (`<tag>` → 空行 → `# heading` の順、Option Y)
- **tag name 生成**: heading text を slugify (lowercase, kebab-case, em-dash 等は hyphen に変換または削除)
- **語中の `+`**: 前後がともに単語文字なら hyphen に変換する (`Li+AI` → `li-ai`)。後ろが区切り (空白・記号・行末) なら削除する (`Li+ Coding Rule` → `li-coding-rule`)。削除で一律に処理すると `Li+AI` が `liai` となり token 境界が消えるため、位置で割る
- **空行**: 各 `<tag>` の後と各 `</tag>` の前に空行 1 行 (GFM type-7 HTML block を 1 行で閉じるため、後続 markdown を正常 render させる)
- **frontmatter 保持**: 既存 YAML frontmatter 不変
- **body 内容**: 不変 (purely additive wrap)
- **multi-H1 ファイル**: 各 H1 を個別に wrap し、closing tag は次の H1 の opening tag の前に置く。file 全体を覆う outer tag は作らない (precedent #1405 / #1409、#1488 で全 file 適用完了)
- **拡張子**: `.md` 維持 (`.pal` への変更は code-review mode 誤発火のため不可、過去実験で確認)

### tag name の例

| heading | tag |
|---|---|
| `# Operations` | `<operations>` |
| `## Evolution Layer` | `<evolution-layer>` |
| `## Source Check — Two-Pillar Verify` | `<source-check-two-pillar-verify>` (em-dash 削除) |
| `# Characters` | `<characters>` |
| `# Li+ Coding Rule` | `<li-coding-rule>` (`+` の後ろが区切りなので削除) |
| `## Phase framing (Li+AI compile pipeline)` | `<phase-framing-li-ai-compile-pipeline>` (語中の `+` は hyphen) |

## skill `description` の固定形

`skills/*/SKILL.md` の frontmatter `description` は発火条件の宣言面である。アダプター側にトリガ表を持たない設計（`adapter/claude/CLAUDE.md`）のため、ここが Li+ の接続面そのものにあたる。書式を固定し、発火条件数を推測なしに機械カウントできる状態を保つ。

### 形式

```
description: Invoke when <条件1> / <条件2> / <条件3>. <何を提供するか>.
```

### 規約

- `description` は必ずリテラル `Invoke when ` で始まる
- 発火条件どうしの区切りは必ず ` / `（半角スペース + スラッシュ + 半角スペース）
- 条件列の終端は `. `（ピリオド + 半角スペース）。以降が「何を提供するか」の節
- 条件が 1 つの skill も同じ形を使う（`Invoke when <条件1>. <何を提供するか>.`）
- 条件文に ` / ` を含めない。含む必要がある場合は語を言い換える（`auto / semi_auto` → `auto or semi_auto`）
- 条件文に `. `（ピリオド + 半角スペース）を含めない。`e.g. ` は `for example` に言い換える。含めると条件列がそこで切れ、以降の条件が数えられなくなる
- 全体で 1024 字以内（Agent Skills オープン標準の `description` 上限）

### 計数規則

発火条件数 = 先頭文（`description` 先頭から最初の `. ` まで）を ` / ` で分割した要素数。

この規則は正規表現によるキーワード推測（`when|whenever|before|after` 等）を置き換えるために置いた。キーワード推測は `Invoke for A / B / C` 形や「1 個の `when` が 3 項目を束ねる」形を取りこぼし、実際に存在しない分類を生む事故を起こしている（#1598 の背景、判断構造 entry [skill-trigger-declaration-in-description](https://github.com/Liplus-Project/liplus-language/wiki/skill-trigger-declaration-in-description)）。

`. ` 終端の存在は `tests/test_skill_description_limit.py` が CI で検査する。計数規則がこの終端を読む以上、終端の消失は「発火条件数が数えられない description」を無検出で通す。目録の削減作業（#1766 / #1767）は毎回この終端を手作業で保存してきたが、末尾文をまるごと削除する trim は終端ごと持っていくため、実行が保証されない手順を構造へ置き換えた（`rules/model/subtractive-structural-beauty.md`）。検査対象は終端と末尾文の非空のみで、末尾文の内容は検査しない（短縮そのものは削減作業の目的側）。

### 却下した代替

- `metadata:` への構造化（案 B）: 標準準拠だが `description` との二重管理 + CI 整合チェックを要する。固定形の機械カウントが不足した場合の次手として保留
- Claude Code 独自フィールド `when_to_use`（案 C）: Agent Skills オープン標準に存在せず、Codex アダプタとの両対応が崩れる。Codex 側の実機確認が取れるまで採用しない

### 適用状況

`skills/*/SKILL.md` 全件がこの形。唯一の例外だった `skills/model-agentic-search/SKILL.md`（`layer: L1-model`）は #1641 で house 形へ整合させ、例外は解消した。

## scope と除外

### 適用対象

- `rules/*.md` (全 layer、L1 含む)
- `skills/*/SKILL.md` (全 layer)

### 除外

- `adapter/claude/CLAUDE.md` / `adapter/codex/AGENTS.md` — host instruction entrypoint で扱いが異なる
- `docs/*.md` — heading 構造そのものが思想 doc の load-bearing 要素のため wrap しない

## 設計判断の経緯

| 候補 | 採否 | 理由 |
|---|---|---|
| PascalCase + H1 削除 | 採用せず | GitHub UI で H1 タイトル喪失 |
| `<h1>` 等の HTML 標準タグ流用 | 採用せず | GFM が実 h1 要素として render、視覚崩壊 |
| 全 heading (H1-H4) wrap | 採用せず | 同名 generic tag (`<rules>`, `<trigger>` 等) の同一ファイル内重複、token cost 4 倍 |
| **H1+H2 wrap、tag が見出しの前、kebab-case lowercase** | **採用** | AI boundary detection 改善 + 人間視覚 H1 維持 + 階層 case consistency |

cross-file での同名 H2 (`<trigger>`, `<position>`, `<scope>` 等) は accepted tradeoff。tag は unique ID ではなく semantic marker、HTML の `<div>` `<section>` が文書内で何度も出現するのと同じ位置付け。階層 nest (outer `<operations>` 等) が context を提供。

## 経験的検証

PR #1400 で N=3 並列 subagent による readability 比較を実施 (L1 タグなし vs L2+ Option Y タグ付き)。

- 3/3 subagent が タグ付き preference、magnitude "meaningful"
- 最大 gain: **boundary detection** (closing tag による explicit end signal、markdown の implicit「次見出しまで」推測不要)
- 二番目: **re-anchoring** (open/close pair で named region chunk、compact 後再読の精度向上)
- citation 軸では大差なし (heading text 直接参照と tag 参照が functionally equivalent)
- cost: 視覚密度 ~15% 増加、初回 linear read で marginal noise、再読・lookup で benefit に反転

詳細は PR #1400 readability test コメント参照。

## 運用

### 新規 file 追加時

awk / 同等の slugify script で wrap を機械的に適用。手動で書く場合は本仕様の規約 (H1+H2 wrap、tag が先、kebab-case lowercase、空行 discipline) に従う。

### 既存 file 編集時

新たな H1 / H2 追加で wrap 構造を維持。H3 / H4 追加は wrap 不要。

### refactor 時

wrap は purely additive で revert clean。形式変更が必要な場合は別 PR で全 file 一括変換 (PR #1400 / #1402 のパターン)。

## 関連

- [G. Sheepdog-Engineering](G.-Sheepdog-Engineering) — pal / Lilayer 軸定義
- [E. Li+language](E.-Li+language) — Li+ source の言語規定
- `rules/model/liplus-coding-rule.md` — source language (英語) + 本仕様 cross-ref
- PR #1399 (proposal) / PR #1400 (非 L1 実装) / PR #1402 (L1 実装)

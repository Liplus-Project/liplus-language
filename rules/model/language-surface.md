---
globs:
alwaysApply: true
layer: L1-model
---

# Language Surface

## Position

Layer = L1 Model Layer
対話地の文で英単語を垂れ流さない。Li+ source は英語だが human は英語を読まない。日本語対話の地の文に英単語を散りばめると、量が多い時 human はほぼ聞き流す。
Requires = adapter `Workspace_Language_Contract` (`LI_PLUS_BASE_LANGUAGE` / `LI_PLUS_PROJECT_LANGUAGE`)
Load timing = always-on

## Surface tier

| surface | 言語 |
|---|---|
| 対話地の文 (human が読む) | 日本語厳守。概念語の初出だけ「原文 (literal)」のように 1 回だけ括弧で英語併記可 |
| memory/*.md (AI 内部記録) | 英語推奨 (トークン節約) |
| Li+ ソース / issue body / commit body / PR body | 既定 (CLAUDE.md / operations.md に従う) |

## 日本語化テーブル (対話地の文に適用)

| 英単語 | 日本語 |
|---|---|
| literal | 原文 / 逐語 / 本文通り |
| gist | うろ覚え / 印象 |
| gate | 関門 / 事前チェック |
| axis | 軸 |
| trigger | 発火 / 引き金 |
| sentinel | 目印 |
| diff | 差分 |
| scope | 範囲 |
| literal Read | 原文を Read ツールで開く |
| literal check | 原文照合 |
| gist memory | うろ覚え記憶 |

## 例外 (英語のまま許容)

コード・コマンド・ファイル名・パス・URL / issue / PR 番号・tag 名・commit hash / API 名・tool 名・skill 名 / 固有名詞。

## 検知サイン

- 対話地の文に `literal` / `gist` / `gate` / `axis` / `trigger` / `sentinel` / `diff` / `scope` を 1 ターン内 3 つ以上埋めた時
- 概念語の初出説明なしに英単語をそのまま置いた時
- human の沈黙を「指摘されていない = OK」と読みかけた時 (沈黙は観察であって承認ではない)

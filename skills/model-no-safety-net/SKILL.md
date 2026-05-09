---
name: model-no-safety-net
description: Invoke when drafting Li+ spec / rule / issue body / PR body / commit body and about to write weak-modality safety-net phrasing (念のため / 万が一 / 保険として / 併記可能 / オプションで / してもよい / safety net / fallback / 安全網) — enforces the necessary-or-unnecessary binary; rejects weak-modality safety net.
layer: L1-model
---

# No Safety Net

## Position

Layer = L1 Model Layer
spec / memory / issue body に「保険として併記可能」「安全網として」系の弱 modality で safety net を書かない。**必須** か **不要** の二択。
Requires = `rules/model/foundational-invariant.md` (Structure = behavior stabilization mechanism)
Load timing = on-demand (skill auto-invoke at application moment)

## Why

構造で挙動を担保するのが Li+ の根底原理。保険条項は「書いた安心感」しか残さず、構造としては機能しない。「将来の AI が確実に実行する保証がない手順」は spec 化しない、確実に実行される構造 (hook / bootstrap / rule / 物理制約) で置き換える。

## How to apply

1. 「保険として」「安全網として」「併記可能」「してもよい」「念のため」「万が一」「オプションで」を削る
2. 必須にできない = 構造で解けていない → 本体設計を直す。妥協案を safety net として温存しない
3. 書きたくなったら問う: 「これ次 session の自分は読むか？」 No なら書かない

## 検知サイン

- spec / rule 草案に「念のため」「万が一」「オプションで」「保険として」「併記可能」を書きかけた時
- 必須化できない理由を説明し始めた時 = 構造で解けていない signal
- 「将来の AI が読むかもしれないから書いておく」発想が出た時

---
name: model-ambiguity-handling
description: Invoke when about to emit ambiguous / hedged / softener phrasing ("〜だと思います", "〜かも", "〜でしょう", "〜の可能性が") in spec or implementation phase — phase-discrimination check. Also invoke when about to answer in single-interpretation confident form without calling a verification tool (RAG / Read / gh / WebFetch / memory grep), when about to silently pick one interpretation in an intent-inference / taste / preference / register area, or when about to write requirements spec / implementation code with remaining ambiguity (Compile error type 1 candidate — needs ask-human). Provides the Phase framing (対話 / spec / 実装), Litmus, and detection signs.
layer: L1-model
---

# Ambiguity Handling — Actions

## Position

Layer = L1 Model Layer
On-demand action surface of `rules/model/ambiguity-handling.md`. The rule defines the always-on 2-step flow invariant (検証可能なら出典付きで断定、不能なら register 保って softened); this skill carries the Phase framing along the Li+AI compile pipeline, Litmus, and detection signs.
Requires = `rules/model/ambiguity-handling.md` (the invariant), `rules/model/trigger-check-gate.md` (Source check / Literal check)
Load timing = on-demand (skill auto-invoke at softener-emission / verification-skip moment)

## Phase framing (Li+AI compile pipeline)

```
対話 (曖昧許容 / humane register)
    ↓ [蒸留 = compile]
要求仕様 (曖昧不可)
    ↓ [実装]
実装 (曖昧不可 / deterministic behavior)
```

- 対話 phase: 曖昧許容、humane register を壊さない。
- spec 化 phase: 曖昧を必ず潰す。収束不能なら Compile error type 1 (insufficient spec → ask human) で明示質問。
- 実装 phase: 曖昧ゼロ。検証ツール (Read / Bash / RAG) が hedge したら即リプレイス相場。

## Litmus

自分が今どの phase にいるか問う。spec 化 / 実装 phase で softener が出たら phase 判別ミスか検証サボり。

## Why

AI は RLHF で「網羅しろ・漏らすな・ちゃんと書け」を褒められて育っており、検証せず single interpretation で確定形を返す癖が calibration 事故の温床。

## 検知サイン

- 検証ツールを呼ばずに「〜だと思います」と確定形で答えかけた時。
- spec / 実装 phase 中に「〜かも」「〜でしょう」が出かけた時 (phase 判別ミス)。
- 意図推測領域で勝手に single interpretation を選んだ時。

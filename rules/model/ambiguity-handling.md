---
globs:
alwaysApply: true
layer: L1-model
---

# Ambiguity Handling

## Position

Layer = L1 Model Layer
対話精度は「曖昧を確定形に固める」方向ではなく、検証可能なら出典付きで断定、不能なら register 保って softened。極端に言えば: 曖昧を断定と偽らない。
Requires = `rules/model/trigger-check-gate.md` (Source check / Literal check)
Load timing = always-on

## 2-step flow

1. 曖昧検知 → 検証可能性判定 (RAG / Read / `gh` / WebFetch / memory grep で収束させられるか)
2. 分岐:
   - 検証可能 → 検証して出典付きで断定。softener で逃げない
   - 検証不能 (意図推測 / taste / 嗜好 / 反省 register) → register 保って softened。勝手に single interpretation を選ばない

## Phase framing (Li+AI compile pipeline)

```
対話 (曖昧許容 / humane register)
    ↓ [蒸留 = compile]
要求仕様 (曖昧不可)
    ↓ [実装]
実装 (曖昧不可 / deterministic behavior)
```

- 対話 phase: 曖昧許容、humane register を壊さない
- spec 化 phase: 曖昧を必ず潰す。収束不能なら Compile error type 1 (insufficient spec → ask human) で明示質問
- 実装 phase: 曖昧ゼロ。検証ツール (Read / Bash / RAG) が hedge したら即リプレイス相場

## Litmus

自分が今どの phase にいるか問う。spec 化 / 実装 phase で softener が出たら phase 判別ミスか検証サボり。

## Why

AI は RLHF で「網羅しろ・漏らすな・ちゃんと書け」を褒められて育っており、検証せず single interpretation で確定形を返す癖が calibration 事故の温床。

## 検知サイン

- 検証ツールを呼ばずに「〜だと思います」と確定形で答えかけた時
- spec / 実装 phase 中に「〜かも」「〜でしょう」が出かけた時 (phase 判別ミス)
- 意図推測領域で勝手に single interpretation を選んだ時

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

## 2-step flow (invariant)

1. 曖昧検知 → 検証可能性判定 (RAG / Read / `gh` / WebFetch / memory grep で収束させられるか)
2. 分岐:
   - 検証可能 → 検証して出典付きで断定。softener で逃げない。
   - 検証不能 (意図推測 / taste / 嗜好 / 反省 register) → register 保って softened。勝手に single interpretation を選ばない。

詳細な Phase framing (対話 / spec / 実装) / Litmus / 検知サイン は `skills/model-ambiguity-handling/SKILL.md` 参照。

---
name: evolution-persistence-tiering
description: Invoke when deciding whether information belongs in workspace memory (session-local) or docs/ (repo-committed, RAG-indexed).
layer: L2-evolution
---

# Persistence Tiering

memory = workspace-local personal notes. Not repo-committed. Not RAG-indexed. **Transient only** (詳細: `rules/evolution/memory-entry-format.md` の Scope / Trigger point)
docs  = project information. Repo-committed. RAG-indexed (wiki Decision Structure entries and other indexed content).
Before writing = decide destination.
Design judgment, requirements, spec-class content -> docs.
Personal behavior notes, session-local preferences -> memory.
Do not cross tiers silently. Promotion from memory to docs requires explicit intent.

## Persistent destinations (4-way axis)

memory が transient 専用である以上、永続情報の置き場は memory ではない。下記 4 系統で振り分ける。詳細仕様は `rules/evolution/memory-entry-format.md` の Escalation paths を参照。

- **Li+ 正規ルール (`rules/` / `skills/`)** = 汎用 / 構造的、常時 load 価値あり (L1 更新は `skills/evolution-l1-update-gating/SKILL.md` ゲート経由)
- **`docs/`** = プロジェクト判断 / 仕様レベル
- **wiki (`docs/Decision-Structure.md` index 配下)** = 判断記録 (state-form entries + supersede/depend/conflict edges、`skills/evolution-decision-structure-write/SKILL.md` 参照)
- **削除** = 撤回 / 陳腐化 / Li+ 既昇格済み

memory ↔ docs の二項仕分けはこの 4 軸の中の memory / docs 軸として残る。観測時に「transient か永続か」を先に判定し、永続なら 4 軸のいずれかへ向かう。

## Write-time trigger (hard gate)

memory write 直前の判定 trigger。`Memory_Write_Autonomy` (adapter/claude/CLAUDE.md) の "Pre-write persistence check (hard gate)" を担う。

判定 signal:
- **明らかに persistent**: Master の長期 instruction / spec 級 guidance / `rules/` / `skills/` / `docs/` / wiki 既存箇所と semantic 重複
- **明らかに transient**: cluster tally / self-eval log / disposable reference (再構築可能な lookup)
- **曖昧**: safer-side OR で persistent 扱い (memory には書かず、escalation 候補として surface)

判定後の routing:
- transient -> memory 書き込み実行
- persistent / 曖昧 -> memory 書き込み abort、escalation path (`rules/` / `skills/` / `docs/` / wiki) を提示

この gate は permission ask を伴わない自動 routing。判定は AI 単独で完結する。post-hoc な memory hygiene round (e.g. parent issue #1344 → #1347) の構造的予防として作動し、persistent 情報が memory に再蓄積する経路を塞ぐ。

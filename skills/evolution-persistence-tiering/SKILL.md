---
name: evolution-persistence-tiering
description: Invoke when deciding whether information belongs in workspace memory (session-local) or docs/ (repo-committed, RAG-indexed).
layer: L2-evolution
---

# Persistence Tiering

memory = workspace-local personal notes. Not repo-committed. Not RAG-indexed. **Transient only** (詳細: `rules/evolution/memory-entry-format.md` の Scope / Trigger point)
docs  = project information. Repo-committed. RAG-indexed via docs/a.- entries and other indexed content.
Before writing = decide destination.
Design judgment, requirements, spec-class content -> docs.
Personal behavior notes, session-local preferences -> memory.
Do not cross tiers silently. Promotion from memory to docs requires explicit intent.

## Persistent destinations (4-way axis)

memory が transient 専用である以上、永続情報の置き場は memory ではない。下記 4 系統で振り分ける。詳細仕様は `rules/evolution/memory-entry-format.md` の Escalation paths を参照。

- **Li+ 正規ルール (`rules/` / `skills/`)** = 汎用 / 構造的、常時 load 価値あり (L1 更新は `skills/evolution-l1-update-gating/SKILL.md` ゲート経由)
- **`docs/`** = プロジェクト判断 / 仕様レベル
- **wiki (`docs/Decision-Log.md` index 配下)** = 判断記録 (`skills/evolution-decision-log-write/SKILL.md` 参照)
- **削除** = 撤回 / 陳腐化 / Li+ 既昇格済み

memory ↔ docs の二項仕分けはこの 4 軸の中の memory / docs 軸として残る。観測時に「transient か永続か」を先に判定し、永続なら 4 軸のいずれかへ向かう。

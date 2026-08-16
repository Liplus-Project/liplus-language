---
name: operations-foreground-webhook-intake
description: Do not invoke. Redirect stub with no invoke condition - the canonical lives in `rules/operations/main-agent-procedures.md` Foreground webhook notification intake, which loads without invocation.
layer: L4-operations
---

<foreground-webhook-notification-intake>

# Foreground Webhook Notification Intake

Redirect stub. Canonical = `rules/operations/main-agent-procedures.md` Foreground webhook notification intake: purpose, source priority, the `LI_PLUS_WEBHOOK_DELIVERY` mode interaction, the local webhook store resolution, foreground handling, and own-operation arrival confirmation all live there.

Why nothing is held here: the firing moment is the start of a user turn, which only the main agent has, and the bar keeps the main agent out of this surface. A pull surface cannot reach an actor whose trigger is the turn boundary itself — that mismatch is what was observed firing against the bar, and residency is the repair.

Why the file is not deleted: `adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` `## Optional Webhook Notification Flow` names this path, and that block is byte-frozen — `Li+update.md` derives the legacy trailer it strips from installed files out of that very block, so drift there breaks the migration for pre-migration installs. The pointer must resolve; this stub is what it resolves to. See `rules/operations/main-agent-procedures.md` The bar and its pair.

</foreground-webhook-notification-intake>

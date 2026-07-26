from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SENTINEL_BEGIN = b"# --- Li+ BEGIN ("
SENTINEL_END = b"# --- Li+ END ---"
WEBHOOK_HEADING = b"## Optional Webhook Notification Flow"
# Exact external trailer bodies from pre-migration commit 509fd0e.
KNOWN_LEGACY_BODIES = {
    "claude/CLAUDE.md": (
        "## Optional Webhook Notification Flow\n\n"
        "Webhook intake policy and procedures: `skills/operations-foreground-webhook-intake/SKILL.md`.\n"
        "Delivery mode (`poll` / `channel` / `mcp_hook`) is selected by `LI_PLUS_WEBHOOK_DELIVERY` in `Li+config.md`. Detailed mode behavior, mcp_tool hook entry semantics, and `github-webhook-mcp >= v0.11.3` connection requirement are documented in the skill above and `adapter/claude/hooks-settings.md`."
    ).encode("utf-8"),
    "codex/AGENTS.md": (
        "## Optional Webhook Notification Flow\n\n"
        "Webhook intake policy and procedures: `skills/operations-foreground-webhook-intake/SKILL.md`.\n"
        "Delivery mode (`poll` / `channel` / `mcp_hook`) is selected by `LI_PLUS_WEBHOOK_DELIVERY` in `Li+config.md`. Detailed mode behavior and `github-webhook-mcp >= v0.11.3` connection requirement are documented in the skill above and `adapter/codex/hooks-config.md`.\n"
        "Codex specifics: the Codex hooks schema documents only `type: \"command\"` handlers (no `type: \"mcp_tool\"` entry like Claude's `settings.json`), so the Codex adapter stays on `poll` \u2014 the `on-user-prompt` hook emits the reminder and the AI calls `mcp__github-webhook-mcp__get_pending_status` itself. Setting `channel` / `mcp_hook` only suppresses the reminder text; a Codex host without an equivalent realtime substrate falls back to `poll`."
    ).encode("utf-8"),
}


def split_sentinel_section(text: bytes) -> tuple[bytes, bytes, bytes]:
    start = text.index(SENTINEL_BEGIN)
    end = text.index(SENTINEL_END, start) + len(SENTINEL_END)
    return text[:start], text[start:end], text[end:]


def legacy_webhook_body(adapter_source: bytes) -> bytes:
    _, section, _ = split_sentinel_section(adapter_source)
    start = section.index(WEBHOOK_HEADING)
    return section[start : section.rindex(SENTINEL_END)].rstrip(b"\r\n")


def legacy_webhook_trailer(adapter_source: bytes) -> bytes:
    return b"\n\n" + legacy_webhook_body(adapter_source) + b"\n"


def known_legacy_webhook_trailer(adapter: str) -> bytes:
    return b"\n\n" + KNOWN_LEGACY_BODIES[adapter] + b"\n"


def remove_legacy_trailers(suffix: bytes, trailer: bytes) -> bytes:
    while suffix.startswith(trailer):
        suffix = suffix[len(trailer) :]
    return suffix


def apply_adapter_update(installed: bytes, adapter_source: bytes) -> bytes:
    prefix, old_section, suffix = split_sentinel_section(installed)
    if WEBHOOK_HEADING not in old_section:
        suffix = remove_legacy_trailers(suffix, legacy_webhook_trailer(adapter_source))
    _, source_section, _ = split_sentinel_section(adapter_source)
    return prefix + source_section + suffix


class AdapterUpdateContractTest(unittest.TestCase):
    def adapter_source(self, adapter: str, tag: str) -> bytes:
        source = (ROOT / "adapter" / adapter).read_bytes()
        return source.replace(b"{LI_PLUS_TAG}", tag.encode("ascii"))

    def legacy_installed(self, adapter: str, tag: str) -> bytes:
        source = self.adapter_source(adapter, tag)
        _, section, _ = split_sentinel_section(source)
        start = section.index(WEBHOOK_HEADING)
        old_section = section[:start].rstrip(b"\r\n") + b"\n\n" + SENTINEL_END
        trailer = known_legacy_webhook_trailer(adapter)
        return old_section + trailer + trailer + b"\nuser-owned suffix\n"

    def test_webhook_flow_is_owned_by_each_adapter_sentinel(self) -> None:
        for adapter in ("claude/CLAUDE.md", "codex/AGENTS.md"):
            source = self.adapter_source(adapter, "build-current")
            _, section, suffix = split_sentinel_section(source)
            self.assertEqual(section.count(WEBHOOK_HEADING), 1)
            self.assertEqual(suffix.count(WEBHOOK_HEADING), 0)
            self.assertEqual(legacy_webhook_body(source), KNOWN_LEGACY_BODIES[adapter])

    def test_sequential_tag_updates_remove_legacy_duplicates_and_preserve_user_suffix(self) -> None:
        for adapter in ("claude/CLAUDE.md", "codex/AGENTS.md"):
            installed = self.legacy_installed(adapter, "build-old")
            updated = apply_adapter_update(installed, self.adapter_source(adapter, "build-next"))
            updated_again = apply_adapter_update(updated, self.adapter_source(adapter, "build-later"))

            self.assertEqual(updated.count(WEBHOOK_HEADING), 1)
            self.assertEqual(updated_again.count(WEBHOOK_HEADING), 1)
            _, next_section, _ = split_sentinel_section(self.adapter_source(adapter, "build-next"))
            _, later_section, _ = split_sentinel_section(self.adapter_source(adapter, "build-later"))
            self.assertEqual(updated, next_section + b"\nuser-owned suffix\n")
            self.assertEqual(updated_again, later_section + b"\nuser-owned suffix\n")
            self.assertTrue(updated_again.endswith(b"\nuser-owned suffix\n"))
            self.assertIn(b"build-later", updated_again)

    def test_canonical_section_preserves_an_external_matching_user_block(self) -> None:
        for adapter in ("claude/CLAUDE.md", "codex/AGENTS.md"):
            source = self.adapter_source(adapter, "build-current")
            user_suffix = known_legacy_webhook_trailer(adapter) + b"\nuser-owned suffix\n"
            updated = apply_adapter_update(source + user_suffix, self.adapter_source(adapter, "build-later"))

            self.assertTrue(updated.endswith(user_suffix))
            self.assertEqual(updated.count(WEBHOOK_HEADING), 2)

    def test_non_byte_exact_legacy_suffix_is_preserved_without_normalization(self) -> None:
        for adapter in ("claude/CLAUDE.md", "codex/AGENTS.md"):
            legacy = self.legacy_installed(adapter, "build-old")
            _, old_section, _ = split_sentinel_section(legacy)
            crlf_trailer = known_legacy_webhook_trailer(adapter).replace(b"\n", b"\r\n")
            installed = old_section + crlf_trailer + b"user-owned suffix\n"
            updated = apply_adapter_update(installed, self.adapter_source(adapter, "build-next"))

            self.assertTrue(updated.endswith(crlf_trailer + b"user-owned suffix\n"))
            self.assertEqual(updated.count(WEBHOOK_HEADING), 2)

    def test_update_contract_requires_byte_exact_legacy_migration_for_both_adapters(self) -> None:
        update = (ROOT / "Li+update.md").read_text(encoding="utf-8")
        self.assertEqual(update.count("Legacy webhook trailer migration:"), 2)
        self.assertEqual(update.count("pre-migration ownership shape"), 2)
        self.assertEqual(update.count("byte-exact legacy trailer"), 2)
        self.assertEqual(update.count("preserve that suffix verbatim"), 2)


if __name__ == "__main__":
    unittest.main()

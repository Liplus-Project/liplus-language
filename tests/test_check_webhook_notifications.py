from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_webhook_notifications as module


class CheckWebhookNotificationsTest(unittest.TestCase):
    def test_resolve_state_dir_uses_configured_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace_root = Path(tmp)
            resolved = module.resolve_state_dir("custom-webhooks", workspace_root)
            self.assertEqual(resolved, workspace_root / "custom-webhooks")

    def test_resolve_state_dir_detects_parent_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace_root = Path(tmp) / "Codex"
            workspace_root.mkdir()
            parent_candidate = workspace_root.parent / "github-webhook-mcp"
            parent_candidate.mkdir()

            resolved = module.resolve_state_dir(None, workspace_root)

            self.assertEqual(resolved, parent_candidate)

    def test_consume_pending_removes_events_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "github-webhook-mcp"
            trigger_dir = state_dir / "trigger-events"
            runs_dir = state_dir / "codex-runs"
            trigger_dir.mkdir(parents=True)
            runs_dir.mkdir()

            events_path = state_dir / "events.json"
            event = {
                "id": "evt-1",
                "type": "issue_comment",
                "processed": False,
                "received_at": "2026-03-15T00:00:00Z",
                "payload": {
                    "action": "created",
                    "repository": {"full_name": "Liplus-Project/liplus-language"},
                    "sender": {"login": "master"},
                    "issue": {"number": 730, "title": "Webhook path fallback"},
                    "comment": {
                        "body": "見れる？",
                        "html_url": "https://github.com/Liplus-Project/liplus-language/issues/730#issuecomment-1",
                    },
                },
            }
            events_path.write_text(json.dumps([event], ensure_ascii=False, indent=2), encoding="utf-8")
            (trigger_dir / "evt-1.json").write_text("{}", encoding="utf-8")
            (runs_dir / "evt-1.md").write_text("result", encoding="utf-8")

            payload = module.consume_pending(events_path, [event], limit=5, state_dir=state_dir)

            self.assertEqual(payload["pending_count"], 1)
            self.assertEqual(payload["consumed_count"], 1)
            self.assertEqual(payload["remaining_count"], 0)
            self.assertEqual(payload["items"][0]["id"], "evt-1")
            self.assertEqual(json.loads(events_path.read_text(encoding="utf-8")), [])
            self.assertFalse((trigger_dir / "evt-1.json").exists())
            self.assertFalse((runs_dir / "evt-1.md").exists())

    def test_no_source_payload_is_silent_noop(self) -> None:
        payload = module.no_source_payload()
        self.assertEqual(payload["source"], "none")
        self.assertEqual(payload["pending_count"], 0)
        self.assertEqual(payload["items"], [])


if __name__ == "__main__":
    unittest.main()

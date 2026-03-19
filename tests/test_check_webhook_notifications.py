from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_webhook_notifications as module


class CheckWebhookNotificationsTest(unittest.TestCase):
    REPO = "Liplus-Project/liplus-language"
    BRANCH = "spec/786-notifications-layer"

    def make_state_dir(self) -> tuple[Path, Path, Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)

        state_dir = Path(tmp.name) / "github-webhook-mcp"
        trigger_dir = state_dir / "trigger-events"
        runs_dir = state_dir / "codex-runs"
        trigger_dir.mkdir(parents=True)
        runs_dir.mkdir()
        return state_dir, trigger_dir, runs_dir

    def inspect_context(self, **overrides: object) -> module.InspectContext:
        data = {
            "repo": self.REPO,
            "numbers": frozenset({"786"}),
            "branches": frozenset({self.BRANCH}),
            "internal_senders": frozenset({"liplus-lin-lay", "lipluscodex"}),
        }
        data.update(overrides)
        return module.InspectContext(**data)

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

    def test_infer_numbers_from_branch_names(self) -> None:
        numbers = module.infer_numbers_from_branches({"spec/786-notifications-layer", "778-repo-first"})
        self.assertEqual(numbers, {"786", "778"})

    def test_inspect_pending_classifies_foreground_notable_and_cleanup(self) -> None:
        state_dir, _, _ = self.make_state_dir()
        events_path = state_dir / "events.json"
        now = module.now_utc()
        recent = now - timedelta(hours=1)
        old = now - timedelta(hours=48)

        events = [
            {
                "id": "evt-1",
                "type": "issue_comment",
                "processed": False,
                "received_at": recent.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "payload": {
                    "action": "created",
                    "repository": {"full_name": self.REPO},
                    "sender": {"login": "master"},
                    "issue": {"number": 786, "title": "Notifications layer"},
                    "comment": {"body": "please check", "html_url": "https://example.com/1"},
                },
            },
            {
                "id": "evt-2",
                "type": "workflow_run",
                "processed": False,
                "received_at": old.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "payload": {
                    "action": "completed",
                    "repository": {"full_name": self.REPO},
                    "sender": {"login": "liplus-lin-lay"},
                    "workflow_run": {
                        "name": "Liplus Governance CI",
                        "head_branch": self.BRANCH,
                        "conclusion": "success",
                        "html_url": "https://example.com/2",
                    },
                },
            },
            {
                "id": "evt-3",
                "type": "issue_comment",
                "processed": False,
                "received_at": recent.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "payload": {
                    "action": "created",
                    "repository": {"full_name": self.REPO},
                    "sender": {"login": "friend"},
                    "issue": {"number": 999, "title": "Other thread"},
                    "comment": {"body": "FYI", "html_url": "https://example.com/3"},
                },
            },
            {
                "id": "evt-4",
                "type": "pull_request_review",
                "processed": False,
                "received_at": recent.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "payload": {
                    "action": "submitted",
                    "repository": {"full_name": self.REPO},
                    "sender": {"login": "reviewer"},
                    "pull_request": {
                        "number": 55,
                        "title": "Notifications PR",
                        "html_url": "https://example.com/4",
                        "head": {"ref": self.BRANCH},
                    },
                    "review": {
                        "state": "changes_requested",
                        "body": "Needs work",
                        "html_url": "https://example.com/review",
                    },
                },
            },
        ]
        events_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")

        payload = module.inspect_pending(
            events_path,
            limit=10,
            state_dir=state_dir,
            context=self.inspect_context(),
            cleanup_after=timedelta(hours=24),
        )

        self.assertEqual(payload["pending_count"], 4)
        self.assertEqual(payload["relevant_count"], 3)
        self.assertEqual(payload["notable_count"], 3)
        self.assertEqual(payload["mention_count"], 4)
        self.assertEqual(payload["cleanup_candidate_count"], 1)
        self.assertEqual({item["id"] for item in payload["relevant_items"]}, {"evt-1", "evt-2", "evt-4"})
        self.assertEqual({item["id"] for item in payload["notable_items"]}, {"evt-1", "evt-3", "evt-4"})
        self.assertEqual([item["id"] for item in payload["cleanup_candidates"]], ["evt-2"])

    def test_mark_events_read_preserves_history(self) -> None:
        state_dir, _, _ = self.make_state_dir()
        events_path = state_dir / "events.json"
        event = {
            "id": "evt-1",
            "type": "issue_comment",
            "processed": False,
            "received_at": "2026-03-15T00:00:00Z",
            "payload": {
                "action": "created",
                "repository": {"full_name": self.REPO},
                "sender": {"login": "master"},
                "issue": {"number": 786, "title": "Notifications layer"},
                "comment": {"body": "seen?", "html_url": "https://example.com/1"},
            },
        }
        events_path.write_text(json.dumps([event], ensure_ascii=False, indent=2), encoding="utf-8")

        read_ids = module.mark_events_read(events_path, [event], {"evt-1"}, state_dir=state_dir)
        payload = module.inspect_pending(
            events_path,
            limit=5,
            state_dir=state_dir,
            context=self.inspect_context(),
            cleanup_after=timedelta(hours=24),
        )

        self.assertEqual(read_ids, ["evt-1"])
        self.assertEqual(payload["pending_count"], 0)
        saved = json.loads(events_path.read_text(encoding="utf-8"))
        self.assertTrue(saved[0]["processed"])

    def test_claim_ids_preserves_existing_claim_by_default(self) -> None:
        state_dir, _, _ = self.make_state_dir()

        claimed_ids, skipped = module.claim_ids(
            state_dir,
            ["evt-1"],
            claimant="Lin",
            reason="foreground",
            force=False,
        )
        self.assertEqual(claimed_ids, ["evt-1"])
        self.assertEqual(skipped, [])

        claimed_ids, skipped = module.claim_ids(
            state_dir,
            ["evt-1"],
            claimant="Lay",
            reason="other session",
            force=False,
        )
        self.assertEqual(claimed_ids, [])
        self.assertEqual(skipped[0]["claimed_by"], "Lin")

    def test_cleanup_safe_success_removes_only_old_internal_success(self) -> None:
        state_dir, trigger_dir, runs_dir = self.make_state_dir()
        events_path = state_dir / "events.json"
        old = "2020-01-01T00:00:00Z"

        success_event = {
            "id": "evt-1",
            "type": "workflow_run",
            "processed": False,
            "received_at": old,
            "payload": {
                "action": "completed",
                "repository": {"full_name": self.REPO},
                "sender": {"login": "liplus-lin-lay"},
                "workflow_run": {
                    "name": "Liplus Governance CI",
                    "head_branch": "build-2026-03-19.3",
                    "conclusion": "success",
                    "html_url": "https://example.com/workflow",
                },
            },
        }
        comment_event = {
            "id": "evt-2",
            "type": "issue_comment",
            "processed": False,
            "received_at": old,
            "payload": {
                "action": "created",
                "repository": {"full_name": self.REPO},
                "sender": {"login": "master"},
                "issue": {"number": 900, "title": "Keep me"},
                "comment": {"body": "still relevant", "html_url": "https://example.com/comment"},
            },
        }
        events = [success_event, comment_event]
        events_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
        for event in events:
            (trigger_dir / f"{event['id']}.json").write_text("{}", encoding="utf-8")
            (runs_dir / f"{event['id']}.md").write_text("result", encoding="utf-8")

        evaluated = module.evaluate_pending(
            events,
            claims={},
            context=self.inspect_context(numbers=frozenset(), branches=frozenset()),
            cleanup_after=timedelta(hours=24),
        )
        removed_ids, deleted_paths = module.remove_events(
            events_path,
            events,
            {item["id"] for item in evaluated["cleanup"]},
            state_dir=state_dir,
        )

        self.assertEqual(removed_ids, ["evt-1"])
        self.assertIn(str(trigger_dir / "evt-1.json"), deleted_paths)
        self.assertIn(str(runs_dir / "evt-1.md"), deleted_paths)
        remaining = json.loads(events_path.read_text(encoding="utf-8"))
        self.assertEqual([event["id"] for event in remaining], ["evt-2"])

    def test_consume_pending_removes_events_and_artifacts(self) -> None:
        state_dir, trigger_dir, runs_dir = self.make_state_dir()
        events_path = state_dir / "events.json"
        event = {
            "id": "evt-1",
            "type": "issue_comment",
            "processed": False,
            "received_at": "2026-03-15T00:00:00Z",
            "payload": {
                "action": "created",
                "repository": {"full_name": self.REPO},
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

    def test_consume_pending_drains_backlog_beyond_limit(self) -> None:
        state_dir, trigger_dir, runs_dir = self.make_state_dir()
        events_path = state_dir / "events.json"
        events = [
            {
                "id": "evt-1",
                "type": "issues",
                "processed": False,
                "received_at": "2026-03-15T00:00:00Z",
                "payload": {
                    "action": "opened",
                    "repository": {"full_name": self.REPO},
                    "issue": {"number": 1, "title": "one"},
                },
            },
            {
                "id": "evt-2",
                "type": "issues",
                "processed": False,
                "received_at": "2026-03-15T00:01:00Z",
                "payload": {
                    "action": "opened",
                    "repository": {"full_name": self.REPO},
                    "issue": {"number": 2, "title": "two"},
                },
            },
            {
                "id": "evt-3",
                "type": "issues",
                "processed": False,
                "received_at": "2026-03-15T00:02:00Z",
                "payload": {
                    "action": "opened",
                    "repository": {"full_name": self.REPO},
                    "issue": {"number": 3, "title": "three"},
                },
            },
        ]
        events_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
        for event in events:
            (trigger_dir / f"{event['id']}.json").write_text("{}", encoding="utf-8")
            (runs_dir / f"{event['id']}.md").write_text("result", encoding="utf-8")

        payload = module.consume_pending(events_path, events, limit=1, state_dir=state_dir)

        self.assertEqual(payload["pending_count"], 3)
        self.assertEqual(payload["consumed_count"], 3)
        self.assertEqual(payload["remaining_count"], 0)
        self.assertEqual([item["id"] for item in payload["items"]], ["evt-3"])
        self.assertEqual(json.loads(events_path.read_text(encoding="utf-8")), [])
        for event in events:
            self.assertFalse((trigger_dir / f"{event['id']}.json").exists())
            self.assertFalse((runs_dir / f"{event['id']}.md").exists())

    def test_no_source_payload_is_silent_noop(self) -> None:
        payload = module.no_source_payload()
        self.assertEqual(payload["source"], "none")
        self.assertEqual(payload["pending_count"], 0)
        self.assertEqual(payload["relevant_count"], 0)
        self.assertEqual(payload["items"], [])


if __name__ == "__main__":
    unittest.main()

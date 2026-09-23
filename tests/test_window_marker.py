"""`scripts/window_marker.py` keeps the span record its callers read.

Claim under test: issue #1901 requirements 1, 2, 4, 6 and 7, as carried into
`skills/evolution-parallel-agent-eval/SKILL.md` Procedure steps 2 and 5. The
requirements are stated there and in the issue body, not here.

Every case runs on a temporary directory standing in for `.claude/`, holding one
`rules/` file and one `skills/` file. Observed on that directory:

- a second `open` is refused while a mark stands, and the standing record is left
  as it was;
- `open` refuses a discriminator whose two counts are equal, one that names no
  version, and a wait that is not a positive finite number, and creates no mark
  when it refuses;
- `applied` is refused while the wait runs with no response recorded, and accepted
  once a response is recorded or `wait_until` has passed;
- `close` leaves a record under `history/` carrying the close, so a directory that
  has closed a span reports `closed` where one that has not opened one reports
  `never_opened`;
- a mark with no record, the state left by an agent stopped between `mkdir` and the
  record's write, reads as open and is closed by a second caller;
- `status` on an open mark names `restore_then_close` only while the tree carries the
  recorded apply digest, `close` while it carries the restore digest, and
  `close_without_restore` when it carries neither, the mark with no record included
  (issue #2016).
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import window_marker as module


NOW = datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)
RULE = Path("rules") / "evolution" / "sample.md"
SKILL = Path("skills") / "sample" / "SKILL.md"
CANONICAL = "canonical body\n"
DRAFT = "canonical body\na line only the draft carries\n"


def discriminator(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "string": "a line only the draft carries",
        "names": {"draft": "PR #1 at abc1234", "reference": "workspace .claude/ at v1.0.0"},
        "counts": {"draft": 1, "reference": 0},
    }
    data.update(overrides)
    return data


class WindowMarkerCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.claude = Path(self._tmp.name) / ".claude"
        for relative, body in ((RULE, CANONICAL), (SKILL, "skill body\n")):
            (self.claude / relative).parent.mkdir(parents=True)
            (self.claude / relative).write_text(body, encoding="utf-8")

    def open(self, now: datetime = NOW, **overrides: object) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "procedure": "evolution-parallel-agent-eval",
            "backup_path": str(Path(self._tmp.name) / "backup"),
            "discriminator": discriminator(),
            "wait_seconds": 60.0,
            "now": now,
        }
        kwargs.update(overrides)
        return module.open_window(self.claude, **kwargs)  # type: ignore[arg-type]

    def write_rule(self, body: str) -> None:
        (self.claude / RULE).write_text(body, encoding="utf-8")

    def open_dir(self) -> Path:
        return module.mark_root(self.claude) / module.OPEN_DIRNAME

    def history_names(self) -> list[str]:
        history = module.mark_root(self.claude) / module.HISTORY_DIRNAME
        return sorted(p.name for p in history.iterdir()) if history.is_dir() else []

    def applied_span(self) -> None:
        self.open()
        module.record_response(self.claude, "peer", now=NOW + timedelta(seconds=5))
        self.write_rule(DRAFT)
        module.mark_applied(self.claude, now=NOW + timedelta(seconds=6))


class OpenTest(WindowMarkerCase):
    def test_open_records_the_restore_target_before_the_apply(self) -> None:
        before = module.tree_digest(self.claude)
        record = self.open()
        self.assertEqual(record["restore_digest"], before)
        self.assertEqual(record["opened_at"], NOW.isoformat())
        self.assertEqual(record["wait_until"], (NOW + timedelta(seconds=60)).isoformat())
        self.assertEqual(record["procedure"], "evolution-parallel-agent-eval")
        self.assertIsNone(record["applied_at"])
        self.assertEqual(module.read_record(self.open_dir()), record)

    def test_writing_the_record_leaves_the_digest_where_it_was(self) -> None:
        before = module.tree_digest(self.claude)
        self.open()
        self.assertEqual(module.tree_digest(self.claude), before)

    def test_second_open_is_refused_and_leaves_the_standing_record(self) -> None:
        first = self.open()
        with self.assertRaises(module.WindowHeld):
            self.open(now=NOW + timedelta(hours=6), procedure="another-procedure")
        self.assertEqual(module.read_record(self.open_dir()), first)

    def test_refused_open_creates_no_mark(self) -> None:
        refused_discriminators = (
            discriminator(counts={"draft": 1, "reference": 1}),
            discriminator(names={"draft": "PR #1 at abc1234"}),
            discriminator(string=" "),
            "not an object",
        )
        for bad in refused_discriminators:
            with self.subTest(discriminator=bad):
                with self.assertRaises(module.WindowError):
                    self.open(discriminator=bad)
        for wait in (0, -1.0, float("nan"), float("inf")):
            with self.subTest(wait_seconds=wait):
                with self.assertRaises(module.WindowError):
                    self.open(wait_seconds=wait)
        self.assertFalse(module.mark_root(self.claude).exists())


class WaitTest(WindowMarkerCase):
    def test_applied_is_refused_while_the_wait_runs(self) -> None:
        record = self.open()
        self.write_rule(DRAFT)
        self.assertFalse(module.wait_is_over(record, NOW + timedelta(seconds=30)))
        with self.assertRaises(module.WindowError):
            module.mark_applied(self.claude, now=NOW + timedelta(seconds=30))
        self.assertIsNone(module.read_record(self.open_dir())["applied_at"])

    def test_a_response_ends_the_wait(self) -> None:
        self.open()
        module.record_response(self.claude, "peer", now=NOW + timedelta(seconds=5))
        self.write_rule(DRAFT)
        record = module.mark_applied(self.claude, now=NOW + timedelta(seconds=6))
        self.assertEqual(record["applied_at"], (NOW + timedelta(seconds=6)).isoformat())
        self.assertEqual(record["applied_digest"], module.tree_digest(self.claude))
        self.assertEqual(record["responses"][0]["by"], "peer")

    def test_the_wait_ends_on_its_deadline_without_a_response(self) -> None:
        self.open()
        self.write_rule(DRAFT)
        record = module.mark_applied(self.claude, now=NOW + timedelta(seconds=61))
        self.assertEqual(record["responses"], [])
        self.assertIsNotNone(record["applied_at"])

    def test_an_apply_that_moved_nothing_is_refused(self) -> None:
        self.open()
        with self.assertRaises(module.WindowError):
            module.mark_applied(self.claude, now=NOW + timedelta(seconds=61))

    def test_a_response_after_the_apply_is_refused(self) -> None:
        self.applied_span()
        with self.assertRaises(module.WindowError):
            module.record_response(self.claude, "late peer", now=NOW + timedelta(seconds=7))


class CloseTest(WindowMarkerCase):
    def test_close_keeps_the_record_under_history(self) -> None:
        self.applied_span()
        self.write_rule(CANONICAL)
        destination, record = module.close_window(self.claude, "opener", now=NOW + timedelta(minutes=2))
        self.assertFalse(self.open_dir().exists())
        self.assertEqual(module.read_record(destination), record)
        self.assertEqual(record["closed_by"], "opener")
        self.assertEqual(record["closed_at"], (NOW + timedelta(minutes=2)).isoformat())
        self.assertTrue(record["restore_matched"])
        self.assertEqual(module.status(self.claude), {"state": "closed", "last": record})

    def test_close_records_a_tree_left_unrestored(self) -> None:
        self.applied_span()
        _, record = module.close_window(self.claude, "another agent", now=NOW + timedelta(minutes=2))
        self.assertFalse(record["restore_matched"])
        self.assertEqual(record["restored_digest"], record["applied_digest"])

    def test_never_opened_and_closed_read_differently(self) -> None:
        self.assertEqual(module.status(self.claude), {"state": "never_opened"})
        self.open()
        module.close_window(self.claude, "opener", now=NOW + timedelta(seconds=10))
        self.assertEqual(module.status(self.claude)["state"], "closed")

    def test_the_mark_is_taken_again_after_a_close(self) -> None:
        self.open()
        module.close_window(self.claude, "opener", now=NOW + timedelta(seconds=10))
        self.open(now=NOW + timedelta(minutes=5))
        module.close_window(self.claude, "opener", now=NOW + timedelta(minutes=6))
        self.assertEqual(len(self.history_names()), 2)

    def test_a_mark_with_no_record_reads_open_and_is_closed_by_a_second_caller(self) -> None:
        self.open_dir().mkdir(parents=True)
        report = module.status(self.claude)
        self.assertEqual(report["state"], "open")
        self.assertEqual(report["record"], {})
        with self.assertRaises(module.WindowHeld):
            self.open()
        _, record = module.close_window(self.claude, "another agent", now=NOW)
        self.assertIsNone(record["restore_matched"])
        self.assertEqual(module.status(self.claude)["state"], "closed")


class StatusTest(WindowMarkerCase):
    def test_tree_carries_follows_the_apply_and_the_restore(self) -> None:
        self.open()
        self.assertEqual(module.status(self.claude)["tree_carries"], "restore")
        module.record_response(self.claude, "peer", now=NOW + timedelta(seconds=5))
        self.write_rule(DRAFT)
        module.mark_applied(self.claude, now=NOW + timedelta(seconds=6))
        self.assertEqual(module.status(self.claude)["tree_carries"], "applied")
        self.write_rule("some third body\n")
        self.assertEqual(module.status(self.claude)["tree_carries"], "neither")
        self.write_rule(CANONICAL)
        self.assertEqual(module.status(self.claude)["tree_carries"], "restore")

    def test_recovery_names_a_restore_only_while_the_tree_carries_the_apply(self) -> None:
        self.open()
        self.assertEqual(module.status(self.claude)["recovery"], "close")
        module.record_response(self.claude, "peer", now=NOW + timedelta(seconds=5))
        self.write_rule(DRAFT)
        module.mark_applied(self.claude, now=NOW + timedelta(seconds=6))
        self.assertEqual(module.status(self.claude)["recovery"], "restore_then_close")
        self.write_rule(CANONICAL)
        self.assertEqual(module.status(self.claude)["recovery"], "close")

    def test_a_tree_written_after_the_apply_is_not_restored_over(self) -> None:
        self.applied_span()
        (self.claude / SKILL).write_text("skill body at a later tag\n", encoding="utf-8")
        report = module.status(self.claude)
        self.assertEqual(report["tree_carries"], "neither")
        self.assertEqual(report["recovery"], "close_without_restore")

    def test_a_mark_with_no_record_is_closed_without_restore(self) -> None:
        self.open_dir().mkdir(parents=True)
        self.assertEqual(module.status(self.claude)["recovery"], "close_without_restore")


class CliTest(WindowMarkerCase):
    def run_cli(self, *argv: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = module.main(["--claude-dir", str(self.claude), *argv])
        return code, out.getvalue()

    def test_the_span_runs_end_to_end_through_the_command_line(self) -> None:
        opener = (
            "open",
            "--procedure", "evolution-parallel-agent-eval",
            "--backup-path", "backup",
            "--discriminator", json.dumps(discriminator()),
            "--wait-seconds", "3600",
        )
        self.assertEqual(self.run_cli(*opener)[0], 0)
        self.assertEqual(self.run_cli("ready")[0], module.EXIT_WAITING)
        self.assertEqual(self.run_cli(*opener)[0], module.EXIT_HELD)
        self.assertEqual(self.run_cli("respond", "--responder", "peer")[0], 0)
        self.assertEqual(self.run_cli("ready")[0], 0)
        self.write_rule(DRAFT)
        self.assertEqual(self.run_cli("applied")[0], 0)
        self.write_rule(CANONICAL)
        self.assertEqual(self.run_cli("close", "--closed-by", "opener")[0], 0)
        code, out = self.run_cli("status")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["last"]["restore_matched"])
        self.assertEqual(self.run_cli("respond", "--responder", "peer")[0], module.EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()

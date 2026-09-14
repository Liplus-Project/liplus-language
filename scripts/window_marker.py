#!/usr/bin/env python3
"""Mark on disk the span in which `.claude/` holds an applied draft.

`skills/evolution-parallel-agent-eval` Procedure step 2 applies an operational copy
to `.claude/` and step 5 restores it. Between the two, `.claude/` is not the tree its
other readers take it to be. The span is opened and closed by one agent, so an agent
that stops inside it leaves the span open with nobody scheduled to close it; measured
once at about four and a half hours (issue #1901). This module is the structure that
outlives that agent: the span leaves a record on disk that any agent can read and any
agent can close.

Five properties carry the design, and one is deliberately absent.

Taking the mark is binary. `mkdir` either creates the open directory or raises, so two
agents cannot both pass through a read-then-write gap. The shape is the one
`scripts/measure_rule_effect.py` `acquire_lock` uses. The implementation is separate
from that lock rather than shared with it: that lock removes itself on a clean exit,
and this record must not.

Closing keeps the record. `close` writes the close into it and moves it under
`history/`. A record deleted on close would make "no open mark" mean both "never
opened" and "closed", and reading one as the other produced a wrong report once
(issue #1901 observation 5).

The record carries what a stranger needs to end the span: the procedure that opened
it, when, the digest of the tree to restore to, and where the backup sits. The agent
that finds an abandoned mark is not the one that wrote it and has no channel to it.

Both ends of the span carry a time and a digest. `opened_at` is when the mark was
taken, `applied_at` when the draft was recorded as landed, `closed_at` when the record
was closed. The digests are computed here over the surfaces an operational copy
writes (`DIGEST_SCOPE`), never supplied by the caller, so two of them always compare
like with like.

The disclosure precedes the apply, and the wait between them is recorded. The record
written by `open` is the disclosure. `applied` refuses until a response has been
recorded or `wait_until` has passed, whichever comes first: a disclosure followed
within seconds by the apply leaves a reader nothing to check before the tree changes,
and a wait only a response could end would let a silent peer hold the span shut.

Absent: a stale threshold. A mark is never taken over on age. `open` refuses while one
stands, and the mark's presence is the whole signal. A threshold has to sit above the
length of a span whose closer is alive, and before this record existed nothing kept
that length (issue #1901, policy (iii)).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STATE_DIRNAME = "state"
MARK_DIRNAME = "window"
OPEN_DIRNAME = "open"
HISTORY_DIRNAME = "history"
RECORD_FILENAME = "window.json"
STAMP_FORMAT = "%Y%m%dT%H%M%S%fZ"

# The surfaces an operational copy writes (`skills/evolution-parallel-agent-eval`
# Procedure step 2): rule bodies and skill bodies. The mark sits under `state/`,
# outside this scope, so writing the record does not move the digest it records.
DIGEST_SCOPE = ("rules", "skills")

EXIT_WAITING = 1
EXIT_ERROR = 2
EXIT_HELD = 3


class WindowError(Exception):
    """The mark could not be taken, changed, or read as asked."""


class WindowHeld(WindowError):
    """A mark is already open."""


def mark_root(claude_dir: Path) -> Path:
    return Path(claude_dir) / STATE_DIRNAME / MARK_DIRNAME


def _open_dir(claude_dir: Path) -> Path:
    return mark_root(claude_dir) / OPEN_DIRNAME


def _history_dir(claude_dir: Path) -> Path:
    return mark_root(claude_dir) / HISTORY_DIRNAME


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


def _parse(stamp: Any) -> datetime | None:
    if not isinstance(stamp, str):
        return None
    try:
        moment = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def _require_text(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WindowError(f"{what} must be a non-empty string")
    return value


def _require_claude_dir(claude_dir: Path) -> None:
    if not Path(claude_dir).is_dir():
        raise WindowError(f"{claude_dir} is not a directory")


def tree_digest(claude_dir: Path) -> str:
    """Digest of every file under `DIGEST_SCOPE`, by relative path and content."""
    root = Path(claude_dir)
    files: list[tuple[str, Path]] = []
    for scope in DIGEST_SCOPE:
        base = root / scope
        if base.is_dir():
            files.extend((p.relative_to(root).as_posix(), p) for p in base.rglob("*") if p.is_file())
    outer = hashlib.sha256()
    for relative, path in sorted(files):
        outer.update(relative.encode("utf-8"))
        outer.update(b"\0")
        outer.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        outer.update(b"\n")
    return "sha256:" + outer.hexdigest()


def read_record(directory: Path) -> dict[str, Any]:
    """The record inside a mark, or `{}` when it cannot be read.

    Unreadable covers an agent stopped between `mkdir` and the record's write. The mark
    then stands with no record: `status` still reports it open, `open` still refuses,
    and `close` still ends it.
    """
    try:
        data = json.loads((Path(directory) / RECORD_FILENAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_record(directory: Path, record: dict[str, Any]) -> None:
    try:
        (Path(directory) / RECORD_FILENAME).write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise WindowError(f"the record at {directory} could not be written: {error}") from None


def _require_open(claude_dir: Path) -> tuple[Path, dict[str, Any]]:
    open_dir = _open_dir(claude_dir)
    if not open_dir.is_dir():
        raise WindowError(f"no mark is open at {open_dir}")
    return open_dir, read_record(open_dir)


def _require_readable(record: dict[str, Any]) -> None:
    if not record.get("opened_at"):
        raise WindowError("the open mark carries no readable record; only close can end it")


def _validate_discriminator(discriminator: Any) -> dict[str, Any]:
    """Refuse a discriminator that does not separate, or does not say between what.

    A string present in the draft settles only whether a reader's context is older or
    newer than one named version. So the two versions it separates are named, the count
    on each side is given, and equal counts are refused (issue #1901 requirement 6).
    """
    if not isinstance(discriminator, dict):
        raise WindowError("discriminator must be an object")
    text = _require_text(discriminator.get("string"), "discriminator field 'string'")
    names = discriminator.get("names")
    counts = discriminator.get("counts")
    if not isinstance(names, dict) or not isinstance(counts, dict):
        raise WindowError("discriminator must carry 'names' and 'counts' objects")
    for side in ("draft", "reference"):
        _require_text(names.get(side), f"discriminator names.{side}")
        count = counts.get(side)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise WindowError(f"discriminator counts.{side} must be a count")
    if counts["draft"] == counts["reference"]:
        raise WindowError("discriminator counts are equal on both sides, so it separates nothing")
    return {
        "string": text,
        "names": {side: names[side] for side in ("draft", "reference")},
        "counts": {side: counts[side] for side in ("draft", "reference")},
    }


def wait_is_over(record: dict[str, Any], now: datetime | None = None) -> bool:
    """A response is recorded, or `wait_until` has passed - whichever comes first."""
    if record.get("responses"):
        return True
    deadline = _parse(record.get("wait_until"))
    return deadline is not None and _now(now) >= deadline


def open_window(
    claude_dir: Path,
    procedure: str,
    backup_path: str,
    discriminator: Any,
    wait_seconds: float,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Take the mark before anything is applied, or raise `WindowHeld`.

    The record written here is the disclosure. `restore_digest` is taken now, while
    `.claude/` still carries the tree the span will be restored to.
    """
    _require_claude_dir(claude_dir)
    _require_text(procedure, "procedure")
    _require_text(backup_path, "backup_path")
    checked = _validate_discriminator(discriminator)
    if not isinstance(wait_seconds, (int, float)) or not math.isfinite(wait_seconds) or wait_seconds <= 0:
        raise WindowError("wait_seconds must be a positive number of seconds")

    moment = _now(now)
    restore_digest = tree_digest(claude_dir)
    open_dir = _open_dir(claude_dir)
    open_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        open_dir.mkdir()
    except FileExistsError:
        held = read_record(open_dir)
        raise WindowHeld(
            f"a mark is already open at {open_dir} (procedure {held.get('procedure', 'unreadable')},"
            f" opened_at {held.get('opened_at', 'unreadable')})"
        ) from None

    record: dict[str, Any] = {
        "procedure": procedure,
        "opened_at": moment.isoformat(),
        "restore_digest": restore_digest,
        "backup_path": backup_path,
        "discriminator": checked,
        "wait_until": (moment + timedelta(seconds=wait_seconds)).isoformat(),
        "responses": [],
        "applied_at": None,
        "applied_digest": None,
    }
    _write_record(open_dir, record)
    return record


def record_response(claude_dir: Path, responder: str, now: datetime | None = None) -> dict[str, Any]:
    """Record that the disclosure was answered, which ends the wait."""
    _require_text(responder, "responder")
    open_dir, record = _require_open(claude_dir)
    _require_readable(record)
    if record.get("applied_at"):
        raise WindowError("the draft is already recorded as applied; a response now answers nothing")
    responses = record.get("responses") if isinstance(record.get("responses"), list) else []
    responses.append({"by": responder, "at": _now(now).isoformat()})
    record["responses"] = responses
    _write_record(open_dir, record)
    return record


def mark_applied(claude_dir: Path, now: datetime | None = None) -> dict[str, Any]:
    """Record that the draft has landed: when, and the digest `.claude/` now carries.

    Refused while the wait runs, so a record showing an apply shows it after the
    disclosure had its time. Refused when the digest has not moved: nothing reached the
    digest scope, and the two digests would name one state.
    """
    open_dir, record = _require_open(claude_dir)
    _require_readable(record)
    if record.get("applied_at"):
        raise WindowError("the draft is already recorded as applied")
    moment = _now(now)
    if not wait_is_over(record, moment):
        raise WindowError(f"the wait runs until {record.get('wait_until')} and no response is recorded")
    digest = tree_digest(claude_dir)
    if digest == record.get("restore_digest"):
        raise WindowError("the tree still carries the restore digest; nothing was applied to rules/ or skills/")
    record["applied_at"] = moment.isoformat()
    record["applied_digest"] = digest
    _write_record(open_dir, record)
    return record


def close_window(
    claude_dir: Path, closed_by: str, now: datetime | None = None
) -> tuple[Path, dict[str, Any]]:
    """Write the close into the record and move it under `history/`.

    Nothing is deleted. Any agent may close, so `closed_by` is written in. The digest
    `.claude/` carries at the close is compared with the restore target and the result
    recorded; a mismatch is recorded rather than refused, because refusing would leave a
    span nobody can end.
    """
    _require_text(closed_by, "closed_by")
    open_dir, record = _require_open(claude_dir)
    moment = _now(now)
    restored = tree_digest(claude_dir)
    restore_target = record.get("restore_digest")
    record["closed_at"] = moment.isoformat()
    record["closed_by"] = closed_by
    record["restored_digest"] = restored
    record["restore_matched"] = (restored == restore_target) if restore_target else None
    _write_record(open_dir, record)

    history = _history_dir(claude_dir)
    history.mkdir(parents=True, exist_ok=True)
    name = (_parse(record.get("opened_at")) or moment).astimezone(timezone.utc).strftime(STAMP_FORMAT)
    destination = history / name
    suffix = 1
    while destination.exists():
        suffix += 1
        destination = history / f"{name}-{suffix}"
    try:
        open_dir.rename(destination)
    except FileNotFoundError:
        raise WindowError("the mark was closed by another agent first") from None
    return destination, record


def status(claude_dir: Path, now: datetime | None = None) -> dict[str, Any]:
    """What an agent walking into the workspace can say about the span."""
    _require_claude_dir(claude_dir)
    moment = _now(now)
    open_dir = _open_dir(claude_dir)
    if open_dir.is_dir():
        record = read_record(open_dir)
        opened = _parse(record.get("opened_at"))
        if opened is None:
            try:
                opened = datetime.fromtimestamp(open_dir.stat().st_mtime, tz=timezone.utc)
            except OSError:
                opened = moment
        current = tree_digest(claude_dir)
        if current == record.get("applied_digest"):
            carries = "applied"
        elif current == record.get("restore_digest"):
            carries = "restore"
        else:
            carries = "neither"
        return {
            "state": "open",
            "age_seconds": (moment - opened).total_seconds(),
            "current_digest": current,
            "tree_carries": carries,
            "record": record,
        }

    history = _history_dir(claude_dir)
    closed = sorted(p.name for p in history.iterdir() if p.is_dir()) if history.is_dir() else []
    if closed:
        return {"state": "closed", "last": read_record(history / closed[-1])}
    return {"state": "never_opened"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mark on disk the span in which .claude/ holds an applied draft.")
    parser.add_argument("--claude-dir", required=True, help="the .claude directory the draft is applied to")
    sub = parser.add_subparsers(dest="command", required=True)

    opener = sub.add_parser("open", help="take the mark before applying anything; the record is the disclosure")
    opener.add_argument("--procedure", required=True)
    opener.add_argument("--backup-path", required=True)
    opener.add_argument(
        "--discriminator",
        required=True,
        help='JSON: {"string": ..., "names": {"draft": ..., "reference": ...}, "counts": {"draft": n, "reference": n}}',
    )
    opener.add_argument("--wait-seconds", type=float, required=True)

    responder = sub.add_parser("respond", help="record an answer to the disclosure, which ends the wait")
    responder.add_argument("--responder", required=True)

    sub.add_parser("ready", help="exit 0 once the apply may proceed, 1 while the wait runs")
    sub.add_parser("applied", help="record that the draft has landed")

    closer = sub.add_parser("close", help="write the close into the record and move it under history/")
    closer.add_argument("--closed-by", required=True)

    sub.add_parser("status", help="report whether a mark is open and what the tree carries")

    args = parser.parse_args(argv)
    claude_dir = Path(args.claude_dir)

    try:
        if args.command == "open":
            try:
                discriminator = json.loads(args.discriminator)
            except ValueError as error:
                raise WindowError(f"--discriminator is not JSON: {error}") from None
            result: Any = open_window(
                claude_dir, args.procedure, args.backup_path, discriminator, args.wait_seconds
            )
        elif args.command == "respond":
            result = record_response(claude_dir, args.responder)
        elif args.command == "ready":
            _, record = _require_open(claude_dir)
            _require_readable(record)
            if not wait_is_over(record):
                print(f"waiting until {record.get('wait_until')}")
                return EXIT_WAITING
            result = "ready"
        elif args.command == "applied":
            result = mark_applied(claude_dir)
        elif args.command == "close":
            destination, record = close_window(claude_dir, args.closed_by)
            result = {"history": str(destination), "record": record}
        else:
            result = status(claude_dir)
    except WindowHeld as error:
        print(f"held: {error}", file=sys.stderr)
        return EXIT_HELD
    except WindowError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR

    print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Inspect lightweight GitHub webhook notifications from a local state dir."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ENV_STATE_DIR = "LI_PLUS_WEBHOOK_STATE_DIR"
CLAIMS_FILENAME = "notification-claims.json"
SUCCESS_CONCLUSIONS = {"success", "skipped", "neutral"}
COMMENT_EVENT_TYPES = {
    "discussion",
    "discussion_comment",
    "issue_comment",
    "pull_request_review",
    "pull_request_review_comment",
}


@dataclass(frozen=True)
class InspectContext:
    repo: str | None
    numbers: frozenset[str]
    branches: frozenset[str]
    internal_senders: frozenset[str]

    def as_payload(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "numbers": sorted(self.numbers),
            "branches": sorted(self.branches),
        }


def default_workspace_root(script_path: Path | None = None) -> Path:
    base = (script_path or Path(__file__)).resolve()
    return base.parents[2]


def candidate_state_dirs(workspace_root: Path) -> list[Path]:
    return [
        workspace_root / "github-webhook-mcp",
        workspace_root.parent / "github-webhook-mcp",
    ]


def resolve_state_dir(configured: str | None, workspace_root: Path) -> Path | None:
    if configured:
        candidate = Path(configured)
        return candidate if candidate.is_absolute() else workspace_root / candidate

    for candidate in candidate_state_dirs(workspace_root):
        if candidate.exists():
            return candidate
    return None


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_events(path: Path, events: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")


def claims_path(state_dir: Path) -> Path:
    return state_dir / CLAIMS_FILENAME


def load_claims(state_dir: Path) -> dict[str, dict[str, Any]]:
    path = claims_path(state_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_claims(state_dir: Path, claims: dict[str, dict[str, Any]]) -> None:
    path = claims_path(state_dir)
    if claims:
        path.write_text(json.dumps(claims, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    if path.exists():
        path.unlink()


def clear_claims(state_dir: Path, ids: set[str]) -> None:
    if not ids:
        return
    claims = load_claims(state_dir)
    changed = False
    for event_id in ids:
        if event_id in claims:
            del claims[event_id]
            changed = True
    if changed:
        save_claims(state_dir, claims)


def body_preview(payload: dict[str, Any]) -> str:
    for key in ("comment", "review", "discussion", "issue", "pull_request"):
        body = (payload.get(key) or {}).get("body")
        if body:
            return " ".join(str(body).split())[:160]
    conclusion = (payload.get("check_run") or {}).get("conclusion") or (
        payload.get("workflow_run") or {}
    ).get("conclusion")
    return conclusion or ""


def item_number(payload: dict[str, Any]) -> int | str | None:
    return (
        payload.get("number")
        or (payload.get("issue") or {}).get("number")
        or (payload.get("pull_request") or {}).get("number")
        or (payload.get("discussion") or {}).get("number")
    )


def item_title(payload: dict[str, Any]) -> str:
    return (
        (payload.get("issue") or {}).get("title")
        or (payload.get("pull_request") or {}).get("title")
        or (payload.get("discussion") or {}).get("title")
        or (payload.get("check_run") or {}).get("name")
        or (payload.get("workflow_run") or {}).get("name")
        or ""
    )


def item_url(payload: dict[str, Any]) -> str:
    return (
        (payload.get("comment") or {}).get("html_url")
        or (payload.get("review") or {}).get("html_url")
        or (payload.get("issue") or {}).get("html_url")
        or (payload.get("pull_request") or {}).get("html_url")
        or (payload.get("discussion") or {}).get("html_url")
        or (payload.get("check_run") or {}).get("html_url")
        or (payload.get("workflow_run") or {}).get("html_url")
        or ""
    )


def item_branches(payload: dict[str, Any]) -> list[str]:
    branches = {
        value
        for value in (
            (payload.get("workflow_run") or {}).get("head_branch"),
            (payload.get("check_suite") or {}).get("head_branch"),
            ((payload.get("check_run") or {}).get("check_suite") or {}).get("head_branch"),
            ((payload.get("pull_request") or {}).get("head") or {}).get("ref"),
        )
        if value
    }
    return sorted(branches)


def item_conclusion(payload: dict[str, Any]) -> str:
    return (
        (payload.get("check_run") or {}).get("conclusion")
        or (payload.get("workflow_run") or {}).get("conclusion")
        or ""
    )


def item_review_state(payload: dict[str, Any]) -> str:
    return (payload.get("review") or {}).get("state") or ""


def summarize(event: dict[str, Any], *, claims: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = event.get("payload") or {}
    event_id = str(event.get("id"))
    return {
        "id": event_id,
        "type": event.get("type"),
        "action": payload.get("action"),
        "repo": (payload.get("repository") or {}).get("full_name"),
        "sender": (payload.get("sender") or {}).get("login"),
        "number": item_number(payload),
        "title": item_title(payload),
        "url": item_url(payload),
        "received_at": event.get("received_at"),
        "preview": body_preview(payload),
        "branches": item_branches(payload),
        "conclusion": item_conclusion(payload),
        "review_state": item_review_state(payload),
        "claim": (claims or {}).get(event_id),
    }


def artifact_paths(event_id: str, *, state_dir: Path) -> list[Path]:
    return [
        state_dir / "trigger-events" / f"{event_id}.json",
        state_dir / "codex-runs" / f"{event_id}.md",
    ]


def delete_artifacts(paths: list[Path]) -> list[str]:
    deleted: list[str] = []
    for path in paths:
        if path.exists():
            path.unlink()
            deleted.append(str(path))
    return deleted


def remove_events(
    path: Path,
    events: list[dict[str, Any]],
    ids: set[str],
    *,
    state_dir: Path,
) -> tuple[list[str], list[str]]:
    removed_ids: list[str] = []
    deleted_paths: list[str] = []
    if not ids:
        return removed_ids, deleted_paths

    remaining_events: list[dict[str, Any]] = []
    for event in events:
        event_id = str(event.get("id"))
        if event_id in ids:
            removed_ids.append(event_id)
            deleted_paths.extend(delete_artifacts(artifact_paths(event_id, state_dir=state_dir)))
            continue
        remaining_events.append(event)

    if removed_ids:
        save_events(path, remaining_events)
        clear_claims(state_dir, set(removed_ids))
    return removed_ids, deleted_paths


def mark_events_read(path: Path, events: list[dict[str, Any]], ids: set[str], *, state_dir: Path) -> list[str]:
    if not ids:
        return []

    marked_ids: list[str] = []
    updated_events: list[dict[str, Any]] = []
    changed = False
    for event in events:
        event_id = str(event.get("id"))
        if event_id in ids and not event.get("processed", False):
            updated_event = dict(event)
            updated_event["processed"] = True
            updated_events.append(updated_event)
            marked_ids.append(event_id)
            changed = True
            continue
        updated_events.append(event)

    if changed:
        save_events(path, updated_events)
        clear_claims(state_dir, set(marked_ids))
    return marked_ids


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_utc_iso() -> str:
    return now_utc().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def infer_numbers_from_branches(branches: set[str]) -> set[str]:
    numbers: set[str] = set()
    pattern = re.compile(r"(?:^|/)(\d+)(?:[-/]|$)")
    for branch in branches:
        match = pattern.search(branch)
        if match:
            numbers.add(match.group(1))
    return numbers


def build_context(args: argparse.Namespace) -> InspectContext:
    branches = {branch for branch in (args.branch or []) if branch}
    numbers = {str(number) for number in (args.number or []) if str(number)}
    if args.infer_numbers_from_branch:
        numbers |= infer_numbers_from_branches(branches)
    return InspectContext(
        repo=args.repo or None,
        numbers=frozenset(numbers),
        branches=frozenset(branches),
        internal_senders=frozenset(args.internal_sender or []),
    )


def is_internal_sender(sender: str | None, internal_senders: frozenset[str]) -> bool:
    if not sender:
        return False
    if sender in internal_senders:
        return True
    return sender.endswith("[bot]")


def foreground_reasons(summary: dict[str, Any], context: InspectContext) -> list[str]:
    if not context.repo or summary.get("repo") != context.repo:
        return []

    reasons: list[str] = []
    number = summary.get("number")
    if context.numbers and number is not None and str(number) in context.numbers:
        reasons.append("number")

    branches = set(summary.get("branches") or [])
    if context.branches and branches.intersection(context.branches):
        reasons.append("branch")

    return reasons


def notable_reason(summary: dict[str, Any], context: InspectContext) -> str | None:
    if not context.repo or summary.get("repo") != context.repo:
        return None
    if is_internal_sender(summary.get("sender"), context.internal_senders):
        return None

    event_type = summary.get("type") or ""
    if event_type not in COMMENT_EVENT_TYPES:
        return None
    if event_type == "pull_request_review":
        return "external_review"
    if event_type == "pull_request_review_comment":
        return "external_review_comment"
    if event_type == "discussion":
        return "external_discussion"
    if event_type == "discussion_comment":
        return "external_discussion_comment"
    return "external_comment"


def is_cleanup_candidate(
    summary: dict[str, Any],
    context: InspectContext,
    *,
    older_than: timedelta,
    current_time: datetime,
) -> bool:
    if not context.repo or summary.get("repo") != context.repo:
        return False
    if not is_internal_sender(summary.get("sender"), context.internal_senders):
        return False
    if summary.get("type") not in {"check_run", "workflow_run"}:
        return False
    if summary.get("conclusion") not in SUCCESS_CONCLUSIONS:
        return False

    received_at = parse_timestamp(summary.get("received_at"))
    if received_at is None:
        return False
    return current_time - received_at >= older_than


def annotated_summary(
    summary: dict[str, Any],
    *,
    relevant_reasons: list[str] | None = None,
    notable: str | None = None,
    cleanup_candidate: bool = False,
) -> dict[str, Any]:
    annotated = dict(summary)
    if relevant_reasons:
        annotated["relevant_reasons"] = relevant_reasons
    if notable:
        annotated["notable_reason"] = notable
    if cleanup_candidate:
        annotated["cleanup_candidate"] = True
    return annotated


def unique_by_id(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        event_id = str(item.get("id"))
        if event_id in seen:
            continue
        seen.add(event_id)
        result.append(item)
    return result


def tail(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        return items
    return items[-limit:]


def evaluate_pending(
    events: list[dict[str, Any]],
    *,
    claims: dict[str, dict[str, Any]],
    context: InspectContext,
    cleanup_after: timedelta,
) -> dict[str, list[dict[str, Any]]]:
    pending_events = [event for event in events if not event.get("processed", False)]
    pending_summaries = [summarize(event, claims=claims) for event in pending_events]

    relevant_items: list[dict[str, Any]] = []
    notable_items: list[dict[str, Any]] = []
    cleanup_candidates: list[dict[str, Any]] = []
    current_time = now_utc()

    for summary in pending_summaries:
        reasons = foreground_reasons(summary, context)
        if reasons:
            relevant_items.append(annotated_summary(summary, relevant_reasons=reasons))

        notable = notable_reason(summary, context)
        if notable:
            notable_items.append(annotated_summary(summary, notable=notable))

        if is_cleanup_candidate(summary, context, older_than=cleanup_after, current_time=current_time):
            cleanup_candidates.append(annotated_summary(summary, cleanup_candidate=True))

    mention_ids = {
        str(item.get("id"))
        for item in relevant_items + notable_items
    }
    mention_items = [summary for summary in pending_summaries if str(summary.get("id")) in mention_ids]

    return {
        "pending": pending_summaries,
        "relevant": relevant_items,
        "notable": notable_items,
        "mention": unique_by_id(mention_items),
        "cleanup": cleanup_candidates,
    }


def no_source_payload() -> dict[str, Any]:
    return {
        "source": "none",
        "state_dir": None,
        "pending_count": 0,
        "consumed_count": 0,
        "remaining_count": 0,
        "relevant_count": 0,
        "notable_count": 0,
        "mention_count": 0,
        "cleanup_candidate_count": 0,
        "context": {"repo": None, "numbers": [], "branches": []},
        "items": [],
        "relevant_items": [],
        "notable_items": [],
        "mention_items": [],
        "cleanup_candidates": [],
        "deleted_paths": [],
    }


def consume_pending(path: Path, events: list[dict[str, Any]], *, limit: int, state_dir: Path) -> dict[str, Any]:
    pending = [event for event in events if not event.get("processed", False)]
    surfaced = tail([summarize(event) for event in pending], limit)
    pending_ids = {str(event.get("id")) for event in pending}
    removed_ids, deleted_paths = remove_events(path, events, pending_ids, state_dir=state_dir)
    return {
        "source": "local_state_dir",
        "state_dir": str(state_dir),
        "pending_count": len(pending),
        "consumed_count": len(removed_ids),
        "remaining_count": max(len(pending) - len(removed_ids), 0),
        "items": surfaced,
        "deleted_paths": deleted_paths,
        "legacy_consume": True,
    }


def inspect_pending(
    path: Path,
    *,
    limit: int,
    state_dir: Path,
    context: InspectContext,
    cleanup_after: timedelta,
) -> dict[str, Any]:
    events = load_events(path)
    claims = load_claims(state_dir)
    evaluated = evaluate_pending(events, claims=claims, context=context, cleanup_after=cleanup_after)
    return {
        "source": "local_state_dir",
        "state_dir": str(state_dir),
        "pending_count": len(evaluated["pending"]),
        "relevant_count": len(evaluated["relevant"]),
        "notable_count": len(evaluated["notable"]),
        "mention_count": len(evaluated["mention"]),
        "cleanup_candidate_count": len(evaluated["cleanup"]),
        "context": context.as_payload(),
        "items": tail(evaluated["pending"], limit),
        "relevant_items": tail(evaluated["relevant"], limit),
        "notable_items": tail(evaluated["notable"], limit),
        "mention_items": tail(evaluated["mention"], limit),
        "cleanup_candidates": tail(evaluated["cleanup"], limit),
    }


def claim_ids(
    state_dir: Path,
    ids: list[str],
    *,
    claimant: str,
    reason: str | None,
    force: bool,
) -> tuple[list[str], list[dict[str, Any]]]:
    claims = load_claims(state_dir)
    claimed_ids: list[str] = []
    skipped: list[dict[str, Any]] = []
    timestamp = now_utc_iso()

    for event_id in ids:
        existing = claims.get(event_id)
        if existing and existing.get("claimed_by") not in {None, "", claimant} and not force:
            skipped.append(
                {
                    "id": event_id,
                    "claimed_by": existing.get("claimed_by"),
                }
            )
            continue

        claims[event_id] = {
            "claimed_by": claimant,
            "claimed_at": timestamp,
            "reason": reason or "",
        }
        claimed_ids.append(event_id)

    if claimed_ids:
        save_claims(state_dir, claims)
    return claimed_ids, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect pending webhook notifications")
    parser.add_argument(
        "--workspace-root",
        default=None,
        help="Workspace root used to resolve relative state-dir values",
    )
    parser.add_argument(
        "--state-dir",
        default=None,
        help="Directory containing github-webhook-mcp state files",
    )
    parser.add_argument("--limit", type=int, default=5, help="Maximum items to return per bucket")
    parser.add_argument("--repo", default=None, help="Foreground repository full name")
    parser.add_argument("--number", action="append", default=[], help="Foreground issue/PR/discussion number")
    parser.add_argument("--branch", action="append", default=[], help="Foreground branch name")
    parser.add_argument(
        "--infer-numbers-from-branch",
        action="store_true",
        help="Infer foreground issue numbers from branch names like spec/786-name",
    )
    parser.add_argument(
        "--internal-sender",
        action="append",
        default=[],
        help="Sender login that should not be treated as external/notable",
    )
    parser.add_argument(
        "--consume",
        action="store_true",
        help="Legacy mode: delete every pending event and related artifacts immediately",
    )
    parser.add_argument(
        "--ack",
        nargs="*",
        default=None,
        help="Legacy alias for --done",
    )
    parser.add_argument(
        "--done",
        nargs="*",
        default=None,
        help="Delete the specified event ids and related generated files",
    )
    parser.add_argument(
        "--read",
        nargs="*",
        default=None,
        help="Mark the specified event ids as read without deleting them",
    )
    parser.add_argument(
        "--claim-matched",
        action="store_true",
        help="Claim all foreground-matched pending events",
    )
    parser.add_argument("--claimant", default=None, help="Name stored in claim metadata")
    parser.add_argument("--reason", default=None, help="Optional reason stored with a claim")
    parser.add_argument(
        "--force-claim",
        action="store_true",
        help="Allow a claimant to overwrite an existing claim held by someone else",
    )
    parser.add_argument(
        "--cleanup-safe-success",
        action="store_true",
        help="Delete old internal success check/workflow notifications for the foreground repo",
    )
    parser.add_argument(
        "--older-than-hours",
        type=float,
        default=24.0,
        help="Age threshold used by --cleanup-safe-success",
    )
    args = parser.parse_args()

    action_count = sum(
        [
            bool(args.consume),
            args.ack is not None,
            args.done is not None,
            args.read is not None,
            bool(args.claim_matched),
            bool(args.cleanup_safe_success),
        ]
    )
    if action_count > 1:
        parser.error("choose only one action")
    if args.claim_matched and not args.claimant:
        parser.error("--claimant is required with --claim-matched")
    return args


def main() -> int:
    args = parse_args()
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else default_workspace_root()
    configured_state_dir = args.state_dir or os.environ.get(ENV_STATE_DIR)
    state_dir = resolve_state_dir(configured_state_dir, workspace_root)
    if state_dir is None:
        print(json.dumps(no_source_payload(), ensure_ascii=False))
        return 0

    events_path = state_dir / "events.json"
    events = load_events(events_path)
    context = build_context(args)
    cleanup_after = timedelta(hours=args.older_than_hours)

    if args.ack is not None or args.done is not None:
        ids = [event_id for event_id in (args.done if args.done is not None else args.ack) if event_id]
        done_ids, deleted_paths = remove_events(events_path, events, set(ids), state_dir=state_dir)
        print(
            json.dumps(
                {
                    "source": "local_state_dir",
                    "state_dir": str(state_dir),
                    "done_ids": done_ids,
                    "done_count": len(done_ids),
                    "deleted_paths": deleted_paths,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.read is not None:
        ids = [event_id for event_id in args.read if event_id]
        read_ids = mark_events_read(events_path, events, set(ids), state_dir=state_dir)
        print(
            json.dumps(
                {
                    "source": "local_state_dir",
                    "state_dir": str(state_dir),
                    "read_ids": read_ids,
                    "read_count": len(read_ids),
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.claim_matched:
        claims = load_claims(state_dir)
        evaluated = evaluate_pending(events, claims=claims, context=context, cleanup_after=cleanup_after)
        claimable_ids = [str(item.get("id")) for item in evaluated["relevant"]]
        claimed_ids, skipped = claim_ids(
            state_dir,
            claimable_ids,
            claimant=args.claimant,
            reason=args.reason,
            force=args.force_claim,
        )
        print(
            json.dumps(
                {
                    "source": "local_state_dir",
                    "state_dir": str(state_dir),
                    "claimed_ids": claimed_ids,
                    "claimed_count": len(claimed_ids),
                    "skipped": skipped,
                    "context": context.as_payload(),
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.cleanup_safe_success:
        claims = load_claims(state_dir)
        evaluated = evaluate_pending(events, claims=claims, context=context, cleanup_after=cleanup_after)
        cleanup_ids = [str(item.get("id")) for item in evaluated["cleanup"]]
        removed_ids, deleted_paths = remove_events(events_path, events, set(cleanup_ids), state_dir=state_dir)
        print(
            json.dumps(
                {
                    "source": "local_state_dir",
                    "state_dir": str(state_dir),
                    "cleanup_ids": removed_ids,
                    "cleanup_count": len(removed_ids),
                    "deleted_paths": deleted_paths,
                    "context": context.as_payload(),
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.consume:
        print(json.dumps(consume_pending(events_path, events, limit=args.limit, state_dir=state_dir), ensure_ascii=False))
        return 0

    print(
        json.dumps(
            inspect_pending(
                events_path,
                limit=args.limit,
                state_dir=state_dir,
                context=context,
                cleanup_after=cleanup_after,
            ),
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

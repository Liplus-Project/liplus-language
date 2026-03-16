#!/usr/bin/env python3
"""Inspect lightweight pending GitHub webhook notifications from a local state dir."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

ENV_STATE_DIR = "LI_PLUS_WEBHOOK_STATE_DIR"


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
        or (payload.get("issue") or {}).get("html_url")
        or (payload.get("pull_request") or {}).get("html_url")
        or (payload.get("discussion") or {}).get("html_url")
        or (payload.get("check_run") or {}).get("html_url")
        or (payload.get("workflow_run") or {}).get("html_url")
        or ""
    )


def summarize(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload") or {}
    return {
        "id": event.get("id"),
        "type": event.get("type"),
        "action": payload.get("action"),
        "repo": (payload.get("repository") or {}).get("full_name"),
        "sender": (payload.get("sender") or {}).get("login"),
        "number": item_number(payload),
        "title": item_title(payload),
        "url": item_url(payload),
        "received_at": event.get("received_at"),
        "preview": body_preview(payload),
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


def remove_events(path: Path, events: list[dict[str, Any]], ids: set[str], *, state_dir: Path) -> tuple[list[str], list[str]]:
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
    return removed_ids, deleted_paths


def no_source_payload() -> dict[str, Any]:
    return {
        "source": "none",
        "state_dir": None,
        "pending_count": 0,
        "consumed_count": 0,
        "remaining_count": 0,
        "items": [],
        "deleted_paths": [],
    }


def consume_pending(path: Path, events: list[dict[str, Any]], *, limit: int, state_dir: Path) -> dict[str, Any]:
    pending = [event for event in events if not event.get("processed", False)]
    surfaced = pending[-limit:] if limit > 0 else pending
    pending_ids = {str(event.get("id")) for event in pending}
    removed_ids, deleted_paths = remove_events(path, events, pending_ids, state_dir=state_dir)
    return {
        "source": "local_state_dir",
        "state_dir": str(state_dir),
        "pending_count": len(pending),
        "consumed_count": len(removed_ids),
        "remaining_count": max(len(pending) - len(removed_ids), 0),
        "items": [summarize(event) for event in surfaced],
        "deleted_paths": deleted_paths,
    }


def inspect_pending(path: Path, *, limit: int, state_dir: Path) -> dict[str, Any]:
    events = load_events(path)
    pending = [event for event in events if not event.get("processed", False)]
    selected = pending[-limit:] if limit > 0 else pending
    return {
        "source": "local_state_dir",
        "state_dir": str(state_dir),
        "pending_count": len(pending),
        "items": [summarize(event) for event in selected],
    }


def main() -> int:
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
    parser.add_argument("--limit", type=int, default=5, help="Maximum pending items to return")
    parser.add_argument(
        "--consume",
        action="store_true",
        help="Return pending summaries and delete the surfaced event logs immediately",
    )
    parser.add_argument(
        "--ack",
        nargs="*",
        default=None,
        help="Delete the specified event ids and related generated files",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else default_workspace_root()
    configured_state_dir = args.state_dir or os.environ.get(ENV_STATE_DIR)
    state_dir = resolve_state_dir(configured_state_dir, workspace_root)
    if state_dir is None:
        print(json.dumps(no_source_payload(), ensure_ascii=False))
        return 0

    events_path = state_dir / "events.json"
    events = load_events(events_path)

    if args.ack is not None:
        acked_ids, deleted_paths = remove_events(events_path, events, set(args.ack), state_dir=state_dir)
        print(
            json.dumps(
                {
                    "source": "local_state_dir",
                    "state_dir": str(state_dir),
                    "acked_ids": acked_ids,
                    "acked_count": len(acked_ids),
                    "deleted_paths": deleted_paths,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.consume:
        print(json.dumps(consume_pending(events_path, events, limit=args.limit, state_dir=state_dir), ensure_ascii=False))
        return 0

    print(json.dumps(inspect_pending(events_path, limit=args.limit, state_dir=state_dir), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

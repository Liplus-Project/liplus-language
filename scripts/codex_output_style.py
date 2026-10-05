"""Project output-style loader; protocol owned by adapter/codex/character-config.md."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tomllib

LIMIT = 128 * 1024
MATCHERS = ["startup", "resume", "clear", "compact"]


class StyleBlocked(ValueError):
    pass


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def stem(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", value):
        raise StyleBlocked("invalid_selection")
    return value


def contained(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise StyleBlocked("outside_project")
    return resolved


def project(cwd: Path, root: Path) -> Path:
    if not cwd.is_absolute() or not root.is_absolute():
        raise StyleBlocked("invalid_project")
    root = root.resolve(strict=True)
    if not root.is_dir() or not contained(cwd, root).is_dir():
        raise StyleBlocked("invalid_project")
    return root


def body_bytes(content: bytes, name: str) -> bytes:
    if len(content) > LIMIT:
        raise StyleBlocked("style_oversize")
    text = content.decode("utf-8-sig")
    payload = content[3:] if content.startswith(b"\xef\xbb\xbf") else content
    lines = payload.splitlines(keepends=True)
    if lines and lines[0].rstrip(b"\r\n") == b"---":
        close = next((i for i in range(1, len(lines))
                      if lines[i].rstrip(b"\r\n") == b"---"), None)
        if close is None:
            raise StyleBlocked("unclosed_frontmatter")
        front = b"".join(lines[1:close]).decode("utf-8")
        entries = re.findall(r"^name:[ \t]*(.*)\r?$", front, re.M)
        keys = re.findall(r"^[ \t]*(?:name|\"name\"|'name')[ \t]*:", front, re.M)
        if len(entries) > 1 or len(keys) != len(entries) or front.lstrip().startswith(("{", "[")):
            raise StyleBlocked("ambiguous_frontmatter_name")
        if entries:
            scalar = entries[0].strip()
            if len(scalar) >= 2 and scalar[0] == scalar[-1] and scalar[0] in "\"'":
                scalar = scalar[1:-1]
            if stem(scalar) != name:
                raise StyleBlocked("frontmatter_name_mismatch")
        payload = b"".join(lines[close + 1:])
        text = payload.decode("utf-8")
    if not text.strip():
        raise StyleBlocked("empty_style")
    # The JSON handler envelope, including escaped controls, has the same byte cap.
    if len(serialize(hook_response(payload)).encode("utf-8")) + 1 > LIMIT:
        raise StyleBlocked("handler_oversize")
    return payload


def hook_response(body: bytes) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                   "additionalContext": body.decode("utf-8")}}


def serialize(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def load(cwd: Path, root: Path, style: str | None = None, *,
         environment: bool = True) -> tuple[dict, bytes]:
    root = project(cwd, root)
    config = root / ".codex" / "config.toml"
    data = tomllib.loads(contained(config, root).read_bytes().decode("utf-8-sig")) if config.exists() or config.is_symlink() else {}
    table = data.get("liplus", {})
    if not isinstance(table, dict):
        raise StyleBlocked("invalid_selection")
    selected = table.get("output_style")
    style_directory = root / ".codex" / "output-styles"
    if selected is None and (style_directory.exists() or style_directory.is_symlink()):
        selected = "character_instance"
    override = os.environ.get("LI_PLUS_OUTPUT_STYLE", "") if environment else ""
    if style is not None:
        selected = stem(style)
    elif override:
        selected = stem(override)
    mode, name, body = "legacy", None, b""
    if selected is False:
        mode = "disabled"
    elif selected is not None:
        name = stem(selected)
        directory = contained(root / ".codex" / "output-styles", root)
        # Check exact spelling even on case-insensitive Windows filesystems.
        if name + ".md" not in {p.name for p in directory.iterdir()}:
            raise StyleBlocked("missing_style")
        path = contained(directory / (name + ".md"), directory)
        with path.open("rb") as stream:
            body = body_bytes(stream.read(LIMIT + 1), name)
        mode = "file"
    helper = Path(__file__).resolve()
    return {"protocol_version": 1, "mode": mode, "name": name, "root": str(root),
            "sha256": digest(body) if mode == "file" else None,
            "byte_count": len(body), "handler": {
                "path": str(helper), "sha256": digest(helper.read_bytes()),
                "additional_context_limit": 0, "matchers": MATCHERS}}, body


def main() -> int:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", choices=("hook", "resolve"), default="hook")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--style")
    args = parser.parse_args()
    try:
        helper = Path(__file__).resolve()
        if (helper.parent.name != "hooks" or helper.parent.parent.name != ".codex"
                or args.root.resolve(strict=True) != helper.parents[2]):
            raise StyleBlocked("helper_root_mismatch")
        if args.mode == "hook":
            event = json.load(sys.stdin)
            if (not isinstance(event, dict) or event.get("hook_event_name") != "SessionStart"
                    or event.get("source") not in MATCHERS or not isinstance(event.get("cwd"), str)):
                raise StyleBlocked("invalid_hook_input")
            cwd = Path(event["cwd"])
        else:
            if args.cwd is None:
                raise StyleBlocked("missing_cwd")
            cwd = args.cwd
        metadata, body = load(cwd, args.root, args.style)
        result = metadata if args.mode == "resolve" else hook_response(body)
    except (ValueError, OSError, UnicodeError) as exc:
        reason = str(exc) if isinstance(exc, StyleBlocked) else "invalid_style_or_project"
        result = {"protocol_version": 1, "status": "blocked", "reason": reason}
        if args.mode == "hook":
            result = {"continue": False, "stopReason": "Li+ output style: " + reason}
        print(serialize(result))
        return 1
    print(serialize(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

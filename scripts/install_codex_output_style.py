"""Install the independent style handler specified by Li+update.md 4x.3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import uuid

from codex_output_style import digest, load, project
from migrate_codex_character import MigrationBlocked, backup

NAME = "codex-output-style.py"


def registration(workspace: Path) -> dict:
    root = workspace.as_posix()
    return {"type": "command",
            "command": f'python3 "{root}/.codex/hooks/{NAME}" hook --root "{root}"',
            "commandWindows": f'python "{root}/.codex/hooks/{NAME}" hook --root "{root}"',
            "timeout": 30, "additionalContextLimit": 0,
            "statusMessage": "Li+ project output style"}


def install(source: Path, workspace: Path, *, apply: bool = False) -> dict:
    workspace = project(workspace, workspace)
    load(workspace, workspace, environment=False)
    helper = workspace / ".codex/hooks" / NAME
    hooks = workspace / ".codex/hooks.json"
    manifest = workspace / ".codex/state/liplus-output-style.json"
    config = workspace / ".codex/config.toml"
    for path in (helper, hooks, manifest):
        if not path.resolve().is_relative_to(workspace):
            raise MigrationBlocked("Installation path leaves the project")
    import tomllib
    config_bytes = config.read_bytes() if config.exists() else None
    if "hooks" in tomllib.loads((config_bytes or b"").decode("utf-8-sig")):
        raise MigrationBlocked("Use the documented TOML handler without duplicate JSON registration")
    originals = {p: p.read_bytes() if p.exists() else None for p in (helper, hooks, manifest)}
    source_bytes = source.read_bytes()
    old = json.loads(originals[manifest]) if originals[manifest] else {}
    if old and (old.get("version") != 1 or not isinstance(old.get("handler"), dict)):
        raise MigrationBlocked("Invalid style handler ownership record")
    if originals[helper] is not None and originals[helper] != source_bytes:
        if digest(originals[helper]) != old.get("helper_sha256"):
            raise MigrationBlocked("Modified installed helper requires ownership resolution")
    data = json.loads(originals[hooks]) if originals[hooks] else {"hooks": {}}
    groups = data.setdefault("hooks", {}).setdefault("SessionStart", [])
    if not isinstance(groups, list):
        raise MigrationBlocked("Invalid SessionStart registration")
    desired = registration(workspace)
    found = []
    for group in groups:
        for index, handler in enumerate(group.get("hooks", [])):
            if any(NAME in handler.get(key, "") for key in ("command", "commandWindows")):
                found.append((group, index, handler))
    if len(found) > 1:
        raise MigrationBlocked("Duplicate output-style handlers require resolution")
    if found:
        group, index, previous = found[0]
        if group.get("matcher") != "startup|resume|clear|compact" or previous not in (desired, old.get("handler")):
            raise MigrationBlocked("Modified output-style registration requires resolution")
        group["hooks"][index] = desired
    else:
        group = next((g for g in groups if g.get("matcher") == "startup|resume|clear|compact"), None)
        if group is None:
            group = {"matcher": "startup|resume|clear|compact", "hooks": []}
            groups.append(group)
        group.setdefault("hooks", []).append(desired)
    changes = {helper: source_bytes,
               hooks: (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode(),
               manifest: (json.dumps({"version": 1, "helper_sha256": digest(source_bytes),
                                      "handler": desired}, indent=2) + "\n").encode()}
    changes = {p: content for p, content in changes.items() if originals[p] != content}
    report = {"status": "ready", "applied": False, "helper_sha256": digest(source_bytes),
              "changed": [str(p) for p in changes], "backups": []}
    if not apply:
        return report
    if source.read_bytes() != source_bytes or (config.read_bytes() if config.exists() else None) != config_bytes:
        raise MigrationBlocked("Installation inputs changed")
    for path, original in originals.items():
        if (path.read_bytes() if path.exists() else None) != original:
            raise MigrationBlocked("Installed handler changed after planning")
    saved = [str(backup(p, originals[p])) for p in changes if originals[p] is not None]
    completed = []
    try:
        for path, content in changes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + "." + uuid.uuid4().hex)
            try:
                mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
                with temporary.open("xb") as stream:
                    temporary.chmod(mode)
                    stream.write(content)
                if temporary.read_bytes() != content:
                    raise MigrationBlocked("Handler read-back failed")
                if (path.read_bytes() if path.exists() else None) != originals[path]:
                    raise MigrationBlocked("Handler changed during installation")
                temporary.replace(path)
                completed.append(path)
            finally:
                temporary.unlink(missing_ok=True)
        if (config.read_bytes() if config.exists() else None) != config_bytes:
            raise MigrationBlocked("Config changed during installation")
    except Exception:
        for path in reversed(completed):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(originals[path])
        raise
    return dict(report, status="installed", applied=True, backups=saved,
                trust_required=bool(changes))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        result = install(args.source, args.workspace, apply=args.apply)
    except (ValueError, OSError, UnicodeError, TypeError, AttributeError):
        print(json.dumps({"status": "blocked", "reason": "Resolve style handler ownership"}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

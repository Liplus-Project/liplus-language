"""Install the rules mirror specified by Li+update.md Phase 4 codex."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
import tomllib
import uuid


CHARACTER = "model/character_Instance.md"
MANIFEST = "liplus-rules.json"


class InstallationBlocked(ValueError):
    pass


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def character_preserved(content: bytes, instructions: str) -> bool:
    body = content.decode("utf-8-sig").replace("\r\n", "\n").strip()
    if body.startswith("---\n"):
        parts = body.split("\n---", 1)
        if len(parts) != 2:
            return False
        body = parts[1].strip()
    lines = body.splitlines()
    lines = [line for line in lines if line.strip() not in (
        "<characters>", "</characters>", "# Characters", "[Character_Instance]")]
    body = "\n".join(lines).strip()
    return bool(re.search(r"^NAME\s*=\s*\S", body, re.M)
                and body in instructions.replace("\r\n", "\n"))


def safe_path(root: Path, relative: str) -> Path:
    rel = PurePosixPath(relative)
    if (not relative or rel.is_absolute() or ".." in rel.parts or "\\" in relative
            or ":" in relative or rel.suffix != ".md" or rel.as_posix() != relative):
        raise InstallationBlocked("Invalid managed rule path")
    target = root.joinpath(*rel.parts)
    check = target
    while check != root.parent:
        if check.is_symlink() or (check.exists() and getattr(check, "is_junction", lambda: False)()):
            raise InstallationBlocked("Linked paths require manual ownership resolution")
        check = check.parent
    if not target.resolve().is_relative_to(root.resolve()):
        raise InstallationBlocked("Rule path leaves the installed tree")
    return target


def install(source: Path, workspace: Path, config: Path, native_state: str, *,
            apply: bool = False, effective_instructions: str | None = None) -> dict:
    if native_state not in ("present", "disabled"):
        raise InstallationBlocked("Resolve and save the native character first")
    original_config = config.read_bytes() if config.exists() else None
    data = tomllib.loads((original_config or b"").decode("utf-8-sig"))
    instructions = (effective_instructions if effective_instructions is not None
                    else data.get("developer_instructions", ""))
    if not isinstance(instructions, str):
        raise InstallationBlocked("Effective instructions must be a string")
    if native_state == "present" and "[Character_Instance]" not in instructions:
        raise InstallationBlocked("Native character read-back has not been confirmed")
    root = workspace / ".codex" / "rules"
    manifest = workspace / ".codex" / "state" / MANIFEST
    # Both the mirror and its ownership record stay inside the workspace.
    for path in (root, manifest):
        if not path.resolve().is_relative_to(workspace.resolve()):
            raise InstallationBlocked("Installed paths leave the workspace")
        for parent in (path, *path.parents):
            if parent == workspace.parent:
                break
            if parent.is_symlink() or (parent.exists() and getattr(parent, "is_junction", lambda: False)()):
                raise InstallationBlocked("Linked installation paths require manual resolution")
    old_manifest = manifest.read_bytes() if manifest.exists() else None
    record = json.loads(old_manifest) if old_manifest else {"version": 1, "files": {}}
    if (not isinstance(record, dict) or record.get("version") != 1
            or not isinstance(record.get("files"), dict)):
        raise InstallationBlocked("Unknown ownership record")
    owned = record["files"]
    desired = {}
    for path in sorted(source.rglob("*.md")):
        relative = path.relative_to(source).as_posix()
        safe_path(source, relative)
        if relative != CHARACTER:
            desired[relative] = path.read_bytes()
    if "evolution/cold-start-synthesis.md" not in desired:
        raise InstallationBlocked("Source rules are incomplete")
    originals = {}
    changes = {}
    for relative in sorted(set(desired) | set(owned) | {CHARACTER}):
        path = safe_path(root, relative)
        existing = path.read_bytes() if path.exists() else None
        originals[relative] = existing
        target = desired.get(relative)
        if relative in owned:
            previous = owned[relative]
            if not isinstance(previous, str) or len(previous) != 64:
                raise InstallationBlocked("Invalid ownership hash")
            if (existing is not None and digest(existing) != previous and existing != target
                    and not (relative == CHARACTER and native_state == "present"
                             and character_preserved(existing, instructions))):
                raise InstallationBlocked("A managed rule was modified; preserve it before updating")
        elif existing is not None and existing != target:
            # A byte-identical distributed character copy can be retired after
            # native read-back. A saved custom copy can be retired; divergent content needs preservation.
            template = source / CHARACTER
            if relative != CHARACTER or not (
                    (template.is_file() and existing == template.read_bytes())
                    or (native_state == "present" and character_preserved(existing, instructions))):
                raise InstallationBlocked("An unowned rule conflicts with the installation")
        if existing != target:
            changes[relative] = target
    new_manifest = (json.dumps({"version": 1, "files": {
        relative: digest(content) for relative, content in sorted(desired.items())
    }}, indent=2) + "\n").encode("utf-8")
    report = {"status": "ready", "applied": False, "write": sorted(
        rel for rel, content in changes.items() if content is not None),
        "remove": sorted(rel for rel, content in changes.items() if content is None),
        "config_sha256": digest(original_config) if original_config is not None else None,
        "backups": []}
    if not apply:
        return report
    # Planning and saving share one call; recheck every touched input before mutation.
    if (config.read_bytes() if config.exists() else None) != original_config:
        raise InstallationBlocked("Native config changed after planning")
    if (manifest.read_bytes() if manifest.exists() else None) != old_manifest:
        raise InstallationBlocked("Ownership record changed after planning")
    for relative, original in originals.items():
        path = safe_path(root, relative)
        if (path.read_bytes() if path.exists() else None) != original:
            raise InstallationBlocked("Rules changed after planning")
    backup_root = workspace / ".codex" / "state" / ("rules-backup-" + uuid.uuid4().hex)
    if changes or old_manifest != new_manifest:
        backup_root.mkdir(parents=True)
        for relative in changes:
            if originals[relative] is not None:
                backup_path = backup_root / "rules" / relative
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_bytes(originals[relative])
        if old_manifest is not None:
            (backup_root / MANIFEST).write_bytes(old_manifest)
        report["backups"].append(str(backup_root))
    completed = []
    try:
        for relative, content in changes.items():
            path = safe_path(root, relative)
            completed.append(relative)
            if content is None:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                if path.read_bytes() != content:
                    raise InstallationBlocked("Rule read-back failed")
        if (config.read_bytes() if config.exists() else None) != original_config:
            raise InstallationBlocked("Native config changed during installation")
        if old_manifest != new_manifest:
            manifest.parent.mkdir(parents=True, exist_ok=True)
            temporary = manifest.with_name(MANIFEST + "." + uuid.uuid4().hex)
            try:
                temporary.write_bytes(new_manifest)
                temporary.replace(manifest)
            finally:
                temporary.unlink(missing_ok=True)
    except Exception:
        for relative in reversed(completed):
            path = safe_path(root, relative)
            original = originals[relative]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        raise
    report.update(status="installed", applied=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--native-state", choices=("present", "disabled"), required=True)
    parser.add_argument("--effective-instructions", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        report = install(args.source, args.workspace, args.config, args.native_state,
                         apply=args.apply, effective_instructions=(
                             args.effective_instructions.read_text(encoding="utf-8")
                             if args.effective_instructions else None))
    except (ValueError, OSError, UnicodeError):
        print(json.dumps({"status": "blocked", "reason": "Resolve rule ownership and native preservation"}))
        return 1
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

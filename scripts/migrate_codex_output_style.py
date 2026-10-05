"""Explicit one-time migration specified in Li+update.md 4x.0s."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import tomllib
import uuid

from codex_output_style import body_bytes, digest, load, project, stem
from migrate_codex_character import MigrationBlocked, backup, instruction_span


def encoded(text: str, original: bytes) -> bytes:
    return (b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b"") + text.encode("utf-8")


def remove_literal(original: bytes, literal: bytes) -> bytes:
    text = original.decode("utf-8-sig")
    data = tomllib.loads(text)
    value = data.get("developer_instructions")
    approved = literal.decode("utf-8-sig")
    if not approved.strip() or not isinstance(value, str) or value.count(approved) != 1:
        raise MigrationBlocked("Approved persona does not have a unique root instruction boundary")
    common = value.replace(approved, "", 1)
    start, end = instruction_span(text)
    rendered = text[:start] + json.dumps(common, ensure_ascii=False) + text[end:]
    expected = dict(data, developer_instructions=common)
    if tomllib.loads(rendered) != expected:
        raise MigrationBlocked("Unrelated config changed")
    return encoded(rendered, original)


def select(original: bytes, name: str) -> bytes:
    text = original.decode("utf-8-sig")
    data = tomllib.loads(text)
    expected = copy.deepcopy(data)
    table = expected.setdefault("liplus", {})
    if not isinstance(table, dict):
        raise MigrationBlocked("Invalid Li+ config")
    table["output_style"] = name
    newline = "\r\n" if "\r\n" in text else "\n"
    headings = list(re.finditer(r"^\[liplus\][ \t]*(?:#[^\r\n]*)?\r?$", text, re.M))
    if "liplus" in data and len(headings) != 1:
        raise MigrationBlocked("Li+ table boundary is ambiguous")
    if headings:
        start = headings[0].end()
        next_table = re.search(r"^\[", text[start:], re.M)
        end = start + next_table.start() if next_table else len(text)
        section = text[start:end]
        assignments = list(re.finditer(r'^output_style[ \t]*=[ \t]*("[^"\r\n]*"|false|true)[ \t]*(?:#[^\r\n]*)?\r?$', section, re.M))
        if "output_style" in data["liplus"]:
            if len(assignments) != 1:
                raise MigrationBlocked("Selection boundary is ambiguous")
            match = assignments[0]
            section = section[:match.start(1)] + '"' + name + '"' + section[match.end(1):]
        else:
            section = newline + 'output_style = "' + name + '"' + section
        rendered = text[:start] + section + text[end:]
    else:
        rendered = text + (newline if text and not text.endswith("\n") else "")
        rendered += '[liplus]' + newline + 'output_style = "' + name + '"' + newline
    if tomllib.loads(rendered) != expected:
        raise MigrationBlocked("Unrelated config changed")
    return encoded(rendered, original)


def migrate(workspace: Path, name: str, persona_file: Path, *,
            removals: list[tuple[Path, Path]] | None = None,
            apply: bool = False, approve_existing: bool = False,
            preserve_selection: bool = False, use_existing_style: bool = False) -> dict:
    workspace = project(workspace, workspace)
    name = stem(name)
    config = workspace / ".codex/config.toml"
    style = workspace / ".codex/output-styles" / (name + ".md")
    for target in (config, style):
        if not target.resolve().is_relative_to(workspace):
            raise MigrationBlocked("Migration target leaves the project")
    persona = persona_file.read_bytes()
    # Metadata is generated without rewriting the approved body bytes.
    body_bytes(persona, name)
    if persona.startswith(b"\xef\xbb\xbf") or persona.splitlines()[0] == b"---":
        raise MigrationBlocked("Approved inline persona must be body-only UTF-8")
    artifact = ('---\nname: ' + name + '\ndescription: Project character instructions\nkeep-coding-instructions: true\n---\n').encode() + persona
    body_bytes(artifact, name)
    source_pairs = removals if removals is not None else [(config, persona_file)]
    if not source_pairs:
        raise MigrationBlocked("Approved inline boundary is required")
    existing_style = style.read_bytes() if style.exists() else None
    selected_body = body_bytes(existing_style, name) if existing_style is not None else persona
    config_original = config.read_bytes() if config.exists() else None
    current_data = tomllib.loads((config_original or b"").decode("utf-8-sig"))
    table = current_data.get("liplus", {})
    if not isinstance(table, dict):
        raise MigrationBlocked("Invalid Li+ config")
    current_name = table.get("output_style", "character_instance")
    if existing_style is not None:
        load(workspace, workspace, name, environment=False)
    has_inline = any(Path(source).exists() and Path(approved).read_bytes().decode("utf-8-sig") in
                     tomllib.loads(Path(source).read_bytes().decode("utf-8-sig")).get("developer_instructions", "")
                     for source, approved in source_pairs)
    if existing_style is not None and not has_inline and (preserve_selection or current_name == name):
        if use_existing_style or selected_body == persona:
            return {"status": "already-migrated", "applied": False, "backups": []}
    if existing_style is not None and not use_existing_style:
        raise MigrationBlocked("Existing user style is protected")
    if existing_style is None and use_existing_style:
        raise MigrationBlocked("Existing style is required")
    if not use_existing_style:
        metadata, _ = load(workspace, workspace, environment=False)
        if metadata["mode"] != "legacy" and not preserve_selection:
            raise MigrationBlocked("Existing selection requires explicit resolution")
    originals: dict[Path, bytes | None] = {}
    changes: dict[Path, bytes] = {}
    evidence = {persona_file: persona}
    for source, approved_file in source_pairs:
        source = source.absolute()
        if (source.parent.resolve() != (workspace / ".codex").resolve()
                or source.suffix != ".toml" or source.resolve().parent != source.parent.resolve()
                or source in originals):
            raise MigrationBlocked("Inline source must be a unique local Codex config")
        approved = approved_file.read_bytes()
        evidence[approved_file] = approved
        original = source.read_bytes()
        originals[source] = original
        changes[source] = remove_literal(original, approved)
    if persona not in evidence.values() or not any(persona.decode("utf-8") in tomllib.loads(v.decode("utf-8-sig")).get("developer_instructions", "") for v in originals.values()):
        raise MigrationBlocked("Selected body has no approved inline source")
    originals.setdefault(config, config_original)
    if not preserve_selection:
        changes[config] = select(changes.get(config, originals[config] or b""), name)
    originals[style] = existing_style
    if existing_style is None:
        changes[style] = artifact
    report = {"status": "ready", "applied": False, "name": name,
              "sha256": digest(selected_body), "byte_count": len(selected_body), "backups": []}
    if not apply:
        return report
    if not approve_existing:
        raise MigrationBlocked("Explicit migration approval is required")
    for path, original in {**originals, **evidence}.items():
        if (path.read_bytes() if path.exists() else None) != original:
            raise MigrationBlocked("Migration input changed after planning")
    saved = []
    for path, original in originals.items():
        if original is not None:
            saved.append(str(backup(path, original)))
    completed = []
    try:
        # Publish the validated style before its selector; restore all touched inputs on failure.
        for path in ([style] if style in changes else []) + [p for p in changes if p != style]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if (path.read_bytes() if path.exists() else None) != originals[path]:
                raise MigrationBlocked("Config changed during migration")
            if originals[path] is None:
                with path.open("xb") as stream:
                    completed.append(path)
                    stream.write(changes[path])
                path.chmod(0o600)
            else:
                completed.append(path)
                path.write_bytes(changes[path])
            if path.read_bytes() != changes[path]:
                raise MigrationBlocked("Migration read-back failed")
        verified, _ = load(workspace, workspace, name, environment=False)
        if verified["sha256"] != digest(selected_body) or style.read_bytes() != (existing_style if existing_style is not None else artifact):
            raise MigrationBlocked("Style read-back failed")
    except Exception:
        for path in reversed(completed):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(originals[path])
        raise
    return dict(report, status="migrated", applied=True, backups=saved)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--persona-file", type=Path, required=True)
    parser.add_argument("--remove", nargs=2, action="append", metavar=("CONFIG", "PRIVATE_PERSONA"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approve-existing", action="store_true")
    parser.add_argument("--preserve-selection", action="store_true")
    parser.add_argument("--use-existing-style", action="store_true")
    args = parser.parse_args()
    try:
        result = migrate(args.workspace, args.name, args.persona_file,
                         removals=[(Path(a), Path(b)) for a, b in args.remove] if args.remove else None,
                         apply=args.apply, approve_existing=args.approve_existing,
                         preserve_selection=args.preserve_selection,
                         use_existing_style=args.use_existing_style)
    except (ValueError, OSError, UnicodeError):
        print(json.dumps({"status": "blocked", "reason": "Resolve approved migration boundaries"}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

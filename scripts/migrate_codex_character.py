"""Save Codex character literals before Li+update.md 4x.1 replaces the adapter."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import tomllib
import uuid


ROOT = Path(__file__).resolve().parents[1]
MARKER = "[Character_Instance]"
BANNER = "#" * 55


class MigrationBlocked(ValueError):
    pass


@dataclass(frozen=True)
class Plan:
    status: str
    config: bytes
    literal: str | None = None


def legacy_literal(agents: bytes) -> str | None:
    text = agents.decode("utf-8-sig")
    markers = list(re.finditer(r"^\[Character_Instance\]\r?$", text, re.M))
    if not markers:
        if MARKER in text or re.search(r"^(?:NAME\s*=|\w+_CONTEXT:)", text, re.M):
            raise MigrationBlocked("Unrecognized legacy character marker")
        return None
    begins = list(re.finditer(r"^# --- Li\+ BEGIN \([^\r\n]*\) ---\r?$", text, re.M))
    ends = list(re.finditer(r"^# --- Li\+ END ---\r?$", text, re.M))
    boundary = list(re.finditer(
        rf"^{BANNER}\r?\nResponsibilities\r?\n{BANNER}\r?$", text, re.M
    ))
    if not (len(markers) == len(begins) == len(ends) == len(boundary) == 1):
        raise MigrationBlocked("Legacy character boundaries require user judgment")
    start, stop = markers[0].start(), boundary[0].start()
    if not begins[0].end() < start < stop < ends[0].start():
        raise MigrationBlocked("Legacy character is outside the recognized region")
    lines = text[start:stop].splitlines(keepends=True)
    while lines and lines[-1].strip() in ("", BANNER):
        lines.pop()
    # Only the distributed separator immediately after the marker is formatting.
    while len(lines) > 1 and lines[1].strip() in ("", BANNER):
        lines.pop(1)
    literal = "".join(lines).rstrip("\r\n")
    if not re.search(r"^NAME\s*=\s*\S", literal, re.M):
        raise MigrationBlocked("Legacy character has no recognizable NAME")
    return literal


def instruction_span(text: str) -> tuple[int, int]:
    key = r'(?:developer_instructions|"developer_instructions"|\'developer_instructions\')'
    for match in re.finditer(rf"^[ \t]*{key}[ \t]*=[ \t]*", text, re.M):
        prefix = text[:match.start()]
        try:
            probe = tomllib.loads(prefix + "\n__li_character_root_probe__ = true\n")
        except tomllib.TOMLDecodeError:
            continue
        if probe.get("__li_character_root_probe__") is not True:
            continue
        start = match.end()
        # Try complete quoted values, allowing embedded quotes in multiline TOML.
        for end in range(start + 1, len(text) + 1):
            if text[end - 1] not in "\"'":
                continue
            if end < len(text) and text[end] in "\"'":
                continue
            try:
                value = tomllib.loads("developer_instructions = " + text[start:end])
            except tomllib.TOMLDecodeError:
                continue
            if isinstance(value.get("developer_instructions"), str):
                return start, end
    raise MigrationBlocked("Cannot safely locate root developer_instructions value")


def adapter_present(agents: bytes) -> bool:
    text = agents.decode("utf-8-sig")
    if "Li+ BEGIN" not in text and "Li+ END" not in text:
        return False
    begins = list(re.finditer(r"^# --- Li\+ BEGIN \([^\r\n]*\) ---\r?$", text, re.M))
    ends = list(re.finditer(r"^# --- Li\+ END ---\r?$", text, re.M))
    if len(begins) != 1 or len(ends) != 1 or begins[0].end() >= ends[0].start():
        raise MigrationBlocked("Li+ adapter boundaries require user judgment")
    return True


def plan_migration(agents: bytes | None, config: bytes | None, native_state: str,
                   inherited_instructions: str = "") -> Plan:
    if native_state not in ("absent", "present", "disabled"):
        raise MigrationBlocked("Effective native character state must be resolved")
    literal = legacy_literal(agents) if agents is not None else None
    if agents is not None:
        adapter_present(agents)
    original = config or b""
    text = original.decode("utf-8-sig")
    data = tomllib.loads(text)
    common = data.get("developer_instructions", inherited_instructions)
    if not isinstance(common, str):
        raise MigrationBlocked("developer_instructions must be a string")
    if native_state != "absent" or MARKER in common or re.search(r"^NAME\s*=\s*\S", common, re.M):
        return Plan("preserve-native", original, literal)
    saving_legacy = literal is not None
    if literal is None:
        literal = tomllib.loads(
            (ROOT / "adapter/codex/character-instructions.toml").read_text(encoding="utf-8")
        )["developer_instructions"].rstrip("\n")
    combined = common + ("\n\n" if common else "") + literal
    encoded = json.dumps(combined, ensure_ascii=False)
    if "developer_instructions" in data:
        start, end = instruction_span(text)
        rendered = text[:start] + encoded + text[end:]
    else:
        newline = "\r\n" if "\r\n" in text else "\n"
        rendered = "developer_instructions = " + encoded + newline + text
    result = (b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b"")
    result += rendered.encode("utf-8")
    expected = dict(data, developer_instructions=combined)
    if tomllib.loads(rendered) != expected:
        raise MigrationBlocked("Proposed config changes unrelated settings")
    return Plan("save-legacy" if saving_legacy else "install-default", result, literal)


def backup(path: Path, content: bytes) -> Path:
    target = path.with_name(path.name + ".liplus-character-backup-" + uuid.uuid4().hex)
    with target.open("xb") as stream:
        stream.write(content)
    # Match the source's access mode on POSIX; Windows keeps directory ACL inheritance.
    target.chmod(path.stat().st_mode & 0o777)
    return target


def migrate(agents: Path, config: Path, native_state: str, *, apply: bool = False,
            approve_existing: bool = False, inherited_instructions: str = "") -> dict[str, object]:
    if agents.resolve() == config.resolve():
        raise MigrationBlocked("Agents and config paths must differ")
    old_agents = agents.read_bytes() if agents.exists() else None
    old_config = config.read_bytes() if config.exists() else None
    plan = plan_migration(old_agents, old_config, native_state, inherited_instructions)
    changed = plan.config != (old_config or b"")
    report: dict[str, object] = {"status": plan.status, "config_change": changed,
                                 "applied": False, "backups": []}
    if not apply:
        return report
    if changed and old_config is not None and not approve_existing:
        raise MigrationBlocked("Existing config change requires prior user approval")
    # Recheck the inputs immediately before saving; the old adapter remains untouched.
    if (agents.read_bytes() if agents.exists() else None) != old_agents:
        raise MigrationBlocked("AGENTS.md changed after planning")
    if (config.read_bytes() if config.exists() else None) != old_config:
        raise MigrationBlocked("Config changed after planning")
    saved: list[str] = []
    if old_agents is not None and plan.literal is not None:
        saved.append(str(backup(agents, old_agents)))
    if changed:
        config.parent.mkdir(parents=True, exist_ok=True)
        if old_config is not None:
            saved.append(str(backup(config, old_config)))
        created = False
        try:
            if old_config is None:
                with config.open("xb") as stream:
                    created = True
                    stream.write(plan.config)
                config.chmod(0o600)
            else:
                config.write_bytes(plan.config)
            if config.read_bytes() != plan.config:
                raise MigrationBlocked("Config read-back differs from the plan")
            tomllib.loads(config.read_bytes().decode("utf-8-sig"))
        except Exception:
            if old_config is not None:
                config.write_bytes(old_config)
            elif created:
                config.unlink()
            raise
    report.update(applied=True, backups=saved)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--native-state", choices=("absent", "present", "disabled"), required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approve-existing", action="store_true")
    parser.add_argument("--inherited-instructions", type=Path,
                        help="Private UTF-8 file with effective common instructions if root has no key")
    args = parser.parse_args()
    try:
        report = migrate(args.agents, args.config, args.native_state,
                         apply=args.apply, approve_existing=args.approve_existing,
                         inherited_instructions=(args.inherited_instructions.read_text(encoding="utf-8")
                                                 if args.inherited_instructions else ""))
    except (ValueError, OSError, UnicodeError):
        # Do not leak config values, paths from parse exceptions, or instruction text.
        print(json.dumps({"status": "blocked", "reason": "Resolve migration inputs before adapter replacement"}))
        return 1
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

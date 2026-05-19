#!/usr/bin/env python3
"""Validate Mozi SPECs after edit tools run."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$")
PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+)$")
PATH_KEYS = {
    "path",
    "file",
    "file_path",
    "filepath",
    "filename",
    "target_file",
    "target_path",
}
MOZI_SPEC_MARKERS = (
    "## 4. Operator Interface / 算子接口",
    "## 8. Functional Semantics / 功能语义",
    "## 18. Open Issues / 待确认问题",
)


def emit_block(message: str) -> None:
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": message,
                "continue": False,
                "stopReason": message,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": message,
                },
            },
            ensure_ascii=False,
        )
    )


def read_event() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        emit_block(f"Mozi SPEC validation hook received malformed JSON: {exc}")
        raise SystemExit(0) from exc
    if not isinstance(data, dict):
        return {}
    return data


def collect_path_values(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = str(key).lower()
            if normalized_key in PATH_KEYS and isinstance(child, str):
                paths.add(child)
            else:
                paths.update(collect_path_values(child))
    elif isinstance(value, list):
        for child in value:
            paths.update(collect_path_values(child))
    return paths


def collect_patch_paths(command: str) -> set[str]:
    paths: set[str] = set()
    for line in command.splitlines():
        match = PATCH_PATH_RE.match(line) or PATCH_MOVE_RE.match(line)
        if match:
            paths.add(match.group(1).strip())
    return paths


def resolve_path(path_text: str, cwd: Path) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return path.resolve()


def is_docs_mozi_spec(path: Path) -> bool:
    parts = path.parts
    for index in range(len(parts) - 2):
        if parts[index] == "docs" and parts[index + 1] == "mozi" and path.name == "spec.md":
            return True
    return False


def is_mozi_spec(path: Path) -> bool:
    if not path.is_file() or path.suffix.lower() != ".md":
        return False
    if is_docs_mozi_spec(path):
        return True
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(re.search(r"^# .+ SPEC$", text, re.MULTILINE)) and all(marker in text for marker in MOZI_SPEC_MARKERS)


def validator_path() -> Path:
    plugin_root = os.environ.get("PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        root = Path(plugin_root).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parents[1]
    return root / "skills" / "create-spec" / "scripts" / "validate_spec.py"


def validate_specs(spec_paths: list[Path], cwd: Path) -> list[str]:
    validator = validator_path()
    if not validator.is_file():
        return [f"Mozi SPEC validator not found: {validator}"]

    failures: list[str] = []
    for spec_path in spec_paths:
        result = subprocess.run(
            [sys.executable, str(validator), str(spec_path)],
            cwd=str(cwd),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
            failures.append(output or f"SPEC validation failed: {spec_path}")
    return failures


def main() -> int:
    event = read_event()
    cwd = Path(event.get("cwd") or os.getcwd()).expanduser().resolve()
    tool_input = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}

    candidate_texts = collect_path_values(tool_input)
    command = tool_input.get("command")
    if isinstance(command, str):
        candidate_texts.update(collect_patch_paths(command))

    candidate_paths = sorted({resolve_path(path_text, cwd) for path_text in candidate_texts})
    spec_paths = [path for path in candidate_paths if is_mozi_spec(path)]
    if not spec_paths:
        return 0

    failures = validate_specs(spec_paths, cwd)
    if failures:
        emit_block("Mozi SPEC completeness validation failed after edit:\n\n" + "\n\n".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

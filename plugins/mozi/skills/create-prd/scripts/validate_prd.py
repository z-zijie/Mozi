#!/usr/bin/env python3
"""Validate completeness of a rendered Mozi operator PRD."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = SKILL_DIR / "template" / "PRD.md.templ"

PLACEHOLDER_RE = re.compile(r"\{\{[^{}\n]+\}\}")
H1_RE = re.compile(r"^# (.+?) PRD$", re.MULTILINE)
H2_RE = re.compile(r"^## .+$", re.MULTILINE)
TBD_RE = re.compile(r"\bTBD\b", re.IGNORECASE)
OPEN_QUESTIONS_HEADING = "## 12. Open Questions / 待澄清问题"
NO_OPEN_QUESTIONS_VALUES = {
    "n/a",
    "none",
    "无",
    "无待澄清问题",
    "no open questions.",
}


def read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read {label} '{path}': {exc}") from exc


def template_headings(template_text: str) -> list[str]:
    headings = H2_RE.findall(template_text)
    if not headings:
        raise ValueError("Template does not contain any H2 section headings")
    return headings


def extract_sections(prd_text: str) -> dict[str, str]:
    matches = list(H2_RE.finditer(prd_text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(0)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(prd_text)
        if heading in sections:
            sections[heading] = sections[heading] + "\n\n" + prd_text[start:end].strip()
        else:
            sections[heading] = prd_text[start:end].strip()
    return sections


def infer_operator(prd_text: str) -> str | None:
    match = H1_RE.search(prd_text)
    return match.group(1) if match else None


def validate(prd_path: Path, template_path: Path, expected_operator: str | None) -> list[str]:
    errors: list[str] = []

    if not prd_path.is_file():
        return [f"PRD file does not exist: {prd_path}"]

    prd_text = read_text(prd_path, "PRD")
    template_text = read_text(template_path, "template")
    expected_headings = template_headings(template_text)

    if not prd_text.strip():
        errors.append("PRD file is empty")
        return errors

    inferred_operator = infer_operator(prd_text)
    operator = expected_operator or inferred_operator
    if not operator:
        errors.append("Missing title matching '# <OP_NAME> PRD'")
    else:
        expected_title = f"# {operator} PRD"
        if expected_title not in prd_text.splitlines():
            errors.append(f"Missing exact title: {expected_title}")

    h1_lines = [line for line in prd_text.splitlines() if line.startswith(("# ", "#\t"))]
    if len(h1_lines) != 1:
        errors.append(f"Expected exactly one H1 title, found {len(h1_lines)}")

    actual_headings = H2_RE.findall(prd_text)
    if actual_headings != expected_headings:
        missing = [heading for heading in expected_headings if heading not in actual_headings]
        unexpected = [heading for heading in actual_headings if heading not in expected_headings]
        if missing:
            errors.append("Missing section headings: " + ", ".join(missing))
        if unexpected:
            errors.append("Unexpected section headings: " + ", ".join(unexpected))
        if not missing and not unexpected:
            errors.append("Section headings are out of order")

    duplicate_headings = sorted({heading for heading in actual_headings if actual_headings.count(heading) > 1})
    if duplicate_headings:
        errors.append("Duplicate section headings: " + ", ".join(duplicate_headings))

    placeholders = sorted(set(PLACEHOLDER_RE.findall(prd_text)))
    if placeholders:
        errors.append("Unresolved template placeholders: " + ", ".join(placeholders))

    if TBD_RE.search(prd_text):
        errors.append("PRD contains TBD")

    sections = extract_sections(prd_text)
    for heading in expected_headings:
        body = sections.get(heading, "").strip()
        if not body:
            errors.append(f"Section body is empty: {heading}")

    open_questions = sections.get(OPEN_QUESTIONS_HEADING, "").strip()
    normalized_open_questions = open_questions.strip().lower()
    if normalized_open_questions not in NO_OPEN_QUESTIONS_VALUES:
        errors.append(
            "Open Questions section must explicitly state no open questions "
            f"({', '.join(sorted(NO_OPEN_QUESTIONS_VALUES))})"
        )

    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate completeness of a rendered Mozi operator PRD.")
    parser.add_argument("prd", type=Path, help="Rendered PRD markdown file to validate")
    parser.add_argument("--operator", help="Expected operator name used in the '# <OP_NAME> PRD' title")
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=f"Template file used to derive required headings (default: {DEFAULT_TEMPLATE})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        errors = validate(args.prd, args.template, args.operator)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print(f"PRD validation failed: {args.prd}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"PRD validation passed: {args.prd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate completeness of a rendered Mozi operator SPEC."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = SKILL_DIR / "template" / "SPEC.md.templ"

PLACEHOLDER_RE = re.compile(r"\{\{[^{}\n]+\}\}")
H1_RE = re.compile(r"^# (.+?) SPEC$", re.MULTILINE)
H2_RE = re.compile(r"^## .+$", re.MULTILINE)
TBD_RE = re.compile(r"\bTBD\b", re.IGNORECASE)
REQUIRED_OPERATOR_HEADINGS = (
    "## 3. Supported Platforms / 支持的NPU平台",
    "## 4. Operator Interface / 算子接口",
    "## 5. Input Specification / 输入规格",
    "## 6. Output Specification / 输出规格",
    "## 8. Functional Semantics / 功能语义",
    "## 9. Numeric Semantics / 数值语义",
    "## 10. Shape Semantics / Shape 语义",
    "## 11. Data Type Support / 数据类型支持",
)
OPERATOR_INTERFACE_HEADING = "## 4. Operator Interface / 算子接口"
OPERATOR_INTERFACE_TEMPLATE_NOTE = "算子接口必须使用 PyTorch ATen IR 形式描述。"
OPEN_ISSUES_HEADING = "## 18. Open Issues / 待确认问题"
NO_OPEN_ISSUES_VALUES = {
    "n/a",
    "none",
    "无",
    "无待确认问题",
    "no open issues.",
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


def extract_sections(spec_text: str) -> dict[str, str]:
    matches = list(H2_RE.finditer(spec_text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(0)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(spec_text)
        if heading in sections:
            sections[heading] = sections[heading] + "\n\n" + spec_text[start:end].strip()
        else:
            sections[heading] = spec_text[start:end].strip()
    return sections


def infer_operator(spec_text: str) -> str | None:
    match = H1_RE.search(spec_text)
    return match.group(1) if match else None


def validate(spec_path: Path, template_path: Path, expected_operator: str | None) -> list[str]:
    errors: list[str] = []

    if not spec_path.is_file():
        return [f"SPEC file does not exist: {spec_path}"]

    spec_text = read_text(spec_path, "SPEC")
    template_text = read_text(template_path, "template")
    expected_headings = template_headings(template_text)

    if not spec_text.strip():
        errors.append("SPEC file is empty")
        return errors

    inferred_operator = infer_operator(spec_text)
    operator = expected_operator or inferred_operator
    if not operator:
        errors.append("Missing title matching '# <OP_NAME> SPEC'")
    else:
        expected_title = f"# {operator} SPEC"
        if expected_title not in spec_text.splitlines():
            errors.append(f"Missing exact title: {expected_title}")

    h1_lines = [line for line in spec_text.splitlines() if line.startswith(("# ", "#\t"))]
    if len(h1_lines) != 1:
        errors.append(f"Expected exactly one H1 title, found {len(h1_lines)}")

    actual_headings = H2_RE.findall(spec_text)
    for heading in REQUIRED_OPERATOR_HEADINGS:
        if heading not in actual_headings:
            errors.append(f"Missing required operator section: {heading}")

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

    placeholders = sorted(set(PLACEHOLDER_RE.findall(spec_text)))
    if placeholders:
        errors.append("Unresolved template placeholders: " + ", ".join(placeholders))

    if TBD_RE.search(spec_text):
        errors.append("SPEC contains TBD")

    sections = extract_sections(spec_text)
    for heading in expected_headings:
        body = sections.get(heading, "").strip()
        if not body:
            errors.append(f"Section body is empty: {heading}")

    operator_interface_body = sections.get(OPERATOR_INTERFACE_HEADING, "").strip()
    operator_interface_content = operator_interface_body.replace(OPERATOR_INTERFACE_TEMPLATE_NOTE, "").strip()
    if operator_interface_body and not operator_interface_content:
        errors.append("Operator interface section must include PyTorch ATen IR content")

    open_issues = sections.get(OPEN_ISSUES_HEADING, "").strip()
    normalized_open_issues = open_issues.strip().lower()
    if normalized_open_issues not in NO_OPEN_ISSUES_VALUES:
        errors.append(
            "Open Issues section must explicitly state no open issues "
            f"({', '.join(sorted(NO_OPEN_ISSUES_VALUES))})"
        )

    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate completeness of a rendered Mozi operator SPEC.")
    parser.add_argument("spec", type=Path, help="Rendered SPEC markdown file to validate")
    parser.add_argument("--operator", help="Expected operator name used in the '# <OP_NAME> SPEC' title")
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
        errors = validate(args.spec, args.template, args.operator)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print(f"SPEC validation failed: {args.spec}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"SPEC validation passed: {args.spec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate machine-readable YAML emitted by the Mozi SPEC review skill."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any


DIMENSIONS: dict[str, int] = {
    "scope_clarity": 8,
    "interface_completeness": 10,
    "type_rules": 10,
    "shape_rules": 10,
    "semantic_precision": 15,
    "boundary_coverage": 10,
    "error_handling": 8,
    "layout_and_memory_rules": 8,
    "platform_constraints": 6,
    "implementability": 7,
    "testability": 8,
}

NORMAL_KEYS = [
    "spec_path",
    "total_score",
    "max_score",
    "grade",
    "summary",
    "dimensions",
    "critical_issues",
    "recommended_actions",
]

ERROR_KEYS = [
    "spec_path",
    "total_score",
    "max_score",
    "grade",
    "summary",
    "error",
    "dimensions",
    "critical_issues",
    "recommended_actions",
]

GRADES = {
    "excellent": range(90, 101),
    "good": range(80, 90),
    "acceptable": range(70, 80),
    "weak": range(60, 70),
    "poor": range(0, 60),
}

ERROR_TYPES = {
    "missing_path",
    "not_absolute_path",
    "file_not_found",
    "not_a_file",
    "read_failed",
}

STATUSES = {"pass", "partial", "fail"}


class ParseError(ValueError):
    """Raised when the constrained YAML parser cannot parse the review."""


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value == "true":
        return True
    if value == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise ParseError(f"Invalid quoted string: {value}") from exc
        if not isinstance(parsed, str):
            raise ParseError(f"Quoted scalar must be a string: {value}")
        return parsed
    raise ParseError(f"Unsupported scalar; quote strings explicitly: {value}")


def parse_block(lines: list[str], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        raise ParseError("Unexpected end of document")
    current_indent = line_indent(lines[index])
    if current_indent != indent:
        raise ParseError(f"Expected indentation {indent}, found {current_indent}: {lines[index]}")
    stripped = lines[index].strip()
    if stripped.startswith("- "):
        return parse_list(lines, index, indent)
    return parse_mapping(lines, index, indent)


def parse_mapping(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    data: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        current_indent = line_indent(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ParseError(f"Unexpected indentation {current_indent}: {line}")
        stripped = line.strip()
        if stripped.startswith("- "):
            break
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):(?:\s*(.*))?", stripped)
        if not match:
            raise ParseError(f"Expected mapping entry: {line}")
        key = match.group(1)
        if key in data:
            raise ParseError(f"Duplicate key: {key}")
        raw_value = match.group(2) or ""
        index += 1
        if raw_value == "":
            if index >= len(lines) or line_indent(lines[index]) <= indent:
                raise ParseError(f"Missing nested value for key: {key}")
            value, index = parse_block(lines, index, indent + 2)
        else:
            value = parse_scalar(raw_value)
        data[key] = value
    return data, index


def parse_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    data: list[Any] = []
    while index < len(lines):
        line = lines[index]
        current_indent = line_indent(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ParseError(f"Unexpected indentation {current_indent}: {line}")
        stripped = line.strip()
        if not stripped.startswith("- "):
            break
        raw_item = stripped[2:].strip()
        if not raw_item:
            raise ParseError("Nested list items are not supported in review YAML")
        data.append(parse_scalar(raw_item))
        index += 1
    return data, index


def parse_review_yaml(text: str) -> dict[str, Any]:
    if "```" in text:
        raise ParseError("Markdown code fences are not allowed")
    if "\t" in text:
        raise ParseError("Tabs are not allowed; use two-space indentation")
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ParseError("Review YAML is empty")
    if any(line.lstrip().startswith("#") for line in lines):
        raise ParseError("YAML comments are not allowed")
    if any(line_indent(line) % 2 != 0 for line in lines):
        raise ParseError("Indentation must use two-space levels")
    parsed, index = parse_block(lines, 0, 0)
    if index != len(lines):
        raise ParseError(f"Unexpected trailing content: {lines[index]}")
    if not isinstance(parsed, dict):
        raise ParseError("Top-level YAML value must be a mapping")
    return parsed


def require_mapping(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{path} must be a mapping")
    return {}


def require_list(value: Any, path: str, errors: list[str]) -> list[Any]:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    errors.append(f"{path} must be a list of strings")
    return []


def require_str(value: Any, path: str, errors: list[str], *, allow_empty: bool = False) -> str:
    if isinstance(value, str) and (allow_empty or bool(value.strip())):
        return value
    errors.append(f"{path} must be a {'possibly empty ' if allow_empty else ''}string")
    return ""


def require_int(value: Any, path: str, errors: list[str], minimum: int, maximum: int) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum:
        return value
    errors.append(f"{path} must be an integer from {minimum} to {maximum}")
    return minimum


def expected_grade(total_score: int) -> str:
    for grade, score_range in GRADES.items():
        if total_score in score_range:
            return grade
    return "poor"


def expected_status(score: int, max_score: int) -> str:
    if score * 100 >= max_score * 80:
        return "pass"
    if score * 100 >= max_score * 40:
        return "partial"
    return "fail"


def validate_error_result(review_result: dict[str, Any], expected_spec_path: str | None, errors: list[str]) -> None:
    if list(review_result.keys()) != ERROR_KEYS:
        errors.append("review_result keys must match the error output contract and order")

    spec_path = require_str(review_result.get("spec_path"), "review_result.spec_path", errors, allow_empty=True)
    total_score = require_int(review_result.get("total_score"), "review_result.total_score", errors, 0, 0)
    max_score = require_int(review_result.get("max_score"), "review_result.max_score", errors, 100, 100)
    grade = require_str(review_result.get("grade"), "review_result.grade", errors)
    summary = require_str(review_result.get("summary"), "review_result.summary", errors)
    error = require_mapping(review_result.get("error"), "review_result.error", errors)
    dimensions = require_mapping(review_result.get("dimensions"), "review_result.dimensions", errors)
    critical_issues = require_list(review_result.get("critical_issues"), "review_result.critical_issues", errors)
    recommended_actions = require_list(review_result.get("recommended_actions"), "review_result.recommended_actions", errors)

    if expected_spec_path is not None and spec_path != expected_spec_path:
        errors.append(f"review_result.spec_path must equal expected path: {expected_spec_path}")
    if total_score != 0:
        errors.append("error result total_score must be 0")
    if max_score != 100:
        errors.append("error result max_score must be 100")
    if grade != "poor":
        errors.append('error result grade must be "poor"')
    if summary != "SPEC file cannot be reviewed because the input path is invalid.":
        errors.append("error result summary must match the output contract")
    if dimensions != {}:
        errors.append("error result dimensions must be {}")
    if not critical_issues:
        errors.append("error result critical_issues must not be empty")
    if not recommended_actions:
        errors.append("error result recommended_actions must not be empty")

    if list(error.keys()) != ["type", "message"]:
        errors.append("review_result.error keys must be type and message")
    error_type = require_str(error.get("type"), "review_result.error.type", errors)
    require_str(error.get("message"), "review_result.error.message", errors)
    if error_type and error_type not in ERROR_TYPES:
        errors.append(f"review_result.error.type must be one of: {', '.join(sorted(ERROR_TYPES))}")


def validate_normal_result(review_result: dict[str, Any], expected_spec_path: str | None, errors: list[str]) -> None:
    if list(review_result.keys()) != NORMAL_KEYS:
        errors.append("review_result keys must match the normal output contract and order")

    spec_path = require_str(review_result.get("spec_path"), "review_result.spec_path", errors)
    total_score = require_int(review_result.get("total_score"), "review_result.total_score", errors, 0, 100)
    max_score = require_int(review_result.get("max_score"), "review_result.max_score", errors, 100, 100)
    grade = require_str(review_result.get("grade"), "review_result.grade", errors)
    summary = require_str(review_result.get("summary"), "review_result.summary", errors)
    dimensions = require_mapping(review_result.get("dimensions"), "review_result.dimensions", errors)
    require_list(review_result.get("critical_issues"), "review_result.critical_issues", errors)
    require_list(review_result.get("recommended_actions"), "review_result.recommended_actions", errors)

    if expected_spec_path is not None and spec_path != expected_spec_path:
        errors.append(f"review_result.spec_path must equal expected path: {expected_spec_path}")
    if not Path(spec_path).is_absolute():
        errors.append("review_result.spec_path must be absolute for a normal review result")
    if max_score != 100:
        errors.append("review_result.max_score must be 100")
    if grade not in GRADES:
        errors.append(f"review_result.grade must be one of: {', '.join(GRADES)}")
    elif grade != expected_grade(total_score):
        errors.append(f"review_result.grade must be {expected_grade(total_score)!r} for total_score {total_score}")
    if len(summary) > 240:
        errors.append("review_result.summary should be one concise sentence")

    if list(dimensions.keys()) != list(DIMENSIONS.keys()):
        errors.append("review_result.dimensions keys must match the output contract and order")

    dimension_scores: dict[str, int] = {}
    for dimension, max_value in DIMENSIONS.items():
        entry = require_mapping(dimensions.get(dimension), f"review_result.dimensions.{dimension}", errors)
        if list(entry.keys()) != ["score", "max_score", "status", "findings", "suggestions"]:
            errors.append(f"review_result.dimensions.{dimension} keys must be score, max_score, status, findings, and suggestions")
        score = require_int(entry.get("score"), f"review_result.dimensions.{dimension}.score", errors, 0, max_value)
        declared_max = require_int(entry.get("max_score"), f"review_result.dimensions.{dimension}.max_score", errors, max_value, max_value)
        status = require_str(entry.get("status"), f"review_result.dimensions.{dimension}.status", errors)
        findings = require_list(entry.get("findings"), f"review_result.dimensions.{dimension}.findings", errors)
        suggestions = require_list(entry.get("suggestions"), f"review_result.dimensions.{dimension}.suggestions", errors)
        dimension_scores[dimension] = score
        if declared_max != max_value:
            errors.append(f"review_result.dimensions.{dimension}.max_score must be {max_value}")
        if status not in STATUSES:
            errors.append(f"review_result.dimensions.{dimension}.status must be one of: pass, partial, fail")
        elif status != expected_status(score, max_value):
            errors.append(
                f"review_result.dimensions.{dimension}.status must be "
                f"{expected_status(score, max_value)!r} for score {score}/{max_value}"
            )
        if not findings:
            errors.append(f"review_result.dimensions.{dimension}.findings must not be empty")
        if not suggestions:
            errors.append(f"review_result.dimensions.{dimension}.suggestions must not be empty")

    calculated_total = sum(dimension_scores.values())
    if total_score != calculated_total:
        errors.append(f"review_result.total_score must equal dimension sum {calculated_total}")


def validate(data: dict[str, Any], expected_spec_path: str | None = None) -> list[str]:
    errors: list[str] = []

    if list(data.keys()) != ["review_result"]:
        errors.append("Top-level YAML key must be exactly review_result")

    review_result = require_mapping(data.get("review_result"), "review_result", errors)
    if "error" in review_result:
        validate_error_result(review_result, expected_spec_path, errors)
    else:
        validate_normal_result(review_result, expected_spec_path, errors)
    return errors


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read review YAML '{path}': {exc}") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Mozi SPEC review YAML.")
    parser.add_argument("review_yaml", type=Path, help="YAML review output file to validate")
    parser.add_argument("--spec-path", help="Expected spec_path value in the YAML output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        data = parse_review_yaml(read_text(args.review_yaml))
    except (ParseError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate(data, args.spec_path)
    if errors:
        print(f"SPEC review YAML validation failed: {args.review_yaml}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"SPEC review YAML validation passed: {args.review_yaml}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

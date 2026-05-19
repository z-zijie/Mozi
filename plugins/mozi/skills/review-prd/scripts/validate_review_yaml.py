#!/usr/bin/env python3
"""Validate machine-readable YAML emitted by the Mozi PRD review skill."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any


DIMENSIONS: dict[str, int] = {
    "goal_clarity": 10,
    "scope_completeness": 15,
    "boundary_clarity": 15,
    "verifiability": 20,
    "unambiguity": 10,
    "internal_consistency": 10,
    "stage_boundary_correctness": 10,
    "risk_and_open_question_management": 5,
    "document_structure_and_readability": 5,
}

TOP_LEVEL_KEYS = [
    "review_result",
    "score_breakdown",
    "key_strengths",
    "key_issues",
    "blocking_issues",
    "improvement_suggestions",
    "spec_entry_decision",
    "review_notes",
]

RATINGS = {
    "Excellent": range(90, 101),
    "Good": range(80, 90),
    "Acceptable but Risky": range(70, 80),
    "Weak": range(60, 70),
    "Failed": range(0, 60),
}


class ParseError(ValueError):
    """Raised when the constrained YAML parser cannot parse the review."""


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "[]":
        return []
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


def require_bool(value: Any, path: str, errors: list[str]) -> bool:
    if isinstance(value, bool):
        return value
    errors.append(f"{path} must be a boolean")
    return False


def require_int(value: Any, path: str, errors: list[str], minimum: int, maximum: int) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum:
        return value
    errors.append(f"{path} must be an integer from {minimum} to {maximum}")
    return minimum


def expected_rating(total_score: int) -> str:
    for rating, score_range in RATINGS.items():
        if total_score in score_range:
            return rating
    return "Failed"


def is_failure_shape(total_score: int, rating: str, scores: dict[str, int], blocking: list[str]) -> bool:
    return (
        total_score == 0
        and rating == "Failed"
        and bool(blocking)
        and all(score == 0 for score in scores.values())
    )


def validate(data: dict[str, Any], expected_prd_path: str | None = None) -> list[str]:
    errors: list[str] = []

    if list(data.keys()) != TOP_LEVEL_KEYS:
        errors.append("Top-level keys must match the output contract and order")

    review_result = require_mapping(data.get("review_result"), "review_result", errors)
    score_breakdown = require_mapping(data.get("score_breakdown"), "score_breakdown", errors)
    spec_entry_decision = require_mapping(data.get("spec_entry_decision"), "spec_entry_decision", errors)
    review_notes = require_mapping(data.get("review_notes"), "review_notes", errors)

    if list(review_result.keys()) != ["prd_path", "total_score", "rating"]:
        errors.append("review_result keys must be prd_path, total_score, and rating")
    prd_path = require_str(review_result.get("prd_path"), "review_result.prd_path", errors, allow_empty=True)
    total_score = require_int(review_result.get("total_score"), "review_result.total_score", errors, 0, 100)
    rating = require_str(review_result.get("rating"), "review_result.rating", errors)

    if expected_prd_path is not None and prd_path != expected_prd_path:
        errors.append(f"review_result.prd_path must equal expected path: {expected_prd_path}")

    if rating not in RATINGS:
        errors.append(f"review_result.rating must be one of: {', '.join(RATINGS)}")
    elif rating != expected_rating(total_score):
        errors.append(f"review_result.rating must be {expected_rating(total_score)!r} for total_score {total_score}")

    dimension_scores: dict[str, int] = {}
    if list(score_breakdown.keys()) != list(DIMENSIONS.keys()):
        errors.append("score_breakdown dimensions must match the output contract and order")
    for dimension, max_score in DIMENSIONS.items():
        entry = require_mapping(score_breakdown.get(dimension), f"score_breakdown.{dimension}", errors)
        if list(entry.keys()) != ["score", "max", "comment"]:
            errors.append(f"score_breakdown.{dimension} keys must be score, max, and comment")
        score = require_int(entry.get("score"), f"score_breakdown.{dimension}.score", errors, 0, max_score)
        max_value = require_int(entry.get("max"), f"score_breakdown.{dimension}.max", errors, max_score, max_score)
        comment = require_str(entry.get("comment"), f"score_breakdown.{dimension}.comment", errors)
        dimension_scores[dimension] = score
        if max_value != max_score:
            errors.append(f"score_breakdown.{dimension}.max must be {max_score}")
        if len(comment) > 240:
            errors.append(f"score_breakdown.{dimension}.comment should be brief")

    calculated_total = sum(dimension_scores.values())
    if total_score != calculated_total:
        errors.append(f"review_result.total_score must equal dimension sum {calculated_total}")

    key_strengths = require_list(data.get("key_strengths"), "key_strengths", errors)
    key_issues = require_list(data.get("key_issues"), "key_issues", errors)
    blocking_issues = require_list(data.get("blocking_issues"), "blocking_issues", errors)
    improvement_suggestions = require_list(data.get("improvement_suggestions"), "improvement_suggestions", errors)
    if list(spec_entry_decision.keys()) != ["allowed", "reason"]:
        errors.append("spec_entry_decision keys must be allowed and reason")
    allowed = require_bool(spec_entry_decision.get("allowed"), "spec_entry_decision.allowed", errors)
    reason = require_str(spec_entry_decision.get("reason"), "spec_entry_decision.reason", errors)

    notes_expected = ["assumptions", "warnings"]
    if list(review_notes.keys()) != notes_expected:
        errors.append("review_notes keys must be assumptions and warnings")
    require_list(review_notes.get("assumptions"), "review_notes.assumptions", errors)
    require_list(review_notes.get("warnings"), "review_notes.warnings", errors)

    if allowed and blocking_issues:
        errors.append("blocking_issues must be [] when SPEC entry is allowed")

    mechanical_gate_failed = (
        total_score < 80
        or dimension_scores.get("verifiability", 0) < 15
        or dimension_scores.get("boundary_clarity", 0) < 10
        or dimension_scores.get("scope_completeness", 0) < 10
    )
    if mechanical_gate_failed and allowed:
        errors.append("SPEC entry must be disallowed when a score-based hard gate fails")

    failure_shape = is_failure_shape(total_score, rating, dimension_scores, blocking_issues)
    if prd_path == "" and not failure_shape:
        errors.append("Empty prd_path is only valid for the missing-input failure result")
    if prd_path and not Path(prd_path).is_absolute() and not failure_shape:
        errors.append("Non-absolute prd_path is only valid for an input-validation failure result")

    if not key_strengths and allowed:
        errors.append("key_strengths should not be empty when SPEC entry is allowed")
    if not improvement_suggestions and not allowed:
        errors.append("improvement_suggestions should explain how to unblock SPEC entry")
    if len(reason) > 360:
        errors.append("spec_entry_decision.reason should be concise")

    return errors


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read review YAML '{path}': {exc}") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Mozi PRD review YAML.")
    parser.add_argument("review_yaml", type=Path, help="YAML review output file to validate")
    parser.add_argument("--prd-path", help="Expected prd_path value in the YAML output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        data = parse_review_yaml(read_text(args.review_yaml))
    except (ParseError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate(data, args.prd_path)
    if errors:
        print(f"Review YAML validation failed: {args.review_yaml}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Review YAML validation passed: {args.review_yaml}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

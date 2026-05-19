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
    "## 8. Mathematical Semantics / 数学语义",
    "## 9. Functional Semantics / 功能语义",
    "## 10. Numeric Semantics / 数值语义",
    "## 11. Shape Semantics / Shape 语义",
    "## 12. Data Type Support / 数据类型支持",
)
OPERATOR_INTERFACE_HEADING = "## 4. Operator Interface / 算子接口"
OPERATOR_INTERFACE_TEMPLATE_NOTE = (
    "Define the operator interface using three canonical forms: the PyTorch ATen IR schema, a pure Python API signature with docstring, and a framework-independent pure C++ function signature with Doxygen documentation. The interface definitions are the documentation: every Python/C++ parameter must be documented in the signature block itself, including its functional role, tensor semantics, shape and dtype constraints, layout requirements, aliasing/mutability behavior, default values, and optionality semantics where relevant."
)
REQUIRED_OPERATOR_INTERFACE_SUBSECTIONS = (
    "### PyTorch ATen IR",
    "### Pure Python Signature",
    "### Pure C++ Signature",
)
OPEN_ISSUES_HEADING = "## 19. Open Issues / 待确认问题"
NO_OPEN_ISSUES_VALUES = {
    "n/a",
    "none",
    "无",
    "无待确认问题",
    "no open issues.",
}
H3_RE = re.compile(r"^### .+$", re.MULTILINE)
FENCE_RE_TEMPLATE = r"```{language}\s*\n(.*?)\n```"
PYTHON_DEF_RE = re.compile(r"\bdef\s+[A-Za-z_]\w*\s*\((.*?)\)\s*(?:->\s*[^:\n]+)?\s*:", re.DOTALL)
CPP_SIGNATURE_RE = re.compile(
    r"(?P<return>[A-Za-z_][\w:<>,\s*&]*?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*"
    r"\((?P<params>.*?)\)\s*(?:const\s*)?;",
    re.DOTALL,
)
CPP_FORBIDDEN_NAMESPACE_RE = re.compile(r"\b(?:at|c10)::")
PYTHON_DOCSTRING_RE = re.compile(
    r"\bdef\s+[A-Za-z_]\w*\s*\(.*?\)\s*(?:->\s*[^:\n]+)?\s*:\s*(?P<quote>\"\"\"|''')(?P<body>.*?)(?P=quote)",
    re.DOTALL,
)
PYTHON_ARGS_SECTION_RE = re.compile(
    r"^\s*Args:\s*$"
    r"(?P<body>.*?)"
    r"(?=^\s*(?:Returns?|Yields?|Raises?|Semantics?|Constraints?|Notes?|Examples?):\s*$|\Z)",
    re.DOTALL | re.MULTILINE,
)
PYTHON_ARG_RE = re.compile(r"^\s{4,}([A-Za-z_]\w*)\s*(?:\([^)\n]*\))?\s*:", re.MULTILINE)
CPP_DOXYGEN_RE = re.compile(r"/\*\*(?P<body>.*?)\*/", re.DOTALL)
CPP_PARAM_RE = re.compile(r"@param(?:\s+\[[^\]\n]+\])?\s+([A-Za-z_]\w*)\b")


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


def strip_template_guidance(section_body: str, template_section_body: str) -> str:
    guidance = PLACEHOLDER_RE.sub("", template_section_body).strip()
    content = section_body.strip()
    if guidance and guidance in content:
        content = content.replace(guidance, "", 1).strip()
    return content


def extract_h3_sections(section_text: str) -> dict[str, str]:
    matches = list(H3_RE.finditer(section_text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(0)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section_text)
        sections[heading] = section_text[start:end].strip()
    return sections


def extract_fenced_block(section_text: str, language: str) -> str | None:
    pattern = re.compile(FENCE_RE_TEMPLATE.format(language=re.escape(language)), re.DOTALL)
    match = pattern.search(section_text)
    if not match:
        return None
    return match.group(1).strip()


def split_params(params_text: str) -> list[str]:
    params: list[str] = []
    current: list[str] = []
    depth = 0
    for char in params_text:
        if char in "([<{":
            depth += 1
        elif char in ")]>}":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            param = "".join(current).strip()
            if param:
                params.append(param)
            current = []
        else:
            current.append(char)
    param = "".join(current).strip()
    if param:
        params.append(param)
    return params


def parse_python_params(signature_text: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    match = PYTHON_DEF_RE.search(signature_text)
    if not match:
        return set(), ["Pure Python signature must contain a def function signature"]

    params: set[str] = set()
    for raw_param in split_params(match.group(1)):
        param = raw_param.strip()
        if param in {"", "/", "*"}:
            continue
        if param.startswith(("*args", "**kwargs")):
            errors.append(f"Pure Python signature uses unsupported variadic parameter: {param}")
            continue
        param = param.lstrip("*").split("=", 1)[0].split(":", 1)[0].strip()
        if not re.fullmatch(r"[A-Za-z_]\w*", param):
            errors.append(f"Cannot parse Pure Python parameter name from: {raw_param}")
            continue
        params.add(param)
    return params, errors


def parse_cpp_params(signature_text: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    if CPP_FORBIDDEN_NAMESPACE_RE.search(signature_text):
        errors.append("Pure C++ signature must use framework-independent types, not at:: or c10:: namespaces")

    match = CPP_SIGNATURE_RE.search(signature_text)
    if not match:
        return set(), errors + ["Pure C++ signature must contain a function declaration ending with semicolon"]

    params_text = match.group("params").strip()
    if params_text in {"", "void"}:
        return set(), errors

    params: set[str] = set()
    for raw_param in split_params(params_text):
        param = raw_param.split("=", 1)[0].strip()
        if not param or param == "void":
            continue
        if "..." in param:
            errors.append(f"Pure C++ signature uses unsupported variadic parameter: {raw_param}")
            continue
        name_match = re.search(r"([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?$", param)
        if not name_match:
            errors.append(f"Cannot parse Pure C++ parameter name from: {raw_param}")
            continue
        name = name_match.group(1)
        type_text = param[: name_match.start(1)].strip()
        if not type_text:
            errors.append(f"Pure C++ parameter is missing a type: {raw_param}")
            continue
        params.add(name)
    return params, errors


def parse_python_documented_params(signature_text: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    docstring_match = PYTHON_DOCSTRING_RE.search(signature_text)
    if not docstring_match:
        return set(), ["Pure Python Signature must include a function docstring"]

    docstring = docstring_match.group("body")
    if "Returns:" not in docstring:
        errors.append("Pure Python docstring must include a Returns section")
    if "Args:" not in docstring:
        return set(), errors + ["Pure Python docstring must include an Args section"]

    args_match = PYTHON_ARGS_SECTION_RE.search(docstring)
    if not args_match:
        return set(), errors + ["Pure Python docstring Args section must include parameter entries"]

    documented = set(PYTHON_ARG_RE.findall(args_match.group("body")))
    if not documented:
        errors.append("Pure Python docstring Args section must include parameter entries")
    return documented, errors


def parse_cpp_documented_params(signature_text: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    comment_match = CPP_DOXYGEN_RE.search(signature_text)
    if not comment_match:
        return set(), ["Pure C++ Signature must include a Doxygen comment"]

    comment = comment_match.group("body")
    if "@brief" not in comment:
        errors.append("Pure C++ Doxygen comment must include @brief")
    if "@return" not in comment:
        errors.append("Pure C++ Doxygen comment must include @return")

    documented = set(CPP_PARAM_RE.findall(comment))
    return documented, errors


def validate_operator_interface(operator_interface_body: str) -> list[str]:
    errors: list[str] = []
    operator_interface_content = operator_interface_body.replace(OPERATOR_INTERFACE_TEMPLATE_NOTE, "").strip()
    if not operator_interface_content:
        return ["Operator interface section must include interface content"]

    h3_sections = extract_h3_sections(operator_interface_body)
    for subsection in REQUIRED_OPERATOR_INTERFACE_SUBSECTIONS:
        if subsection not in h3_sections:
            errors.append(f"Operator interface section is missing subsection: {subsection}")

    aten_block = extract_fenced_block(h3_sections.get("### PyTorch ATen IR", ""), "text")
    if not aten_block:
        errors.append("PyTorch ATen IR subsection must include a text fenced code block")
    elif "aten::" not in aten_block:
        errors.append("PyTorch ATen IR code block must include aten:: operator interface content")

    python_block = extract_fenced_block(h3_sections.get("### Pure Python Signature", ""), "python")
    python_params: set[str] = set()
    if not python_block:
        errors.append("Pure Python Signature subsection must include a python fenced code block")
    else:
        python_params, python_errors = parse_python_params(python_block)
        errors.extend(python_errors)
        documented_python_params, python_doc_errors = parse_python_documented_params(python_block)
        errors.extend(python_doc_errors)
        missing_python_docs = sorted(param for param in python_params if param not in documented_python_params)
        if missing_python_docs:
            errors.append("Pure Python docstring Args section is missing parameters: " + ", ".join(missing_python_docs))

    cpp_block = extract_fenced_block(h3_sections.get("### Pure C++ Signature", ""), "cpp")
    cpp_params: set[str] = set()
    if not cpp_block:
        errors.append("Pure C++ Signature subsection must include a cpp fenced code block")
    else:
        cpp_params, cpp_errors = parse_cpp_params(cpp_block)
        errors.extend(cpp_errors)
        documented_cpp_params, cpp_doc_errors = parse_cpp_documented_params(cpp_block)
        errors.extend(cpp_doc_errors)
        missing_cpp_docs = sorted(param for param in cpp_params if param not in documented_cpp_params)
        if missing_cpp_docs:
            errors.append("Pure C++ Doxygen @param documentation is missing parameters: " + ", ".join(missing_cpp_docs))

    if python_params and cpp_params and python_params != cpp_params:
        only_python = sorted(python_params - cpp_params)
        only_cpp = sorted(cpp_params - python_params)
        if only_python:
            errors.append("Parameters present only in Pure Python signature: " + ", ".join(only_python))
        if only_cpp:
            errors.append("Parameters present only in Pure C++ signature: " + ", ".join(only_cpp))

    return errors


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
    template_sections = extract_sections(template_text)

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
        substantive_body = strip_template_guidance(body, template_sections.get(heading, ""))
        if not substantive_body:
            errors.append(f"Section body is empty: {heading}")

    operator_interface_body = sections.get(OPERATOR_INTERFACE_HEADING, "").strip()
    if operator_interface_body:
        errors.extend(validate_operator_interface(operator_interface_body))

    open_issues = strip_template_guidance(
        sections.get(OPEN_ISSUES_HEADING, "").strip(),
        template_sections.get(OPEN_ISSUES_HEADING, ""),
    )
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

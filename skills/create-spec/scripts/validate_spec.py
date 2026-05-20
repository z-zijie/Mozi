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
FUNCTIONAL_SEMANTICS_HEADING = "## 9. Functional Semantics / 功能语义"
SHAPE_SEMANTICS_HEADING = "## 11. Shape Semantics / Shape 语义"
DATA_TYPE_SUPPORT_HEADING = "## 12. Data Type Support / 数据类型支持"
ACCEPTANCE_CRITERIA_HEADING = "## 18. Acceptance Criteria / 验收标准"
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
H4_RE = re.compile(r"^#### .+$", re.MULTILINE)
FENCE_RE_TEMPLATE = r"```{language}\s*\n(.*?)\n```"
PYTHON_SIGNATURE_RE = re.compile(
    r"\bdef\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>.*?)\)\s*(?:->\s*(?P<return>[^:\n]+))?\s*:",
    re.DOTALL,
)
CPP_SIGNATURE_RE = re.compile(
    r"(?P<return>[A-Za-z_][\w:<>,\s*&]*?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*"
    r"\((?P<params>.*?)\)\s*(?P<qualifiers>(?:(?:const|noexcept(?:\s*\([^)]*\))?)\s*)*);",
    re.DOTALL,
)
CPP_DEFINITION_RE = re.compile(
    r"(?P<return>[A-Za-z_][\w:<>,\s*&]*?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*"
    r"\((?P<params>.*?)\)\s*(?P<qualifiers>(?:(?:const|noexcept(?:\s*\([^)]*\))?)\s*)*)\{(?P<body>.*)\}\s*$",
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
CPP_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
NUMPY_IMPORT_RE = re.compile(r"^\s*import\s+numpy\s+as\s+np\s*$", re.MULTILINE)
RETURN_RE = re.compile(r"^\s*return\b", re.MULTILINE)
CPP_RETURN_RE = re.compile(r"\breturn\b")
TABLE_RULES_ASSIGNMENT_RE = re.compile(
    r"^\s*[A-Za-z_]\w*(?:_?(?:table|rules))\s*(?::[^=\n]+)?=\s*(?:\{|\[|\()",
    re.MULTILINE,
)
MARKDOWN_TABLE_RE = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
NUMERIC_LITERAL_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
REQUIRED_NUMERICAL_ANALYSIS_SUBSECTIONS = (
    "#### Floating Point Error Analysis / 浮点误差分析",
    "#### Stability Analysis / 稳定性分析",
    "#### Conditioning / 条件数",
    "#### Reduction Error Analysis / 归约误差分析",
    "#### Mixed Precision Analysis / 混合精度分析",
    "#### Error Budget / 误差预算",
)
CONCLUSION_RE = re.compile(r"^\s*(?:Conclusion|结论)\s*[:：]\s*\S", re.IGNORECASE)


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


def extract_h4_sections(section_text: str) -> dict[str, str]:
    matches = list(H4_RE.finditer(section_text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(0)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section_text)
        sections[heading] = section_text[start:end].strip()
    return sections


def remove_fenced_blocks(section_text: str) -> str:
    return re.sub(r"```.*?```", "", section_text, flags=re.DOTALL).strip()


def extract_fenced_block(section_text: str, language: str) -> str | None:
    pattern = re.compile(FENCE_RE_TEMPLATE.format(language=re.escape(language)), re.DOTALL)
    match = pattern.search(section_text)
    if not match:
        return None
    return match.group(1).strip()


def extract_fenced_blocks(section_text: str, language: str) -> list[str]:
    pattern = re.compile(FENCE_RE_TEMPLATE.format(language=re.escape(language)), re.DOTALL)
    return [match.group(1).strip() for match in pattern.finditer(section_text)]


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


def normalize_python_param(raw_param: str) -> str:
    return re.sub(r"\s+", "", raw_param.strip())


def normalize_python_signature(signature_text: str, label: str) -> tuple[str | None, list[str]]:
    match = PYTHON_SIGNATURE_RE.search(signature_text)
    if not match:
        return None, [f"{label} must contain a def function signature"]
    params = ",".join(normalize_python_param(raw_param) for raw_param in split_params(match.group("params")))
    return_annotation = re.sub(r"\s+", "", (match.group("return") or "").strip())
    normalized = f"def {match.group('name')}({params})->{return_annotation}"
    return normalized, []


def normalize_cpp_signature_match(match: re.Match[str]) -> str:
    return_type = re.sub(r"\s+", "", match.group("return").strip())
    params = ",".join(re.sub(r"\s+", "", raw_param.strip()) for raw_param in split_params(match.group("params")))
    qualifiers = re.sub(r"\s+", "", (match.group("qualifiers") or "").strip())
    return f"{return_type} {match.group('name')}({params}) {qualifiers}".strip()


def strip_cpp_block_comments(signature_text: str) -> str:
    return CPP_BLOCK_COMMENT_RE.sub("", signature_text)


def normalize_cpp_declaration(signature_text: str, label: str) -> tuple[str | None, list[str]]:
    if CPP_FORBIDDEN_NAMESPACE_RE.search(signature_text):
        return None, [f"{label} must use framework-independent types, not at:: or c10:: namespaces"]
    match = CPP_SIGNATURE_RE.search(strip_cpp_block_comments(signature_text))
    if not match:
        return None, [f"{label} must contain a function declaration ending with semicolon"]
    return normalize_cpp_signature_match(match), []


def normalize_cpp_definition(signature_text: str, label: str) -> tuple[str | None, str | None, list[str]]:
    if CPP_FORBIDDEN_NAMESPACE_RE.search(signature_text):
        return None, None, [f"{label} must use framework-independent types, not at:: or c10:: namespaces"]
    match = CPP_DEFINITION_RE.search(strip_cpp_block_comments(signature_text))
    if not match:
        return None, None, [f"{label} must contain a function definition with a body"]
    return normalize_cpp_signature_match(match), match.group("body"), []


def parse_python_signature_details(
    signature_text: str,
    label: str,
) -> tuple[str | None, list[str], list[str], list[str]]:
    errors: list[str] = []
    match = PYTHON_SIGNATURE_RE.search(signature_text)
    if not match:
        return None, [], [], [f"{label} must contain a def function signature"]

    params: list[str] = []
    raw_params = split_params(match.group("params"))
    normalized_params = [normalize_python_param(raw_param) for raw_param in raw_params]
    for raw_param in raw_params:
        param = raw_param.strip()
        if param in {"", "/", "*"}:
            continue
        if param.startswith(("*args", "**kwargs")):
            errors.append(f"{label} uses unsupported variadic parameter: {param}")
            continue
        param = param.lstrip("*").split("=", 1)[0].split(":", 1)[0].strip()
        if not re.fullmatch(r"[A-Za-z_]\w*", param):
            errors.append(f"Cannot parse {label} parameter name from: {raw_param}")
            continue
        params.append(param)
    return match.group("name"), params, normalized_params, errors


def parse_python_signature(signature_text: str, label: str) -> tuple[str | None, list[str], list[str]]:
    name, params, _normalized_params, errors = parse_python_signature_details(signature_text, label)
    return name, params, errors


def parse_python_params(signature_text: str) -> tuple[set[str], list[str]]:
    _name, params, errors = parse_python_signature(signature_text, "Pure Python signature")
    return set(params), errors


def parse_cpp_params_text(params_text: str, label: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    params_text = params_text.strip()
    if params_text in {"", "void"}:
        return set(), errors

    params: set[str] = set()
    for raw_param in split_params(params_text):
        param = raw_param.split("=", 1)[0].strip()
        if not param or param == "void":
            continue
        if "..." in param:
            errors.append(f"{label} uses unsupported variadic parameter: {raw_param}")
            continue
        name_match = re.search(r"([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?$", param)
        if not name_match:
            errors.append(f"Cannot parse {label} parameter name from: {raw_param}")
            continue
        name = name_match.group(1)
        type_text = param[: name_match.start(1)].strip()
        if not type_text:
            errors.append(f"{label} parameter is missing a type: {raw_param}")
            continue
        params.add(name)
    return params, errors


def parse_cpp_params(signature_text: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    if CPP_FORBIDDEN_NAMESPACE_RE.search(signature_text):
        errors.append("Pure C++ signature must use framework-independent types, not at:: or c10:: namespaces")

    match = CPP_SIGNATURE_RE.search(strip_cpp_block_comments(signature_text))
    if not match:
        return set(), errors + ["Pure C++ signature must contain a function declaration ending with semicolon"]

    params, param_errors = parse_cpp_params_text(match.group("params"), "Pure C++ signature")
    return params, errors + param_errors


def parse_cpp_definition_params(signature_text: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    if CPP_FORBIDDEN_NAMESPACE_RE.search(signature_text):
        errors.append(
            "Functional Semantics Pure C++17 Reference Function must use framework-independent types, not at:: or c10:: namespaces"
        )

    match = CPP_DEFINITION_RE.search(strip_cpp_block_comments(signature_text))
    if not match:
        return set(), errors + ["Functional Semantics Pure C++17 Reference Function must contain a function definition with a body"]

    params, param_errors = parse_cpp_params_text(
        match.group("params"),
        "Functional Semantics Pure C++17 Reference Function",
    )
    return params, errors + param_errors


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


def extract_operator_python_block(operator_interface_body: str) -> str | None:
    h3_sections = extract_h3_sections(operator_interface_body)
    return extract_fenced_block(h3_sections.get("### Pure Python Signature", ""), "python")


def extract_operator_cpp_block(operator_interface_body: str) -> str | None:
    h3_sections = extract_h3_sections(operator_interface_body)
    return extract_fenced_block(h3_sections.get("### Pure C++ Signature", ""), "cpp")


def validate_functional_semantics(
    functional_body: str,
    operator_python_block: str | None,
    operator_cpp_block: str | None,
) -> list[str]:
    errors: list[str] = []
    h3_sections = extract_h3_sections(functional_body)
    required_subsections = (
        "### NumPy Reference Function",
        "### Pure C++17 Reference Function",
    )
    for subsection in required_subsections:
        if subsection not in h3_sections:
            errors.append(f"Functional Semantics section is missing subsection: {subsection}")

    numpy_block = extract_fenced_block(h3_sections.get("### NumPy Reference Function", ""), "python")
    if not numpy_block:
        errors.append("Functional Semantics NumPy Reference Function must include a python fenced code block")
    else:
        if not NUMPY_IMPORT_RE.search(numpy_block):
            errors.append("Functional Semantics NumPy Reference Function must include 'import numpy as np'")

        numpy_signature, numpy_signature_errors = normalize_python_signature(
            numpy_block,
            "Functional Semantics NumPy Reference Function",
        )
        errors.extend(numpy_signature_errors)

        numpy_name, numpy_params, _numpy_param_texts, numpy_parse_errors = parse_python_signature_details(
            numpy_block,
            "Functional Semantics NumPy Reference Function",
        )
        errors.extend(numpy_parse_errors)

        if operator_python_block:
            operator_signature, operator_signature_errors = normalize_python_signature(
                operator_python_block,
                "Pure Python Signature",
            )
            if not operator_signature_errors and not numpy_signature_errors and numpy_signature != operator_signature:
                errors.append("Functional Semantics NumPy Reference Function signature must match Pure Python Signature")

        documented_numpy_params, doc_errors = parse_python_documented_params(numpy_block)
        errors.extend(
            error.replace("Pure Python Signature", "Functional Semantics NumPy Reference Function").replace(
                "Pure Python docstring",
                "Functional Semantics NumPy Reference Function docstring",
            )
            for error in doc_errors
        )
        missing_numpy_docs = sorted(param for param in numpy_params if param not in documented_numpy_params)
        if missing_numpy_docs:
            errors.append(
                "Functional Semantics NumPy Reference Function docstring Args section is missing parameters: "
                + ", ".join(missing_numpy_docs)
            )
        if not RETURN_RE.search(numpy_block):
            errors.append("Functional Semantics NumPy Reference Function must include a return statement")
        if numpy_name is None:
            errors.append("Functional Semantics NumPy Reference Function must define a named function")

    cpp17_block = extract_fenced_block(h3_sections.get("### Pure C++17 Reference Function", ""), "cpp")
    if not cpp17_block:
        errors.append("Functional Semantics Pure C++17 Reference Function must include a cpp fenced code block")
    else:
        cpp17_signature, cpp17_body, cpp17_signature_errors = normalize_cpp_definition(
            cpp17_block,
            "Functional Semantics Pure C++17 Reference Function",
        )
        errors.extend(cpp17_signature_errors)

        if operator_cpp_block:
            operator_cpp_signature, operator_cpp_errors = normalize_cpp_declaration(
                operator_cpp_block,
                "Pure C++ Signature",
            )
            if not operator_cpp_errors and not cpp17_signature_errors and cpp17_signature != operator_cpp_signature:
                errors.append("Functional Semantics Pure C++17 Reference Function signature must match Pure C++ Signature")

        cpp17_params, cpp17_param_errors = parse_cpp_definition_params(cpp17_block)
        errors.extend(cpp17_param_errors)
        documented_cpp17_params, cpp17_doc_errors = parse_cpp_documented_params(cpp17_block)
        errors.extend(
            error.replace("Pure C++ Signature", "Functional Semantics Pure C++17 Reference Function").replace(
                "Pure C++ Doxygen",
                "Functional Semantics Pure C++17 Reference Function Doxygen",
            )
            for error in cpp17_doc_errors
        )
        missing_cpp17_docs = sorted(param for param in cpp17_params if param not in documented_cpp17_params)
        if missing_cpp17_docs:
            errors.append(
                "Functional Semantics Pure C++17 Reference Function Doxygen @param documentation is missing parameters: "
                + ", ".join(missing_cpp17_docs)
            )
        if cpp17_body is not None and not CPP_RETURN_RE.search(cpp17_body):
            errors.append("Functional Semantics Pure C++17 Reference Function must include a return statement")

    return errors


def validate_shape_semantics(shape_body: str, operator_python_block: str | None) -> list[str]:
    errors: list[str] = []

    if H3_RE.search(shape_body):
        errors.append("Shape Semantics section must not add subsection headings")

    shape_python_block = extract_fenced_block(shape_body, "python")
    if not shape_python_block:
        return errors + ["Shape Semantics section must include a python fenced code block for NumPy InferShape"]

    if not NUMPY_IMPORT_RE.search(shape_python_block):
        errors.append("Shape Semantics InferShape code block must include 'import numpy as np'")

    shape_name, shape_params, shape_param_texts, shape_signature_errors = parse_python_signature_details(
        shape_python_block,
        "Shape Semantics InferShape function",
    )
    errors.extend(shape_signature_errors)

    if operator_python_block:
        (
            operator_name,
            _operator_params,
            operator_param_texts,
            operator_signature_errors,
        ) = parse_python_signature_details(operator_python_block, "Pure Python signature")
        if not operator_signature_errors and not shape_signature_errors:
            if shape_name != operator_name:
                errors.append(
                    "Shape Semantics InferShape function name must match Pure Python Signature "
                    f"({operator_name})"
                )
            if shape_param_texts != operator_param_texts:
                errors.append(
                    "Shape Semantics InferShape parameters must match Pure Python Signature "
                    f"({', '.join(operator_param_texts)})"
                )

    documented_shape_params, doc_errors = parse_python_documented_params(shape_python_block)
    errors.extend(
        error.replace("Pure Python Signature", "Shape Semantics InferShape").replace(
            "Pure Python docstring",
            "Shape Semantics InferShape docstring",
        )
        for error in doc_errors
    )
    missing_shape_docs = sorted(param for param in shape_params if param not in documented_shape_params)
    if missing_shape_docs:
        errors.append(
            "Shape Semantics InferShape docstring Args section is missing parameters: "
            + ", ".join(missing_shape_docs)
        )

    if not RETURN_RE.search(shape_python_block):
        errors.append("Shape Semantics InferShape function must include a return statement")

    return errors


def validate_data_type_support(dtype_body: str, operator_python_block: str | None) -> list[str]:
    errors: list[str] = []

    dtype_python_block = extract_fenced_block(dtype_body, "python")
    if not dtype_python_block:
        return errors + ["Data Type Support section must include a python fenced code block for InferDtype"]

    dtype_name, dtype_params, dtype_param_texts, dtype_signature_errors = parse_python_signature_details(
        dtype_python_block,
        "Data Type Support InferDtype function",
    )
    errors.extend(dtype_signature_errors)

    if operator_python_block:
        (
            operator_name,
            _operator_params,
            operator_param_texts,
            operator_signature_errors,
        ) = parse_python_signature_details(operator_python_block, "Pure Python signature")
        if not operator_signature_errors and not dtype_signature_errors:
            if dtype_name != operator_name:
                errors.append(
                    "Data Type Support InferDtype function name must match Pure Python Signature "
                    f"({operator_name})"
                )
            if dtype_param_texts != operator_param_texts:
                errors.append(
                    "Data Type Support InferDtype parameters must match Pure Python Signature "
                    f"({', '.join(operator_param_texts)})"
                )

    documented_dtype_params, doc_errors = parse_python_documented_params(dtype_python_block)
    errors.extend(
        error.replace("Pure Python Signature", "Data Type Support InferDtype").replace(
            "Pure Python docstring",
            "Data Type Support InferDtype docstring",
        )
        for error in doc_errors
    )
    missing_dtype_docs = sorted(param for param in dtype_params if param not in documented_dtype_params)
    if missing_dtype_docs:
        errors.append(
            "Data Type Support InferDtype docstring Args section is missing parameters: "
            + ", ".join(missing_dtype_docs)
        )

    if not RETURN_RE.search(dtype_python_block):
        errors.append("Data Type Support InferDtype function must include a return statement")

    if not TABLE_RULES_ASSIGNMENT_RE.search(dtype_python_block):
        errors.append(
            "Data Type Support InferDtype function must use table-driven dtype rules "
            "with a local table/rules assignment"
        )

    return errors


def parse_yaml_scalar(raw_value: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_yaml_key_value(text: str, label: str) -> tuple[str | None, str | None, str | None]:
    if ":" not in text:
        return None, None, f"{label} must use 'key: value' entries"
    key, raw_value = text.split(":", 1)
    key = key.strip()
    if not re.fullmatch(r"[A-Za-z_]\w*", key):
        return None, None, f"{label} has invalid key: {key or text}"
    return key, parse_yaml_scalar(raw_value), None


def parse_precision_yaml(yaml_text: str) -> tuple[list[dict[str, object]], list[str]]:
    errors: list[str] = []
    scenarios: list[dict[str, object]] = []
    current_scenario: dict[str, object] | None = None
    current_output: dict[str, object] | None = None
    seen_top_level = False
    in_outputs = False

    content_lines = [
        line.rstrip()
        for line in yaml_text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not content_lines:
        return [], ["Precision Standards YAML block must not be empty"]

    for line_number, line in enumerate(content_lines, start=1):
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            if stripped != "scenarios:":
                errors.append(f"Precision Standards YAML line {line_number} must be top-level 'scenarios:'")
            elif seen_top_level:
                errors.append("Precision Standards YAML must contain exactly one top-level scenarios key")
            seen_top_level = True
            current_scenario = None
            current_output = None
            in_outputs = False
            continue

        if not seen_top_level:
            errors.append("Precision Standards YAML must start with top-level scenarios key")
            continue

        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            key: str | None = None
            value: str | None = None
            if item_text:
                key, value, key_error = parse_yaml_key_value(item_text, f"Precision Standards YAML line {line_number}")
                if key_error:
                    errors.append(key_error)
                    continue

            if indent == 2:
                current_scenario = {"outputs": []}
                scenarios.append(current_scenario)
                current_output = None
                in_outputs = False
                if key:
                    current_scenario[key] = value or ""
            elif indent == 6 and current_scenario is not None and in_outputs:
                current_output = {}
                outputs = current_scenario.setdefault("outputs", [])
                if isinstance(outputs, list):
                    outputs.append(current_output)
                if key:
                    current_output[key] = value or ""
            else:
                errors.append(f"Precision Standards YAML line {line_number} has invalid list indentation")
            continue

        key, value, key_error = parse_yaml_key_value(stripped, f"Precision Standards YAML line {line_number}")
        if key_error:
            errors.append(key_error)
            continue

        if indent == 4 and current_scenario is not None:
            if key == "outputs":
                current_scenario.setdefault("outputs", [])
                in_outputs = True
                current_output = None
                if value:
                    errors.append("Precision Standards scenario outputs must be a nested non-empty list")
            else:
                current_scenario[key] = value or ""
                in_outputs = False
        elif indent == 8 and current_output is not None:
            current_output[key] = value or ""
        else:
            errors.append(f"Precision Standards YAML line {line_number} has invalid indentation")

    if not seen_top_level:
        errors.append("Precision Standards YAML must include top-level scenarios key")
    return scenarios, errors


def validate_precision_yaml(yaml_text: str) -> list[str]:
    errors: list[str] = []
    if MARKDOWN_TABLE_RE.search(yaml_text):
        errors.append("Precision Standards must use YAML entries, not Markdown table syntax")

    scenarios, parse_errors = parse_precision_yaml(yaml_text)
    errors.extend(parse_errors)
    if parse_errors:
        return errors

    if not scenarios:
        errors.append("Precision Standards scenarios must be a non-empty list")
        return errors

    required_scenario_keys = ("name", "condition", "outputs")
    required_output_keys = ("name", "dtype", "atol", "rtol", "rationale")
    for scenario_index, scenario in enumerate(scenarios, start=1):
        for key in required_scenario_keys:
            if key not in scenario:
                errors.append(f"Precision Standards scenario {scenario_index} is missing {key}")
        for key in ("name", "condition"):
            if not str(scenario.get(key, "")).strip():
                errors.append(f"Precision Standards scenario {scenario_index} has empty {key}")
        outputs = scenario.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            errors.append(f"Precision Standards scenario {scenario_index} outputs must be a non-empty list")
            continue
        for output_index, output in enumerate(outputs, start=1):
            if not isinstance(output, dict):
                errors.append(f"Precision Standards scenario {scenario_index} output {output_index} must be a mapping")
                continue
            for key in required_output_keys:
                if key not in output:
                    errors.append(f"Precision Standards scenario {scenario_index} output {output_index} is missing {key}")
            for key in ("name", "dtype", "rationale"):
                if not str(output.get(key, "")).strip():
                    errors.append(f"Precision Standards scenario {scenario_index} output {output_index} has empty {key}")
            for key in ("atol", "rtol"):
                value = str(output.get(key, "")).strip()
                if not NUMERIC_LITERAL_RE.fullmatch(value):
                    errors.append(
                        f"Precision Standards scenario {scenario_index} output {output_index} {key} must be numeric"
                    )

    return errors


def validate_acceptance_criteria(acceptance_body: str) -> list[str]:
    errors: list[str] = []
    h3_sections = extract_h3_sections(acceptance_body)
    required_subsections = (
        "### Numerical Analysis / 数值分析",
        "### Precision Standards / 精度标准",
        "### NumPy Compare Function / NumPy 精度比对函数",
    )
    for subsection in required_subsections:
        if subsection not in h3_sections:
            errors.append(f"Acceptance Criteria section is missing subsection: {subsection}")

    numerical_body = h3_sections.get("### Numerical Analysis / 数值分析", "").strip()
    if not numerical_body:
        errors.append("Acceptance Criteria Numerical Analysis subsection must include prose")
    elif "```" in numerical_body:
        errors.append("Acceptance Criteria Numerical Analysis subsection must be prose, not code only")
    else:
        h4_sections = extract_h4_sections(numerical_body)
        for subsection in REQUIRED_NUMERICAL_ANALYSIS_SUBSECTIONS:
            subsection_body = h4_sections.get(subsection, "").strip()
            if subsection not in h4_sections:
                errors.append(f"Acceptance Criteria Numerical Analysis is missing subsection: {subsection}")
                continue
            if not subsection_body:
                errors.append(f"Acceptance Criteria Numerical Analysis subsection must include prose: {subsection}")
                continue
            prose_body = remove_fenced_blocks(subsection_body)
            if not prose_body:
                errors.append(f"Acceptance Criteria Numerical Analysis subsection must be prose, not code only: {subsection}")
                continue
            non_empty_lines = [line.strip() for line in prose_body.splitlines() if line.strip()]
            if not non_empty_lines or not CONCLUSION_RE.match(non_empty_lines[-1]):
                errors.append(
                    "Acceptance Criteria Numerical Analysis subsection must end with an explicit "
                    f"Conclusion: or 结论: sentence: {subsection}"
                )

    precision_body = h3_sections.get("### Precision Standards / 精度标准", "")
    if MARKDOWN_TABLE_RE.search(precision_body):
        errors.append("Acceptance Criteria Precision Standards subsection must not use Markdown table syntax")
    yaml_blocks = extract_fenced_blocks(precision_body, "yaml")
    if len(yaml_blocks) != 1:
        errors.append("Acceptance Criteria Precision Standards subsection must include exactly one yaml fenced code block")
    else:
        errors.extend(validate_precision_yaml(yaml_blocks[0]))

    compare_body = h3_sections.get("### NumPy Compare Function / NumPy 精度比对函数", "")
    python_blocks = extract_fenced_blocks(compare_body, "python")
    if len(python_blocks) != 1:
        errors.append("Acceptance Criteria NumPy Compare Function subsection must include exactly one python fenced code block")
    else:
        compare_block = python_blocks[0]
        if "acutal_outputs" in compare_block:
            errors.append("Acceptance Criteria compare function must not use misspelled acutal_outputs")
        compare_signature, compare_signature_errors = normalize_python_signature(
            compare_block,
            "Acceptance Criteria NumPy Compare Function",
        )
        errors.extend(compare_signature_errors)
        if not compare_signature_errors and compare_signature != "def compare(actual_outputs,expected_outputs)->Tuple[bool]":
            errors.append(
                "Acceptance Criteria NumPy Compare Function signature must be "
                "def compare(actual_outputs, expected_outputs) -> Tuple[bool]"
            )
        if not NUMPY_IMPORT_RE.search(compare_block) and not re.search(r"\bnp\.", compare_block):
            errors.append("Acceptance Criteria NumPy Compare Function must import or use NumPy")
        if not RETURN_RE.search(compare_block):
            errors.append("Acceptance Criteria NumPy Compare Function must include a return statement")

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

    functional_semantics_body = sections.get(FUNCTIONAL_SEMANTICS_HEADING, "").strip()
    if functional_semantics_body:
        errors.extend(
            validate_functional_semantics(
                functional_semantics_body,
                extract_operator_python_block(operator_interface_body),
                extract_operator_cpp_block(operator_interface_body),
            )
        )

    shape_semantics_body = sections.get(SHAPE_SEMANTICS_HEADING, "").strip()
    if shape_semantics_body:
        errors.extend(
            validate_shape_semantics(
                shape_semantics_body,
                extract_operator_python_block(operator_interface_body),
            )
        )

    data_type_support_body = sections.get(DATA_TYPE_SUPPORT_HEADING, "").strip()
    if data_type_support_body:
        errors.extend(
            validate_data_type_support(
                data_type_support_body,
                extract_operator_python_block(operator_interface_body),
            )
        )

    acceptance_criteria_body = sections.get(ACCEPTANCE_CRITERIA_HEADING, "").strip()
    if acceptance_criteria_body:
        errors.extend(validate_acceptance_criteria(acceptance_criteria_body))

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

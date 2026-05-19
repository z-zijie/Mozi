---
name: review-spec
description: Reviews NPU operator SPEC Markdown files using a fixed 100-point engineering-quality rubric and YAML-only output. Use when the user invokes $mozi:review-spec with a SPEC file path, asks to review or score an NPU operator SPEC, or needs a machine-readable SPEC quality report.
---

# Review SPEC

Review exactly one SPEC file path from the user request and emit the final answer as YAML only.

## Workflow

1. Extract exactly one SPEC path from the user request.
2. Resolve the path before reading:
   - Missing path: set `spec_path: ""` and `error.type: "missing_path"`.
   - More than one candidate SPEC path: set `spec_path` to the raw path text and return `error.type: "not_absolute_path"`.
   - Absolute path: use it directly.
   - Relative path: resolve it against the target repository root.
   - Nonexistent path: set `spec_path` to the raw provided value and return `error.type: "file_not_found"`.
   - Existing path that is not a file: set `spec_path` to the raw provided value and return `error.type: "not_a_file"`.
   - Unreadable file: set `spec_path` to the raw provided value and return `error.type: "read_failed"`.
   - For any input failure, return the error YAML schema from [references/output-contract.md](references/output-contract.md). Do not ask the user to repeat a path already provided.
3. For a readable path, use the resolved absolute path in `review_result.spec_path`, read the SPEC content, and load:
   - [references/rubric.md](references/rubric.md) for SPEC checks, scoring, grade rules, and review priorities.
   - [references/output-contract.md](references/output-contract.md) for the exact YAML schema.
4. Score each rubric dimension as an integer. Ensure `total_score` equals the sum of all dimension scores.
5. Set each dimension `status` from the dimension-specific status rules in [references/output-contract.md](references/output-contract.md).
6. Before final output, write the draft YAML to a temporary file and validate it:

Treat validator scripts as black-box executables. Do not read, inspect, summarize, or reason from validator source code before running validation. Only inspect validator source code when the user explicitly asks to debug or modify the validator itself.

```bash
python3 plugins/mozi/skills/review-spec/scripts/validate_review_yaml.py <review-yaml-file> --spec-path <resolved-absolute-spec-path>
```

If using an installed plugin outside the repo, run the same script from this skill directory: `scripts/validate_review_yaml.py`.

7. Fix and revalidate until the script passes. Then output the validated YAML only.

## Output Rules

- Do not wrap YAML in Markdown fences.
- Do not output prose, tables, or comments before or after the YAML.
- If the document is readable but not SPEC-like, still output the full review schema, include a critical issue, and score the missing SPEC contract areas accordingly.
- Review the SPEC as an engineering contract for DESIGN, IMPLEMENT, and TEST stages. Do not reward PRD background, business value, roadmap content, or length unless it also makes the SPEC more precise, implementable, and testable.

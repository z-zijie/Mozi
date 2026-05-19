---
name: review-spec
description: Reviews NPU operator SPEC Markdown files using a fixed 100-point engineering-quality rubric and YAML-only output. Use when the user invokes $mozi:review-spec with a SPEC file path, asks to review or score an NPU operator SPEC, or needs a machine-readable SPEC quality report.
---

# Review SPEC

Review exactly one SPEC file path and emit the final answer as YAML only.

## Workflow

1. Accept exactly one argument: `spec_path`.
2. Validate the argument before reading:
   - Missing path: set `spec_path: ""` and `error.type: "missing_path"`.
   - More than one argument: treat the raw provided argument string as the path and return `error.type: "not_absolute_path"` unless it is a single valid absolute path.
   - Non-absolute path: return `error.type: "not_absolute_path"`.
   - Nonexistent path: return `error.type: "file_not_found"`.
   - Existing path that is not a file: return `error.type: "not_a_file"`.
   - Unreadable file: return `error.type: "read_failed"`.
   - For any input failure, return the error YAML schema from [references/output-contract.md](references/output-contract.md). Do not ask the user to repeat a path already provided.
3. For a readable path, read the SPEC content and load:
   - [references/rubric.md](references/rubric.md) for SPEC checks, scoring, grade rules, and review priorities.
   - [references/output-contract.md](references/output-contract.md) for the exact YAML schema.
4. Score each rubric dimension as an integer. Ensure `total_score` equals the sum of all dimension scores.
5. Set each dimension `status` from its score:
   - `pass`: score is at least 80% of the dimension max score.
   - `partial`: score is at least 40% and below 80%.
   - `fail`: score is below 40%.
6. Before final output, write the draft YAML to a temporary file and validate it:

Treat validator scripts as black-box executables. Do not read, inspect, summarize, or reason from validator source code before running validation. Only inspect validator source code when the user explicitly asks to debug or modify the validator itself.

```bash
python3 plugins/mozi/skills/review-spec/scripts/validate_review_yaml.py <review-yaml-file> --spec-path <spec_path>
```

If using an installed plugin outside the repo, run the same script from this skill directory: `scripts/validate_review_yaml.py`.

7. Fix and revalidate until the script passes. Then output the validated YAML only.

## Output Rules

- Do not wrap YAML in Markdown fences.
- Do not output prose, tables, or comments before or after the YAML.
- If the document is readable but not SPEC-like, still output the full review schema, include a critical issue, and score the missing SPEC contract areas accordingly.
- Review the SPEC as an engineering contract for DESIGN, IMPLEMENT, and TEST stages. Do not reward PRD background, business value, roadmap content, or length unless it also makes the SPEC more precise, implementable, and testable.

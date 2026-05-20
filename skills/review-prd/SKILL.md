---
name: review-prd
description: Reviews Mozi/NPU operator PRD Markdown files before the SPEC stage using a 100-point rubric and YAML-only output. Use when the user invokes $mozi:review-prd, asks to review or score an operator PRD, or needs a machine-readable SPEC entry decision for a PRD.
---

# Review PRD

Review exactly one PRD file path from the user request and emit the final answer as YAML only.

## Workflow

1. Extract exactly one PRD path from the user request.
2. Resolve the path before reading:
   - Missing path: set `prd_path: ""` in the YAML failure result.
   - More than one candidate PRD path: set `prd_path` to the raw path text from the request.
   - Absolute path: use it directly.
   - Relative path: resolve it against the target repository root.
   - Nonexistent or unreadable path: set `prd_path` to the raw provided value.
   - For any input failure, return the normal YAML schema with all scores `0`, `rating: "Failed"`, `spec_entry_decision.allowed: false`, and a clear blocking issue.
3. For a readable path, use the resolved absolute path in `review_result.prd_path`, read the PRD content, and load:
   - [references/rubric.md](references/rubric.md) for PRD checks, scoring, ratings, and SPEC gates.
   - [references/output-contract.md](references/output-contract.md) for the exact YAML schema.
4. Score each rubric dimension as an integer. Ensure `total_score` equals the sum of all dimension scores.
5. Before final output, write the draft YAML to a temporary file and validate it:

Treat validator scripts as black-box executables. Do not read, inspect, summarize, or reason from validator source code before running validation. Only inspect validator source code when the user explicitly asks to debug or modify the validator itself.

```bash
python3 skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <resolved-absolute-prd-path>
```

If using an installed plugin outside the repo, run the same script from this skill directory: `scripts/validate_review_yaml.py`.

6. Fix and revalidate until the script passes. Then output the validated YAML only.

## Output Rules

- Do not wrap YAML in Markdown fences.
- Do not output prose, tables, or comments before or after the YAML.
- If the document is readable but not PRD-like, still output the full review schema, include a blocking issue, and set `spec_entry_decision.allowed` to false.

# Review YAML Output Contract

## Contents

- General rules
- Invalid input result
- Exact schema

## General Rules

- Output YAML only.
- Do not use Markdown code fences, Markdown tables, prose prefaces, or YAML comments.
- Use the exact top-level keys shown below.
- Use integer scores only.
- `total_score` must equal the sum of all dimension scores.
- Use `blocking_issues: []` when there are no blocking issues.
- Use `review_notes.assumptions: []` and `review_notes.warnings: []` when none exist.
- Use short quoted strings for comments, issues, suggestions, reasons, assumptions, and warnings.

## Invalid Input Result

For missing, extra, nonexistent, or unreadable input, return the normal schema with:

- all dimension scores set to `0`
- `total_score: 0`
- `rating: "Failed"`
- `spec_entry_decision.allowed: false`
- a clear blocking issue explaining the input error
- `prd_path: ""` only when the path is missing; otherwise use the raw provided path text

Readable relative paths are valid inputs. Resolve them against the target repository root and output the resolved absolute path in successful reviews.

## Exact Schema

```yaml
review_result:
  prd_path: "<absolute path>"
  total_score: <integer 0-100>
  rating: "<Excellent | Good | Acceptable but Risky | Weak | Failed>"

score_breakdown:
  goal_clarity:
    score: <integer 0-10>
    max: 10
    comment: "<brief comment>"
  scope_completeness:
    score: <integer 0-15>
    max: 15
    comment: "<brief comment>"
  boundary_clarity:
    score: <integer 0-15>
    max: 15
    comment: "<brief comment>"
  verifiability:
    score: <integer 0-20>
    max: 20
    comment: "<brief comment>"
  unambiguity:
    score: <integer 0-10>
    max: 10
    comment: "<brief comment>"
  internal_consistency:
    score: <integer 0-10>
    max: 10
    comment: "<brief comment>"
  stage_boundary_correctness:
    score: <integer 0-10>
    max: 10
    comment: "<brief comment>"
  risk_and_open_question_management:
    score: <integer 0-5>
    max: 5
    comment: "<brief comment>"
  document_structure_and_readability:
    score: <integer 0-5>
    max: 5
    comment: "<brief comment>"

key_strengths:
  - "<strength 1>"
  - "<strength 2>"

key_issues:
  - "<issue 1>"
  - "<issue 2>"

blocking_issues:
  - "<blocking issue 1>"

improvement_suggestions:
  - "<suggestion 1>"
  - "<suggestion 2>"

spec_entry_decision:
  allowed: <true | false>
  reason: "<explain whether this PRD can enter SPEC stage and why>"

review_notes:
  assumptions:
    - "<assumption 1>"
  warnings:
    - "<warning 1>"
```

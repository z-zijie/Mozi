# SPEC Review YAML Output Contract

## Contents

- General rules
- Path handling
- Status rules
- Grade rules
- Invalid input result
- Exact schema
- Error schema

## General Rules

- Output YAML only.
- Do not use Markdown code fences, Markdown tables, prose prefaces, or YAML comments.
- Use the exact top-level key and nested keys shown below.
- Use integer scores only.
- `total_score` must equal the sum of all dimension scores.
- `max_score` must be `100`.
- Use short quoted strings for summaries, findings, suggestions, issues, actions, and error messages.
- Use `critical_issues: []` only when there are no critical issues.
- Use `recommended_actions: []` only when there are no recommended actions.

## Path Handling

- Successful reviews must output the resolved absolute SPEC path in `review_result.spec_path`.
- Readable relative SPEC paths are valid inputs. Resolve them against the target repository root.
- Invalid input results use `spec_path: ""` only for missing input. Otherwise use the raw path text supplied by the user.
- Multiple candidate paths are invalid because the skill reviews exactly one SPEC.

## Status Rules

Set `status` from the rubric band for each dimension:

- `scope_clarity`: `pass` 7-8, `partial` 3-6, `fail` 0-2.
- `interface_completeness`: `pass` 9-10, `partial` 3-8, `fail` 0-2.
- `type_rules`: `pass` 9-10, `partial` 3-8, `fail` 0-2.
- `shape_rules`: `pass` 9-10, `partial` 3-8, `fail` 0-2.
- `semantic_precision`: `pass` 13-15, `partial` 5-12, `fail` 0-4.
- `boundary_coverage`: `pass` 9-10, `partial` 3-8, `fail` 0-2.
- `error_handling`: `pass` 7-8, `partial` 3-6, `fail` 0-2.
- `layout_and_memory_rules`: `pass` 7-8, `partial` 3-6, `fail` 0-2.
- `platform_constraints`: `pass` 6, `partial` 2-5, `fail` 0-1.
- `implementability`: `pass` 6-7, `partial` 2-5, `fail` 0-1.
- `testability`: `pass` 7-8, `partial` 3-6, `fail` 0-2.

## Grade Rules

- 90-100: `excellent`
- 80-89: `good`
- 70-79: `acceptable`
- 60-69: `weak`
- 0-59: `poor`

## Invalid Input Result

For missing, ambiguous, nonexistent, non-file, or unreadable input, return the error schema with:

- `total_score: 0`
- `max_score: 100`
- `grade: "poor"`
- `summary: "SPEC file cannot be reviewed because the input path is invalid."`
- `dimensions: {}`
- at least one critical issue and one recommended action
- one of these error types: `missing_path`, `not_absolute_path`, `file_not_found`, `not_a_file`, `read_failed`

Readable relative paths are valid inputs. Resolve them against the target repository root and output the resolved absolute path in successful reviews.

## Exact Schema

```yaml
review_result:
  spec_path: "<absolute path>"
  total_score: <int>
  max_score: 100
  grade: "<excellent|good|acceptable|weak|poor>"
  summary: "<one sentence summary>"
  dimensions:
    scope_clarity:
      score: <int>
      max_score: 8
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    interface_completeness:
      score: <int>
      max_score: 10
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    type_rules:
      score: <int>
      max_score: 10
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    shape_rules:
      score: <int>
      max_score: 10
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    semantic_precision:
      score: <int>
      max_score: 15
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    boundary_coverage:
      score: <int>
      max_score: 10
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    error_handling:
      score: <int>
      max_score: 8
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    layout_and_memory_rules:
      score: <int>
      max_score: 8
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    platform_constraints:
      score: <int>
      max_score: 6
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    implementability:
      score: <int>
      max_score: 7
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
    testability:
      score: <int>
      max_score: 8
      status: "<pass|partial|fail>"
      findings:
        - "<finding>"
      suggestions:
        - "<suggestion>"
  critical_issues:
    - "<issue>"
  recommended_actions:
    - "<action>"
```

## Error Schema

```yaml
review_result:
  spec_path: "<input path>"
  total_score: 0
  max_score: 100
  grade: "poor"
  summary: "SPEC file cannot be reviewed because the input path is invalid."
  error:
    type: "<missing_path|not_absolute_path|file_not_found|not_a_file|read_failed>"
    message: "<error message>"
  dimensions: {}
  critical_issues:
    - "<issue>"
  recommended_actions:
    - "<action>"
```

# SPEC Review YAML Output Contract

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

## Status Rules

- `pass`: score is at least 80% of the dimension max score.
- `partial`: score is at least 40% and below 80%.
- `fail`: score is below 40%.

## Grade Rules

- 90-100: `excellent`
- 80-89: `good`
- 70-79: `acceptable`
- 60-69: `weak`
- 0-59: `poor`

## Invalid Input Result

For missing, non-absolute, nonexistent, non-file, or unreadable input, return the error schema with:

- `total_score: 0`
- `max_score: 100`
- `grade: "poor"`
- `summary: "SPEC file cannot be reviewed because the input path is invalid."`
- `dimensions: {}`
- at least one critical issue and one recommended action
- one of these error types: `missing_path`, `not_absolute_path`, `file_not_found`, `not_a_file`, `read_failed`

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

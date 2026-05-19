# PRD Review Rubric

## Contents

- PRD-like document checks
- Scoring rubric
- Rating levels
- SPEC entry gates

## PRD-like Document Checks

Before scoring, decide whether the file is PRD-like. A valid PRD-like document should generally have:

- A PRD/operator-oriented title or opening.
- Structured sections or headings.
- Goal, scope, requirements, input/output behavior, constraints, acceptance criteria, risks, or references.
- Content that describes what and why, not mostly low-level implementation.

If the document is readable but not PRD-like, still score it using the rubric, add a blocking issue, and set SPEC readiness to false.

## Scoring Rubric

Use integer scores only. The maximum total is 100.

### 1. Goal Clarity / 目标清晰度 - 10 points

Evaluate whether the PRD clearly explains why the requirement exists, what problem it solves, what needs to be delivered, and who or what scenario it serves.

- 9-10: Goal is explicit, concrete, and easy to understand.
- 6-8: Goal is mostly clear but some context is missing.
- 3-5: Goal is vague or incomplete.
- 0-2: Goal is absent or unusable.

### 2. Scope Completeness / 范围完整性 - 15 points

Evaluate whether the PRD defines functional scope, input/output, supported dtype, shape, rank, layout or relevant constraints, main user scenarios, and normal/boundary cases.

- 13-15: Scope is complete and actionable.
- 9-12: Scope is mostly complete with minor missing items.
- 5-8: Scope has obvious gaps.
- 0-4: Scope is unclear or mostly missing.

### 3. Boundary Clarity / 边界清晰度 - 15 points

Evaluate whether the PRD defines non-goals, unsupported features, out-of-scope behaviors, assumptions, constraints, and TBD items that affect scope.

- 13-15: Boundaries are explicit and prevent scope creep.
- 9-12: Boundaries are mostly clear.
- 5-8: Some important boundaries are missing.
- 0-4: Boundaries are unclear or absent.

### 4. Verifiability / 可验证性 - 20 points

Evaluate whether the PRD can be turned into tests. Acceptance criteria should have clear inputs/expected outputs, cover normal cases, edge cases, unsupported or error cases where applicable, and map to automated tests.

- 18-20: Acceptance criteria are concrete and testable.
- 14-17: Mostly testable with minor gaps.
- 8-13: Some testable items, but important gaps exist.
- 0-7: Acceptance criteria are vague or missing.

### 5. Unambiguity / 表述无歧义性 - 10 points

Evaluate whether the PRD avoids ambiguous language such as "good performance", "common cases", "support as much as possible", "reasonable", "appropriate", or "optimize if possible".

- 9-10: Language is precise and low ambiguity.
- 6-8: Minor ambiguous expressions exist.
- 3-5: Several important ambiguous expressions exist.
- 0-2: The document is highly ambiguous.

### 6. Internal Consistency / 一致性 - 10 points

Evaluate whether goals, requirements, constraints, and acceptance criteria agree; repeated definitions do not conflict; and terminology is consistent.

- 9-10: No meaningful inconsistency.
- 6-8: Minor inconsistencies.
- 3-5: Important inconsistencies exist.
- 0-2: The document is internally contradictory.

### 7. Stage Boundary Correctness / 阶段边界正确性 - 10 points

Evaluate whether the PRD stays within PRD responsibilities: what and why. Penalize over-specification of kernel implementation, tiling strategy, memory planning, hardware instruction choice, code structure, low-level API design, or optimization details.

- 9-10: Correct PRD/SPEC/DESIGN boundary.
- 6-8: Minor implementation leakage.
- 3-5: Significant design or implementation leakage.
- 0-2: The document is essentially a design or implementation document.

### 8. Risk and Open Question Management / 风险与开放问题识别 - 5 points

Evaluate whether the PRD identifies open questions, dependencies, risks, TBD items, and items that must be clarified before SPEC.

- 5: Open questions are clear and well classified.
- 3-4: Open questions exist but are not well classified.
- 1-2: Some implicit risks exist but are not clearly listed.
- 0: No risk or open question management.

### 9. Document Structure and Readability / 文档结构与可读性 - 5 points

Evaluate whether the document is well structured, easy to read and review, easy to parse by tools or agents, and maintained with stable headings.

- 5: Clear, stable, readable structure.
- 3-4: Mostly readable with minor structure issues.
- 1-2: Hard to follow.
- 0: Poorly structured or unreadable.

## Rating Levels

- 90-100: `Excellent`
- 80-89: `Good`
- 70-79: `Acceptable but Risky`
- 60-69: `Weak`
- 0-59: `Failed`

## SPEC Entry Gates

Set `spec_ready: false` and `spec_entry_decision.allowed: false` if any gate is true:

- Total score is below 80.
- Verifiability score is below 15.
- Boundary Clarity score is below 10.
- Scope Completeness score is below 10.
- Input/output behavior is missing or unclear.
- Unresolved PRD-level TBDs affect core scope.
- Major contradictions exist.
- Implementation details are so heavy that the document is no longer a PRD.

Otherwise set both values to true.

# SPEC Review Rubric

## Contents

- SPEC-like document checks
- Mandatory Mozi SPEC contract checks
- Scoring rubric
- Grade levels
- Review priorities

## SPEC-like Document Checks

Before scoring, decide whether the file is SPEC-like. A valid NPU operator SPEC should generally define:

- Operator scope, support boundaries, and non-goals.
- Operator interface, inputs, outputs, attributes, signatures, and parameter semantics.
- Dtype, shape, mathematical, functional, numeric, layout, memory, boundary, and error behavior.
- Platform assumptions for target NPU architecture or CANN compatibility where relevant.
- Acceptance criteria or requirements that can drive DESIGN, IMPLEMENT, and TEST work.

If the document is readable but not SPEC-like, still score it using the rubric, add a critical issue, and use specific suggestions to explain how to make it a SPEC.

## Mandatory Mozi SPEC Contract Checks

Apply these checks before assigning high scores:

- Operator Interface must include PyTorch ATen IR, Pure Python Signature with docstring, and framework-independent Pure C++ Signature with Doxygen.
- Python and C++ interface documentation must describe every signature parameter directly, including role, tensor semantics, shape and dtype constraints, layout, aliasing or mutability, defaults, and optionality where relevant.
- Mathematical Semantics must define the operator as a rigorous pure mathematical mapping using professional mathematical language and LaTeX formulas.
- Functional Semantics must include NumPy and Pure C++17 Reference Functions as executable behavioral references.
- The NumPy Reference Function signature must strictly match the Pure Python Signature, including function name, parameter list, defaults, annotations, and return annotation after whitespace normalization.
- The Pure C++17 Reference Function signature must strictly match the Pure C++ Signature, including function name, return type, parameter declarations, parameter order, defaults, and qualifiers after whitespace and declaration-vs-definition normalization.
- Functional reference functions must document every parameter and return actual computed reference outputs.
- Shape Semantics must keep direct section content without subsection headings and include NumPy InferShape code whose function name and parameters match the Pure Python Signature.
- InferShape must include a complete docstring documenting purpose, every parameter, return shape contract, unsupported or error cases, and shape-rule notes.
- Data Type Support must include table-driven InferDtype code whose function name and parameters match the Pure Python Signature.
- InferDtype must include a complete docstring documenting purpose, every parameter, return dtype contract, unsupported or error cases, and promotion-rule notes.
- The SPEC must remain a behavioral contract and avoid kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level runtime API design, or optimization approach.

## Scoring Rubric

Use integer scores only. The maximum total is 100. Do not give high scores for length alone. Reward unambiguous, structured, implementable, and testable engineering rules. Penalize vague phrases such as "reasonable handling", "support as much as possible", "good performance", "normal error", or "appropriate precision".

### 1. scope_clarity - 8 points

Evaluate whether the SPEC clearly defines covered behavior, supported features, unsupported features, assumptions, non-goals, and stage boundaries.

- 7-8: Scope and non-goals are explicit and prevent ambiguity.
- 5-6: Scope is mostly clear with minor gaps.
- 3-4: Scope exists but important boundaries are missing.
- 0-2: Scope is absent, PRD-like, or unusable.

### 2. interface_completeness - 10 points

Evaluate whether the SPEC completely defines operator name, inputs, outputs, attributes, function signatures, parameter semantics, defaults, optionality, and return semantics. Require ATen IR, Pure Python Signature with docstring, and framework-independent Pure C++ Signature with Doxygen before awarding 9-10.

- 9-10: Interface is complete and directly usable.
- 6-8: Interface is mostly complete with minor missing details.
- 3-5: Interface has significant gaps.
- 0-2: Interface is absent or unusable.

### 3. type_rules - 10 points

Evaluate whether dtype support, input/output dtype relations, illegal dtype behavior, and type promotion or non-promotion rules are explicit. Require a table-driven InferDtype function with matching signature and complete docstring before awarding 9-10.

- 9-10: Dtype rules are complete and testable.
- 6-8: Dtype rules are mostly clear.
- 3-5: Dtype rules are partial or ambiguous.
- 0-2: Dtype rules are missing.

### 4. shape_rules - 10 points

Evaluate rank, shape constraints, output shape inference, scalar tensor, empty tensor, broadcasting or reduction rules, and dynamic shape behavior. Require direct Shape Semantics content and NumPy InferShape code with matching signature and complete docstring before awarding 9-10.

- 9-10: Shape rules are complete and testable.
- 6-8: Shape rules are mostly clear.
- 3-5: Shape rules are partial or ambiguous.
- 0-2: Shape rules are missing.

### 5. semantic_precision - 15 points

Evaluate mathematical, functional, and numerical semantics, including rigorous pure mathematical definition, executable NumPy and Pure C++17 behavioral reference functions with signatures matching the operator interface, elementwise or aggregate behavior, special values, precision, rounding, NaN, Inf, and +0/-0 behavior where applicable.

- 13-15: Semantics are rigorous, unambiguous, and cover numeric edge behavior.
- 9-12: Semantics are mostly precise with minor omissions.
- 5-8: Semantics are present but incomplete or vague.
- 0-4: Semantics are missing or not implementable.

### 6. boundary_coverage - 10 points

Evaluate coverage of empty tensors, scalar tensors, extremes, NaN, Inf, zero, negative values, illegal inputs, and operator-specific edge cases.

- 9-10: Boundary cases are broad, specific, and testable.
- 6-8: Boundary coverage is mostly adequate.
- 3-5: Important boundary cases are missing.
- 0-2: Boundary coverage is absent.

### 7. error_handling - 8 points

Evaluate whether illegal inputs have explicit outcomes such as validation failure, compile error, runtime error, unsupported behavior, or undefined behavior.

- 7-8: Error behavior is explicit and actionable.
- 5-6: Error behavior is mostly clear.
- 3-4: Error behavior is partial or vague.
- 0-2: Error behavior is missing.

### 8. layout_and_memory_rules - 8 points

Evaluate layout, format, contiguous and non-contiguous behavior, aliasing, in-place behavior, and input/output buffer relationships.

- 7-8: Layout and memory rules are explicit.
- 5-6: Rules are mostly clear.
- 3-4: Rules are partial or ambiguous.
- 0-2: Rules are missing.

### 9. platform_constraints - 6 points

Evaluate target NPU ARCH, CANN version, hardware constraints, API restrictions, and platform assumptions.

- 6: Platform constraints are explicit.
- 4-5: Platform constraints are mostly clear.
- 2-3: Platform constraints are partial.
- 0-1: Platform constraints are missing.

### 10. implementability - 7 points

Evaluate whether the SPEC gives enough engineering constraints for DESIGN and IMPLEMENT stages to proceed without major product or semantic decisions.

- 6-7: DESIGN and IMPLEMENT can start directly from the SPEC.
- 4-5: Mostly implementable with limited clarification.
- 2-3: Several engineering decisions remain unresolved.
- 0-1: Not implementable as a SPEC.

### 11. testability - 8 points

Evaluate whether key rules naturally become correctness, boundary, negative, dtype, shape, numeric, and compatibility test cases.

- 7-8: Rules are directly convertible to tests.
- 5-6: Mostly testable with minor gaps.
- 3-4: Some testable content exists, but key cases are vague.
- 0-2: Testability is poor or absent.

## Grade Levels

- 90-100: `excellent`
- 80-89: `good`
- 70-79: `acceptable`
- 60-69: `weak`
- 0-59: `poor`

## Review Priorities

- Do not score PRD background, business goals, roadmap, or value statements as primary SPEC quality.
- Penalize SPECs that describe intent but omit dtype, shape, boundary, error, layout, or test requirements.
- Penalize ambiguous phrases that cannot be directly implemented or tested.
- Penalize missing mandatory Mozi SPEC contract structures even if surrounding prose is detailed.
- Reward stable contracts that can drive DESIGN, IMPLEMENT, and TEST work without inventing missing behavior.

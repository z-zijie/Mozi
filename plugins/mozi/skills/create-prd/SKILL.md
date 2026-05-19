---
name: create-prd
description: Creates normalized NPU operator PRD documents from brief prompts, or revises an existing PRD in place from review feedback. Use when the user invokes $mozi:create-prd, asks to create a structured PRD for an operator such as AddRelu, or asks to update a PRD using review comments.
---

# Create PRD

When invoked, either generate a normalized operator PRD from the user's brief prompt or revise an existing PRD from review feedback.

Use this skill when the user invokes `$mozi:create-prd`, asks to create a PRD for an operator, or asks to update an existing PRD using review comments. The output should be a structured PRD document.

## Modes

### Create Mode

Use create mode when the prompt identifies an operator request but does not provide an existing PRD path plus review feedback.

### Revision Mode

Use revision mode when the prompt includes one readable Markdown PRD path and either inline review content or one readable review file path.

- Accept absolute PRD paths and paths relative to the target repository root.
- Treat the provided PRD as the source of truth and modify that same file in place.
- Do not create a new PRD path in revision mode.
- If multiple candidate PRD paths are present, or if the PRD path or review content is missing or unreadable, ask the user to clarify before editing.
- If the review file path is provided, read it as the review input. If inline review content is provided, use that content directly.
- Prefer structured `$mozi:review-prd` YAML when the review matches the review contract. Use `blocking_issues`, `key_issues`, `improvement_suggestions`, `score_breakdown`, `spec_entry_decision`, and `review_notes` as the main sources of requested changes.
- If the review is plain text or invalid YAML, extract the actionable PRD-level issues from the text and apply those changes.
- Do not invent missing product facts. If the review requests missing information but does not provide it, add or keep the item in `Open Questions / 待澄清问题` and let validation report the PRD as incomplete.
- Preserve or restore the canonical template headings and order from `template/PRD.md.templ`.
- Keep edits within PRD boundaries: requirement intent, scope, supported behavior, input/output interface, constraints, risks, references, and acceptance criteria.
- Do not add SPEC/DESIGN/IMPLEMENT details such as kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level API design, or optimization approach.

## Operator Name

Extract the operator name from the user prompt and use it as `<OP_NAME>`.

- Preserve the user's operator-name casing in the PRD title.
- Use a kebab-case directory name for the output path.
- For example, `AddRelu` writes to `docs/mozi/add-relu/prd.md`.
- Split CamelCase boundaries and preserve digit groups: `Conv2D` writes to `docs/mozi/conv2-d/prd.md`; `MatMulV2` writes to `docs/mozi/mat-mul-v2/prd.md`.
- If the prompt does not identify an operator name, ask the user for the operator name before creating the PRD.
- In revision mode, extract `<OP_NAME>` from the PRD title `# <OP_NAME> PRD`. If the title is missing or malformed, infer the operator name from the PRD directory name only as a fallback and report that assumption.

## Output

In create mode, create or overwrite:

```text
docs/mozi/<op-name-kebab-case>/prd.md
```

Always overwrite the target PRD with the rendered PRD generated from the template source. This workflow is deterministic; regeneration replaces the prior generated PRD.

In revision mode, update the provided PRD file in place. Do not overwrite it with a freshly rendered document unless the existing document must be restored to the canonical template structure.

## Template Source

Use `template/PRD.md.templ` in this skill directory as the PRD structure.

- Replace `{{OP_NAME}}` with the parsed operator name.
- Fill each `{{...}}` placeholder with concise PRD content inferred from the user's brief prompt.
- If the prompt does not provide enough information for a section, write `TBD` for that section and add the missing decision to `Open Questions / 待澄清问题`.
- The PRD must include `NPU ARCH` and `算子原型` sections as requirement/interface context only.
- Use `NPU ARCH` to describe the target architecture scope or dependency stated by the prompt, not a hardware execution design.
- Write the operator prototype in PyTorch ATen IR form in the `算子原型` section.
- Do not invent hardware, dtype, shape, framework, accuracy, or requirement-level performance constraints that are not supported by the prompt.
- Keep the section headings and numbering from the template.
- Write section bodies in the user's language. If the prompt mixes languages, prefer concise English technical terms with Chinese explanations where useful.
- In revision mode, use the template as the required section structure while preserving valid existing content that is not contradicted by review feedback.

## PRD Quality

The generated PRD should be requirement-oriented and easy for an operator-development engineer to review before SPEC/DESIGN work begins. It should describe what is needed and why, not how to implement it.

- Keep the document within PRD boundaries: intent, scope, supported behavior, input/output interface, requirement-level constraints, and acceptance criteria.
- Do not include kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level API design, or optimization approach.
- Avoid vague performance promises such as "good performance", "optimized", or "high throughput". Include measurable product requirements only when the prompt explicitly provides them.
- Keep acceptance criteria testable at the requirement level; do not prescribe implementation strategy.
- Prefer concrete bullets over prose when the prompt provides concrete facts. Keep uncertainty explicit instead of filling gaps with assumptions.

## Validation

After writing the PRD, run the completeness validator before reporting success.

Treat validator scripts as black-box executables. Do not read, inspect, summarize, or reason from validator source code before running validation. Only inspect validator source code when the user explicitly asks to debug or modify the validator itself.

First resolve the target repository root. Do not decide that `plugins/mozi/` is missing from a nested output directory such as `docs/mozi/<op-name-kebab-case>/`.

When working in the Mozi plugin repository, prefer the repo-local validator from the repository root:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

In revision mode, validate the actual PRD path that was modified:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py <provided-prd-path> --operator <OP_NAME>
```

When using an installed Mozi plugin in a target repository that does not contain the plugin source tree at `plugins/mozi/`, run the bundled validator from this skill directory instead:

```bash
python3 <this-skill-dir>/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

In revision mode outside the Mozi plugin repository, pass the actual modified PRD path to the bundled validator.

If validation fails, keep the generated or revised PRD file and report the validator errors to the user. The validator is strict: unresolved `TBD` content and open questions make the PRD incomplete.

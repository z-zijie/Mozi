---
name: create-spec
description: Creates behavioral NPU operator SPEC documents from Mozi PRDs, or revises an existing SPEC in place from review feedback. Use when the user invokes $mozi:create-spec, asks to create a SPEC from an operator PRD, or asks to update a SPEC using review comments.
---

# Create SPEC

When invoked, either generate a normalized operator SPEC from an existing PRD or revise an existing SPEC from review feedback.

Use this skill when the user invokes `$mozi:create-spec`, asks to create a SPEC from a Mozi operator PRD, or asks to update an existing SPEC using review comments. The output should be a structured SPEC document.

## Modes

### Create Mode

Use create mode when the prompt includes exactly one readable Markdown PRD path and does not include an existing SPEC path plus review feedback.

- Accept absolute PRD paths and paths relative to the target repository root.
- Read the PRD as the source of truth.
- Create or overwrite the sibling SPEC path:

```text
docs/mozi/<op-name-kebab-case>/spec.md
```

- Do not require a `$mozi:review-prd` pass before generating the SPEC.
- If the PRD lacks facts needed for a final SPEC, do not invent them. Write the unresolved item in `Open Issues / 待确认问题`; strict validation will fail until the item is resolved.

### Revision Mode

Use revision mode when the prompt includes one readable PRD path, one readable SPEC path, and either inline review content or one readable review file path.

- Accept absolute paths and paths relative to the target repository root.
- Treat the PRD as the requirement source of truth.
- Treat the provided SPEC as the document to modify in place.
- Do not create a new SPEC path in revision mode.
- If multiple candidate PRD or SPEC paths are present, or if review content is missing or unreadable, ask the user to clarify before editing.
- If a review file path is provided, read it as the review input. If inline review content is provided, use that content directly.
- Prefer structured YAML review content when present. Otherwise extract actionable SPEC-level issues from natural language comments.
- Preserve or restore the canonical template headings and order from `template/SPEC.md.templ`.
- Keep edits within SPEC boundaries: operator contract, interface, supported inputs/outputs, attributes, functional/numeric/shape semantics, dtype/layout constraints, boundary cases, errors, compatibility, performance requirements, and acceptance criteria.
- Do not add DESIGN/IMPLEMENT details such as kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level runtime API design, or optimization approach.

## Operator Name

In create mode, extract `<OP_NAME>` from the PRD title `# <OP_NAME> PRD`.

- Preserve the operator-name casing in the SPEC title.
- If the PRD title is missing or malformed, infer the operator name from the PRD directory name only as a fallback and report that assumption.
- In revision mode, prefer the SPEC title `# <OP_NAME> SPEC`; if missing, use the PRD title fallback.

## Output

In create mode, create or overwrite:

```text
docs/mozi/<op-name-kebab-case>/spec.md
```

Always overwrite the target SPEC with the rendered SPEC generated from the template source. This workflow is deterministic; regeneration replaces the prior generated SPEC.

In revision mode, update the provided SPEC file in place. Do not overwrite it with a freshly rendered document unless the existing document must be restored to the canonical template structure.

## Template Source

Use `template/SPEC.md.templ` in this skill directory as the SPEC structure.

- Replace `{{OP_NAME}}` with the parsed operator name.
- Fill each `{{...}}` placeholder with concise SPEC content derived from the PRD and user prompt.
- Keep the section headings and numbering from the template.
- Write section bodies in the user's language. If the prompt mixes languages, prefer concise English technical terms with Chinese explanations where useful.
- In revision mode, use the template as the required section structure while preserving valid existing SPEC content that is not contradicted by the PRD or review feedback.

## SPEC Quality

The generated SPEC should be precise enough for DESIGN and implementation work to start, but it should remain a behavioral contract rather than an implementation plan.

- Define the operator interface in PyTorch ATen IR form when available from the PRD.
- Split PRD-level input/output overview into exact input, output, and attribute specifications.
- State supported and unsupported dtype, shape, rank, scalar, empty tensor, layout, and format behavior when the PRD provides it.
- Make functional, numeric, and shape semantics testable.
- Define error handling for unsupported inputs when the PRD or compatibility context supports it. If the PRD does not establish the behavior, list it in `Open Issues / 待确认问题`.
- Preserve PRD constraints unless the review explicitly corrects them.
- Use measurable performance requirements only when the PRD provides them. Otherwise state that no additional performance requirement is specified by the PRD.
- Keep acceptance criteria concrete and suitable for operator-level validation.
- Do not invent hardware, dtype, shape, framework, layout, accuracy, error, or performance requirements that are not supported by the PRD.

## Validation

Completeness validation is handled by the Mozi plugin's bundled `PostToolUse` hook after SPEC edits.

Treat validator scripts as black-box executables. Do not read, inspect, summarize, or reason from validator source code before running validation. Only inspect validator source code when the user explicitly asks to debug or modify the validator itself.

When plugin hooks are enabled and trusted, the hook validates edited Mozi SPECs automatically and reports validator errors back into the turn. If the hook reports validation failure, either fix the SPEC and let the hook run again after the next edit, or report the validation errors to the user if the missing information cannot be resolved from the PRD or prompt.

If plugin hooks are disabled, unavailable, or not trusted, run the completeness validator manually before reporting success.

First resolve the target repository root before choosing a manual validator path. Do not decide that `plugins/mozi/` is missing from a nested output directory such as `docs/mozi/<op-name-kebab-case>/`.

When working in the Mozi plugin repository, prefer the repo-local validator from the repository root:

```bash
python3 plugins/mozi/skills/create-spec/scripts/validate_spec.py docs/mozi/<op-name-kebab-case>/spec.md --operator <OP_NAME>
```

In revision mode, validate the actual SPEC path that was modified:

```bash
python3 plugins/mozi/skills/create-spec/scripts/validate_spec.py <provided-spec-path> --operator <OP_NAME>
```

When using an installed Mozi plugin in a target repository that does not contain the plugin source tree at `plugins/mozi/`, run the bundled validator from this skill directory instead:

```bash
python3 <this-skill-dir>/scripts/validate_spec.py docs/mozi/<op-name-kebab-case>/spec.md --operator <OP_NAME>
```

In revision mode outside the Mozi plugin repository, pass the actual modified SPEC path to the bundled validator.

If validation fails, keep the generated or revised SPEC file and report the validator errors to the user. The validator is strict: unresolved `TBD` content and open issues make the SPEC incomplete.

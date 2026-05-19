---
name: create-prd
description: Creates normalized NPU operator PRD documents from brief prompts. Use when the user invokes $mozi:create-prd or asks to create a structured PRD for an operator such as AddRelu.
---

# Create PRD

When invoked, generate a normalized operator PRD from the user's brief prompt.

Use this skill when the user invokes `$mozi:create-prd` or asks to create a PRD for an operator. The output should be a structured PRD document.

## Operator Name

Extract the operator name from the user prompt and use it as `<OP_NAME>`.

- Preserve the user's operator-name casing in the PRD title.
- Use a kebab-case directory name for the output path.
- For example, `AddRelu` writes to `docs/mozi/add-relu/prd.md`.
- Split CamelCase boundaries and preserve digit groups: `Conv2D` writes to `docs/mozi/conv2-d/prd.md`; `MatMulV2` writes to `docs/mozi/mat-mul-v2/prd.md`.
- If the prompt does not identify an operator name, ask the user for the operator name before creating the PRD.

## Output

Create or overwrite:

```text
docs/mozi/<op-name-kebab-case>/prd.md
```

Always overwrite the target PRD with the rendered PRD generated from the template source. This workflow is deterministic; regeneration replaces the prior generated PRD.

## Template Source

Use `template/PRD.md.templ` in this skill directory as the PRD structure.

- Replace `{{OP_NAME}}` with the parsed operator name.
- Fill each `{{...}}` placeholder with concise PRD content inferred from the user's brief prompt.
- If the prompt does not provide enough information for a section, write `TBD` for that section and add the missing decision to `Open Questions / 待澄清问题`.
- Do not invent hardware, dtype, shape, framework, accuracy, or performance requirements that are not supported by the prompt.
- Keep the section headings and numbering from the template.
- Write section bodies in the user's language. If the prompt mixes languages, prefer concise English technical terms with Chinese explanations where useful.

## PRD Quality

The generated PRD should be implementation-oriented and easy for an operator-development engineer to review. Prefer concrete bullets over prose when the prompt provides concrete facts. Keep uncertainty explicit instead of filling gaps with assumptions.

## Validation

After writing the PRD, run the completeness validator from the repository root:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

If validation fails, keep the generated PRD file and report the validator errors to the user. The validator is strict: unresolved `TBD` content and open questions make the PRD incomplete.

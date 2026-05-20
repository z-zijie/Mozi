# Mozi - Contributor Guidelines

## Project Shape

This repository follows the same root-level plugin structure as `superpowers`.

- Keep shared workflow skills in `skills/`.
- Keep Codex metadata in `.codex-plugin/plugin.json`.
- Keep Claude Code metadata in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- Keep Cursor metadata in `.cursor-plugin/plugin.json`.
- Keep Gemini context in `GEMINI.md` and `gemini-extension.json`.
- Keep OpenCode packaging in `.opencode/`.
- Keep lifecycle hooks in `hooks/`.
- Keep evaluation fixtures and scenarios in `tests/`.

The plugin name is `mozi`. Do not reintroduce a nested `plugins/mozi` plugin root.

## Validation

Validate the repository layout before publishing or installing the plugin:

```bash
scripts/validate-plugin-layout.sh
```

Run workflow-specific validators before reporting success for generated artifacts:

```bash
python3 skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
python3 skills/create-spec/scripts/validate_spec.py docs/mozi/<op-name-kebab-case>/spec.md --operator <OP_NAME>
python3 skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <absolute-prd-path>
python3 skills/review-spec/scripts/validate_review_yaml.py <review-yaml-file> --spec-path <absolute-spec-path>
```

Plugin hooks provide early feedback only. Manual validators are the final success gate.

## Workflow Boundaries

Generated PRDs describe requirements, scope, operator behavior, constraints, and acceptance criteria. They must not include SPEC, DESIGN, IMPLEMENT, tiling, kernel, scheduling, memory-planning, or hardware-instruction details.

Generated SPECs describe the behavioral operator contract, interfaces, mathematical semantics, functional references, dtype and shape rules, layout constraints, boundary cases, error handling, compatibility, performance requirements, and acceptance criteria. They must not include implementation design.

Update `README.md` and this file whenever workflow behavior, supported hosts, or repository structure changes.

# Agent Guide

## Project Shape

This repository is a Codex plugin repository.

- Keep the Codex plugin at `plugins/mozi/`.
- Keep `plugins/mozi/.codex-plugin/plugin.json` present.
- Keep the repo-local marketplace entry at `.agents/plugins/marketplace.json`.
- The plugin folder name and `plugin.json` `name` value must remain `mozi`.
- The marketplace entry must point to `./plugins/mozi`.
- Keep manifest metadata aligned with implemented plugin components. Do not add hooks, MCP servers, apps, or asset references unless the referenced files exist.
- Treat unrelated project skeleton files as incidental unless the user explicitly asks to work on them.

## Validation

Validate `plugins/mozi/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` as JSON before publishing or installing the plugin.

There is no plugin test suite yet. For the `$mozi:create-prd` and `$mozi:review-prd` workflows, validate the manifest, template source, skill files, and validator scripts from the repository root:

```bash
python3 -m json.tool plugins/mozi/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/mozi/hooks/hooks.json >/dev/null
test -f plugins/mozi/hooks/post_edit_validate_prd.py
test -f plugins/mozi/skills/create-prd/SKILL.md
test -f plugins/mozi/skills/create-prd/template/PRD.md.templ
test -f plugins/mozi/skills/create-prd/scripts/validate_prd.py
test -f plugins/mozi/skills/review-prd/SKILL.md
test -f plugins/mozi/skills/review-prd/references/rubric.md
test -f plugins/mozi/skills/review-prd/references/output-contract.md
test -f plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py
```

The PRD completeness validator is strict and intended for final PRDs:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

The `$mozi:create-prd` completeness validator is also wired into a plugin-bundled `PostToolUse` hook at `plugins/mozi/hooks/`. When plugin hooks are enabled with `[features].plugin_hooks = true` and trusted through `/hooks`, PRD edits are validated automatically after edit/write tool calls. If plugin hooks are disabled, unavailable, or not trusted, run the validator manually before reporting success.

Generated PRDs must include the template's NPU ARCH and 算子原型 sections. Treat these as requirement/interface context only: NPU ARCH describes target architecture scope or dependency, and 算子原型 describes the operator prototype in PyTorch ATen IR form.

Generated PRDs must stay within PRD boundaries. They should describe requirement intent, scope, supported behavior, input/output interface, constraints, and acceptance criteria. Do not include SPEC/DESIGN/IMPLEMENT details such as kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level API design, or optimization approach.

When `$mozi:create-prd` receives an existing PRD path plus review feedback, treat it as a review-driven revision workflow. Modify the provided PRD in place, accept either `$mozi:review-prd` YAML or natural-language review comments, preserve the canonical PRD template headings, and keep changes at PRD level. Rely on the post-edit hook for completeness validation when available; otherwise run the same PRD completeness validator on the modified PRD before finishing.

When `$mozi:create-prd` runs from an installed plugin in another target repository, that repository might not have `plugins/mozi/`. In that case, use the loaded skill directory's bundled `scripts/validate_prd.py` and do not treat the missing repo-local plugin source as a workflow failure.

It fails on unresolved template placeholders, `TBD`, missing or reordered template sections, empty section bodies, and unresolved open questions.

The PRD review validator checks the YAML-only review contract:

```bash
python3 plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <absolute-prd-path>
```

It fails on Markdown fences, malformed constrained YAML, missing keys, invalid score ranges, total-score mismatches, rating mismatches, invalid SPEC entry decisions, and score-based hard-gate violations.

## Editing Guidelines

- Prefer small, scoped changes that preserve the plugin layout.
- Preserve the Codex marketplace entry unless explicitly asked to remove it.
- If the marketplace entry is updated, use source path `./plugins/mozi` and include `policy.installation`, `policy.authentication`, and `category`.

## Documentation

Update `README.md` whenever the supported workflow changes. Update this file whenever future agents need new repo-specific instructions.

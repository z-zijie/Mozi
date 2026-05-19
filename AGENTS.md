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

When `$mozi:create-prd` runs from an installed plugin in another target repository, that repository might not have `plugins/mozi/`. In that case, use the loaded skill directory's bundled `scripts/validate_prd.py` and do not treat the missing repo-local plugin source as a workflow failure.

It fails on unresolved template placeholders, `TBD`, missing or reordered template sections, empty section bodies, and unresolved open questions.

The PRD review validator checks the YAML-only review contract:

```bash
python3 plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <absolute-prd-path>
```

It fails on Markdown fences, malformed constrained YAML, missing keys, invalid score ranges, total-score mismatches, rating mismatches, inconsistent SPEC readiness booleans, and score-based hard-gate violations.

## Editing Guidelines

- Prefer small, scoped changes that preserve the plugin layout.
- Preserve the Codex marketplace entry unless explicitly asked to remove it.
- If the marketplace entry is updated, use source path `./plugins/mozi` and include `policy.installation`, `policy.authentication`, and `category`.

## Documentation

Update `README.md` whenever the supported workflow changes. Update this file whenever future agents need new repo-specific instructions.

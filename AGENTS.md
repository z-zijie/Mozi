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

There is no plugin test suite yet. For the `$mozi:create-prd` workflow, validate the manifest, template source, and AddRelu PRD from the repository root:

```bash
python3 -m json.tool plugins/mozi/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
test -f plugins/mozi/skills/create-prd/SKILL.md
test -f plugins/mozi/skills/create-prd/template/PRD.md.templ
test -f docs/mozi/add-relu/prd.md
test -s docs/mozi/add-relu/prd.md
grep -q '^# AddRelu PRD$' docs/mozi/add-relu/prd.md
grep -q '^## 13. References / 参考资料$' docs/mozi/add-relu/prd.md
```

## Editing Guidelines

- Prefer small, scoped changes that preserve the plugin layout.
- Preserve the Codex marketplace entry unless explicitly asked to remove it.
- If the marketplace entry is updated, use source path `./plugins/mozi` and include `policy.installation`, `policy.authentication`, and `category`.

## Documentation

Update `README.md` whenever the supported workflow changes. Update this file whenever future agents need new repo-specific instructions.

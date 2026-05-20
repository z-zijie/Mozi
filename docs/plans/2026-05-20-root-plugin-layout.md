# Mozi Root Plugin Layout Plan

Date: 2026-05-20
Status: Implemented

## Objective

Make Mozi use the same root-level multi-harness plugin structure as `/Users/eureka/Workspace/Github/superpowers`.

## Target Structure

Mozi's repository root is the plugin root:

```text
.
├── .claude-plugin/
├── .codex-plugin/
├── .cursor-plugin/
├── .opencode/
├── assets/
├── docs/
├── tests/
├── hooks/
├── scripts/
└── skills/
```

Shared workflow behavior lives in `skills/`. Host-specific manifests and wrappers are thin adapters around that shared tree.

## Implemented Layout

- Codex manifest: `.codex-plugin/plugin.json`
- Claude Code manifest and marketplace: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- Cursor manifest: `.cursor-plugin/plugin.json`
- Gemini extension: `gemini-extension.json`, `GEMINI.md`
- OpenCode package wrapper: `package.json`, `.opencode/INSTALL.md`, `.opencode/plugins/mozi.js`
- Shared skills: `skills/`
- Shared hooks: `hooks/`
- Evaluation scenarios and fixtures: `tests/`
- Layout verifier: `scripts/validate-plugin-layout.sh`

## Workflow Skills

- `skills/create-prd`
- `skills/review-prd`
- `skills/create-spec`
- `skills/review-spec`
- `skills/using-mozi`

## Acceptance

Run from the repository root:

```bash
scripts/validate-plugin-layout.sh
```

Generated or revised PRD/SPEC artifacts must still pass their workflow-specific validators before completion is reported.

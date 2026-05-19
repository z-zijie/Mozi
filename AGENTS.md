# Agent Guide

## Project Shape

This repository is a Codex plugin repository.

- Keep the Codex plugin at `plugins/mozi/`.
- Keep `plugins/mozi/.codex-plugin/plugin.json` present.
- The plugin folder name and `plugin.json` `name` value must remain `mozi`.
- Leave manifest `[TODO: ...]` placeholders in place until the actual plugin metadata, assets, skills, hooks, MCP servers, or apps are known.
- Treat unrelated project skeleton files as incidental unless the user explicitly asks to work on them.

## Validation

Validate `plugins/mozi/.codex-plugin/plugin.json` as JSON before publishing or installing the plugin.

There is no plugin test suite yet. When adding plugin behavior, add focused validation and document the command here.

## Editing Guidelines

- Prefer small, scoped changes that preserve the plugin layout.
- Do not create a Codex marketplace entry unless explicitly requested.
- If a marketplace entry is requested, use source path `./plugins/mozi` and include `policy.installation`, `policy.authentication`, and `category`.

## Documentation

Update `README.md` whenever the supported workflow changes. Update this file whenever future agents need new repo-specific instructions.

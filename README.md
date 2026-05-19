# Mozi

Mozi is a Codex plugin repository.

## Current Structure

- `plugins/mozi/.codex-plugin/plugin.json`: Codex plugin manifest scaffold.

The plugin manifest intentionally still contains `[TODO: ...]` placeholders. Fill those in once the plugin description, ownership, assets, skills, hooks, MCP servers, or apps are defined.

## Validation

Validate `plugins/mozi/.codex-plugin/plugin.json` as JSON before publishing or installing the plugin.

## Plugin Notes

The plugin name is `mozi`, and the outer folder name matches the manifest `name` field as required by the Codex plugin format.

No marketplace entry has been generated yet. If this plugin should appear in a local Codex marketplace, add `.agents/plugins/marketplace.json` with a local source path of `./plugins/mozi`.

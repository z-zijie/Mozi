# Mozi

Mozi is a Codex plugin repository.

The plugin manifest intentionally still contains `[TODO: ...]` placeholders for unknown plugin metadata. Fill those in once the plugin description, ownership, assets, hooks, MCP servers, or apps are defined.

## Supported Workflows

Invoke `$mozi:create-prd` with an AddRelu operator request to create the initialized PRD stub at `docs/mozi/addrelu/prd.md`. The current version intentionally leaves the PRD empty.

## Installation

Install the Mozi Codex plugin marketplace:

```bash
codex plugin marketplace add z-zijie/Mozi
```

## Plugin Notes

The plugin name is `mozi`, and the outer folder name matches the manifest `name` field as required by the Codex plugin format.

The marketplace name is `mozi-marketplace`, and its plugin entry uses the repo-local source path `./plugins/mozi`.

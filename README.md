# Mozi

Mozi is a Codex plugin for an end-to-end NPU operator development harness.

## Supported Workflows

Invoke `$mozi:create-prd` with an AddRelu operator request to create the initialized PRD stub at `docs/mozi/addrelu/prd.md`. The current workflow intentionally leaves the PRD empty and does not expand the AddRelu requirements unless explicitly requested.

## Installation

Install the Mozi Codex plugin marketplace:

```bash
codex plugin marketplace add z-zijie/Mozi
```

## Plugin Notes

The plugin name is `mozi`, and the outer folder name matches the manifest `name` field as required by the Codex plugin format.

The marketplace name is `mozi-marketplace`, and its plugin entry uses the repo-local source path `./plugins/mozi`.

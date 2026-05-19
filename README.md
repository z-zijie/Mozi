# Mozi

Mozi is a Codex plugin for an end-to-end NPU operator development harness.

## Supported Workflows

Invoke `$mozi:create-prd` with a brief operator request to generate a normalized PRD at `docs/mozi/<op-name-kebab-case>/prd.md`. For example, an AddRelu request writes `docs/mozi/add-relu/prd.md` with the title `# AddRelu PRD`.

The workflow uses `plugins/mozi/skills/create-prd/template/PRD.md.templ` as the canonical PRD structure. It fills sections from the brief prompt, marks missing details as `TBD`, and tracks unresolved decisions in the open questions section.

## Installation

Install the Mozi Codex plugin marketplace:

```bash
codex plugin marketplace add z-zijie/Mozi
```

## Plugin Notes

The plugin name is `mozi`, and the outer folder name matches the manifest `name` field as required by the Codex plugin format.

The marketplace name is `mozi-marketplace`, and its plugin entry uses the repo-local source path `./plugins/mozi`.

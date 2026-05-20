# Mozi

Mozi is an agent CLI plugin for NPU operator development. It provides workflow skills for PRD generation, PRD review, SPEC generation, and SPEC review.

## Quickstart

Install Mozi separately for each harness you use: [Claude Code](#claude-code), [Codex CLI](#codex-cli), [Codex App](#codex-app), [Gemini CLI](#gemini-cli), [OpenCode](#opencode), and [Cursor](#cursor).

## How It Works

Mozi follows the same repository method as `superpowers`: shared behavior lives in one root `skills/` tree, while each host gets a thin adapter around that tree.

The workflows are:

1. **create-prd** - Creates or revises normalized operator PRDs from prompts or review feedback.
2. **review-prd** - Scores a PRD for SPEC readiness and returns YAML only.
3. **create-spec** - Creates or revises behavioral operator SPECs from PRDs.
4. **review-spec** - Scores SPEC quality and returns YAML only.

Hook validation is early feedback. The bundled validators are the final success gates before reporting completion.

## Installation

### Claude Code

Register this repository as a Claude Code plugin marketplace, then install `mozi`:

```bash
/plugin marketplace add z-zijie/Mozi
/plugin install mozi@mozi-dev
```

For local development, `.claude-plugin/marketplace.json` points to `./`, matching the Superpowers root-plugin layout.

### Codex CLI

Install Mozi through the Codex plugin interface:

```bash
/plugins
```

Search for `mozi`, then select `Install Plugin`.

### Codex App

In the Codex app, open Plugins, find `Mozi`, and install it. The Codex plugin manifest is `.codex-plugin/plugin.json`.

### Gemini CLI

Install the extension:

```bash
gemini extensions install https://github.com/z-zijie/Mozi
```

### OpenCode

Tell OpenCode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/z-zijie/Mozi/refs/heads/main/.opencode/INSTALL.md
```

### Cursor

Install Mozi from the Cursor plugin marketplace when available. The Cursor plugin manifest is `.cursor-plugin/plugin.json`.

## Repository Structure

Mozi uses a root-level plugin layout:

```text
.
├── .claude-plugin/
├── .codex-plugin/
├── .cursor-plugin/
├── .opencode/
├── docs/
├── tests/
├── hooks/
├── scripts/
└── skills/
```

Do not reintroduce a nested `plugins/mozi` plugin root. The root is the plugin root.

## Validation

Validate the plugin layout from the repository root:

```bash
scripts/validate-plugin-layout.sh
```

Validate generated PRDs and SPECs with the bundled validators:

```bash
python3 skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
python3 skills/create-spec/scripts/validate_spec.py docs/mozi/<op-name-kebab-case>/spec.md --operator <OP_NAME>
```

Validate review YAML:

```bash
python3 skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <absolute-prd-path>
python3 skills/review-spec/scripts/validate_review_yaml.py <review-yaml-file> --spec-path <absolute-spec-path>
```

## License

GPL-3.0-only. See [LICENSE](LICENSE) for details.

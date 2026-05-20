# Installing Mozi for OpenCode

## Prerequisites

- OpenCode installed

## Installation

Add Mozi to the `plugin` array in your `opencode.json`:

```json
{
  "plugin": ["mozi@git+https://github.com/z-zijie/Mozi.git"]
}
```

Restart OpenCode. The plugin registers all Mozi skills.

Verify by asking:

```text
Tell me about your Mozi workflows
```

OpenCode installs Mozi separately from Claude Code, Codex, Cursor, or Gemini.

## Usage

Use OpenCode's native `skill` tool to list and load Mozi skills:

```text
use skill tool to list skills
use skill tool to load mozi/create-prd
```

## Updating

If OpenCode keeps using a cached git package, clear OpenCode's package cache or reinstall the plugin.

To pin a specific version:

```json
{
  "plugin": ["mozi@git+https://github.com/z-zijie/Mozi.git#v0.1.0"]
}
```

#!/usr/bin/env bash
set -euo pipefail

python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m json.tool .claude-plugin/plugin.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .cursor-plugin/plugin.json >/dev/null
python3 -m json.tool gemini-extension.json >/dev/null
python3 -m json.tool package.json >/dev/null
python3 -m json.tool hooks/hooks.json >/dev/null
python3 -m json.tool hooks/hooks-cursor.json >/dev/null

test -f hooks/post_edit_validate_prd.py
test -f hooks/post_edit_validate_spec.py
test -f hooks/session-start
test -f hooks/run-hook.cmd

test -f skills/create-prd/SKILL.md
test -f skills/create-prd/agents/openai.yaml
test -f skills/create-prd/template/PRD.md.templ
test -f skills/create-prd/scripts/validate_prd.py

test -f skills/review-prd/SKILL.md
test -f skills/review-prd/agents/openai.yaml
test -f skills/review-prd/references/rubric.md
test -f skills/review-prd/references/output-contract.md
test -f skills/review-prd/scripts/validate_review_yaml.py

test -f skills/create-spec/SKILL.md
test -f skills/create-spec/agents/openai.yaml
test -f skills/create-spec/template/SPEC.md.templ
test -f skills/create-spec/scripts/validate_spec.py

test -f skills/review-spec/SKILL.md
test -f skills/review-spec/agents/openai.yaml
test -f skills/review-spec/references/rubric.md
test -f skills/review-spec/references/output-contract.md
test -f skills/review-spec/scripts/validate_review_yaml.py

test -f skills/using-mozi/SKILL.md

test -f AGENTS.md
test -f CLAUDE.md
test -f GEMINI.md
test -f README.md
test -f RELEASE-NOTES.md
test -f CODE_OF_CONDUCT.md
test -f docs/README.opencode.md
test -f docs/testing.md
test -f .github/PULL_REQUEST_TEMPLATE.md
test -f .opencode/INSTALL.md
test -f .opencode/plugins/mozi.js
test -f assets/mozi-small.svg
test -f assets/app-icon.svg
test -f tests/skill-scenarios.json
test -f tests/fixtures/add-relu/prd.md
test -f tests/fixtures/add-relu/spec.md

python3 - <<'PY'
import json
from pathlib import Path

codex = json.loads(Path(".codex-plugin/plugin.json").read_text())
claude = json.loads(Path(".claude-plugin/plugin.json").read_text())
cursor = json.loads(Path(".cursor-plugin/plugin.json").read_text())
gemini = json.loads(Path("gemini-extension.json").read_text())
package = json.loads(Path("package.json").read_text())
claude_marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text())

assert codex["name"] == "mozi", "Codex manifest name must be mozi"
assert claude["name"] == "mozi", "Claude manifest name must be mozi"
assert cursor["name"] == "mozi", "Cursor manifest name must be mozi"
assert gemini["name"] == "mozi", "Gemini extension name must be mozi"
assert package["name"] == "mozi", "package name must be mozi"
assert codex["version"] == claude["version"], "Codex and Claude manifest versions must match"
assert cursor["version"] == codex["version"], "Cursor and Codex manifest versions must match"
assert gemini["version"] == codex["version"], "Gemini and Codex manifest versions must match"
assert package["version"] == codex["version"], "package and Codex manifest versions must match"
assert codex.get("skills") == "./skills/", "Codex manifest must point skills to ./skills/"
assert codex.get("hooks") == "./hooks/hooks.json", "Codex manifest must point hooks to ./hooks/hooks.json"
assert cursor.get("skills") == "./skills/", "Cursor manifest must point skills to ./skills/"
assert cursor.get("hooks") == "./hooks/hooks-cursor.json", "Cursor manifest must point hooks to ./hooks/hooks-cursor.json"

claude_plugins = {entry["name"]: entry for entry in claude_marketplace["plugins"]}

assert claude_plugins["mozi"]["source"] == "./", "Claude marketplace must point to repo root"
PY

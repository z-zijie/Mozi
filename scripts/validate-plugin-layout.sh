#!/usr/bin/env bash
set -euo pipefail

python3 -m json.tool plugins/mozi/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/mozi/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool plugins/mozi/hooks/hooks.json >/dev/null

test -f plugins/mozi/hooks/post_edit_validate_prd.py
test -f plugins/mozi/hooks/post_edit_validate_spec.py

test -f plugins/mozi/skills/create-prd/SKILL.md
test -f plugins/mozi/skills/create-prd/template/PRD.md.templ
test -f plugins/mozi/skills/create-prd/scripts/validate_prd.py

test -f plugins/mozi/skills/review-prd/SKILL.md
test -f plugins/mozi/skills/review-prd/references/rubric.md
test -f plugins/mozi/skills/review-prd/references/output-contract.md
test -f plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py

test -f plugins/mozi/skills/create-spec/SKILL.md
test -f plugins/mozi/skills/create-spec/template/SPEC.md.templ
test -f plugins/mozi/skills/create-spec/scripts/validate_spec.py

test -f plugins/mozi/skills/review-spec/SKILL.md
test -f plugins/mozi/skills/review-spec/references/rubric.md
test -f plugins/mozi/skills/review-spec/references/output-contract.md
test -f plugins/mozi/skills/review-spec/scripts/validate_review_yaml.py

python3 - <<'PY'
import json
from pathlib import Path

codex = json.loads(Path("plugins/mozi/.codex-plugin/plugin.json").read_text())
claude = json.loads(Path("plugins/mozi/.claude-plugin/plugin.json").read_text())
codex_marketplace = json.loads(Path(".agents/plugins/marketplace.json").read_text())
claude_marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text())

assert codex["name"] == "mozi", "Codex manifest name must be mozi"
assert claude["name"] == "mozi", "Claude manifest name must be mozi"
assert codex["version"] == claude["version"], "Codex and Claude manifest versions must match"
assert codex.get("skills") == "./skills/", "Codex manifest must point skills to ./skills/"
assert codex.get("hooks") == "./hooks/hooks.json", "Codex manifest must point hooks to ./hooks/hooks.json"

codex_plugins = {entry["name"]: entry for entry in codex_marketplace["plugins"]}
claude_plugins = {entry["name"]: entry for entry in claude_marketplace["plugins"]}

assert codex_plugins["mozi"]["source"]["path"] == "./plugins/mozi", "Codex marketplace must point to ./plugins/mozi"
assert claude_plugins["mozi"]["source"] == "./plugins/mozi", "Claude marketplace must point to ./plugins/mozi"

policy = codex_plugins["mozi"]["policy"]
assert policy["installation"] == "AVAILABLE", "Codex marketplace policy.installation must be AVAILABLE"
assert policy["authentication"] == "ON_INSTALL", "Codex marketplace policy.authentication must be ON_INSTALL"
assert codex_plugins["mozi"]["category"], "Codex marketplace category is required"
PY

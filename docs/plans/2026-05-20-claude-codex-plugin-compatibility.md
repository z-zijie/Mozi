# Mozi Claude Code and Codex Plugin Compatibility Plan

Date: 2026-05-20
Status: Phase 1-2 implemented

## Objective

Refactor Mozi so one repository can support both Claude Code plugin installation and Codex plugin installation without losing any current Mozi workflows:

- `$mozi:create-prd`
- `$mozi:review-prd`
- `$mozi:create-spec`
- `$mozi:review-spec`
- PRD and SPEC validation hooks where the host supports plugin hooks
- future development that keeps Claude Code and Codex CLI agent behavior aligned

## Superpowers Compatibility Model

The Superpowers repository supports multiple agent CLIs by keeping shared skill content in one canonical skills tree and adding thin host-specific packaging around it.

Observed structure in `/Users/eureka/Workspace/Github/superpowers`:

- `skills/*/SKILL.md` is the shared behavior surface.
- `.claude-plugin/plugin.json` describes the Claude Code plugin.
- `.claude-plugin/marketplace.json` publishes a Claude marketplace entry whose plugin source is `./`.
- `.codex-plugin/plugin.json` describes the Codex plugin and points `skills` to `./skills/`.
- `.opencode/plugins/superpowers.js`, `package.json`, and `.opencode/INSTALL.md` provide a native OpenCode wrapper.
- `CLAUDE.md`, `GEMINI.md`, and host reference files add bootstrap and tool-mapping instructions for hosts that need them.
- `scripts/sync-to-codex-plugin.sh` copies the same upstream plugin content into the OpenAI Codex marketplace repository, while excluding host-specific files that should not be embedded in the Codex plugin.

The important design choice is that host-specific files are adapters, not forks. The skills remain the source of truth, while manifests, marketplaces, hooks, and install docs are per-host packaging.

## Current Mozi State

Mozi is currently Codex-first:

- Canonical plugin source is `plugins/mozi/`.
- Codex manifest exists at `plugins/mozi/.codex-plugin/plugin.json`.
- Repo-local Codex marketplace exists at `.agents/plugins/marketplace.json` and points to `./plugins/mozi`.
- Shared skills exist at `plugins/mozi/skills/`.
- Codex plugin hooks exist at `plugins/mozi/hooks/hooks.json`.
- Per-skill Codex metadata exists as `plugins/mozi/skills/*/agents/openai.yaml`.
- There is no Claude plugin manifest or Claude marketplace file.
- README documents Codex installation only.

## Compatibility Strategy

Keep `plugins/mozi/` as the canonical plugin source. Add Claude Code packaging inside and around that same source tree instead of duplicating skills.

### Directory Layout

Target structure:

```text
.
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
├── plugins/mozi/
│   ├── .codex-plugin/plugin.json
│   ├── .claude-plugin/plugin.json
│   ├── hooks/
│   │   ├── hooks.json
│   │   ├── post_edit_validate_prd.py
│   │   └── post_edit_validate_spec.py
│   └── skills/
│       ├── create-prd/
│       ├── review-prd/
│       ├── create-spec/
│       └── review-spec/
└── README.md
```

Rationale:

- Preserves the repo rule that the Codex plugin stays at `plugins/mozi/`.
- Lets Claude marketplace source point at `./plugins/mozi`, so Claude sees a plugin root with `.claude-plugin/plugin.json` and `skills/`.
- Avoids a second top-level `skills/` tree that would drift from Codex.
- Keeps one implementation of validator scripts, templates, references, and hooks.

### Manifest Model

Codex remains in `plugins/mozi/.codex-plugin/plugin.json`:

- `name` stays `mozi`.
- `skills` stays `./skills/`.
- `hooks` stays `./hooks/hooks.json`.
- Existing interface metadata and default prompts remain aligned with implemented workflows.

Claude adds `plugins/mozi/.claude-plugin/plugin.json`:

- `name` must be `mozi`.
- `version`, `description`, `author`, `homepage`, `repository`, `license`, and `keywords` should match the Codex manifest where possible.
- It should not declare Codex-only `interface`, `hooks`, apps, or MCP server fields unless Claude's plugin format supports and consumes them.
- The Claude plugin source root is `plugins/mozi`, so its `skills/` directory remains adjacent to the manifest.

Repo-local Claude marketplace adds `.claude-plugin/marketplace.json`:

```json
{
  "name": "mozi-dev",
  "description": "Development marketplace for the Mozi NPU operator workflow plugin",
  "owner": {
    "name": "z-zijie",
    "email": "z-zijie@users.noreply.github.com"
  },
  "plugins": [
    {
      "name": "mozi",
      "description": "NPU operator PRD and SPEC workflow plugin",
      "version": "0.1.0",
      "source": "./plugins/mozi",
      "author": {
        "name": "z-zijie",
        "email": "z-zijie@users.noreply.github.com"
      }
    }
  ]
}
```

This mirrors Superpowers' Claude marketplace pattern but changes `source` from `./` to `./plugins/mozi` because Mozi's plugin root is nested.

### Skill Compatibility

The `SKILL.md` files should remain host-neutral and be used by both CLIs. The current `$mozi:*` invocation names can remain in the descriptions because they are user-facing workflow names, not Codex-only implementation details.

Host-specific assumptions should be isolated:

- Keep Codex-specific agent metadata in `agents/openai.yaml`.
- Add Claude-specific metadata only if Claude Code requires it, and keep it under Claude-recognized paths.
- Do not fork skill prose for Claude and Codex. If behavior differs, document the difference inside the shared skill as host-aware guidance.
- Keep validator paths resilient: the skills already support repo-local validators and installed-plugin bundled validators. Preserve that pattern.

### Hook Compatibility

Codex currently uses `plugins/mozi/hooks/hooks.json` as a plugin-bundled `PostToolUse` hook.

For Claude Code:

- Reuse the same Python validator wrapper scripts if Claude supports compatible hook execution from plugin roots.
- If Claude hook manifest syntax differs, add a Claude-specific hook manifest rather than changing the Codex `hooks.json`.
- If Claude plugin hooks are unavailable or not trusted, the skills' manual validation requirement remains the compatibility fallback.

The compatibility contract should be:

- Hook validation is early feedback.
- Manual validator execution is the final success gate in both hosts.
- No workflow may rely exclusively on hooks to prove success.

### Marketplace and Publishing

Use separate host marketplaces:

- Codex local marketplace: `.agents/plugins/marketplace.json`, source `./plugins/mozi`.
- Claude local marketplace: `.claude-plugin/marketplace.json`, source `./plugins/mozi`.

If Mozi later publishes to a central Codex marketplace, use a Superpowers-style sync script that copies `plugins/mozi/` into the destination marketplace while preserving destination-owned metadata. Mozi does not need that script for local dual support.

## Refactoring Plan

### Phase 1: Add Claude Packaging

1. Add `plugins/mozi/.claude-plugin/plugin.json`.
2. Add `.claude-plugin/marketplace.json` with `source: "./plugins/mozi"`.
3. Validate both new JSON files.
4. Do not move skills, templates, validators, hooks, or Codex manifest.

Acceptance:

- `python3 -m json.tool plugins/mozi/.claude-plugin/plugin.json >/dev/null`
- `python3 -m json.tool .claude-plugin/marketplace.json >/dev/null`
- Existing Codex manifest and marketplace validation still pass.

### Phase 2: Document Dual Installation

1. Update `README.md` with separate Claude Code and Codex installation sections.
2. State that Claude and Codex install separately, but both use the same `plugins/mozi/skills` workflows.
3. Document the hook fallback: if plugin hooks are unavailable or untrusted, workflows run validators manually.
4. Keep Codex install instructions and plugin notes intact.

Acceptance:

- README names both hosts.
- README includes Claude marketplace add/install commands for the repo-local marketplace.
- README still documents Codex marketplace installation and plugin hook behavior.

### Phase 3: Host-Neutral Skill Audit

Audit all four skills for Codex-only language that would confuse Claude Code:

- `plugins/mozi/skills/create-prd/SKILL.md`
- `plugins/mozi/skills/review-prd/SKILL.md`
- `plugins/mozi/skills/create-spec/SKILL.md`
- `plugins/mozi/skills/review-spec/SKILL.md`

Expected edits are small:

- Replace "Codex plugin" wording with "Mozi plugin" where the workflow is host-neutral.
- Keep `agents/openai.yaml` references out of shared prose unless needed.
- Preserve all validation requirements.
- Preserve current workflow names and output contracts.

Acceptance:

- No generated PRD/SPEC behavior changes.
- Validation commands in AGENTS.md still pass.
- No skill duplicates are introduced.

### Phase 4: Hook Compatibility Decision

Decide whether Claude Code can consume the existing hook files directly.

If yes:

- Document that the shared hook files are used by both hosts.

If no:

- Add the smallest Claude-specific hook adapter manifest.
- Reuse `post_edit_validate_prd.py` and `post_edit_validate_spec.py`.
- Keep Codex `hooks/hooks.json` unchanged.

Acceptance:

- Hook manifests only reference files that exist.
- Manual validator fallback remains documented in every workflow.
- Codex hook validation remains unchanged.

### Phase 5: Validation Script

Add a repo validation script, for example `scripts/validate-plugin-layout.sh`, to make dual-host maintenance cheap.

Checks:

```bash
python3 -m json.tool plugins/mozi/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/mozi/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool plugins/mozi/hooks/hooks.json >/dev/null
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
```

Acceptance:

- One command verifies both host manifests and all workflow assets.
- The validation script is documented in README or AGENTS.md.

### Phase 6: Installation Smoke Tests

Run real install smoke tests in both hosts when available:

Claude Code:

```text
/plugin marketplace add <repo-or-local-marketplace>
/plugin install mozi@mozi-dev
```

Codex CLI:

```text
/plugins
```

or the current local marketplace install path used by the development environment.

Workflow smoke prompts:

```text
$mozi:create-prd AddRelu
$mozi:review-prd docs/mozi/add-relu/prd.md
$mozi:create-spec docs/mozi/add-relu/prd.md
$mozi:review-spec docs/mozi/add-relu/spec.md
```

Acceptance:

- Both hosts discover all four skills.
- Both hosts can load the same skill content.
- Create/review workflows still invoke the same bundled templates, references, and validators.
- Hook absence does not block manual validation.

## Development Rules After Refactor

- Treat `plugins/mozi/skills` as the single workflow source of truth.
- Add new Mozi workflows as one shared skill plus per-host metadata only when required.
- Keep Codex and Claude manifests version-aligned.
- Keep marketplace sources pointed at `./plugins/mozi`.
- Never add manifest references to hooks, apps, MCP servers, assets, or commands unless those files exist.
- Any workflow change must update README and the validation script if files or install behavior change.
- Any new validator or template must be checked by the dual-host layout validation script.

## Risks and Mitigations

Risk: Claude Code marketplace may not accept nested plugin source paths.

Mitigation: Test `.claude-plugin/marketplace.json` with `source: "./plugins/mozi"` before changing repo layout. If unsupported, add a root-level Claude plugin wrapper only as a packaging shim, while keeping `plugins/mozi` canonical for Codex.

Risk: Claude hook format differs from Codex hooks.

Mitigation: Keep hook manifests host-specific and reuse Python wrapper scripts. Manual validation remains required and host-independent.

Risk: Skill prose drifts between hosts.

Mitigation: Do not duplicate `SKILL.md`. Add host-aware notes only inside shared skills when needed.

Risk: Future contributors update one manifest but not the other.

Mitigation: Add `scripts/validate-plugin-layout.sh` and make it part of publishing/install validation.

## Recommended First Patch

Implement Phase 1 and Phase 2 together:

1. Add Claude manifest and marketplace files.
2. Update README installation docs.
3. Run JSON validation for all manifests and marketplace files.

This produces immediate Claude installability without touching workflow behavior. Phases 3-6 can then harden the cross-host maintenance model.

## Implementation Notes

Implemented in the first compatibility refactor:

- Added `plugins/mozi/.claude-plugin/plugin.json`.
- Added `.claude-plugin/marketplace.json` with source `./plugins/mozi`.
- Kept the canonical skill source at `plugins/mozi/skills/`.
- Kept the Codex plugin source and marketplace path unchanged.
- Added `scripts/validate-plugin-layout.sh` to verify both host manifests, both marketplaces, hooks, and workflow assets.
- Updated `README.md` with separate Codex CLI and Claude Code installation instructions.
- Updated `AGENTS.md` so future agents preserve the dual-host plugin shape.

The Codex hook manifest remains Codex-specific. The shared Mozi workflows still run validators manually as the final success gate, so Claude Code installation does not lose PRD/SPEC validation behavior when host hook support differs.

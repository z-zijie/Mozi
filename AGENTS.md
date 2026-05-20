# Agent Guide

## Project Shape

This repository is a dual Codex and Claude Code plugin repository.

- Keep the Codex plugin at `plugins/mozi/`.
- Keep `plugins/mozi/.codex-plugin/plugin.json` present.
- Keep `plugins/mozi/.claude-plugin/plugin.json` present.
- Keep the repo-local marketplace entry at `.agents/plugins/marketplace.json`.
- Keep the repo-local Claude marketplace entry at `.claude-plugin/marketplace.json`.
- The plugin folder name and `plugin.json` `name` value must remain `mozi`.
- Both marketplace entries must point to `./plugins/mozi`.
- Keep manifest metadata aligned with implemented plugin components. Do not add hooks, MCP servers, apps, or asset references unless the referenced files exist.
- Treat `plugins/mozi/skills/` as the single workflow source of truth. Do not duplicate skills for Claude and Codex.
- Treat unrelated project skeleton files as incidental unless the user explicitly asks to work on them.

## Validation

Validate `plugins/mozi/.codex-plugin/plugin.json`, `plugins/mozi/.claude-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and `.claude-plugin/marketplace.json` as JSON before publishing or installing the plugin.

There is no plugin test suite yet. For the `$mozi:create-prd`, `$mozi:review-prd`, `$mozi:create-spec`, and `$mozi:review-spec` workflows, validate the manifest, template source, skill files, and validator scripts from the repository root:

```bash
scripts/validate-plugin-layout.sh
```

The PRD completeness validator is strict and intended for final PRDs:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

The `$mozi:create-prd` completeness validator is also wired into a Codex plugin-bundled `PostToolUse` hook at `plugins/mozi/hooks/`. When plugin hooks are enabled with `[features].plugin_hooks = true` and trusted through `/hooks`, PRD edits are validated automatically after edit/write tool calls. Claude Code hook support may differ. If plugin hooks are disabled, unavailable, or not trusted, run the validator manually before reporting success.

Generated PRDs must include the template's NPU ARCH and 算子原型 sections. Treat these as requirement/interface context only: NPU ARCH describes target architecture scope or dependency, and 算子原型 describes the operator prototype in PyTorch ATen IR form.

Generated PRDs must stay within PRD boundaries. They should describe requirement intent, scope, supported behavior, input/output interface, constraints, and acceptance criteria. Do not include SPEC/DESIGN/IMPLEMENT details such as kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level API design, or optimization approach.

When `$mozi:create-prd` receives an existing PRD path plus review feedback, treat it as a review-driven revision workflow. Modify the provided PRD in place, accept either `$mozi:review-prd` YAML or natural-language review comments, preserve the canonical PRD template headings, and keep changes at PRD level. Rely on the post-edit hook for completeness validation when available; otherwise run the same PRD completeness validator on the modified PRD before finishing.

When `$mozi:create-prd` runs from an installed plugin in another target repository, that repository might not have `plugins/mozi/`. In that case, use the loaded skill directory's bundled `scripts/validate_prd.py` and do not treat the missing repo-local plugin source as a workflow failure.

It fails on unresolved template placeholders, `TBD`, missing or reordered template sections, empty section bodies, and unresolved open questions.

The PRD review validator checks the YAML-only review contract:

```bash
python3 plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <absolute-prd-path>
```

It fails on Markdown fences, malformed constrained YAML, missing keys, invalid score ranges, total-score mismatches, rating mismatches, invalid SPEC entry decisions, and score-based hard-gate violations.

The SPEC review validator checks the YAML-only SPEC quality review contract:

```bash
python3 plugins/mozi/skills/review-spec/scripts/validate_review_yaml.py <review-yaml-file> --spec-path <absolute-spec-path>
```

It fails on Markdown fences, malformed constrained YAML, missing keys, invalid score ranges, total-score mismatches, grade mismatches, invalid dimension statuses, invalid error result shapes, and dimension order drift.

The SPEC completeness validator is strict and intended for final SPECs:

```bash
python3 plugins/mozi/skills/create-spec/scripts/validate_spec.py docs/mozi/<op-name-kebab-case>/spec.md --operator <OP_NAME>
```

The `$mozi:create-spec` workflow has two modes. With one readable PRD path, it creates or overwrites the sibling SPEC at `docs/mozi/<op-name-kebab-case>/spec.md`. With a readable PRD path, readable SPEC path, and review feedback, it revises that SPEC in place.

Generated SPECs must stay within SPEC boundaries: operator contract, interface, input/output and attribute specifications, mathematical/functional/numeric/shape semantics, dtype/layout constraints, boundary cases, error handling, compatibility, performance requirements, and acceptance criteria. The Operator Interface / 算子接口 section must include PyTorch ATen IR, a Pure Python `def` function signature with docstring, and a framework-independent Pure C++ function signature with Doxygen documentation. The interface definitions document every Python/C++ signature parameter directly. The Mathematical Semantics / 数学语义 section must describe the operator as a rigorous pure mathematical definition using professional mathematical language and LaTeX formulas. The Functional Semantics / 功能语义 section must include NumPy and Pure C++17 Reference Functions as executable behavioral references; the NumPy reference signature must strictly match the Pure Python Signature, and the Pure C++17 reference signature must strictly match the Pure C++ Signature after whitespace and declaration-vs-definition normalization. The Shape Semantics / Shape 语义 section must keep its canonical heading, add no subsection heading, and directly include NumPy InferShape code whose function name and parameter list match the Pure Python Signature; that InferShape function must include a complete docstring documenting purpose, every parameter, return shape contract, unsupported/error cases, and shape-rule notes. The Data Type Support / 数据类型支持 section must include a table-driven InferDtype Python function whose function name and parameter list match the Pure Python Signature; that InferDtype function must include a complete docstring documenting purpose, every parameter, return dtype contract, unsupported/error cases, and promotion-rule notes. The Acceptance Criteria / 验收标准 section must include `### Numerical Analysis / 数值分析`, `### Precision Standards / 精度标准`, and `### NumPy Compare Function / NumPy 精度比对函数`; Numerical Analysis must include the six required H4 subsections for floating-point error analysis, stability, conditioning, reduction error analysis, mixed precision analysis, and error budget, with every subsection ending in an explicit conclusion; precision standards must be a single YAML fenced block with top-level `scenarios` and per-output `name`, `dtype`, numeric `atol`, numeric `rtol`, and `rationale`; and the compare function must use signature `def compare(actual_outputs, expected_outputs) -> Tuple[bool]:`. Do not include DESIGN/IMPLEMENT details such as kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level runtime API design, or optimization approach.

The `$mozi:create-spec` completeness validator is wired into the Codex plugin-bundled `PostToolUse` hook at `plugins/mozi/hooks/`. When plugin hooks are enabled and trusted, SPEC edits are validated automatically after edit/write tool calls. Claude Code hook support may differ. If plugin hooks are disabled, unavailable, or not trusted, run the validator manually before reporting success.

It fails on unresolved template placeholders, `TBD`, missing or reordered template sections, empty section bodies, missing Operator Interface subsections, missing ATen/Python/C++ signature code blocks, framework-dependent C++ namespace types, missing Python docstring or C++ Doxygen parameter documentation, missing or mismatched Functional Semantics NumPy and Pure C++17 Reference Functions, missing or mismatched Shape Semantics NumPy InferShape code and docstring documentation, missing or mismatched Data Type Support table-driven InferDtype code and docstring documentation, missing Acceptance Criteria subsections, missing/empty/code-only Numerical Analysis H4 subsections, Numerical Analysis H4 subsections without explicit conclusions, Markdown-table precision standards, malformed precision YAML, missing output tolerances, invalid compare signatures such as `acutal_outputs`, and unresolved open issues.

## Editing Guidelines

- Prefer small, scoped changes that preserve the plugin layout.
- Preserve the Codex and Claude marketplace entries unless explicitly asked to remove them.
- If the Codex marketplace entry is updated, use source path `./plugins/mozi` and include `policy.installation`, `policy.authentication`, and `category`.
- If the Claude marketplace entry is updated, use source path `./plugins/mozi` and keep manifest metadata version-aligned with the Codex manifest.

## Documentation

Update `README.md` whenever the supported workflow changes. Update this file whenever future agents need new repo-specific instructions.

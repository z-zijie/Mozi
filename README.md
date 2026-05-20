# Mozi

Mozi is an agent CLI plugin for an end-to-end NPU operator development harness. It is packaged from one shared plugin source at `plugins/mozi/` for both Codex and Claude Code, following the same single-source packaging model used by Superpowers.

## Supported Workflows

Invoke `$mozi:create-prd` with a brief operator request to generate a normalized PRD at `docs/mozi/<op-name-kebab-case>/prd.md`. For example, an AddRelu request writes `docs/mozi/add-relu/prd.md` with the title `# AddRelu PRD`. If the target PRD already exists, the workflow asks for confirmation unless the user explicitly requested overwrite or regeneration.

The workflow uses `plugins/mozi/skills/create-prd/template/PRD.md.templ` as the canonical PRD structure. It fills requirement-level sections from the brief prompt, requires NPU ARCH and operator prototype sections as scope/interface context, and asks for clarification before finalizing when required facts are missing. Operator prototypes are written in PyTorch ATen IR form. Generated PRDs describe intent, scope, behavior, constraints, and acceptance criteria; SPEC/DESIGN/IMPLEMENT details such as kernel strategy, tiling, memory planning, or optimization approach are out of scope.

`$mozi:create-prd` also supports revising an existing PRD from review feedback. When the input includes one readable PRD path plus inline review content or a readable review file path, the workflow updates that PRD in place instead of generating a new one. Review input may be `$mozi:review-prd` YAML or natural-language comments. Structured YAML fields such as `blocking_issues`, `key_issues`, `improvement_suggestions`, `score_breakdown`, `spec_entry_decision`, and `review_notes` are preferred when present.

Example revision prompts:

```text
$mozi:create-prd docs/mozi/add-relu/prd.md using this review: <paste review YAML or comments>

$mozi:create-prd /abs/path/docs/mozi/add-relu/prd.md using review /abs/path/review.yaml
```

Revision mode preserves the canonical PRD headings, keeps valid existing requirement content, applies only PRD-level changes, and does not invent missing product facts. If review feedback requires information that was not provided, the workflow asks for clarification before finalizing the PRD.

When plugin hooks are enabled with `[features].plugin_hooks = true` and the Mozi hook is trusted through `/hooks`, `$mozi:create-prd` PRD edits may be checked automatically by the bundled post-edit hook. Hook output is early failure feedback. The workflow still runs the strict completeness validator manually before reporting success:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

When `$mozi:create-prd` runs from an installed plugin in a target repository that does not contain the Mozi source tree, the workflow uses the bundled validator from the active skill directory instead of requiring `plugins/mozi/` in that target repository.

The validator requires the rendered or revised PRD to keep the template headings, include the NPU ARCH and operator prototype sections, contain no unresolved placeholders, contain no `TBD`, and explicitly state that there are no open questions.

Invoke `$mozi:review-prd <prd-path>` to review an existing operator PRD before the SPEC stage. The workflow extracts exactly one absolute or repo-root-relative PRD path from the request, resolves readable relative paths to absolute paths, scores the document with a 100-point rubric, applies hard SPEC-entry gates, and outputs YAML only for CI or agent workflows.

Review output includes the total score, rating, per-dimension scores, strengths, issues, blocking issues, improvement suggestions, and a SPEC entry decision. The bundled validator checks the YAML contract:

```bash
python3 plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <resolved-absolute-prd-path>
```

Invoke `$mozi:review-spec <spec-path>` to review an existing NPU operator SPEC. The workflow reads exactly one absolute or repo-root-relative SPEC path, resolves readable relative paths to absolute paths, scores the document with a fixed 100-point engineering-quality rubric, and outputs YAML only for CI or agent workflows.

The SPEC review focuses on whether the SPEC is precise enough to drive DESIGN, IMPLEMENT, and TEST work. It scores scope clarity, mandatory operator interface forms, dtype rules including table-driven InferDtype, shape rules including NumPy InferShape, mathematical and numerical semantics, boundary cases, error handling, layout and memory rules, platform constraints, implementability, and testability. Missing or shallow coverage of the six required numerical-analysis dimensions caps semantic precision and can reduce testability. PRD background, business goals, and roadmap content are not primary scoring inputs.

If the input path is missing, ambiguous, nonexistent, not a file, or unreadable, the workflow returns a YAML error report instead of asking for the path again. The bundled validator checks the YAML contract and rejects normal review results for invalid paths:

```bash
python3 plugins/mozi/skills/review-spec/scripts/validate_review_yaml.py <review-yaml-file> --spec-path <resolved-absolute-spec-path>
```

Invoke `$mozi:create-spec <prd-path>` to generate a behavioral operator SPEC from a readable Mozi PRD. The workflow reads the PRD as the source of truth and creates the sibling file at `docs/mozi/<op-name-kebab-case>/spec.md`. If the target SPEC already exists, the workflow asks for confirmation unless the user explicitly requested overwrite or regeneration.

The SPEC stage expands PRD requirements into an operator contract suitable for DESIGN and implementation work. It covers overview, scope, supported NPU platforms, operator interface, input/output and attribute specifications, mathematical/functional/numeric/shape semantics, dtype support, layout and format constraints, boundary cases, error handling, compatibility, performance requirements, acceptance criteria, and open issues. The operator interface section includes PyTorch ATen IR, a Pure Python `def` function signature with docstring, and a framework-independent Pure C++ function signature with Doxygen documentation. The interface definitions document every Python/C++ signature parameter directly. The mathematical semantics section defines the operator as a pure mathematical mapping using rigorous language and LaTeX formulas. The functional semantics section includes NumPy and Pure C++17 Reference Functions as executable behavioral references; their signatures must strictly match the corresponding Pure Python and Pure C++ operator interface signatures after whitespace and declaration-vs-definition normalization. The shape semantics section includes a NumPy InferShape reference function, and the dtype support section includes a table-driven InferDtype reference function; both functions use the same name and parameters as the Pure Python signature. Acceptance criteria include required numerical analysis prose with six H4 subsections for floating-point error analysis, stability, conditioning, reduction error analysis, mixed precision analysis, and error budget. Each subsection ends with an explicit conclusion. Acceptance criteria also include YAML precision standards with scenario-to-output tolerance entries and a NumPy compare function with signature `def compare(actual_outputs, expected_outputs) -> Tuple[bool]:`. It does not include kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level runtime API design, or optimization approach.

`$mozi:create-spec` also supports revising an existing SPEC from review feedback. When the input includes one readable PRD path, one readable SPEC path, and inline review content or a readable review file path, the workflow updates that SPEC in place instead of generating a new path. The PRD remains the requirement source of truth, and review feedback is applied only at the SPEC level.

Example SPEC prompts:

```text
$mozi:create-spec docs/mozi/add-relu/prd.md

$mozi:create-spec /abs/path/docs/mozi/add-relu/prd.md /abs/path/docs/mozi/add-relu/spec.md using review /abs/path/spec-review.yaml
```

When plugin hooks are enabled and trusted, `$mozi:create-spec` SPEC edits may be checked automatically by the bundled post-edit hook. Hook output is early failure feedback. The workflow still runs the strict SPEC completeness validator manually before reporting success:

```bash
python3 plugins/mozi/skills/create-spec/scripts/validate_spec.py docs/mozi/<op-name-kebab-case>/spec.md --operator <OP_NAME>
```

The SPEC validator requires the rendered or revised SPEC to keep the template headings, include the required Operator Interface subsections and ATen/Python/C++ signature code blocks, use framework-independent Pure C++ signature types, document every Python/C++ signature parameter inside the Python docstring and C++ Doxygen comment, include Functional Semantics content with NumPy and Pure C++17 Reference Functions whose signatures match the corresponding operator interface signatures and whose bodies return computed reference outputs, include direct Shape Semantics content with a NumPy InferShape code block whose function name and parameters match the Pure Python Signature and whose docstring documents every parameter and return shape contract, include Data Type Support content with a table-driven InferDtype code block whose function name and parameters match the Pure Python Signature and whose docstring documents every parameter and return dtype contract, include Acceptance Criteria subsections for numerical analysis, YAML precision standards, and a NumPy compare function, contain no unresolved placeholders, contain no `TBD`, and explicitly state that there are no open issues. The numerical analysis subsection must include all six required H4 subsections, and each must end with an explicit conclusion sentence. The validator rejects Markdown tables in precision standards, malformed precision YAML, missing output `atol`/`rtol` values, and invalid compare signatures such as `acutal_outputs`.

## Installation

Install Mozi separately in each agent CLI you use. Both installations load the same shared workflows from `plugins/mozi/skills/`.

### Codex CLI

Install the Mozi Codex plugin marketplace:

```bash
codex plugin marketplace add z-zijie/Mozi
```

For local development, the repo-local Codex marketplace is `.agents/plugins/marketplace.json`, and its `mozi` entry points to `./plugins/mozi`.

### Claude Code

Register this repository as a Claude Code plugin marketplace, then install `mozi` from it:

```text
/plugin marketplace add z-zijie/Mozi
/plugin install mozi@mozi-dev
```

For local development, the Claude marketplace is `.claude-plugin/marketplace.json`, and its `mozi` entry points to `./plugins/mozi`.

## Plugin Notes

The plugin name is `mozi`, and the canonical plugin folder is `plugins/mozi/`. Codex uses `plugins/mozi/.codex-plugin/plugin.json`; Claude Code uses `plugins/mozi/.claude-plugin/plugin.json`.

The Codex marketplace name is `mozi-marketplace`. The Claude Code development marketplace name is `mozi-dev`. Both plugin entries use the repo-local source path `./plugins/mozi`.

The plugin bundles Codex lifecycle hooks at `plugins/mozi/hooks/hooks.json`. Plugin-bundled hooks are opt-in in this Codex release, so users must enable `plugin_hooks` and trust the non-managed hook before it runs. Claude Code hook support may differ by release; the Mozi workflows do not rely on hooks as the final success signal. They run the bundled validators manually before reporting success.

Validate the dual-host plugin layout from the repository root:

```bash
scripts/validate-plugin-layout.sh
```

# Mozi

Mozi is a Codex plugin for an end-to-end NPU operator development harness.

## Supported Workflows

Invoke `$mozi:create-prd` with a brief operator request to generate a normalized PRD at `docs/mozi/<op-name-kebab-case>/prd.md`. For example, an AddRelu request writes `docs/mozi/add-relu/prd.md` with the title `# AddRelu PRD`.

The workflow uses `plugins/mozi/skills/create-prd/template/PRD.md.templ` as the canonical PRD structure. It fills requirement-level sections from the brief prompt, requires NPU ARCH and operator prototype sections as scope/interface context, marks missing details as `TBD`, and tracks unresolved decisions in the open questions section. Operator prototypes are written in PyTorch ATen IR form. Generated PRDs describe intent, scope, behavior, constraints, and acceptance criteria; SPEC/DESIGN/IMPLEMENT details such as kernel strategy, tiling, memory planning, or optimization approach are out of scope.

`$mozi:create-prd` also supports revising an existing PRD from review feedback. When the input includes one readable PRD path plus inline review content or a readable review file path, the workflow updates that PRD in place instead of generating a new one. Review input may be `$mozi:review-prd` YAML or natural-language comments. Structured YAML fields such as `blocking_issues`, `key_issues`, `improvement_suggestions`, `score_breakdown`, `spec_entry_decision`, and `review_notes` are preferred when present.

Example revision prompts:

```text
$mozi:create-prd docs/mozi/add-relu/prd.md using this review: <paste review YAML or comments>

$mozi:create-prd /abs/path/docs/mozi/add-relu/prd.md using review /abs/path/review.yaml
```

Revision mode preserves the canonical PRD headings, keeps valid existing requirement content, applies only PRD-level changes, and does not invent missing product facts. If review feedback requires information that was not provided, the workflow keeps or adds the item under `Open Questions / 待澄清问题`; the strict completeness validator will report the PRD as incomplete until that information is resolved.

When plugin hooks are enabled with `[features].plugin_hooks = true` and the Mozi hook is trusted through `/hooks`, `$mozi:create-prd` PRD edits are checked automatically by the bundled post-edit hook. The hook runs the strict completeness validator after edit/write tool calls and feeds validation failures back into the agent turn.

If plugin hooks are disabled, unavailable, or not trusted, final PRDs can be checked manually with the strict completeness validator:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

When `$mozi:create-prd` runs from an installed plugin in a target repository that does not contain the Mozi source tree, the workflow uses the bundled validator from the active skill directory instead of requiring `plugins/mozi/` in that target repository.

The validator requires the rendered or revised PRD to keep the template headings, include the NPU ARCH and operator prototype sections, contain no unresolved placeholders, contain no `TBD`, and explicitly state that there are no open questions.

Invoke `$mozi:review-prd <absolute-prd-path>` to review an existing operator PRD before the SPEC stage. The workflow reads exactly one absolute PRD path, scores the document with a 100-point rubric, applies hard SPEC-entry gates, and outputs YAML only for CI or agent workflows.

Review output includes the total score, rating, per-dimension scores, strengths, issues, blocking issues, improvement suggestions, and a SPEC entry decision. The bundled validator checks the YAML contract:

```bash
python3 plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <absolute-prd-path>
```

Invoke `$mozi:create-spec <prd-path>` to generate a behavioral operator SPEC from a readable Mozi PRD. The workflow reads the PRD as the source of truth and creates or overwrites the sibling file at `docs/mozi/<op-name-kebab-case>/spec.md`.

The SPEC stage expands PRD requirements into an operator contract suitable for DESIGN and implementation work. It covers overview, scope, supported NPU platforms, operator interface, input/output and attribute specifications, mathematical/functional/numeric/shape semantics, dtype support, layout and format constraints, boundary cases, error handling, compatibility, performance requirements, acceptance criteria, and open issues. The mathematical semantics section defines the operator as a pure mathematical mapping using rigorous language and LaTeX formulas. It does not include kernel design, tiling strategy, memory planning, hardware instruction choice, scheduling, code structure, low-level runtime API design, or optimization approach.

`$mozi:create-spec` also supports revising an existing SPEC from review feedback. When the input includes one readable PRD path, one readable SPEC path, and inline review content or a readable review file path, the workflow updates that SPEC in place instead of generating a new path. The PRD remains the requirement source of truth, and review feedback is applied only at the SPEC level.

Example SPEC prompts:

```text
$mozi:create-spec docs/mozi/add-relu/prd.md

$mozi:create-spec /abs/path/docs/mozi/add-relu/prd.md /abs/path/docs/mozi/add-relu/spec.md using review /abs/path/spec-review.yaml
```

When plugin hooks are enabled and trusted, `$mozi:create-spec` SPEC edits are checked automatically by the bundled post-edit hook. The hook runs the strict SPEC completeness validator after edit/write tool calls and feeds validation failures back into the agent turn.

If plugin hooks are disabled, unavailable, or not trusted, final SPECs can be checked manually with the strict completeness validator:

```bash
python3 plugins/mozi/skills/create-spec/scripts/validate_spec.py docs/mozi/<op-name-kebab-case>/spec.md --operator <OP_NAME>
```

The SPEC validator requires the rendered or revised SPEC to keep the template headings, include PyTorch ATen IR operator interface content, contain no unresolved placeholders, contain no `TBD`, and explicitly state that there are no open issues.

## Installation

Install the Mozi Codex plugin marketplace:

```bash
codex plugin marketplace add z-zijie/Mozi
```

## Plugin Notes

The plugin name is `mozi`, and the outer folder name matches the manifest `name` field as required by the Codex plugin format.

The marketplace name is `mozi-marketplace`, and its plugin entry uses the repo-local source path `./plugins/mozi`.

The plugin bundles lifecycle hooks at `plugins/mozi/hooks/hooks.json`. Plugin-bundled hooks are opt-in in this Codex release, so users must enable `plugin_hooks` and trust the non-managed hook before it runs.

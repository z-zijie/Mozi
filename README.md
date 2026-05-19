# Mozi

Mozi is a Codex plugin for an end-to-end NPU operator development harness.

## Supported Workflows

Invoke `$mozi:create-prd` with a brief operator request to generate a normalized PRD at `docs/mozi/<op-name-kebab-case>/prd.md`. For example, an AddRelu request writes `docs/mozi/add-relu/prd.md` with the title `# AddRelu PRD`.

The workflow uses `plugins/mozi/skills/create-prd/template/PRD.md.templ` as the canonical PRD structure. It fills requirement-level sections from the brief prompt, requires NPU ARCH and operator prototype sections as scope/interface context, marks missing details as `TBD`, and tracks unresolved decisions in the open questions section. Operator prototypes are written in PyTorch ATen IR form. Generated PRDs describe intent, scope, behavior, constraints, and acceptance criteria; SPEC/DESIGN/IMPLEMENT details such as kernel strategy, tiling, memory planning, or optimization approach are out of scope.

Final PRDs can be checked with the strict completeness validator:

```bash
python3 plugins/mozi/skills/create-prd/scripts/validate_prd.py docs/mozi/<op-name-kebab-case>/prd.md --operator <OP_NAME>
```

When `$mozi:create-prd` runs from an installed plugin in a target repository that does not contain the Mozi source tree, the workflow uses the bundled validator from the active skill directory instead of requiring `plugins/mozi/` in that target repository.

The validator requires the rendered PRD to keep the template headings, include the NPU ARCH and operator prototype sections, contain no unresolved placeholders, contain no `TBD`, and explicitly state that there are no open questions.

Invoke `$mozi:review-prd <absolute-prd-path>` to review an existing operator PRD before the SPEC stage. The workflow reads exactly one absolute PRD path, scores the document with a 100-point rubric, applies hard SPEC-entry gates, and outputs YAML only for CI or agent workflows.

Review output includes the total score, rating, per-dimension scores, strengths, issues, blocking issues, improvement suggestions, and a SPEC entry decision. The bundled validator checks the YAML contract:

```bash
python3 plugins/mozi/skills/review-prd/scripts/validate_review_yaml.py <review-yaml-file> --prd-path <absolute-prd-path>
```

## Installation

Install the Mozi Codex plugin marketplace:

```bash
codex plugin marketplace add z-zijie/Mozi
```

## Plugin Notes

The plugin name is `mozi`, and the outer folder name matches the manifest `name` field as required by the Codex plugin format.

The marketplace name is `mozi-marketplace`, and its plugin entry uses the repo-local source path `./plugins/mozi`.

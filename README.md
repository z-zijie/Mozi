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

Final PRDs can be checked with the strict completeness validator:

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

## Installation

Install the Mozi Codex plugin marketplace:

```bash
codex plugin marketplace add z-zijie/Mozi
```

## Plugin Notes

The plugin name is `mozi`, and the outer folder name matches the manifest `name` field as required by the Codex plugin format.

The marketplace name is `mozi-marketplace`, and its plugin entry uses the repo-local source path `./plugins/mozi`.

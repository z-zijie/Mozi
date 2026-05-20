---
name: using-mozi
description: Introduction to Mozi NPU operator workflows and when to invoke the PRD, SPEC, and review skills.
---

# Using Mozi

Mozi provides four NPU operator workflow skills:

- `mozi:create-prd` creates or revises normalized operator PRDs.
- `mozi:review-prd` reviews PRDs for SPEC readiness and outputs YAML only.
- `mozi:create-spec` creates or revises behavioral operator SPECs from PRDs.
- `mozi:review-spec` reviews SPEC quality and outputs YAML only.

Use the matching skill whenever the user asks for one of these workflows, names a `$mozi:*` command, or asks to create/review NPU operator PRD or SPEC artifacts.

Keep PRD work at requirements level. Keep SPEC work at behavioral contract level. Do not add design, implementation, scheduling, tiling, kernel, memory-planning, or hardware-instruction details unless the active Mozi skill explicitly requires them.

Before reporting completion for generated or revised PRDs and SPECs, run the bundled validator named by the active skill. Hook validation is early feedback only; manual validation is the final success gate.

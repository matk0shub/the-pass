---
name: "the-pass:research"
description: "Convert studies, books, investor notes, vendor docs, or strategy-review pages into structured source notes and falsifiable trading hypotheses."
---

# The Pass Research

Use this skill when the user asks to study a topic, review sources, or turn research into
strategy hypotheses.

## Rules

- Treat sources as claims, not truth.
- Tag OxfordStrat and similar pages as `strategy-review`, not academic proof.
- Every source note must include claim, evidence, limitations, market applicability,
  required tests, and failure modes.
- Do not recommend promotion from reading alone.

## Output

- Source notes based on `templates/source_note.yaml`.
- Hypotheses that can become `StrategySpec` files.
- Missing evidence and required tests.

---
name: "the-pass:spec"
description: "Turn a trading idea into a StrategySpec with edge thesis, data needs, execution assumptions, risks, done_when, and kill_when."
---

# The Pass Spec

Use this skill when converting an idea, source claim, or existing strategy into a formal
`StrategySpec`.

## Rules

- Classify by edge mechanism, not indicator name.
- Include null/random baselines and kill criteria.
- Require data, cost, fill, latency, and risk assumptions.
- If the idea cannot state a falsifiable edge thesis, keep it in research.

## Output

- A `StrategySpec` based on `templates/strategy_spec.yaml`.
- Open assumptions and blocked fields.
- Gate requirements for research, paper, and live approval.

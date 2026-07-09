---
name: "the-pass:backtest"
description: "Design or run a reproducible backtest package with manifest, receipt, metrics, cost waterfall, and verdict artifacts."
---

# The Pass Backtest

Use this skill for full reproducible strategy tests.

## Rules

- Every backtest needs a data manifest and run receipt.
- Promotion tests must use pessimistic fills and explicit costs.
- Record event time, receive time, decision time, and simulated execution timing when
  available.
- If data, cost, or fill assumptions are incomplete, mark the verdict `blocked`.

## Output

- Data manifest.
- Run receipt.
- Metrics report.
- Cost waterfall.
- Verdict report.

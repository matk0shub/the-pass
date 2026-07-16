# The Pass v0.15.0

Version 0.15.0 strengthens the scientific backtest engine and makes long-running replay practical
without weakening the evidence or live-trading boundaries.

## Highlights

- `robustness_report.v3` executes every variant on train and test data, selects each fold only from
  train evidence, and stores stitched untouched OOS returns for validator-side statistics.
- Execution config v2 adds enforceable latency, participation limits, event-level fees, explicit
  market impact, and multiplier-aware futures, funding, borrow, roll, and settlement accounting.
- Custom strategy workers stream canonical JSONL instead of receiving inline event arrays.
- Checkpoint-capable paper strategies process only new immutable batches and periodically prove
  parity against a clean cumulative replay.
- The public V3 audit fixture was regenerated through the production robustness workflow and is
  correctly blocked from promotion because it uses synthetic trusted-local evidence.

## Compatibility

- CLI command names, JSON envelopes, exit codes, ledgers, gates, and StrategySpec identities remain
  compatible.
- Robustness v2, execution config v1, and worker request v1 remain readable for historical replay.
- New paper candidates require robustness v3 and execution v2 evidence.
- Strategies without checkpoint methods continue in `cumulative_compatibility` paper mode.
- Live execution remains technically locked; no order transport or credential loader was added.

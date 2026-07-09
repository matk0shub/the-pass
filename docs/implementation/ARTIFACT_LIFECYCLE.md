# Artifact Lifecycle

The Pass is artifact-first. A strategy only moves forward when the required files exist,
validate, and support the gate claim.

## Lifecycle

```text
source -> source_note -> StrategySpec -> screen -> backtest package
       -> taste -> refire/simmer -> paper -> plate -> receipts
```

## Artifact Ownership

| Stage | Primary Artifact | Created By | Mutable? | Promotion Use |
| --- | --- | --- | --- | --- |
| Source review | `source_note` | `research` | yes until reviewed | Required for source-backed claims |
| Strategy definition | `StrategySpec` | `spec` | yes before first run | Required for all runs |
| Data evidence | `data_manifest` | `backtest` or adapter | no after run | Required for every run |
| Run evidence | `run_receipt` | runner or skill | no after run | Required for every run |
| Performance evidence | `metrics_report` | runner or skill | no after run | Required for verdict |
| Cost evidence | `cost_waterfall` | runner or skill | no after run | Required for verdict |
| Decision | `verdict_report` | `taste` or gate skill | append/supersede | Required for gate |
| Ledger | receipt index | `receipts` | append-only | Required for audit |

## Package Layout

Recommended run package:

```text
experiments/runs/<strategy-id>/<run-id>/
  source_notes/
  strategy_spec.yaml
  data_manifest.yaml
  run_receipt.yaml
  metrics_report.yaml
  cost_waterfall.yaml
  verdict_report.yaml
  logs/
```

Generated outputs should not overwrite prior run packages. A rerun creates a new `run-id`
and may link to the previous package in its receipt.

## Immutability Rules

- Raw data is immutable.
- Normalized data is derived and must reference raw fingerprints.
- Run receipts are append-only.
- Metrics and cost reports are immutable after the verdict is recorded.
- A revised StrategySpec must create a new version before rerun.
- A corrected artifact supersedes the old artifact; it does not silently replace it.

## Gate Inputs

Research gate requires:

- Reviewed source notes or explicit synthetic/example marker.
- Complete StrategySpec.
- Data manifest.
- Run receipt.
- Metrics report.
- Cost waterfall.
- Verdict report.

Paper gate additionally requires:

- Paper plan.
- Observation manifest.
- Paper-vs-backtest divergence policy.
- Risk review checklist.

Live approval pack additionally requires:

- Explicit human approval.
- Exact config hash.
- Adapter and venue.
- Credential boundary.
- Dry-run proof.
- Rollback plan.
- Incident runbook.

## Verdict States

- `kill`: stop this hypothesis.
- `revise`: fix spec, data, cost, or execution assumptions and rerun.
- `paper_candidate`: evidence is strong enough for paper/replay only.
- `blocked`: missing evidence or unresolved safety issue.

No verdict can approve live trading.

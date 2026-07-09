# Synthetic Breakout Example

This is the first public-safe golden path for The Pass.

It is not a profitable strategy claim. It is a synthetic workflow fixture used to prove that
The Pass can move from source note to StrategySpec to run package to verdict without
secrets, paid data, live APIs, or real order paths.

## Purpose

- Exercise the artifact lifecycle.
- Exercise schema validation.
- Exercise `taste` blocking/passing logic.
- Provide a stable CI fixture.

## Package

The package in `package/` contains JSON artifacts that mirror the core schemas:

- `adapter.json`
- `source_note.json`
- `strategy_spec.json`
- `data_manifest.json`
- `run_receipt.json`
- `metrics_report.json`
- `cost_waterfall.json`
- `verdict_report.json`

## Expected Verdict

`blocked`.

The example is intentionally diagnostic-only. It can demonstrate the workflow, but it must
not promote to paper because it uses synthetic data and a fixture-only adapter.

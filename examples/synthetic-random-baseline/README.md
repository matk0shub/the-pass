# Synthetic Random Baseline Example

This package is the intentionally bad baseline for The Pass.

It is not a strategy claim. It proves that the workflow can validate a complete artifact
package and still kill a candidate when the thesis is random, net metrics are weak, and
the evidence cannot justify promotion.

## Purpose

- Exercise the `kill` verdict path.
- Keep a negative control beside the synthetic breakout fixture.
- Prove that CI checks more than artifact presence.

## Package

The package in `package/` contains the same core artifacts as the golden path fixture:

- `adapter.json`
- `source_note.json`
- `strategy_spec.json`
- `data_manifest.json`
- `run_receipt.json`
- `metrics_report.json`
- `cost_waterfall.json`
- `verdict_report.json`

## Expected Verdict

`kill`.

The candidate is a deterministic random-signal fixture with no edge thesis. It should stay
dead unless this example is intentionally redesigned.

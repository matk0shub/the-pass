# Scientific Engine Upgrade v0.15

Status: implemented and locally verified on 2026-07-16.

## Objective

Version 0.15 upgrades The Pass from an evidence-trustworthy framework to a scientifically stronger
and operationally scalable strategy-testing engine. The release closes three gaps:

1. walk-forward reports currently record train windows but execute and score variants only on test
   slices;
2. execution uses simplified latency, fee, queue, and lifecycle assumptions;
3. custom replay and paper observation repeatedly materialize and replay the complete event history.

The public live boundary remains locked. No order transport, credential loader, or authenticated
trading client will be added.

## W1: Train-Select-Test Walk-Forward

### Artifact contract

- Add `robustness_report.v3`.
- Keep v2 readable as historical evidence, but new `paper_candidate` packages require v3.
- Register the selection metric and deterministic tie-break before execution.
- Store every train and test cell, including failures.
- Every cell records aggregate net return, periodic equity returns, runtime eligibility, execution
  fingerprint, and result fingerprint.
- Each fold selects its variant only from train-cell evidence.
- The selected variant is then evaluated on the corresponding untouched test cell.
- The report stores stitched selected OOS returns and aligned OOS returns for every variant.

### Statistics

- PBO and Reality Check/SPA use the aligned OOS return matrix, not one aggregate value per fold.
- PSR and DSR use stitched selected OOS periodic returns.
- Effective sample size is reduced for lag-1 autocorrelation and is recorded in the report.
- DSR trial Sharpe values come from complete OOS periodic returns for all registered variants.
- Null comparison uses the preregistered null variant on the same OOS observations.
- Parameter stability is evaluated from OOS neighboring variants for every selected configuration.

### Promotion rules

Promotion requires:

- at least four complete purged walk-forward folds;
- deterministic train-only selection for every fold;
- at least 30 effective selected OOS observations;
- complete runtime-promotional train and test cells;
- selected OOS mean above the aligned null mean;
- positive neighboring OOS stability;
- all mandatory stress scenarios passing;
- finite recomputed PBO, PSR, DSR, and Reality Check/SPA values.

### Regression gates

- Changing any train score must either change the selected variant or invalidate the report.
- Changing an OOS return must invalidate all affected statistics.
- Selecting from test evidence must be impossible.
- A profitable train winner with negative OOS performance must be blocked.
- Existing v2 evidence remains readable but cannot create a new paper candidate.

## W2: Execution And Lifecycle v2

### Execution config

Add execution config schema version 2 with:

- `minimum_latency_ns`;
- `participation_rate`;
- `impact_bps`;
- existing fee, slippage, queue, and adverse-selection fields.

Version 1 remains replayable. New v3 promotion evidence requires execution v2.

### Fill and cost behavior

- A fill may use only evidence received at or after `decision_time + minimum_latency_ns`.
- Market fills walk depth but consume no more than the configured participation rate.
- Limit fills apply queue and adverse-selection haircuts after participation limits.
- Event-level `fee_rate` overrides the static fallback when present and valid.
- Market impact is explicit and recorded separately from spread and configured bar slippage.
- Every fill records the evidence event and effective latency.

### Instrument lifecycle

- Instrument-definition events register `instrument_type` and positive contract multiplier.
- Spot and prediction positions use cash inventory accounting.
- Futures positions use multiplier-aware cash-settled PnL accounting.
- Funding events apply signed long/short funding cashflows from the current marked notional.
- Settlement events close the full position at the recorded settlement price.
- Borrow and roll costs may be applied from explicit canonical event payloads.
- Missing instrument metadata blocks promotion for derivative lifecycle events.

### Regression gates

- Same-event and pre-latency fills are impossible.
- Participation limits cap fills deterministically.
- Dynamic fee evidence reconciles with the cost waterfall.
- Long and short funding cashflows have opposite signs.
- Futures multiplier PnL and settlement accounting conserve equity.
- Prediction settlement closes inventory at 0 or 1 without synthetic profit creation.

## W3: Streaming Replay And Paper Checkpoints

### Event transport

- Add worker request v2 using a canonical JSONL event file plus count and fingerprint.
- CLI backtest, robustness, reproduction, and paper paths pass event files instead of embedding all
  events in a JSON request.
- The worker validates event order, count, and fingerprint while reading.
- Keep request v1 readable for compatibility tests.

### Simulator streaming

- Add ordered streaming replay without sorting or duplicating the complete event list.
- Execution v2 supports deterministic equity sampling through `equity_sampling_interval`.
- The final equity snapshot is always retained.
- Full-resolution equity is required for robustness v3 statistical cells.

### Incremental paper state

- Add a JSON-only strategy checkpoint protocol: `export_state()` and `import_state(state)`.
- Add simulator checkpoints containing strategy state, portfolio state, pending intents, intent
  identifiers, cost totals, counters, and the last event key.
- Paper observation processes only the new immutable batch when the strategy supports checkpoints.
- The cumulative event hash chain and checkpoint fingerprint bind every batch.
- A configurable full replay audit periodically compares incremental and clean cumulative results.
- Strategies without checkpoint support remain on deterministic cumulative replay and are marked
  `scaling_mode: cumulative_compatibility`.

### Performance gates

- File transport must produce the same semantic result as inline compatibility transport.
- A 100k-event custom replay must not embed events in the worker request.
- Incremental paper results must equal a clean cumulative replay at audit checkpoints.
- Peak Python memory for file transport must not grow by duplicating the entire serialized event
  payload in the parent process.

## Public API And Migration

- Release version: `0.15.0`.
- New schema: `robustness_report.v3`.
- New runtime request: `strategy-worker-request/v2`.
- New execution config: schema version 2.
- Existing StrategySpec, ledger, gate decision, and package identities remain compatible.
- Candidate assembly requires v3 for new paper candidates.
- CLI command names remain stable; new execution and robustness fields are additive.
- JSON output envelopes and exit codes remain unchanged.

## Test Matrix

- Unit: walk-forward selection, effective sample size, execution latency, impact, lifecycle,
  checkpoints, and file transport.
- Property: train/test separation, deterministic tie-breaking, funding sign, settlement
  conservation, checkpoint prefix identity, and event-order rejection.
- Mutation: changed train winner, changed OOS return, forged latency, changed multiplier, changed
  checkpoint, and truncated event file.
- Golden: true walk-forward winner switching, futures settlement, prediction settlement, and
  incremental paper parity.
- Compatibility: robustness v2 readable, execution v1 replayable, worker request v1 readable.
- Performance: 10k/100k file-transport replay and incremental paper growth.
- Distribution: wheel contains new schemas and clean-installed CLI passes offline smoke.

## Definition Of Done

The release is complete only when:

- all three workstreams are implemented;
- all schemas and packaged copies match;
- the full offline test suite, Ruff, public-repository validation, plugin validation, build, and
  installed-wheel validation pass;
- new mutation and parity tests pass;
- README, usage guide, CLI contract, skills, changelog, release notes, and release audit are
  updated;
- no P0/P1 finding remains;
- PR CI passes on Python 3.9 and 3.12;
- the audited merge is tagged and the public release wheel passes a clean post-release install.

## Implementation Result

- W1 is implemented with `robustness_report.v3`, train-only fold selection, aligned OOS returns,
  effective sample-size adjustment, validator-side recomputation, and paper-candidate v3
  enforcement.
- W2 is implemented with execution config v2, latency and participation constraints, event-level
  fees, explicit impact, multiplier-aware futures accounting, signed funding, and settlement.
- W3 is implemented with canonical JSONL worker transport, ordered streaming simulation,
  checkpoint export/import, incremental paper batches, and periodic full-replay parity audits.
- The public V3 fixture contains 6 folds, 48 complete train/test cells, 192 selected OOS
  observations, no failed cells, and remains correctly non-promotional on synthetic trusted-local
  evidence.
- Release verification commands and final results are recorded in
  [`RELEASE_AUDIT_0.15.0.md`](../../reports/RELEASE_AUDIT_0.15.0.md).

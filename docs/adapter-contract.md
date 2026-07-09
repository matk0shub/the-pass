# Asset-Class Adapter Contract

The Pass core is market-agnostic. Asset-class adapters are responsible for translating
market-specific data, costs, execution assumptions, and settlement rules into common
artifacts.

## Required Adapter Outputs

- Source notes for provider and market-structure assumptions.
- StrategySpec with asset class, venue, instrument universe, horizon, and edge thesis.
- Data manifest with provider, license note, schema, time coverage, fingerprints, and gaps.
- Metrics report with gross and net results.
- Cost waterfall with fees, spread, slippage, funding/borrow/roll/settlement costs where
  relevant.
- Verdict report with gate status and blockers.

## Required Adapter Decisions

- Provider and licensing ADR.
- Instrument metadata policy.
- Timestamp policy: event time, receive time, decision time, execution time.
- Cost model policy.
- Fill model policy.
- Risk and sizing policy.
- Settlement or corporate-action policy where relevant.

## Adapter Modes

| Mode | Meaning | Promotion |
| --- | --- | --- |
| diagnostic | Useful for exploration only. | Cannot promote to paper |
| research | Can support backtest research. | Can enter `taste` |
| paper | Can support paper/replay observation. | Can recommend risk review |
| live-capable | Has separate live ADR, dry-run, risk, and credential boundary. | Human approval only |

## Examples

- Crypto perp adapter: funding, mark/index price, liquidation events, book depth, venue
  outages.
- Futures adapter: contract metadata, roll policy, sessions, tick value, exchange fees.
- Prediction-market adapter: market semantics, resolution source, fee endpoint, depth,
  settlement reconciliation.
- Equities/options adapter: corporate actions, borrow, expiries, assignment/exercise,
  exchange/broker fees.

# ADR-0001: MVP Scope

Status: proposed
Date: 2026-07-09
Owner: head_researcher

## Context

The lab needs a narrow first target. Building a universal trading platform before the
research loop works would create avoidable complexity and weak evidence.

## Decision

The MVP is The Pass v0: a research-only strategy review station focused on crypto
perpetual futures. It must prove that the system can kill bad strategies, reproduce
experiments, and promote only well-evidenced candidates to paper review.

Primary MVP:

- Venues: Binance USD-M public data first, Bybit public data as cross-venue check.
- Instruments: BTCUSDT, ETHUSDT, SOLUSDT; XRPUSDT as optional regime/liquidity check.
- Horizons: 1m, 5m, 15m, 1h, 4h.
- Families: time-series momentum, breakout, funding/carry, intraday reversal/momentum
  after liquidity shocks.
- Mode: historical research and replay/paper only.

Out of MVP:

- Live trading.
- Options.
- DeFi execution.
- News/NLP-driven strategies.
- Real market making.
- Cross-exchange arbitrage requiring transfers or borrow.
- Any edge requiring sub-100ms latency.

## Alternatives Considered

- Start with listed futures: rejected for MVP because licensed data, roll policy, and
  contract metadata must be solved first.
- Start with prediction markets: rejected for this repo's initial MVP because AlphaLab
  already covers Polymarket-specific research.
- Build live bot first: rejected because research gates and evidence ledger must exist
  before any live boundary.

## Consequences

- Faster first loop with accessible data.
- Less execution complexity.
- Futures and prediction-market adapters remain planned, not first-class MVP work.

## Validation

The MVP is complete only when three strategy families have full specs, at least two
independent crypto data sources exist for one instrument, and every run creates manifest,
receipt, metrics, cost waterfall, and verdict artifacts.

## Review Trigger

Revisit when the first crypto MVP has killed at least one intentionally bad baseline and
promoted at least one plausible baseline to paper-candidate status.

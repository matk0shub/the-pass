# ADR-0004: Data Providers

Status: accepted
Date: 2026-07-09
Owner: data_steward

## Context

The Pass is public and market-agnostic. It must not hardcode a default provider as if one
market were the product. Provider choices belong to adapters and strategy specs, while the
core enforces provider acceptance and evidence requirements.

## Decision

The core ships provider acceptance rules, not provider lock-in. Public/free data may be
used for scaffolding. Any candidate that depends on queue, depth, funding, open interest,
corporate actions, settlement semantics, or intraday fills must be retested on licensed,
archived, or independently verifiable data before paper promotion.

Provider examples:

- Crypto: Binance, Bybit, Tardis.dev, Kaiko.
- Futures: Databento or another licensed historical provider.
- Prediction markets: Polymarket/Kalshi public APIs plus archived raw store or licensed
  warehouse.
- Equities/options/FX/rates/credit: adapter-specific provider ADR required before final
  verdicts.

Acceptance checklist:

- Raw response can be stored immutably.
- Terms/licensing allow internal research and backtesting.
- Event time and receive time can be separated.
- Instrument metadata includes tick size, lot size, multiplier, quote currency, and
  contract semantics.
- Historical data can be replayed deterministically.
- Provider outage or truncation is detectable.
- Data can be cross-checked against another source for a sample window.

## Alternatives Considered

- Declare a single default provider: rejected because the framework must cover many markets.
- Buy broad institutional data immediately: rejected until an adapter has a concrete
  validation need.
- Use public data for final verdicts in execution-sensitive strategies: rejected.

## Consequences

- Public repo can document provider contracts without redistributing data.
- Adapter authors must solve licensing and timestamp semantics explicitly.
- Surviving candidates cannot hide weak data under generic backtest metrics.

## Validation

Provider trial reports must include field coverage, timestamp quality, outage handling,
licensing notes, deterministic replay proof, and cross-source comparison.

## Review Trigger

Revisit before adding a provider-specific adapter as first-class core functionality.

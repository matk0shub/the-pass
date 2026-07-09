# ADR-0004: Data Providers

Status: proposed
Date: 2026-07-09
Owner: data_steward

## Context

Free/public data is useful for scaffolding, but final verdicts that depend on queue,
depth, funding, open interest, or fills need audited and preferably independently archived
data.

## Decision

Start with Binance USD-M public REST/WS for scaffolding and Bybit public data for a
cross-venue assumption check. Trial Tardis.dev or Kaiko before any crypto strategy reaches
paper promotion. Trial Databento for listed futures only after the crypto MVP proves the
ledger/backtest/audit loop.

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

- Buy broad institutional data immediately: rejected until the framework proves it can kill
  bad baselines.
- Use exchange public data for final verdicts: rejected for strategies whose edge depends
  on depth, queue, funding, or execution realism.

## Consequences

- Low-cost start.
- Provider/license work remains explicit.
- Surviving candidates cannot be promoted from public-only data.

## Validation

Provider trial reports must include field coverage, timestamp quality, outage handling,
licensing notes, deterministic replay proof, and cross-source comparison.

## Review Trigger

Revisit before any paid provider purchase, before futures research leaves exploratory mode,
or when a candidate needs paper promotion.

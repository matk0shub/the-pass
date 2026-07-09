# ADR-0003: Engine

Status: proposed
Date: 2026-07-09
Owner: automation_engineer

## Context

The core asset is not a backtesting package. It is the evidence ledger, data manifest,
cost model, audit workflow, and promotion gates.

## Decision

Use pandas/NumPy for first screening, optional vectorbt for large parameter sweeps, and a
small in-house event simulator for MVP execution realism. Evaluate NautilusTrader only
after the canonical event model, paper broker, risk gates, and reconciliation requirements
are stable.

## Alternatives Considered

- NautilusTrader immediately: rejected because adapter complexity is premature before the
  research event model is fixed.
- Backtrader: rejected as default because it is too bar-centric for modern crypto/funding
  and orderbook realism.
- QuantConnect/LEAN local runtime: rejected for MVP, but useful as an architectural
  reference for Alpha -> Portfolio -> Risk -> Execution separation.

## Consequences

- Faster first experiments.
- Fill and cost assumptions remain explicit.
- Some engine work may be replaced later if two or more strategy families need shared
  live/backtest semantics.

## Validation

The first simulator must support conservative taker fills, forbidden mid fills for
promotion, configurable slippage/fees, partial/rejected fills, and timestamp separation.

## Review Trigger

Revisit when at least two strategy families require shared order lifecycle or portfolio
accounting logic, or when a paper-surviving candidate needs micro-live reconciliation.

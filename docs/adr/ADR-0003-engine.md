# ADR-0003: Engine

Status: accepted
Date: 2026-07-09
Owner: automation_engineer

## Context

The core asset is not a backtesting package. It is the plugin workflow, evidence ledger,
data manifest, cost model, audit workflow, and promotion gates. The Pass must be able to
wrap many engines instead of becoming locked to one.

## Decision

The Pass core is engine-neutral. The plugin owns artifact contracts and gates. Asset-class
or strategy adapters may use pandas/NumPy, vectorbt, Backtrader, NautilusTrader,
QuantConnect/LEAN, custom simulators, broker paper APIs, or other engines only if they emit
the required artifacts.

Default local examples may use pandas/NumPy and a lightweight simulator, but those are
examples, not product identity.

## Alternatives Considered

- Pick one engine as mandatory: rejected because The Pass should judge multiple trading
  stacks.
- Build a full engine first: rejected because the plugin can create value by validating
  evidence before engine integration is mature.
- Ignore engine semantics: rejected because the artifact contract must still capture data,
  cost, fill, latency, and risk assumptions.

## Consequences

- The public repo stays broadly applicable.
- Each adapter must document what its engine can and cannot prove.
- Promotion gates can compare outputs across engines when needed.

## Validation

Every engine adapter must produce data manifests, receipts, metrics, cost waterfalls,
verdicts, and explicit execution assumptions. Any adapter that cannot do this stays
diagnostic-only.

## Review Trigger

Revisit if two or more adapters need shared order lifecycle, portfolio accounting, or
paper/live reconciliation code in core.

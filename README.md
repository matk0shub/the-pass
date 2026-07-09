# Strategy Lab

Research operating system for testing trading strategy ideas and building safe
automation workflows.

This repository starts from the plan in
`docs/research/strategy-lab-automation-plan.md`. The project is intentionally
research-first: it should kill weak ideas quickly, preserve evidence for good ideas,
and keep any live trading boundary behind explicit human approval.

## Scope

- Crypto perpetual futures research first.
- Futures research second, only after provider/licensing ADR.
- Prediction-market adapters later.
- No live trading or real order placement in this repository until a separate live
  approval ADR exists.

## Current Starting Point

- Main plan: `docs/research/strategy-lab-automation-plan.md`
- Decisions: `docs/adr/`
- Templates: `templates/`
- Backlog: `research/backlog/`
- Source notes: `research/sources/`
- Experiment receipts: `experiments/`
- Reports: `reports/`

## First Milestones

1. Accept or amend the initial ADRs.
2. Fill the first three `StrategySpec` files.
3. Create source notes for P0/P1 studies and provider docs.
4. Build a read-only data manifest and experiment ledger.
5. Run baseline experiments with explicit kill criteria.

## Safety

Live trading is out of scope. Any code or workflow that can place real orders must be
isolated behind a new ADR, separate credentials, dry-run proof, risk review, and explicit
human approval tied to an exact config hash.

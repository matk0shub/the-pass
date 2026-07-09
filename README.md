# The Pass

The final review station for trading strategy research.

The Pass is a research operating system for testing trading strategy ideas and building
safe automation workflows. It borrows the kitchen metaphor deliberately: strategy ideas
are recipes, data is mise en place, backtests are cooks, audits are tasting, and nothing
gets plated for paper or live review until it passes the line.

This repository starts from the plan in `docs/research/the-pass-plan.md`. The project is
intentionally research-first: it should kill weak ideas quickly, preserve evidence for
good ideas, and keep any live trading boundary behind explicit human approval.

## Scope

- Public plugin-first framework for trading strategy research.
- Market-agnostic artifact contracts: source notes, strategy specs, data manifests, run
  receipts, metrics reports, cost waterfalls, verdicts, and gate packs.
- Asset-class adapters for crypto, futures, prediction markets, equities, FX, options, or
  other markets can be added without changing the core gate model.
- No live trading or real order placement until a separate live approval ADR exists for an
  exact adapter, config hash, venue, and risk envelope.

## Current Starting Point

- Main plan: `docs/research/the-pass-plan.md`
- Decisions: `docs/adr/`
- Plugin manifest: `.codex-plugin/plugin.json`
- Plugin skills: `skills/`
- Templates: `templates/`
- Schemas: `schemas/`
- Backlog: `research/backlog/`
- Source notes: `research/sources/`
- Experiment receipts: `experiments/`
- Reports: `reports/`

## First Milestones

1. Accept or amend the initial ADRs.
2. Make the plugin skills usable as the primary interface.
3. Add schema validation tooling for templates and artifacts.
4. Create source notes for P0/P1 studies and provider docs.
5. Build a read-only data manifest and experiment ledger.

## Safety

Live trading is out of scope. Any code or workflow that can place real orders must be
isolated behind a new ADR, separate credentials, dry-run proof, risk review, and explicit
human approval tied to an exact config hash.

## Public Repo Policy

This repository is intended to be public. Keep secrets, private data, broker credentials,
paid data files, and proprietary strategy results out of git. Public artifacts should describe
contracts, workflows, examples, and safety boundaries rather than leaking live edge or account
details.

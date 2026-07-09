# Security Policy

The Pass starts as a research and review workflow. It must fail closed around live trading,
credentials, private data, and paid datasets.

## Reporting

Open a private security report through the hosting platform when available. If the project
does not yet have private reporting enabled, contact the maintainer out of band before
publishing exploit details.

## Sensitive Data

Do not include:

- Exchange or broker API keys.
- Wallet keys, seed phrases, or signing material.
- Session tokens or cookies.
- Paid market data files.
- Private account identifiers, balances, fills, order IDs, or PnL.

## Live Trading Boundary

Live trading code is not accepted by default. A live-capable contribution requires an
accepted ADR that defines the exact adapter, venue, credential model, risk envelope,
dry-run proof, rollback plan, and human approval process.

## Public Examples

Examples must be synthetic or explicitly public-safe. If an example cannot be published
without exposing edge, account details, or licensed data, it belongs outside this public
repository.

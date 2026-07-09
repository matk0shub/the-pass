# Public Release Checklist

Use this before pushing or publishing The Pass.

## Repository Safety

- [ ] No secrets, keys, tokens, cookies, or credentials.
- [ ] No paid data files or license-restricted data.
- [ ] No private account balances, fills, order IDs, or PnL.
- [ ] No live order placement path.
- [ ] No proprietary strategy parameters unless intentionally public.

## Plugin Readiness

- [ ] `.codex-plugin/plugin.json` validates.
- [ ] Every skill has a clear trigger and safety boundary.
- [ ] README explains the product and live-trading boundary.
- [ ] ADRs for product scope, storage, engine, providers, risk, and public distribution are
      accepted.

## Artifact Readiness

- [ ] Templates exist for source notes, StrategySpec, data manifests, run receipts, metrics,
      cost waterfalls, and verdicts.
- [ ] Schemas or schema-ready examples exist for core artifacts.
- [ ] Public examples are synthetic or public-safe.

## Distribution

- [ ] LICENSE exists.
- [ ] CONTRIBUTING exists.
- [ ] SECURITY exists.
- [ ] GitHub repository visibility is public only after this checklist passes.

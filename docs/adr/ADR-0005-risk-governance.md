# ADR-0005: Risk Governance

Status: accepted
Date: 2026-07-09
Owner: risk_officer

## Context

Trading research can quietly become live-capable if risk boundaries are not explicit. The
lab must separate research, paper, risk review, and live approval.

## Decision

Risk is independent from strategy research. A strategy cannot grant itself size, leverage,
live access, or new venues.

Roles:

- `Head Researcher`: approves specs and kill/revise/paper-candidate verdicts.
- `Stats Auditor`: blocks promotion for overfitting, leakage, or multiple-testing issues.
- `Execution Skeptic`: blocks promotion for unrealistic fills, costs, or latency.
- `Risk Officer`: owns sizing, exposure, drawdown, live boundary, and freeze decisions.
- `Operator`: runs approved runbooks; cannot change strategy specs or risk limits ad hoc.

Default caps before first live ADR:

- Research capital: 0.
- Paper capital: virtual only.
- Micro-live cap: min(100 USD notional, 0.25% of approved account equity) per strategy,
  only after explicit live ADR.
- Max daily micro-live loss: min(25 USD, 0.10% account equity), only after explicit live ADR.
- Max leverage in MVP: 1.0x effective exposure unless a risk ADR approves a hedge structure.

## Alternatives Considered

- Let strategy code own sizing: rejected because research and risk must be separated.
- Add live credentials early for convenience: rejected because this repo starts research-only.

## Consequences

- Slower path to live, intentionally.
- Stronger auditability.
- Every live-capable config change requires explicit human approval.

## Validation

Before any live-capable code exists, a safety audit must prove that research workflows have
no order credentials and no real order path.

## Review Trigger

Revisit only when a paper candidate has passed research, paper, execution realism, and risk
review gates.

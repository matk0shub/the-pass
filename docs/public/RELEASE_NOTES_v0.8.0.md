# The Pass v0.8.0

`v0.8.0` replaces the original eleven-command Codex interface with seven focused skills and a
bounded whole-line front door: `/the-pass:run`.

## Highlights

- Seven public skills: `run`, `research`, `test`, `review`, `paper`, `plate`, and `status`.
- Durable workflow state with explicit targets, owners, blockers, evidence, and next actions.
- Bounded transitions and remediation with terminal no-progress protection.
- Ledger-backed immutable successor packages for paper and risk progression.
- Exact-package v2 gate authority with independent reviewers and semantic replay.
- Regression protection against label bypasses, copied packages, forged/out-of-order decisions,
  duplicate package IDs, and resumable exhausted budgets.

The Python CLI remains granular and scheduler-neutral. Existing v1 evidence remains readable but
cannot authorize v2 promotion, remediation, or completion.

## Safety

The public package still contains no real order transport, authenticated order client, or
credential loader. `/the-pass:run` cannot target `live_gate`; approval packs remain pending human
decision inputs and cannot grant approval.

See the [implementation audit](../../reports/SLASH_SKILL_CONSOLIDATION_AUDIT_2026-07-10.md) and
[`v0.8.0` release audit](../../reports/RELEASE_AUDIT_0.8.0.md) for the verified matrix and residual
limits.

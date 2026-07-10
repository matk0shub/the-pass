# The Pass v0.7.0

`v0.7.0` is the release-hardening milestone for the public strategy-testing framework.

## Highlights

- Framework capability and candidate promotion states are independently validated.
- Automation jobs run in cancellable child processes with enforced deadlines, staged outputs,
  restricted retries, and incident/freeze evidence.
- CI validates Python 3.9 and 3.12, Ruff, lock state, public safety, wheel/sdist builds, and a
  clean installed-wheel workflow outside the checkout.
- Every CLI group has a stable machine-readable JSON envelope contract.
- Public maintenance workflows detect adapter, dependency, research-link, fixture, and
  performance drift without mutating promotion evidence.
- Canonical Parquet writes are chunked and feature generation avoids duplicate materialization.

## Safety

- No live order transport, authenticated venue channel, or credential loader is included.
- Candidate `paper_gate` and public `live_gate` remain blocked in diagnostic evidence.
- This release does not claim that any strategy has edge.

## Compatibility

- Python 3.9 and 3.12 are supported.
- v1 artifacts remain readable but cannot prove v2 candidate promotion.
- New evidence and templates use v2 schemas.

## Scope

Describe the exact behavior and ownership boundary changed.

## Evidence

List artifacts, tests, or source material that support the change.

## Safety Impact

- [ ] No live order path or credential access added.
- [ ] Candidate and framework gate states remain separate.
- [ ] Paid, private, or license-restricted data is not included.

## Validation

```text
uv lock --check
uv run --extra dev ruff check .
uv run --extra data --extra research python scripts/validate_public_repo.py
uv run --extra data --extra research python -m unittest discover -s tests
uv build
```

## Review

- [ ] Findings are resolved or explicitly recorded as blockers.
- [ ] Generated evidence and documentation links are current.

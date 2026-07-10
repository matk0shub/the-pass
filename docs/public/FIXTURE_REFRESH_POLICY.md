# Fixture Refresh Policy

Public fixtures are evidence contracts, not disposable caches.

1. Never refresh a fixture automatically from a scheduled workflow.
2. Preserve the previous fixture or its exact fingerprint in release history.
3. Record provider, endpoint, capture time, license mode, and redaction method.
4. Explain every field-level schema change in the changelog or a migration note.
5. Run adapter contract, mutation, deterministic replay, and public safety tests.
6. Do not include credentials, account channels, paid data, or provider-prohibited payloads.
7. A changed fixture cannot silently rewrite golden strategy results.

Provider drift creates an issue and evidence artifact. A maintainer reviews semantics before a
fixture or adapter is changed.

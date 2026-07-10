# Schema Compatibility Policy

Artifact dispatch uses `(artifact_type, schema_version)`.

## Supported Generations

- v1 artifacts remain readable compatibility evidence.
- v1 ledger labels cannot prove a v2 candidate promotion.
- New templates and generated promotion evidence use v2.
- Unknown versions fail closed with a list of supported versions.

## Compatible Changes

A v2 schema may receive optional fields, stricter validation of previously invalid states, or
new artifact types when existing valid artifacts remain readable. Templates may adopt new
optional fields immediately.

## Breaking Changes

Removing or renaming a field, changing a required field's meaning, changing an exit-code
meaning, or making a previously valid evidence state invalid requires:

1. a new schema version,
2. a migration note and compatibility fixture,
3. read support for the prior version during the announced compatibility window,
4. a major package version if the public Python or CLI contract also breaks.

Schemas in `schemas/` and `src/the_pass/schemas/` must remain byte-identical. Policies in
`config/` and `src/the_pass/policies/` follow the same rule. CI and distribution validation
enforce both copies.

## Artifact Immutability

An artifact used by a recorded run or gate decision is never migrated in place. Migration
creates a new artifact ID, schema version, fingerprint, and receipt while retaining the old
evidence.

# Framework Performance Policy

Performance evidence measures The Pass itself, never strategy profitability.

- Fixed deterministic event counts are 10k, 100k, and 1m.
- Measured operations are canonical event creation, sorting, quality checks, feature build,
  event replay, immutable Parquet commit, ledger verification, and dashboard generation.
- Every report records Python, platform, dependency versions, input fingerprints, throughput,
  and peak Python-managed memory.
- The first `v0.7.0` scheduled report is the reference baseline for that runner class.
- A later result above 120% of the matching baseline opens a performance review; it does not
  automatically change strategy evidence or artifact fingerprints.
- Optimization requires a measured regression or user-relevant bottleneck.
- Default pull-request CI runs functional checks; the large matrix runs on schedule or manual
  dispatch to keep normal feedback efficient.

# Schemas

These JSON Schemas define the first public contract for The Pass artifacts. They are
intentionally conservative: a file can contain more detail than the schema requires, but
gate-critical fields should be present and typed.

Core artifacts:

- `source_note.schema.json`
- `strategy_spec.schema.json`
- `data_manifest.schema.json`
- `run_receipt.schema.json`
- `metrics_report.schema.json`
- `cost_waterfall.schema.json`
- `verdict_report.schema.json`

Future validators should accept YAML or JSON input, parse it into structured data, and
validate against these schemas before a gate can pass.

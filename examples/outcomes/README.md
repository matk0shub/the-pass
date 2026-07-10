# Outcome Examples

These examples distinguish framework capability from candidate research outcomes.

| Outcome | Evidence | Meaning |
| --- | --- | --- |
| framework `pass` | `../../reports/gates/P4_2026-07-10.yaml` | paper capability works and correctly evaluates its diagnostic candidate |
| candidate `blocked` | `../synthetic-breakout/package/verdict_report.json` | required promotion evidence is missing |
| candidate `revise` | `revise/verdict_report.yaml` | a specific assumption must change before a new versioned run |
| candidate `kill` | `../synthetic-random-baseline/package/verdict_report.json` | the negative control is retained and stopped |

The framework pass does not assert edge. Blocked, revise, and kill are successful outputs of
the testing process when supported by evidence.

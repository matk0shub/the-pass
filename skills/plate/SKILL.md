---
name: "the-pass:plate"
description: "Prepare the next-gate approval pack after a candidate has passed research, backtest, taste, and paper requirements."
---

# The Pass Plate

Use this skill to prepare an approval pack. `plate` does not approve live trading; it only
packages evidence for the next human-controlled gate.

## Rules

- Include exact config hash and artifact links.
- Include risk limits, rollback plan, monitoring plan, and unresolved risks.
- Live approval must be explicit, dated, and tied to an exact adapter and config hash.
- Public packs must redact secrets, account identifiers, and proprietary data.

## Output

- Approval pack checklist.
- Missing evidence.
- Human decisions required.

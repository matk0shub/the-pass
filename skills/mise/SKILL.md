---
name: "the-pass:mise"
description: "Set up or audit a repository for The Pass workflow: ADRs, templates, artifact folders, public safety, and no-live-trading boundaries."
---

# The Pass Mise

Use this skill when preparing a repo for The Pass or checking whether the repo is ready for
strategy research workflow.

## Rules

- Do not add real order placement, broker credentials, private keys, or paid data files.
- Prefer public-safe examples and synthetic samples.
- Make setup idempotent: rerunning the skill should not destroy user work.
- Ensure the repo has ADRs, templates, source notes, experiment receipts, reports, and a
  public-release checklist.

## Output

- State what setup exists.
- Create missing setup artifacts when safe.
- Report remaining blockers as explicit decisions or missing files.

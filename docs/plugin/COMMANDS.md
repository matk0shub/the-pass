# The Pass Commands

The Pass uses kitchen-language commands because the product is a review station. Strategy
ideas are recipes; evidence is the plate; gates decide whether anything leaves the line.

## Commands

| Command | Purpose | Can Promote? |
| --- | --- | --- |
| `/the-pass:mise` | Prepare repo structure, templates, ADRs, and safety checks. | No |
| `/the-pass:research <topic>` | Turn sources into source notes and hypotheses. | No |
| `/the-pass:spec <idea>` | Convert an idea into a falsifiable StrategySpec. | No |
| `/the-pass:screen <spec>` | Run or design diagnostic screening. | No |
| `/the-pass:backtest <spec>` | Build a reproducible backtest artifact package. | No |
| `/the-pass:taste <run>` | Independently review data, stats, execution, and risk. | Can block |
| `/the-pass:refire <findings>` | Fix confirmed findings without expanding scope. | No |
| `/the-pass:simmer <gate>` | Iterate toward one gate or kill condition. | No |
| `/the-pass:paper <candidate>` | Prepare paper/replay observation. | Can recommend risk review |
| `/the-pass:plate <candidate>` | Package evidence for the next human-controlled gate. | No live approval |
| `/the-pass:receipts` | Summarize evidence, costs, decisions, and open blockers. | No |

## Live Boundary

No command sends real orders. `plate` can prepare an approval pack, but live approval must
be explicit, dated, human-controlled, and tied to an exact config hash.

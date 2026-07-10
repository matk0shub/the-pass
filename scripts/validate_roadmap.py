#!/usr/bin/env python3
"""Validate the machine-readable trading roadmap without claiming incomplete work."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from the_pass.roadmap import RoadmapValidationError, validate_roadmap_files  # noqa: E402


STATUS_PATH = ROOT / "docs" / "implementation" / "roadmap-status.yaml"
PLAN_PATH = ROOT / "docs" / "implementation" / "TRADING_ROADMAP_EXECUTION_PLAN.md"


def fail(message: str) -> None:
    print(f"roadmap validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    try:
        validate_roadmap_files(root=ROOT, status_path=STATUS_PATH, plan_path=PLAN_PATH)
    except (OSError, RoadmapValidationError) as exc:
        fail(str(exc))

    print("roadmap validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

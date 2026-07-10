"""Isolated worker for whitelisted scheduler-neutral automation jobs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from the_pass.data.contracts import stable_fingerprint

from .runner import AUTOMATION_COMMANDS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", choices=AUTOMATION_COMMANDS, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--attempt", type=int, required=True)
    args = parser.parse_args()
    inputs = json.loads(args.inputs.read_text(encoding="utf-8"))
    if not isinstance(inputs, dict):
        raise ValueError("automation inputs must be an object")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"{args.command}-snapshot.json"
    output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command": args.command,
                "inputs_fingerprint": stable_fingerprint(inputs),
                "attempt": args.attempt,
                "status": "complete",
                "read_only_external_boundary": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "worker-result.json").write_text(
        json.dumps({"outputs": [output.name]}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

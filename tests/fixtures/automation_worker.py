from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--attempt", type=int, required=True)
    args = parser.parse_args()
    inputs = json.loads(args.inputs.read_text(encoding="utf-8"))
    behavior = inputs.get("fixture_behavior", "complete")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if behavior == "sleep":
        time.sleep(float(inputs.get("sleep_seconds", 2)))
    if behavior == "fail" or (behavior == "fail_once" and args.attempt == 1):
        raise RuntimeError("fixture failure")
    if behavior == "partial_fail":
        (args.output_dir / "partial.json").write_text("{}\n", encoding="utf-8")
        raise RuntimeError("fixture partial failure")
    output = args.output_dir / "fixture-output.json"
    output.write_text(json.dumps({"attempt": args.attempt}) + "\n", encoding="utf-8")
    (args.output_dir / "worker-result.json").write_text(
        json.dumps({"outputs": [output.name]}) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

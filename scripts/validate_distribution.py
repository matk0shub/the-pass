#!/usr/bin/env python3
"""Build-independent validation of an installed The Pass wheel."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ENVELOPE = {"ok", "status", "artifact_paths", "issues", "receipt_id"}
FORBIDDEN_WHEEL_PREFIXES = ("reports/", "research/", "tests/", "examples/", "automations/")
FORBIDDEN_LIVE_PATTERNS = (
    "place_" + "order(",
    "submit_" + "order(",
    "create_" + "order(",
    "send_" + "order(",
    "market_" + "order(",
    "limit_" + "order(",
    "load_" + "credentials(",
)


def fail(message: str) -> None:
    print(f"distribution validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        fail(f"command exited {result.returncode}: {' '.join(command)}\n{result.stdout}\n{result.stderr}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        fail(f"wheel does not exist: {wheel}")

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        packaged_schemas = {Path(name).name for name in names if name.startswith("the_pass/schemas/")}
        packaged_policies = {Path(name).name for name in names if name.startswith("the_pass/policies/")}
        expected_schemas = {path.name for path in (ROOT / "schemas").glob("*.json")}
        expected_policies = {path.name for path in (ROOT / "config").glob("*.yaml")}
        if packaged_schemas != expected_schemas:
            fail("wheel schema set differs from the public schema registry")
        if packaged_policies != expected_policies:
            fail("wheel policy set differs from tracked config policies")
        if any(name.startswith(FORBIDDEN_WHEEL_PREFIXES) for name in names):
            fail("wheel contains repository-only evidence or fixtures")
        for name in names:
            if not name.startswith("the_pass/") or not name.endswith(".py"):
                continue
            text = archive.read(name).decode("utf-8")
            if any(pattern in text for pattern in FORBIDDEN_LIVE_PATTERNS):
                fail(f"wheel contains a forbidden live-order or credential pattern: {name}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        environment = root / "venv"
        run(["uv", "venv", "--seed", "--python", sys.executable, str(environment)], cwd=root)
        bin_dir = environment / ("Scripts" if os.name == "nt" else "bin")
        python = bin_dir / ("python.exe" if os.name == "nt" else "python")
        executable = bin_dir / ("the-pass.exe" if os.name == "nt" else "the-pass")
        run([str(python), "-m", "pip", "install", f"{wheel}[data,research,paper]"], cwd=root)
        version = run([str(executable), "--version"], cwd=root)
        if "the-pass" not in version.stdout:
            fail("installed CLI did not report its version")
        imports = run(
            [
                str(python),
                "-c",
                "import duckdb,numpy,pandas,pyarrow,scipy,the_pass.data,the_pass.engine,the_pass.paper",
            ],
            cwd=root,
        )
        if imports.stderr:
            fail(f"installed extras emitted import errors: {imports.stderr}")

        artifact = root / "human_decision.yaml"
        shutil.copy2(ROOT / "templates" / "human_decision.yaml", artifact)
        validation = run([str(executable), "validate", str(artifact), "--format", "json"], cwd=root)
        envelope = json.loads(validation.stdout)
        if not REQUIRED_ENVELOPE <= set(envelope) or not envelope["ok"]:
            fail("installed CLI validation envelope is invalid")

        package = root / "package"
        shutil.copytree(ROOT / "examples" / "synthetic-breakout" / "package", package)
        run([str(executable), "validate-package", str(package)], cwd=root)
        ledger = root / "ledger.jsonl"
        run([str(executable), "receipts", "add", str(package), "--ledger", str(ledger)], cwd=root)
        run([str(executable), "receipts", "verify", "--ledger", str(ledger)], cwd=root)

    print("distribution validation passed: wheel contents and clean installed CLI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from the_pass.validator import validate_artifact, validate_package


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PACKAGE = ROOT / "examples" / "synthetic-breakout" / "package"
SCHEMA_DIR = ROOT / "schemas"


class ValidatorTests(unittest.TestCase):
    def test_synthetic_package_validates(self) -> None:
        result = validate_package(EXAMPLE_PACKAGE, schema_dir=SCHEMA_DIR)

        self.assertTrue(result.ok, [issue.as_dict() for issue in result.issues])

    def test_single_yaml_artifact_validates_with_explicit_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "adapter.yaml"
            artifact.write_text(
                """
id: test-adapter
name: Test Adapter
mode: diagnostic
asset_classes: [synthetic]
owner: tester
providers:
  - id: synthetic
    type: synthetic
    license: public-safe
    fields: [timestamp, close]
engine:
  name: none
  role: fixture-only
  limitations: []
policies:
  timestamp: synthetic
  cost_model: none
  fill_model: none
  risk_model: none
  settlement: none
safety:
  live_trading_enabled: false
  real_order_path_available: false
  credentials_required: false
""".strip(),
                encoding="utf-8",
            )

            result = validate_artifact(artifact, schema_dir=SCHEMA_DIR, artifact_type="adapter")

        self.assertTrue(result.ok, [issue.as_dict() for issue in result.issues])
        self.assertEqual(result.artifact_type, "adapter")

    def test_package_blocks_missing_required_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            shutil.copytree(EXAMPLE_PACKAGE, package)
            (package / "metrics_report.json").unlink()

            result = validate_package(package, schema_dir=SCHEMA_DIR)

        self.assertFalse(result.ok)
        self.assertTrue(any("missing required artifact: metrics_report" in issue.message for issue in result.issues))

    def test_diagnostic_adapter_cannot_be_paper_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            shutil.copytree(EXAMPLE_PACKAGE, package)
            verdict_path = package / "verdict_report.json"
            verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
            verdict["verdict"] = "paper_candidate"
            verdict_path.write_text(json.dumps(verdict, indent=2), encoding="utf-8")

            result = validate_package(package, schema_dir=SCHEMA_DIR)

        self.assertFalse(result.ok)
        self.assertTrue(any("diagnostic adapters cannot produce paper_candidate" in issue.message for issue in result.issues))


if __name__ == "__main__":
    unittest.main()

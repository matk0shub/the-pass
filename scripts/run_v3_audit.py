#!/usr/bin/env python3
"""Build deterministic V3 robustness, risk, and independent audit evidence."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from the_pass.audit import build_audit_report, reproduce_baseline_cli  # noqa: E402
from the_pass.data.contracts import canonical_value  # noqa: E402
from the_pass.engine.baselines import generate_synthetic_bars  # noqa: E402
from the_pass.ledger import build_run_entry  # noqa: E402
from the_pass.risk import build_risk_policy_artifact, build_risk_report  # noqa: E402
from the_pass.robustness import (  # noqa: E402
    StressParameters,
    run_strategy_sweep,
    run_stress_suite,
)
from the_pass.validator import validate_artifact  # noqa: E402


def write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(canonical_value(document, allow_float=True), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "v3" / "donchian_momentum")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    try:
        if args.clean and output.exists():
            shutil.rmtree(output)
        package = ROOT / "examples" / "b2-baselines" / "donchian_momentum" / "package"

        costs = json.loads((package / "cost_waterfall.json").read_text(encoding="utf-8"))
        stress = run_stress_suite(
            StressParameters(
                gross_pnl=Decimal(str(costs["gross_pnl"])),
                fees=Decimal(str(costs["costs"]["fees"])),
                slippage=Decimal(str(costs["costs"]["slippage"])),
                missed_fill_cost=Decimal(2),
                outage_loss=Decimal(10),
                gap_loss=Decimal(30),
                deleverage_loss=Decimal(40),
            )
        )
        stress_evidence = [
            {
                "scenario": row["scenario"],
                "status": "pass" if row["pass"] else "blocked",
                "net_pnl": row["net_pnl"],
                "summary": (
                    "scenario remains net positive"
                    if row["pass"]
                    else "scenario is net negative and blocks promotion"
                ),
            }
            for row in stress
        ]
        fixture = ROOT / "examples" / "robustness-donchian"
        descriptor = json.loads(
            (fixture / "descriptor.json").read_text(encoding="utf-8")
        )
        execution = json.loads(
            (fixture / "execution.json").read_text(encoding="utf-8")
        )
        variants = json.loads(
            (fixture / "variants.json").read_text(encoding="utf-8")
        )
        package_id = build_run_entry(package)["package_id"]
        robustness = run_strategy_sweep(
            generate_synthetic_bars(
                instrument_id="BTCUSDT",
                count=320,
                profile="trend",
            ),
            descriptor=descriptor,
            execution=execution,
            variants=variants,
            splits=None,
            selected_index=1,
            registration_path=output / "robustness_registration.json",
            workspace_root=fixture,
            source_package_id=package_id,
            created_at="2026-07-10T00:00:00Z",
            train_size=96,
            test_size=32,
            purge=2,
            embargo=2,
            null_variant_index=3,
            stress_results=stress_evidence,
        )
        selected_returns = robustness["selected_oos_returns"]
        pbo = robustness["statistics"]["pbo"]
        policy = build_risk_policy_artifact("crypto_intraday")
        blockers = [
            "synthetic sample does not provide 12 to 24 months of history",
            "two fills are below the 500-trade intraday threshold",
            "next-bar synthetic fills are not executable book replay",
        ]
        if pbo["pbo"] > policy["promotion_thresholds"]["maximum_pbo"]:
            blockers.append("PBO exceeds the crypto intraday threshold")
        if any(not result["pass"] for result in stress):
            blockers.append("one or more mandatory stress scenarios is net-negative")
        risk_report = build_risk_report(
            package_id=package_id,
            policy=policy,
            returns=selected_returns,
            scenario_losses=stress,
            capacity=1_000_000,
            blockers=blockers,
        )
        reproduction = reproduce_baseline_cli("donchian_momentum", package)
        stats_findings = [
            {
                "severity": "P2",
                "title": "History and trade-count gates are not met",
                "evidence": "risk_report.json",
                "status": "confirmed",
                "recommendation": "Collect the required history and at least 500 intraday trades before promotion review.",
                "promotion_impact": "blocks_promotion",
                "blocks_promotion": True,
            }
        ]
        if pbo["pbo"] > policy["promotion_thresholds"]["maximum_pbo"]:
            stats_findings.append(
                {
                    "severity": "P2",
                    "title": "PBO exceeds the asset policy threshold",
                    "evidence": "robustness_report.json",
                    "status": "confirmed",
                    "recommendation": "Reduce the strategy zoo or add independent history before retesting.",
                    "promotion_impact": "blocks_promotion",
                    "blocks_promotion": True,
                }
            )
        stats_audit = build_audit_report(
            report_id="donchian-stats-audit-v1",
            target="examples/b2-baselines/donchian_momentum/package",
            owner="strategy_implementer",
            reviewer="stats_auditor",
            findings=stats_findings,
            evidence=["robustness_report.json", "risk_report.json", "reproduction_report.json"],
            limitations=["synthetic fixture cannot establish market edge"],
        )
        execution_audit = build_audit_report(
            report_id="donchian-execution-audit-v1",
            target="examples/b2-baselines/donchian_momentum/package",
            owner="strategy_implementer",
            reviewer="execution_skeptic",
            findings=[
                {
                    "severity": "P2",
                    "title": "Bar fills do not prove executable liquidity",
                    "evidence": "../../../examples/b2-baselines/donchian_momentum/package/run_receipt.json",
                    "status": "confirmed",
                    "recommendation": "Repeat on archived trades and books with depth, latency, and rejection evidence.",
                    "promotion_impact": "blocks_promotion",
                    "blocks_promotion": True,
                }
            ],
            evidence=["stress_report.json", "reproduction_report.json"],
            limitations=["no venue archive or order-book replay"],
        )

        artifacts = {
            "robustness_report.json": robustness,
            "stress_report.json": {"schema_version": 1, "created_at": "2026-07-10T00:00:00Z", "scenarios": stress},
            "risk_policy.json": policy,
            "risk_report.json": risk_report,
            "stats_audit.json": stats_audit,
            "execution_audit.json": execution_audit,
            "reproduction_report.json": reproduction,
        }
        for name, document in artifacts.items():
            write_json(output / name, document)
        for name, artifact_type in (
            ("robustness_report.json", "robustness_report"),
            ("risk_policy.json", "risk_policy"),
            ("risk_report.json", "risk_report"),
            ("stats_audit.json", "audit_report"),
            ("execution_audit.json", "audit_report"),
        ):
            validation = validate_artifact(output / name, artifact_type=artifact_type)
            if not validation.ok:
                details = "; ".join(f"{issue.path}: {issue.message}" for issue in validation.issues)
                raise RuntimeError(f"generated {name} failed validation: {details}")
        response = {
            "ok": True,
            "status": "complete",
            "artifact_paths": [
                str(output / "robustness_registration.json"),
                *[str(output / name) for name in artifacts],
            ],
            "issues": [],
            "receipt_id": None,
        }
        print(json.dumps(response, indent=2, sort_keys=True) if args.format == "json" else "V3 audit evidence generated")
        return 0
    except Exception as exc:
        response = {"ok": False, "status": "error", "artifact_paths": [], "issues": [{"path": str(output), "message": str(exc)}], "receipt_id": None}
        print(json.dumps(response) if args.format == "json" else f"V3 audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

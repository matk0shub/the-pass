"""Machine-readable framework roadmap validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


EXPECTED_ORDER = ["H0", "R0", "D1", "B2", "V3", "P4", "L5_L6"]
ALLOWED_STATUSES = {"not_started", "in_progress", "blocked", "gate_failed", "complete"}
PUBLIC_BLOCKED_CANDIDATES = {"P4", "L5_L6"}
CAPABILITY_SCOPES = {"framework_capability", "locked_public_boundary"}


class RoadmapValidationError(ValueError):
    """Raised when roadmap state overstates capability or candidate evidence."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RoadmapValidationError(message)


def load_roadmap(path: Path) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise RoadmapValidationError("status document must be an object")
    return document


def validate_roadmap_document(document: dict[str, Any], *, root: Path) -> None:
    root = root.resolve()
    _require(document.get("schema_version") == 1, "schema_version must be 1")
    _require(document.get("order") == EXPECTED_ORDER, f"order must be {EXPECTED_ORDER}")
    _require(
        set(document.get("allowed_statuses", [])) == ALLOWED_STATUSES,
        "allowed_statuses does not match the roadmap contract",
    )
    milestones = document.get("milestones")
    _require(isinstance(milestones, list), "milestones must be an array")
    _require(len(milestones) == len(EXPECTED_ORDER), "milestones must appear once in dependency order")
    by_id = {item.get("id"): item for item in milestones if isinstance(item, dict)}
    _require(list(by_id) == EXPECTED_ORDER, "milestones must appear once in dependency order")

    completed: set[str] = set()
    for milestone_id in EXPECTED_ORDER:
        item = by_id[milestone_id]
        status = item.get("status")
        _require(status in ALLOWED_STATUSES, f"{milestone_id} has invalid status: {status}")
        dependencies = item.get("depends_on")
        _require(
            isinstance(dependencies, list) and all(dep in EXPECTED_ORDER for dep in dependencies),
            f"{milestone_id} has invalid dependencies",
        )
        _require(
            not (status in {"in_progress", "complete"} and any(dep not in completed for dep in dependencies)),
            f"{milestone_id} started before dependencies completed",
        )
        evidence = item.get("evidence")
        _require(isinstance(evidence, list), f"{milestone_id}.evidence must be an array")
        if status != "complete":
            continue

        _require(item.get("gate_result") == "pass", f"{milestone_id} is complete without gate_result: pass")
        _require(bool(evidence), f"{milestone_id} is complete without evidence")
        for relative in evidence:
            _require(
                isinstance(relative, str) and (root / relative).is_file(),
                f"{milestone_id} evidence does not exist: {relative}",
            )
        gate_relative = item.get("gate_evidence")
        _require(
            isinstance(gate_relative, str) and bool(gate_relative),
            f"{milestone_id} is complete without machine-readable gate evidence",
        )
        gate_path = root / gate_relative
        _require(gate_path.is_file(), f"{milestone_id} gate evidence does not exist: {gate_relative}")
        gate = yaml.safe_load(gate_path.read_text(encoding="utf-8"))
        _require(isinstance(gate, dict), f"{milestone_id} gate evidence must be an object")
        _require(
            gate.get("milestone_id") == milestone_id and gate.get("gate_result") == "pass",
            f"{milestone_id} gate evidence is not a pass for the same milestone",
        )
        candidate_state = item.get("candidate_gate_state")
        if candidate_state is not None:
            _require(
                candidate_state in {"blocked", "gate_failed", "pass"},
                f"{milestone_id} has an invalid candidate gate state",
            )
            _require(
                gate.get("candidate_gate_state") == candidate_state,
                f"{milestone_id} capability and candidate gate records disagree",
            )
        if milestone_id in PUBLIC_BLOCKED_CANDIDATES:
            _require(gate.get("scope") in CAPABILITY_SCOPES, f"{milestone_id} gate does not declare its framework scope")
            _require(candidate_state == "blocked", f"{milestone_id} public candidate gate must remain blocked")
        checks = gate.get("acceptance_checks")
        _require(isinstance(checks, list) and bool(checks), f"{milestone_id} gate evidence has no acceptance checks")
        for check in checks:
            _require(
                isinstance(check, dict) and check.get("status") == "pass",
                f"{milestone_id} has a non-passing acceptance check",
            )
            paths = check.get("evidence_paths")
            _require(isinstance(paths, list) and bool(paths), f"{milestone_id} acceptance check has no evidence paths")
            for relative in paths:
                _require(
                    isinstance(relative, str) and (root / relative).is_file(),
                    f"{milestone_id} acceptance evidence does not exist: {relative}",
                )
        _require(gate.get("open_p0_p1") == [], f"{milestone_id} gate has open P0/P1 findings")
        completed.add(milestone_id)


def validate_roadmap_files(*, root: Path, status_path: Path, plan_path: Path) -> None:
    _require(plan_path.is_file(), f"missing execution plan: {plan_path}")
    _require(status_path.is_file(), f"missing roadmap status: {status_path}")
    validate_roadmap_document(load_roadmap(status_path), root=root)

"""Strategy-driven, preregistered train-select-test robustness generation."""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence

from the_pass.data.contracts import CanonicalEvent, stable_fingerprint
from the_pass.strategy_runtime import (
    parse_execution_config,
    parse_strategy_descriptor,
    run_strategy_verified,
)

from .statistics import (
    cscv_pbo,
    deflated_sharpe_ratio,
    effective_sample_size,
    probabilistic_sharpe_ratio_effective,
    purged_walk_forward_splits,
    reality_check,
    select_train_winner,
)


def _persist_registration(path: Path, registration: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(
            registration,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise FileExistsError(
            f"robustness registration is create-only and already exists: {path}"
        ) from exc


def _periodic_returns(
    result: Mapping[str, Any], *, initial_cash: Decimal
) -> tuple[float, list[float]]:
    values = [initial_cash]
    for row in result.get("equity", []):
        if isinstance(row, Mapping) and "equity" in row:
            values.append(Decimal(str(row["equity"])))
    final_equity = Decimal(str(result["final_portfolio"]["equity"]))
    if values[-1] != final_equity:
        values.append(final_equity)
    periodic = [
        float(current / previous - Decimal(1))
        for previous, current in zip(values, values[1:])
        if previous != 0
    ]
    if not periodic:
        periodic = [float(final_equity / initial_cash - Decimal(1))]
    if any(not math.isfinite(value) for value in periodic):
        raise ValueError("strategy result contains non-finite periodic returns")
    return float(final_equity / initial_cash - Decimal(1)), periodic


def _run_cell(
    rows: Sequence[CanonicalEvent],
    *,
    fold_id: int,
    phase: str,
    variant_index: int,
    variant: Mapping[str, Any],
    descriptor: Mapping[str, Any],
    execution: Mapping[str, Any],
    initial_cash: Decimal,
    workspace_root: Path,
    timeout_seconds: float,
    runtime_mode: str,
    sandbox_launcher: Path | None,
    sandbox_policy: Path | None,
) -> dict[str, Any]:
    candidate = dict(descriptor)
    candidate["config"] = {
        **dict(descriptor.get("config", {})),
        **dict(variant),
    }
    try:
        result = run_strategy_verified(
            rows,
            descriptor=candidate,
            execution=execution,
            workspace_root=workspace_root,
            timeout_seconds=timeout_seconds,
            runtime_mode=runtime_mode,
            sandbox_launcher=sandbox_launcher,
            sandbox_policy=sandbox_policy,
        )
        net_return, periodic_returns = _periodic_returns(
            result, initial_cash=initial_cash
        )
        return {
            "fold_id": fold_id,
            "phase": phase,
            "variant_index": variant_index,
            "status": "complete",
            "net_return": net_return,
            "periodic_returns": periodic_returns,
            "result_fingerprint": result["result_fingerprint"],
            "runtime_promotion_eligible": result["runtime_promotion_eligible"],
            "execution_schema_version": int(execution["schema_version"]),
        }
    except Exception as exc:
        return {
            "fold_id": fold_id,
            "phase": phase,
            "variant_index": variant_index,
            "status": "failed",
            "net_return": None,
            "periodic_returns": [],
            "result_fingerprint": None,
            "runtime_promotion_eligible": False,
            "execution_schema_version": int(execution["schema_version"]),
            "error_type": type(exc).__name__,
        }


def _normalized_folds(
    rows: Sequence[CanonicalEvent],
    *,
    splits: Sequence[Mapping[str, int]] | None,
    train_size: int | None,
    test_size: int | None,
    purge: int,
    embargo: int,
) -> tuple[str, list[dict[str, Any]]]:
    folds: list[dict[str, Any]] = []
    if train_size is not None or test_size is not None:
        if splits is not None:
            raise ValueError("use explicit splits or generated walk-forward, not both")
        if train_size is None or test_size is None:
            raise ValueError("walk-forward requires both train_size and test_size")
        generated = purged_walk_forward_splits(
            len(rows),
            train_size=train_size,
            test_size=test_size,
            purge=purge,
            embargo=embargo,
            anchored=True,
        )
        for index, fold in enumerate(generated):
            folds.append(
                {
                    "id": index,
                    "train_start": fold.train[0],
                    "train_end": fold.train[-1] + 1,
                    "test_start": fold.test[0],
                    "test_end": fold.test[-1] + 1,
                    "purged": list(fold.purged),
                    "embargoed": list(fold.embargoed),
                }
            )
        return "purged_walk_forward", folds

    if splits is None:
        raise ValueError("diagnostic sweep requires splits")
    previous_end = 0
    for index, split in enumerate(splits):
        if set(split) != {"start", "end"}:
            raise ValueError("each split must contain only start and end indexes")
        start, end = int(split["start"]), int(split["end"])
        if (
            start < previous_end
            or start < 2
            or end <= start
            or end > len(rows)
        ):
            raise ValueError(
                "diagnostic splits require at least two train rows and ordered non-overlapping tests"
            )
        folds.append(
            {
                "id": index,
                "train_start": 0,
                "train_end": start,
                "test_start": start,
                "test_end": end,
                "purged": [],
                "embargoed": [],
            }
        )
        previous_end = end
    return "diagnostic_splits", folds


def run_strategy_sweep(
    events: Sequence[CanonicalEvent],
    *,
    descriptor: Mapping[str, Any],
    execution: Mapping[str, Any],
    variants: Sequence[Mapping[str, Any]],
    splits: Sequence[Mapping[str, int]] | None,
    selected_index: int,
    registration_path: Path,
    workspace_root: Path,
    timeout_seconds: float = 60.0,
    source_package_id: str | None = None,
    created_at: str | None = None,
    train_size: int | None = None,
    test_size: int | None = None,
    purge: int = 0,
    embargo: int = 0,
    null_variant_index: int | None = None,
    stress_results: Sequence[Mapping[str, Any]] = (),
    runtime_mode: str = "trusted_local",
    sandbox_launcher: Path | None = None,
    sandbox_policy: Path | None = None,
) -> dict[str, Any]:
    """Execute all train/test cells and select each fold only from train evidence."""

    rows = sorted(events, key=CanonicalEvent.sort_key)
    if len(variants) < 2:
        raise ValueError(
            "train-select-test robustness requires at least one candidate and one null variant"
        )
    if not 0 <= selected_index < len(variants):
        raise ValueError("selected_index is outside the preregistered variants")
    if null_variant_index is None:
        null_variant_index = len(variants) - 1
    if not 0 <= null_variant_index < len(variants):
        raise ValueError("null_variant_index is outside the preregistered variants")
    if null_variant_index == selected_index:
        raise ValueError("reference variant must differ from the null baseline")

    validation_mode, folds = _normalized_folds(
        rows,
        splits=splits,
        train_size=train_size,
        test_size=test_size,
        purge=purge,
        embargo=embargo,
    )
    if len(folds) < 4:
        raise ValueError("robustness sweep requires at least four folds")

    parsed_descriptor = parse_strategy_descriptor(
        descriptor, workspace_root=workspace_root
    )
    parsed_execution = parse_execution_config(execution)
    registration_core = {
        "schema_version": 3,
        "descriptor_fingerprint": parsed_descriptor.descriptor_fingerprint,
        "strategy_source_sha256": parsed_descriptor.source_sha256,
        "execution_fingerprint": parsed_execution.fingerprint,
        "events_fingerprint": stable_fingerprint(
            [event.as_dict() for event in rows]
        ),
        "variants": [dict(variant) for variant in variants],
        "reference_variant_index": selected_index,
        "null_variant_index": null_variant_index,
        "selection_metric": "net_return",
        "tie_break": "lowest_variant_index",
        "selection_policy": "select each fold only from complete train-cell net returns",
    }
    registration = {
        **registration_core,
        "registration_fingerprint": stable_fingerprint(registration_core),
    }
    _persist_registration(registration_path, registration)

    initial_cash = Decimal(str(execution["initial_cash"]))
    cells: list[dict[str, Any]] = []
    fold_results: list[dict[str, Any]] = []
    variant_oos_returns: list[list[float]] = [
        [] for _variant in variants
    ]
    selected_oos_returns: list[float] = []
    null_oos_returns: list[float] = []
    neighbor_test_returns: list[float] = []
    alignment_failed = False

    for fold in folds:
        train_rows = rows[fold["train_start"] : fold["train_end"]]
        test_rows = rows[fold["test_start"] : fold["test_end"]]
        train_cells = [
            _run_cell(
                train_rows,
                fold_id=fold["id"],
                phase="train",
                variant_index=index,
                variant=variant,
                descriptor=descriptor,
                execution=execution,
                initial_cash=initial_cash,
                workspace_root=workspace_root,
                timeout_seconds=timeout_seconds,
                runtime_mode=runtime_mode,
                sandbox_launcher=sandbox_launcher,
                sandbox_policy=sandbox_policy,
            )
            for index, variant in enumerate(variants)
        ]
        test_cells = [
            _run_cell(
                test_rows,
                fold_id=fold["id"],
                phase="test",
                variant_index=index,
                variant=variant,
                descriptor=descriptor,
                execution=execution,
                initial_cash=initial_cash,
                workspace_root=workspace_root,
                timeout_seconds=timeout_seconds,
                runtime_mode=runtime_mode,
                sandbox_launcher=sandbox_launcher,
                sandbox_policy=sandbox_policy,
            )
            for index, variant in enumerate(variants)
        ]
        cells.extend(train_cells)
        cells.extend(test_cells)
        if any(cell["status"] != "complete" for cell in train_cells):
            selected_variant = None
        else:
            selected_variant = select_train_winner(
                [float(cell["net_return"]) for cell in train_cells],
                excluded_indices=(null_variant_index,),
            )

        selected_test_return = None
        selected_train_score = None
        if selected_variant is not None:
            selected_train_score = train_cells[selected_variant]["net_return"]
            selected_test = test_cells[selected_variant]
            if selected_test["status"] == "complete":
                selected_test_return = selected_test["net_return"]
                selected_oos_returns.extend(selected_test["periodic_returns"])
                null_oos_returns.extend(
                    test_cells[null_variant_index]["periodic_returns"]
                )
                fold_neighbors = []
                for neighbor in (
                    selected_variant - 1,
                    selected_variant + 1,
                ):
                    if (
                        0 <= neighbor < len(variants)
                        and neighbor != null_variant_index
                        and test_cells[neighbor]["status"] == "complete"
                    ):
                        fold_neighbors.append(
                            float(test_cells[neighbor]["net_return"])
                        )
                if fold_neighbors:
                    neighbor_test_returns.append(min(fold_neighbors))

        lengths = {
            len(cell["periodic_returns"])
            for cell in test_cells
            if cell["status"] == "complete"
        }
        if (
            len(lengths) != 1
            or any(cell["status"] != "complete" for cell in test_cells)
        ):
            alignment_failed = True
        else:
            for index, cell in enumerate(test_cells):
                variant_oos_returns[index].extend(cell["periodic_returns"])

        fold_results.append(
            {
                "fold_id": fold["id"],
                "selected_variant_index": selected_variant,
                "selected_train_score": selected_train_score,
                "selected_test_return": selected_test_return,
            }
        )

    failed = [cell for cell in cells if cell["status"] == "failed"]
    complete_statistics = (
        not failed
        and not alignment_failed
        and len(selected_oos_returns) >= 4
        and len({len(values) for values in variant_oos_returns}) == 1
    )
    sample = {
        "observations": float(len(selected_oos_returns)),
        "lag1_autocorrelation": 0.0,
        "effective_observations": 0.0,
    }
    statistics: dict[str, Any] = {
        "pbo": {
            "pbo": 1.0,
            "combinations": 1,
            "logits": [],
            "selected_variants": [],
        },
        "psr": 0.0,
        "dsr": 0.0,
        "reality_check": {
            "reality_check_pvalue": 1.0,
            "spa_pvalue": 1.0,
        },
    }
    oos_matrix: list[list[float]] = []
    if complete_statistics:
        sample = effective_sample_size(selected_oos_returns)
        oos_matrix = [
            [variant_oos_returns[column][row] for column in range(len(variants))]
            for row in range(len(selected_oos_returns))
        ]
        trial_sharpes = []
        for values in variant_oos_returns:
            average = sum(values) / len(values)
            variance = sum((value - average) ** 2 for value in values) / max(
                1, len(values) - 1
            )
            trial_sharpes.append(
                average / variance**0.5 if variance else 0.0
            )
        blocks = min(8, len(oos_matrix))
        blocks -= blocks % 2
        statistics = {
            "pbo": cscv_pbo(oos_matrix, blocks=blocks),
            "psr": probabilistic_sharpe_ratio_effective(
                selected_oos_returns,
                effective_observations=sample["effective_observations"],
            ),
            "dsr": deflated_sharpe_ratio(
                selected_oos_returns,
                trial_sharpes=trial_sharpes,
                effective_observations=sample["effective_observations"],
            ),
            "reality_check": reality_check(
                oos_matrix,
                bootstrap_samples=500,
                seed=7,
            ),
        }

    selected_mean = (
        sum(selected_oos_returns) / len(selected_oos_returns)
        if selected_oos_returns
        else 0.0
    )
    baseline_mean = (
        sum(null_oos_returns) / len(null_oos_returns)
        if null_oos_returns
        else 0.0
    )
    worst_neighbor = (
        min(neighbor_test_returns) if neighbor_test_returns else None
    )
    null_status = (
        "pass"
        if complete_statistics and selected_mean > baseline_mean
        else "blocked"
    )
    stability_status = (
        "pass"
        if complete_statistics
        and len(neighbor_test_returns) == len(folds)
        and worst_neighbor is not None
        and worst_neighbor > 0
        else "blocked"
    )
    normalized_stress = [
        {
            "scenario": str(row["scenario"]),
            "status": str(row["status"]),
            "net_pnl": float(row["net_pnl"]),
            "summary": str(row["summary"]),
        }
        for row in stress_results
    ]
    all_runtime_promotional = not failed and all(
        cell["runtime_promotion_eligible"] for cell in cells
    )
    promotion_eligible = (
        validation_mode == "purged_walk_forward"
        and complete_statistics
        and sample["effective_observations"] >= 30
        and parsed_execution.schema_version == 2
        and null_status == "pass"
        and stability_status == "pass"
        and bool(normalized_stress)
        and all(row["status"] == "pass" for row in normalized_stress)
        and all_runtime_promotional
    )
    first_holdout = rows[folds[0]["test_start"]]
    last_holdout = rows[folds[-1]["test_end"] - 1]

    def timestamp(value: int) -> str:
        return (
            datetime.fromtimestamp(
                value / 1_000_000_000, tz=timezone.utc
            )
            .isoformat()
            .replace("+00:00", "Z")
        )

    report = {
        "schema_version": 3,
        "id": f"robustness-{parsed_descriptor.strategy_id}",
        "created_at": created_at or timestamp(rows[-1].receive_time_ns),
        "source_package_id": source_package_id,
        "registration": registration,
        "status": "blocked" if failed or alignment_failed else "complete",
        "cells": cells,
        "fold_results": fold_results,
        "failed_cells": len(failed) + int(alignment_failed),
        "oos_matrix": oos_matrix,
        "selected_oos_returns": selected_oos_returns,
        "sample": sample,
        "statistics": statistics,
        "validation": {
            "mode": validation_mode,
            "purge_observations": purge,
            "embargo_observations": embargo,
            "cscv_blocks": (
                min(8, len(oos_matrix)) - min(8, len(oos_matrix)) % 2
                if oos_matrix
                else 4
            ),
            "holdout_start_time": timestamp(first_holdout.event_time_ns),
            "holdout_end_time": timestamp(last_holdout.event_time_ns + 1),
            "folds": folds,
        },
        "null_baseline": {
            "variant_index": null_variant_index,
            "status": null_status,
            "selected_mean_return": selected_mean,
            "baseline_mean_return": baseline_mean,
            "summary": (
                "train-selected OOS returns exceed the preregistered aligned null"
                if null_status == "pass"
                else "train-selected OOS returns do not exceed the aligned null"
            ),
        },
        "stress_results": normalized_stress,
        "parameter_stability": {
            "status": stability_status,
            "neighbor_indices": sorted(
                {
                    neighbor
                    for fold in fold_results
                    if fold["selected_variant_index"] is not None
                    for neighbor in (
                        fold["selected_variant_index"] - 1,
                        fold["selected_variant_index"] + 1,
                    )
                    if 0 <= neighbor < len(variants)
                    and neighbor != null_variant_index
                }
            ),
            "worst_neighbor_return": worst_neighbor,
            "summary": (
                "every train-selected configuration has a positive OOS neighbor"
                if stability_status == "pass"
                else "train-selected configurations lack positive aligned OOS neighbors"
            ),
        },
        "promotion_eligible": promotion_eligible,
    }
    report["report_fingerprint"] = stable_fingerprint(report)
    return report

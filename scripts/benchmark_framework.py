#!/usr/bin/env python3
"""Deterministic framework throughput and memory benchmark."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import platform
import sys
import tempfile
import time
import tracemalloc
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from the_pass.data.contracts import CanonicalEvent, EventType  # noqa: E402
from the_pass.data.features import build_bar_features  # noqa: E402
from the_pass.data.quality import QualityPolicy, build_quality_report  # noqa: E402
from the_pass.data.storage import ImmutableParquetStore  # noqa: E402
from the_pass.engine.baselines import BuyAndHoldBaseline  # noqa: E402
from the_pass.engine.costs import LinearCostModel  # noqa: E402
from the_pass.engine.fills import BarFillModel  # noqa: E402
from the_pass.engine.simulator import EventSimulator  # noqa: E402
from the_pass.ledger import verify_ledger_file  # noqa: E402
from the_pass.reporting import build_static_dashboard  # noqa: E402


def timed(operation: Callable[[], Any]) -> tuple[Any, float]:
    started = time.perf_counter()
    value = operation()
    return value, time.perf_counter() - started


def generate_events(count: int) -> list[CanonicalEvent]:
    start = 1_704_067_200_000_000_000
    interval = 60_000_000_000
    rows = []
    for index in range(count):
        close = Decimal("100") + Decimal(index % 1000) / Decimal("100")
        timestamp = start + index * interval
        rows.append(
            CanonicalEvent.from_raw(
                raw={"index": index, "close": format(close, "f")},
                source="benchmark",
                venue="synthetic",
                asset_class="crypto_spot",
                instrument_id="BENCHMARK",
                event_type=EventType.BAR,
                event_time_ns=timestamp,
                receive_time_ns=timestamp + 1_000_000,
                ingest_id=f"benchmark-{index:09d}",
                sequence=index,
                payload={
                    "open": close,
                    "high": close + Decimal("0.01"),
                    "low": close - Decimal("0.01"),
                    "close": close,
                    "volume": Decimal("1"),
                },
            )
        )
    return rows


def event_fingerprint(events: list[CanonicalEvent]) -> str:
    digest = hashlib.sha256()
    for event in events:
        digest.update(event.raw_fingerprint.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def benchmark_size(count: int) -> dict[str, Any]:
    gc.collect()
    tracemalloc.start()
    events, generation_seconds = timed(lambda: generate_events(count))
    fingerprint = event_fingerprint(events)
    _, sort_seconds = timed(lambda: sorted(reversed(events), key=CanonicalEvent.sort_key))
    quality, quality_seconds = timed(
        lambda: build_quality_report(
            f"benchmark-{count}",
            events,
            policy=QualityPolicy(expected_interval_ns=60_000_000_000),
            created_at="2026-07-10T00:00:00Z",
        )
    )
    features, feature_seconds = timed(
        lambda: build_bar_features(
            events,
            dataset_fingerprint=fingerprint,
            code_version="benchmark-v1",
            config={"features": ["close", "return_1"]},
            created_at="2026-07-10T00:00:00Z",
        )
    )
    if quality["promotion_impact"] == "blocked" or features.manifest["rows"] != count:
        raise RuntimeError("benchmark fixture failed deterministic data contracts")
    del features
    gc.collect()
    simulator = EventSimulator(
        fill_model=BarFillModel(Decimal("5")),
        cost_model=LinearCostModel(Decimal("0.001")),
    )
    result, replay_seconds = timed(lambda: simulator.run(BuyAndHoldBaseline(), events))
    if result.events_processed != count:
        raise RuntimeError("benchmark replay did not process every event")
    del result
    gc.collect()
    with tempfile.TemporaryDirectory() as tmp:
        store = ImmutableParquetStore(Path(tmp))
        partition, parquet_seconds = timed(
            lambda: store.commit(
                events,
                source="benchmark",
                venue="synthetic",
                instrument="BENCHMARK",
                date="2024-01-01",
            )
        )
        parquet_bytes = (partition[0] / "events.parquet").stat().st_size
    _current, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "events": count,
        "input_fingerprint": fingerprint,
        "peak_python_bytes": peak_bytes,
        "parquet_bytes": parquet_bytes,
        "seconds": {
            "generation": generation_seconds,
            "deterministic_sort": sort_seconds,
            "quality": quality_seconds,
            "features": feature_seconds,
            "replay": replay_seconds,
            "parquet_commit": parquet_seconds,
        },
    }


def version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[10_000])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if any(size < 2 for size in args.sizes):
        raise ValueError("benchmark sizes must be at least two")
    results = [benchmark_size(size) for size in args.sizes]
    with tempfile.TemporaryDirectory() as tmp:
        _, dashboard_seconds = timed(lambda: build_static_dashboard(ROOT, Path(tmp) / "dashboard"))
    ledger = ROOT / "examples" / "b2-baselines" / "buy_hold" / "package" / "receipt-ledger.jsonl"
    ledger_issues, ledger_seconds = timed(lambda: verify_ledger_file(ledger))
    if ledger_issues:
        raise RuntimeError("benchmark ledger fixture does not verify")
    report = {
        "schema_version": 1,
        "created_at": "2026-07-10T00:00:00Z",
        "purpose": "framework performance regression evidence; not strategy performance",
        "machine": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python": platform.python_version(),
        },
        "dependencies": {name: version(name) for name in ("duckdb", "numpy", "pandas", "pyarrow", "scipy")},
        "results": results,
        "fixed_operations_seconds": {"dashboard_build": dashboard_seconds, "ledger_verify": ledger_seconds},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"framework benchmark written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

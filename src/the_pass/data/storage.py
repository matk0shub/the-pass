"""Immutable atomic Parquet storage for canonical market events."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from .contracts import CanonicalEvent, canonical_json_bytes, canonical_value


SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9._=-]+$")


class StorageDependencyError(RuntimeError):
    pass


class PartitionExistsError(RuntimeError):
    pass


def _segment(value: str) -> str:
    if not SAFE_SEGMENT.fullmatch(value) or value in {".", ".."}:
        raise ValueError(f"unsafe partition segment: {value!r}")
    return value


def _arrow_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    number = value if isinstance(value, Decimal) else Decimal(str(value))
    if not number.is_finite() or number.as_tuple().exponent < -18:
        raise ValueError("Arrow decimal values must be finite with at most 18 fractional digits")
    return number


class ImmutableParquetStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def partition_path(self, *, source: str, venue: str, instrument: str, date: str) -> Path:
        return self.root / _segment(source) / _segment(venue) / _segment(instrument) / _segment(date)

    def commit(
        self,
        events: Iterable[CanonicalEvent],
        *,
        source: str,
        venue: str,
        instrument: str,
        date: str,
    ) -> tuple[Path, str]:
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise StorageDependencyError("Parquet storage requires the 'data' extra") from exc

        ordered = sorted(events, key=CanonicalEvent.sort_key)
        if not ordered:
            raise ValueError("cannot commit an empty partition")
        for event in ordered:
            if event.source != source or event.venue != venue or event.instrument_id != instrument:
                raise ValueError("every event must match the target partition")

        final_path = self.partition_path(source=source, venue=venue, instrument=instrument, date=date)
        if final_path.exists():
            raise PartitionExistsError(f"partition already exists: {final_path}")
        final_path.parent.mkdir(parents=True, exist_ok=True)
        staging = final_path.parent / f".{final_path.name}.staging-{uuid.uuid4().hex}"
        staging.mkdir()
        writer = None
        try:
            data_path = staging / "events.parquet"
            fingerprint_digest = hashlib.sha256()
            fingerprint_digest.update(b"[")
            first = True
            for start in range(0, len(ordered), 10_000):
                rows = [event.as_dict() for event in ordered[start : start + 10_000]]
                for row in rows:
                    if not first:
                        fingerprint_digest.update(b",")
                    fingerprint_digest.update(canonical_json_bytes(row))
                    first = False
                payload_json = [
                    json.dumps(canonical_value(row["payload"]), sort_keys=True, separators=(",", ":"))
                    for row in rows
                ]
                table = pa.table(
                    {
                        "schema_version": pa.array([2] * len(rows), type=pa.int16()),
                        "source": [row["source"] for row in rows],
                        "venue": [row["venue"] for row in rows],
                        "asset_class": [row["asset_class"] for row in rows],
                        "instrument_id": [row["instrument_id"] for row in rows],
                        "event_type": [row["event_type"] for row in rows],
                        "event_time_ns": pa.array(
                            [row["event_time_ns"] for row in rows], type=pa.timestamp("ns", tz="UTC")
                        ),
                        "receive_time_ns": pa.array(
                            [row["receive_time_ns"] for row in rows], type=pa.timestamp("ns", tz="UTC")
                        ),
                        "sequence": pa.array([row["sequence"] for row in rows], type=pa.int64()),
                        "ingest_id": [row["ingest_id"] for row in rows],
                        "raw_fingerprint": [row["raw_fingerprint"] for row in rows],
                        "price": pa.array(
                            [_arrow_decimal(row["payload"].get("price")) for row in rows],
                            type=pa.decimal128(38, 18),
                        ),
                        "size": pa.array(
                            [_arrow_decimal(row["payload"].get("size")) for row in rows],
                            type=pa.decimal128(38, 18),
                        ),
                        "payload_json": payload_json,
                    }
                )
                if writer is None:
                    writer = pq.ParquetWriter(data_path, table.schema, compression="zstd", use_dictionary=True)
                writer.write_table(table)
            if writer is not None:
                writer.close()
                writer = None
            fingerprint_digest.update(b"]")
            fingerprint = fingerprint_digest.hexdigest()
            (staging / "fingerprint.sha256").write_text(fingerprint + "\n", encoding="ascii")
            try:
                os.rename(staging, final_path)
            except FileExistsError as exc:
                raise PartitionExistsError(f"partition already exists: {final_path}") from exc
            return final_path, fingerprint
        except Exception:
            try:
                if writer is not None:
                    writer.close()
            finally:
                shutil.rmtree(staging, ignore_errors=True)
            raise

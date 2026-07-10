#!/usr/bin/env python3
"""Opt-in link and recency check that never mutates research source status."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml


ROOT = Path(__file__).resolve().parents[1]


def now_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def check(row: dict[str, Any]) -> dict[str, Any]:
    url = row.get("url")
    if not isinstance(url, str) or not url:
        return {"id": row.get("id"), "status": "no_url", "url": url}
    try:
        with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": "the-pass-link-audit/0.7"}) as client:
            response = client.head(url)
            if response.status_code in {405, 501}:
                with client.stream("GET", url, headers={"Range": "bytes=0-0"}) as streamed:
                    status_code = streamed.status_code
                    final_url = str(streamed.url)
            else:
                status_code = response.status_code
                final_url = str(response.url)
        status = "reachable" if status_code < 500 else "provider_error"
        return {"id": row.get("id"), "status": status, "url": url, "final_url": final_url, "status_code": status_code}
    except Exception as exc:
        return {"id": row.get("id"), "status": "network_error", "url": url, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="Required explicit opt-in for HTTP requests.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    if not args.network:
        print("research link check requires --network", file=sys.stderr)
        return 3
    registry = yaml.safe_load((ROOT / "research" / "sources.yaml").read_text(encoding="utf-8"))
    index_rows = registry.get("sources", []) if isinstance(registry, dict) else []
    rows = []
    for row in index_rows:
        if not isinstance(row, dict):
            continue
        note_path = row.get("path")
        note = {}
        if isinstance(note_path, str) and (ROOT / note_path).is_file():
            loaded = yaml.safe_load((ROOT / note_path).read_text(encoding="utf-8"))
            note = loaded if isinstance(loaded, dict) else {}
        rows.append({**row, "url": note.get("url")})
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        results = list(executor.map(check, rows))
    report = {
        "schema_version": 1,
        "created_at": now_rfc3339(),
        "network_opt_in": True,
        "registry_mutated": False,
        "sources": results,
        "summary": {
            "total": len(results),
            "reachable": sum(row["status"] == "reachable" for row in results),
            "restricted_or_missing_url": sum(row["status"] in {"no_url"} or row.get("status_code") in {401, 403} for row in results),
            "errors": sum(row["status"] in {"provider_error", "network_error"} for row in results),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"research link report written: {args.output}")
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

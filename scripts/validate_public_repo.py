#!/usr/bin/env python3
"""Validate the public-safe The Pass repository scaffold."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TODO_MARKER = "[" + "TODO:"

FORBIDDEN_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".venv"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def validate_json(path: Path) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def validate_plugin_manifest() -> None:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    if not manifest_path.exists():
        fail("missing .codex-plugin/plugin.json")
    validate_json(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("name") != "the-pass":
        fail("plugin name must be the-pass")
    if manifest.get("skills") != "./skills/":
        fail("plugin must point skills to ./skills/")
    interface = manifest.get("interface") or {}
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if not interface.get(field):
            fail(f"plugin interface missing {field}")


def validate_skills() -> None:
    skills_dir = ROOT / "skills"
    expected = {
        "mise",
        "research",
        "spec",
        "screen",
        "backtest",
        "taste",
        "refire",
        "simmer",
        "paper",
        "plate",
        "receipts",
    }
    present = {path.name for path in skills_dir.iterdir() if path.is_dir()}
    missing = expected - present
    if missing:
        fail(f"missing skills: {', '.join(sorted(missing))}")
    for name in sorted(expected):
        skill_path = skills_dir / name / "SKILL.md"
        if not skill_path.exists():
            fail(f"missing {skill_path.relative_to(ROOT)}")
        text = skill_path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            fail(f"{skill_path.relative_to(ROOT)} missing front matter")
        if f'name: "the-pass:{name}"' not in text and f"name: the-pass:{name}" not in text:
            fail(f"{skill_path.relative_to(ROOT)} has wrong skill name")


def validate_schemas() -> None:
    required = {
        "source_note.schema.json",
        "strategy_spec.schema.json",
        "data_manifest.schema.json",
        "run_receipt.schema.json",
        "metrics_report.schema.json",
        "cost_waterfall.schema.json",
        "verdict_report.schema.json",
    }
    schemas_dir = ROOT / "schemas"
    present = {path.name for path in schemas_dir.glob("*.json")}
    missing = required - present
    if missing:
        fail(f"missing schemas: {', '.join(sorted(missing))}")
    for path in schemas_dir.glob("*.json"):
        validate_json(path)


def validate_public_safety() -> None:
    for path in iter_files():
        if path.stat().st_size > 1_000_000:
            fail(f"unexpected large tracked-style file: {path.relative_to(ROOT)}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if TODO_MARKER in text:
            fail(f"leftover scaffold placeholder in {path.relative_to(ROOT)}")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                fail(f"secret-like pattern in {path.relative_to(ROOT)}")


def main() -> int:
    for path in iter_files():
        if path.suffix == ".json":
            validate_json(path)
    validate_plugin_manifest()
    validate_skills()
    validate_schemas()
    validate_public_safety()
    print("public repo validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

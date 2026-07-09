#!/usr/bin/env python3
"""Validate the public-safe The Pass repository scaffold."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER_MARKER = "[" + "TO" + "DO:"

FORBIDDEN_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "venv",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if any(part.endswith(".egg-info") for part in path.parts):
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


def validate_python_package() -> None:
    pyproject_path = ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        fail("missing pyproject.toml")
    cli_path = ROOT / "src" / "the_pass" / "cli.py"
    validator_path = ROOT / "src" / "the_pass" / "validator.py"
    if not cli_path.exists():
        fail("missing src/the_pass/cli.py")
    if not validator_path.exists():
        fail("missing src/the_pass/validator.py")


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
        "adapter.schema.json",
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


def validate_example_package() -> None:
    package_dir = ROOT / "examples" / "synthetic-breakout" / "package"
    required = {
        "adapter.json",
        "source_note.json",
        "strategy_spec.json",
        "data_manifest.json",
        "run_receipt.json",
        "metrics_report.json",
        "cost_waterfall.json",
        "verdict_report.json",
    }
    if not package_dir.exists():
        fail("missing examples/synthetic-breakout/package")
    present = {path.name for path in package_dir.glob("*.json")}
    missing = required - present
    if missing:
        fail(f"synthetic example missing artifacts: {', '.join(sorted(missing))}")
    for name in sorted(required):
        validate_json(package_dir / name)

    adapter = json.loads((package_dir / "adapter.json").read_text(encoding="utf-8"))
    if adapter.get("mode") != "diagnostic":
        fail("synthetic example adapter must stay diagnostic")
    adapter_safety = adapter.get("safety") or {}
    for field in ("live_trading_enabled", "real_order_path_available", "credentials_required"):
        if adapter_safety.get(field) is not False:
            fail(f"synthetic adapter safety.{field} must be false")

    receipt = json.loads((package_dir / "run_receipt.json").read_text(encoding="utf-8"))
    receipt_safety = receipt.get("safety") or {}
    for field in ("live_trading_enabled", "real_order_path_available", "credentials_available"):
        if receipt_safety.get(field) is not False:
            fail(f"synthetic run receipt safety.{field} must be false")

    verdict = json.loads((package_dir / "verdict_report.json").read_text(encoding="utf-8"))
    if verdict.get("verdict") != "blocked":
        fail("synthetic example verdict must stay blocked")


def validate_markdown_links() -> None:
    for path in iter_files():
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (path.parent / target_path).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                fail(f"markdown link escapes repo in {path.relative_to(ROOT)}: {target}")
            if not resolved.exists():
                fail(f"broken markdown link in {path.relative_to(ROOT)}: {target}")


def validate_public_safety() -> None:
    for path in iter_files():
        if path.stat().st_size > 1_000_000:
            fail(f"unexpected large tracked-style file: {path.relative_to(ROOT)}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if PLACEHOLDER_MARKER in text:
            fail(f"leftover scaffold placeholder in {path.relative_to(ROOT)}")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                fail(f"secret-like pattern in {path.relative_to(ROOT)}")


def main() -> int:
    for path in iter_files():
        if path.suffix == ".json":
            validate_json(path)
    validate_plugin_manifest()
    validate_python_package()
    validate_skills()
    validate_schemas()
    validate_example_package()
    validate_markdown_links()
    validate_public_safety()
    print("public repo validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

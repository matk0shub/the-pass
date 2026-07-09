"""Command line interface for The Pass."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .validator import ARTIFACT_TYPES, ValidationResult, validate_artifact, validate_package


def print_result(result: ValidationResult, *, output_format: str, success_message: str) -> None:
    if output_format == "json":
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
        return

    if result.ok:
        print(success_message)
        return

    print("validation failed", file=sys.stderr)
    for issue in result.issues:
        print(f"- {issue.path}: {issue.message}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="the-pass", description="Validate The Pass artifacts and packages.")
    parser.add_argument("--version", action="version", version=f"the-pass {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate one artifact.")
    validate_parser.add_argument("artifact", type=Path, help="Artifact path, JSON or YAML.")
    validate_parser.add_argument(
        "--type",
        choices=sorted(ARTIFACT_TYPES),
        help="Artifact type. If omitted, inferred from filename or fields.",
    )
    validate_parser.add_argument("--schema-dir", type=Path, help="Override schema directory.")
    validate_parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")

    package_parser = subparsers.add_parser("validate-package", help="Validate a run package directory.")
    package_parser.add_argument("package", type=Path, help="Package directory.")
    package_parser.add_argument("--schema-dir", type=Path, help="Override schema directory.")
    package_parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        result = validate_artifact(args.artifact, schema_dir=args.schema_dir, artifact_type=args.type)
        artifact_type = result.artifact_type or "artifact"
        print_result(
            result,
            output_format=args.format,
            success_message=f"{args.artifact} validates as {artifact_type}",
        )
        return 0 if result.ok else 1

    if args.command == "validate-package":
        result = validate_package(args.package, schema_dir=args.schema_dir)
        print_result(
            result,
            output_format=args.format,
            success_message=f"{args.package} package validates",
        )
        return 0 if result.ok else 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

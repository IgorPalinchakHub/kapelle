#!/usr/bin/env python3
"""Write current, fingerprinted feature-verification evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from feature_state import (
    FeatureStateError,
    _project_root,
    atomic_write_json,
    file_fingerprint,
    input_fingerprints,
    refresh_feature_status,
    resolve_feature_dir,
    schema_errors,
)


def implementation_fingerprints(
    feature_dir: Path, relative_paths: list[str]
) -> dict[str, str]:
    root = _project_root(feature_dir).resolve()
    fingerprints: dict[str, str] = {}
    for raw_path in relative_paths:
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise FeatureStateError(
                f"implementation path must stay inside the project: {raw_path}"
            )
        path = (root / relative).resolve()
        try:
            normalized = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise FeatureStateError(
                f"implementation path escapes the project: {raw_path}"
            ) from exc
        if not path.is_file():
            raise FeatureStateError(
                f"implementation file is missing or not a file: {raw_path}"
            )
        fingerprints[normalized] = file_fingerprint(path)
    if not fingerprints:
        raise FeatureStateError("at least one implementation file is required")
    return dict(sorted(fingerprints.items()))


def build_verification(
    feature_dir: Path,
    *,
    status: str,
    evidence_source: str,
    categories: list[str],
    checks: list[str],
    implementation_files: list[str],
    developer_confirmation: str | None,
) -> dict[str, object]:
    confirmation = (developer_confirmation or "").strip()
    if evidence_source in {"developer-attested", "mixed"} and not confirmation:
        raise FeatureStateError(
            "developer-attested verification requires an explicit confirmation"
        )
    payload: dict[str, object] = {
        "status": status,
        "evidence_source": evidence_source,
        "categories": list(dict.fromkeys(categories)),
        # Compatibility field: entries are exact executed commands or concise manual checks.
        "commands": list(dict.fromkeys(checks)),
        "input_fingerprints": input_fingerprints(feature_dir),
        "implementation_fingerprints": implementation_fingerprints(
            feature_dir, implementation_files
        ),
    }
    if confirmation:
        payload["developer_confirmation"] = confirmation
    errors = schema_errors(payload, "verification.schema.json")
    if errors:
        raise FeatureStateError(
            "verification evidence is invalid: " + "; ".join(errors)
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record agent-observed or developer-attested feature verification"
    )
    parser.add_argument("feature_dir")
    parser.add_argument(
        "--status",
        required=True,
        choices=["PASS", "FAILED", "validation-deferred"],
    )
    parser.add_argument(
        "--evidence-source",
        required=True,
        choices=["agent-observed", "developer-attested", "mixed"],
    )
    parser.add_argument(
        "--category",
        action="append",
        required=True,
        choices=[
            "functional",
            "unit",
            "integration",
            "contract",
            "static-analysis",
            "lint",
            "build",
        ],
    )
    parser.add_argument(
        "--check",
        action="append",
        required=True,
        help="Exact command or concise manual check covered by the result.",
    )
    parser.add_argument(
        "--implementation-file",
        action="append",
        required=True,
        help="Project-relative implementation, test, config, or migration file.",
    )
    parser.add_argument("--developer-confirmation")
    args = parser.parse_args()

    try:
        feature_dir = resolve_feature_dir(Path(args.feature_dir))
        payload = build_verification(
            feature_dir,
            status=args.status,
            evidence_source=args.evidence_source,
            categories=args.category,
            checks=args.check,
            implementation_files=args.implementation_file,
            developer_confirmation=args.developer_confirmation,
        )
        path = feature_dir / "_kapelle" / "verification.json"
        atomic_write_json(path, payload)
        refresh_feature_status(feature_dir)
    except (FeatureStateError, OSError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"RECORDED: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

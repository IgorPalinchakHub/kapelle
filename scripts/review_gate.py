#!/usr/bin/env python3
"""Check and write canonical, fingerprinted Kapelle review gates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from feature_state import (
    FeatureStateError,
    approval_current,
    atomic_write_json,
    refresh_feature_status,
    reconstruction_review_current,
    relative_fingerprint,
    resolve_feature_dir,
    review_gate_artifacts,
    workflow_lane,
)
from validate_architecture_package import validate as validate_architecture_package

PRIOR_GATES = {
    "business-spec": "outline",
    "architecture": "business-spec",
    "delivery-plan": "architecture",
    "reconstruction-spec": "reconstruction-scope",
    "reconstruction-design": "reconstruction-spec",
    "reconstruction": "reconstruction-design",
}


def require_prior_gate(feature_dir: Path, gate: str) -> None:
    prior = PRIOR_GATES.get(gate)
    if gate == "final":
        prior = "feature-plan" if workflow_lane(feature_dir) == "fast" else "delivery-plan"
    if prior and not approval_current(feature_dir, prior):
        raise FeatureStateError(
            f"gate {gate} requires current prior gate {prior}"
        )
    if gate == "reconstruction" and not reconstruction_review_current(feature_dir):
        raise FeatureStateError(
            "gate reconstruction requires current PASS reconstruction review"
        )


def build_gate(feature_dir: Path, gate: str, confirmation: str) -> dict[str, object]:
    confirmation = confirmation.strip()
    if not confirmation:
        raise FeatureStateError("approval confirmation must be non-empty")
    artifacts = review_gate_artifacts(gate)
    fingerprints: dict[str, str] = {}
    missing: list[str] = []
    for relative in artifacts:
        digest = relative_fingerprint(feature_dir, relative)
        if digest is None:
            missing.append(relative)
        else:
            fingerprints[relative] = digest
    if missing:
        raise FeatureStateError(
            f"gate {gate} has missing or empty artifacts: {', '.join(missing)}"
        )
    return {
        "gate": gate,
        "status": "approved",
        "confirmation": confirmation,
        "artifact_fingerprints": fingerprints,
    }


def approve(
    feature_dir: Path,
    gate: str,
    confirmation: str,
    *,
    refresh: bool = True,
) -> Path:
    feature_dir = resolve_feature_dir(feature_dir)
    require_prior_gate(feature_dir, gate)
    if gate == "architecture":
        errors = validate_architecture_package(feature_dir)
        if errors:
            raise FeatureStateError(
                "architecture package is not approval-ready: " + "; ".join(errors)
            )
    payload = build_gate(feature_dir, gate, confirmation)
    path = feature_dir / "_kapelle" / "approvals" / f"{gate}.json"
    atomic_write_json(path, payload)
    if refresh:
        refresh_feature_status(feature_dir)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("feature_dir")
    check_parser.add_argument("gate")

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("feature_dir")
    approve_parser.add_argument("gate")
    approve_parser.add_argument("--confirmation", required=True)
    approve_parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="Write only the gate; intended for deterministic tests.",
    )

    args = parser.parse_args()
    try:
        feature_dir = resolve_feature_dir(args.feature_dir)
        if args.action == "check":
            if approval_current(feature_dir, args.gate):
                print(f"CURRENT: review gate {args.gate}")
                return 0
            print(f"STALE-OR-MISSING: review gate {args.gate}")
            return 1
        path = approve(
            feature_dir,
            args.gate,
            args.confirmation,
            refresh=not args.no_refresh,
        )
    except FeatureStateError as exc:
        print(f"REFUSED: {exc}")
        return 2
    print(f"APPROVED: {args.gate} | path={path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

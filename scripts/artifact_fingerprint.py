#!/usr/bin/env python3
"""Compute deterministic SHA-256 fingerprints for project artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("paths", nargs="+", help="Project-relative artifact paths")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    artifacts: dict[str, str] = {}

    for raw in args.paths:
        candidate = (root / raw).resolve()
        try:
            relative = candidate.relative_to(root)
        except ValueError as exc:
            raise SystemExit(f"path escapes project root: {raw}") from exc
        if not candidate.is_file():
            raise SystemExit(f"artifact does not exist or is not a file: {raw}")
        artifacts[relative.as_posix()] = fingerprint(candidate)

    print(json.dumps({"algorithm": "sha256", "artifacts": artifacts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

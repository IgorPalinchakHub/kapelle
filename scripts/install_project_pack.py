#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RESOURCE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a Kapelle reference pack into Claude Code native project directories."
    )
    parser.add_argument(
        "--pack",
        required=True,
        help="Reference pack id under kapelle/packs or an explicit pack directory.",
    )
    parser.add_argument("--project", required=True, help="Target project root.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite conflicting installed resources. Identical files are always skipped.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print operations without writing.")
    return parser.parse_args()


def resolve_pack(value: str) -> Path:
    explicit = Path(value).expanduser()
    if explicit.is_dir():
        return explicit.resolve()
    bundled = ROOT / "packs" / value
    if bundled.is_dir():
        return bundled.resolve()
    raise ValueError(f"pack not found: {value}")


def discover_resources(pack: Path, project: Path) -> list[tuple[Path, Path]]:
    operations: list[tuple[Path, Path]] = []

    skills_dir = pack / "skills"
    for source in sorted(skills_dir.glob("*.md")):
        name = source.stem
        operations.append(
            (source, project / ".claude" / "skills" / name / "SKILL.md")
        )
    for source in sorted(skills_dir.glob("*/SKILL.md")):
        name = source.parent.name
        operations.append(
            (source, project / ".claude" / "skills" / name / "SKILL.md")
        )

    for kind in ("agents", "rules"):
        for source in sorted((pack / kind).glob("*.md")):
            operations.append(
                (source, project / ".claude" / kind / source.name)
            )

    return operations


def main() -> int:
    args = parse_args()
    try:
        pack = resolve_pack(args.pack)
        project = Path(args.project).expanduser().resolve()
        manifest_path = pack / "pack.manifest.json"
        manifest = json.loads(manifest_path.read_text())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    pack_id = manifest.get("id", "")
    if not RESOURCE_NAME.fullmatch(pack_id):
        print(f"ERROR: invalid pack id: {pack_id}", file=sys.stderr)
        return 2
    version = manifest.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        print(f"ERROR: invalid pack version: {version}", file=sys.stderr)
        return 2
    unexpected_manifest_keys = set(manifest) - {"id", "version", "description"}
    if unexpected_manifest_keys:
        keys = ", ".join(sorted(unexpected_manifest_keys))
        print(f"ERROR: runtime metadata is not allowed in a distribution manifest: {keys}", file=sys.stderr)
        return 2

    operations = discover_resources(pack, project)
    if not operations:
        print(f"ERROR: pack contains no native resources: {pack}", file=sys.stderr)
        return 2
    for source, _ in operations:
        name = source.parent.name if source.name == "SKILL.md" else source.stem
        if not RESOURCE_NAME.fullmatch(name):
            print(f"ERROR: invalid native resource name: {name}", file=sys.stderr)
            return 2

    conflicts = [
        destination
        for source, destination in operations
        if destination.exists()
        and not filecmp.cmp(source, destination, shallow=False)
    ]
    if conflicts and not args.force:
        print("ERROR: conflicting files already exist; rerun with --force to replace them:", file=sys.stderr)
        for path in conflicts:
            print(f"- {path}", file=sys.stderr)
        return 3

    for source, destination in operations:
        if destination.exists() and filecmp.cmp(source, destination, shallow=False):
            print(f"SKIP {destination}")
            continue
        action = "WOULD INSTALL" if args.dry_run else "INSTALL"
        print(f"{action} {destination}")
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    print(f"{'DRY RUN ' if args.dry_run else ''}DONE: {pack_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

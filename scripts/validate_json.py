#!/usr/bin/env python3
"""Validate one JSON instance against a Kapelle JSON Schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jsonschema_lite import (
    audit_schema,
    validate_file,
    validate_file_at_pointer,
    validate_jsonl_file,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instance")
    parser.add_argument("schema")
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Audit supported keywords and references without an instance.",
    )
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="Validate every non-empty JSON Lines record as an instance.",
    )
    parser.add_argument(
        "--pointer",
        default="",
        help="Validate the value at this RFC 6901 JSON pointer.",
    )
    args = parser.parse_args()
    if args.schema_only and (args.jsonl or args.pointer):
        parser.error("--schema-only cannot be combined with --jsonl or --pointer")
    if args.jsonl and args.pointer:
        parser.error("--jsonl and --pointer are mutually exclusive")
    schema = Path(args.schema)
    errors = (
        audit_schema(schema)
        if args.schema_only
        else (
            validate_jsonl_file(Path(args.instance), schema)
            if args.jsonl
            else (
                validate_file_at_pointer(Path(args.instance), schema, args.pointer)
                if args.pointer
                else validate_file(Path(args.instance), schema)
            )
        )
    )
    if errors:
        print(f"FAILED: {len(errors)} JSON Schema error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    action = "schema subset is supported" if args.schema_only else "JSON instance is valid"
    print(f"PASSED: {action}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

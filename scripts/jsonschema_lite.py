#!/usr/bin/env python3
"""Fail-closed validator for the JSON Schema subset used by Kapelle.

This is intentionally not advertised as a complete Draft 2020-12 implementation. The schema audit
rejects unsupported validation keywords so a newly introduced construct cannot be silently ignored.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ANNOTATION_KEYWORDS = {
    "$id",
    "$schema",
    "default",
    "description",
    "title",
}
VALIDATION_KEYWORDS = {
    "$defs",
    "$ref",
    "additionalProperties",
    "allOf",
    "const",
    "else",
    "enum",
    "format",
    "if",
    "items",
    "maxLength",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "oneOf",
    "pattern",
    "properties",
    "required",
    "then",
    "type",
    "uniqueItems",
}
SUPPORTED_KEYWORDS = ANNOTATION_KEYWORDS | VALIDATION_KEYWORDS
SUPPORTED_TYPES = {"array", "boolean", "integer", "null", "number", "object", "string"}
SUPPORTED_FORMATS = {"date-time"}


def _json_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return type(left) is type(right) and left == right


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return False


def _is_datetime(value: str) -> bool:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return "T" in value and parsed.tzinfo is not None


class SchemaEngine:
    def __init__(self, root_schema_path: Path):
        self.root_schema_path = root_schema_path.resolve()
        self.schema_root = self.root_schema_path.parent
        self._documents: dict[Path, Any] = {}

    def load_schema(self, path: Path) -> Any:
        resolved = path.resolve()
        try:
            resolved.relative_to(self.schema_root)
        except ValueError as exc:
            raise ValueError(f"schema reference escapes schema root: {resolved}") from exc
        if resolved not in self._documents:
            self._documents[resolved] = json.loads(resolved.read_text())
        return self._documents[resolved]

    def _resolve_ref(
        self, ref: str, document: Any, document_path: Path
    ) -> tuple[Any, Any, Path]:
        if "://" in ref:
            raise ValueError(f"remote schema references are unsupported: {ref}")
        target_name, separator, fragment = ref.partition("#")
        if target_name:
            target_path = (document_path.parent / target_name).resolve()
            target_document = self.load_schema(target_path)
        else:
            target_path = document_path
            target_document = document
        target = target_document
        if separator and fragment:
            if not fragment.startswith("/"):
                raise ValueError(f"unsupported JSON pointer fragment: #{fragment}")
            for raw_part in fragment[1:].split("/"):
                part = raw_part.replace("~1", "/").replace("~0", "~")
                if isinstance(target, list):
                    try:
                        target = target[int(part)]
                    except (ValueError, IndexError) as exc:
                        raise ValueError(f"unresolved schema reference: {ref}") from exc
                elif isinstance(target, dict) and part in target:
                    target = target[part]
                else:
                    raise ValueError(f"unresolved schema reference: {ref}")
        return target, target_document, target_path

    def audit(self) -> list[str]:
        document = self.load_schema(self.root_schema_path)
        return self._audit_node(
            document,
            schema_location="$",
            document=document,
            document_path=self.root_schema_path,
            visited=set(),
        )

    def _audit_node(
        self,
        schema: Any,
        *,
        schema_location: str,
        document: Any,
        document_path: Path,
        visited: set[tuple[Path, int]],
    ) -> list[str]:
        if isinstance(schema, bool):
            return []
        if not isinstance(schema, dict):
            return [f"{schema_location}: schema node must be an object or boolean"]
        identity = (document_path, id(schema))
        if identity in visited:
            return []
        visited.add(identity)
        errors: list[str] = []
        unknown = set(schema) - SUPPORTED_KEYWORDS
        if unknown:
            errors.append(
                f"{schema_location}: unsupported schema keywords: {sorted(unknown)}"
            )

        declared_types = schema.get("type")
        if declared_types is not None:
            values = (
                declared_types if isinstance(declared_types, list) else [declared_types]
            )
            if (
                not values
                or not all(isinstance(item, str) and item in SUPPORTED_TYPES for item in values)
                or len(values) != len(set(values))
            ):
                errors.append(f"{schema_location}.type: invalid supported type declaration")
        if "format" in schema and (
            not isinstance(schema["format"], str)
            or schema["format"] not in SUPPORTED_FORMATS
        ):
            errors.append(f"{schema_location}.format: unsupported format {schema['format']!r}")
        if "pattern" in schema:
            try:
                re.compile(schema["pattern"])
            except (TypeError, re.error):
                errors.append(f"{schema_location}.pattern: invalid regular expression")
        required = schema.get("required")
        if required is not None and (
            not isinstance(required, list)
            or not all(isinstance(item, str) for item in required)
            or len(required) != len(set(required))
        ):
            errors.append(f"{schema_location}.required: must be an array of unique strings")
        enum = schema.get("enum")
        if enum is not None and (not isinstance(enum, list) or not enum):
            errors.append(f"{schema_location}.enum: must be a non-empty array")
        for keyword in ("minItems", "minLength", "maxLength", "minProperties"):
            value = schema.get(keyword)
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                errors.append(f"{schema_location}.{keyword}: must be a non-negative integer")
        minimum = schema.get("minimum")
        if minimum is not None and (
            not isinstance(minimum, (int, float)) or isinstance(minimum, bool)
        ):
            errors.append(f"{schema_location}.minimum: must be a number")
        if "uniqueItems" in schema and not isinstance(schema["uniqueItems"], bool):
            errors.append(f"{schema_location}.uniqueItems: must be a boolean")
        if "$ref" in schema and not isinstance(schema["$ref"], str):
            errors.append(f"{schema_location}.$ref: must be a string")

        for keyword in ("properties", "$defs"):
            value = schema.get(keyword)
            if value is None:
                continue
            if not isinstance(value, dict):
                errors.append(f"{schema_location}.{keyword}: must be an object")
                continue
            for name, child in value.items():
                errors.extend(
                    self._audit_node(
                        child,
                        schema_location=f"{schema_location}.{keyword}.{name}",
                        document=document,
                        document_path=document_path,
                        visited=visited,
                    )
                )
        for keyword in ("items", "additionalProperties", "if", "then", "else"):
            child = schema.get(keyword)
            if child is None:
                continue
            if isinstance(child, bool):
                continue
            errors.extend(
                self._audit_node(
                    child,
                    schema_location=f"{schema_location}.{keyword}",
                    document=document,
                    document_path=document_path,
                    visited=visited,
                )
            )
        for keyword in ("allOf", "oneOf"):
            children = schema.get(keyword)
            if children is None:
                continue
            if not isinstance(children, list) or not children:
                errors.append(f"{schema_location}.{keyword}: must be a non-empty array")
                continue
            for index, child in enumerate(children):
                errors.extend(
                    self._audit_node(
                        child,
                        schema_location=f"{schema_location}.{keyword}[{index}]",
                        document=document,
                        document_path=document_path,
                        visited=visited,
                    )
                )
        if "$ref" in schema and isinstance(schema["$ref"], str):
            try:
                target, target_document, target_path = self._resolve_ref(
                    schema["$ref"], document, document_path
                )
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{schema_location}.$ref: {exc}")
            else:
                errors.extend(
                    self._audit_node(
                        target,
                        schema_location=f"{schema_location}.$ref({schema['$ref']})",
                        document=target_document,
                        document_path=target_path,
                        visited=visited,
                    )
                )
        return errors

    def validate(self, instance: Any) -> list[str]:
        schema = self.load_schema(self.root_schema_path)
        audit_errors = self.audit()
        if audit_errors:
            return [f"schema: {error}" for error in audit_errors]
        return self._validate_node(
            instance,
            schema,
            instance_path="$",
            document=schema,
            document_path=self.root_schema_path,
        )

    def _validate_node(
        self,
        instance: Any,
        schema: Any,
        *,
        instance_path: str,
        document: Any,
        document_path: Path,
    ) -> list[str]:
        if schema is True:
            return []
        if schema is False:
            return [f"{instance_path}: rejected by boolean schema"]
        errors: list[str] = []
        if "$ref" in schema:
            target, target_document, target_path = self._resolve_ref(
                schema["$ref"], document, document_path
            )
            errors.extend(
                self._validate_node(
                    instance,
                    target,
                    instance_path=instance_path,
                    document=target_document,
                    document_path=target_path,
                )
            )

        declared_types = schema.get("type")
        if declared_types is not None:
            expected = (
                declared_types if isinstance(declared_types, list) else [declared_types]
            )
            if not any(_matches_type(instance, item) for item in expected):
                errors.append(
                    f"{instance_path}: expected type {' | '.join(expected)}, "
                    f"got {type(instance).__name__}"
                )
                return errors

        if "const" in schema and not _json_equal(instance, schema["const"]):
            errors.append(f"{instance_path}: value must equal {schema['const']!r}")
        if "enum" in schema and not any(
            _json_equal(instance, item) for item in schema["enum"]
        ):
            errors.append(f"{instance_path}: value is not in enum")

        if isinstance(instance, str):
            if len(instance) < schema.get("minLength", 0):
                errors.append(
                    f"{instance_path}: string is shorter than {schema['minLength']}"
                )
            if "maxLength" in schema and len(instance) > schema["maxLength"]:
                errors.append(
                    f"{instance_path}: string is longer than {schema['maxLength']}"
                )
            if "pattern" in schema and not re.search(schema["pattern"], instance):
                errors.append(f"{instance_path}: string does not match required pattern")
            if schema.get("format") == "date-time" and not _is_datetime(instance):
                errors.append(f"{instance_path}: invalid date-time")

        if isinstance(instance, (int, float)) and not isinstance(instance, bool):
            if "minimum" in schema and instance < schema["minimum"]:
                errors.append(
                    f"{instance_path}: number is below minimum {schema['minimum']}"
                )

        if isinstance(instance, list):
            if len(instance) < schema.get("minItems", 0):
                errors.append(
                    f"{instance_path}: array has fewer than {schema['minItems']} items"
                )
            if schema.get("uniqueItems"):
                canonical = [_canonical(item) for item in instance]
                if len(canonical) != len(set(canonical)):
                    errors.append(f"{instance_path}: array items must be unique")
            if "items" in schema:
                for index, item in enumerate(instance):
                    errors.extend(
                        self._validate_node(
                            item,
                            schema["items"],
                            instance_path=f"{instance_path}[{index}]",
                            document=document,
                            document_path=document_path,
                        )
                    )

        if isinstance(instance, dict):
            required = schema.get("required", [])
            for key in required:
                if key not in instance:
                    errors.append(f"{instance_path}: missing required property {key!r}")
            if len(instance) < schema.get("minProperties", 0):
                errors.append(
                    f"{instance_path}: object has fewer than "
                    f"{schema['minProperties']} properties"
                )
            properties = schema.get("properties", {})
            for key, child_schema in properties.items():
                if key in instance:
                    errors.extend(
                        self._validate_node(
                            instance[key],
                            child_schema,
                            instance_path=f"{instance_path}.{key}",
                            document=document,
                            document_path=document_path,
                        )
                    )
            extras = set(instance) - set(properties)
            additional = schema.get("additionalProperties", True)
            if additional is False and extras:
                errors.append(
                    f"{instance_path}: unexpected properties {sorted(extras)}"
                )
            elif isinstance(additional, dict):
                for key in sorted(extras):
                    errors.extend(
                        self._validate_node(
                            instance[key],
                            additional,
                            instance_path=f"{instance_path}.{key}",
                            document=document,
                            document_path=document_path,
                        )
                    )

        for child in schema.get("allOf", []):
            errors.extend(
                self._validate_node(
                    instance,
                    child,
                    instance_path=instance_path,
                    document=document,
                    document_path=document_path,
                )
            )
        if "oneOf" in schema:
            matches = sum(
                not self._validate_node(
                    instance,
                    child,
                    instance_path=instance_path,
                    document=document,
                    document_path=document_path,
                )
                for child in schema["oneOf"]
            )
            if matches != 1:
                errors.append(
                    f"{instance_path}: expected exactly one oneOf branch, matched {matches}"
                )
        if "if" in schema:
            condition_matches = not self._validate_node(
                instance,
                schema["if"],
                instance_path=instance_path,
                document=document,
                document_path=document_path,
            )
            branch = schema.get("then") if condition_matches else schema.get("else")
            if branch is not None:
                errors.extend(
                    self._validate_node(
                        instance,
                        branch,
                        instance_path=instance_path,
                        document=document,
                        document_path=document_path,
                    )
                )
        return errors


def audit_schema(schema_path: Path) -> list[str]:
    try:
        return SchemaEngine(schema_path).audit()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]


def validate_instance(instance: Any, schema_path: Path) -> list[str]:
    try:
        return SchemaEngine(schema_path).validate(instance)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]


def validate_file(instance_path: Path, schema_path: Path) -> list[str]:
    try:
        instance = json.loads(instance_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{instance_path}: {exc}"]
    return validate_instance(instance, schema_path)


def resolve_instance_pointer(instance: Any, pointer: str) -> Any:
    if pointer == "":
        return instance
    if not pointer.startswith("/"):
        raise ValueError("JSON pointer must be empty or start with '/'")
    target = instance
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(target, list):
            try:
                target = target[int(part)]
            except (ValueError, IndexError) as exc:
                raise ValueError(f"unresolved instance JSON pointer: {pointer}") from exc
        elif isinstance(target, dict) and part in target:
            target = target[part]
        else:
            raise ValueError(f"unresolved instance JSON pointer: {pointer}")
    return target


def validate_file_at_pointer(
    instance_path: Path, schema_path: Path, pointer: str
) -> list[str]:
    try:
        instance = json.loads(instance_path.read_text())
        selected = resolve_instance_pointer(instance, pointer)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{instance_path}: {exc}"]
    return validate_instance(selected, schema_path)


def validate_jsonl_file(instance_path: Path, schema_path: Path) -> list[str]:
    try:
        lines = instance_path.read_text().splitlines()
    except OSError as exc:
        return [f"{instance_path}: {exc}"]
    errors: list[str] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            instance = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
            continue
        errors.extend(
            f"line {line_number}: {error}"
            for error in validate_instance(instance, schema_path)
        )
    return errors

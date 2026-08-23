#!/usr/bin/env python3
"""Shared acceptance-criterion identifier parsing."""

from __future__ import annotations

import re


AC_PATTERN = re.compile(r"\bAC-[A-Za-z0-9][A-Za-z0-9._-]*\b")
NUMERIC_AC_PATTERN = re.compile(r"\bAC-\d+\b")
AC_RANGE_PATTERN = re.compile(r"\bAC-(\d+)\s*[–—-]\s*AC-(\d+)\b")


def expand_acceptance_criteria(
    text: str,
    *,
    numeric_only: bool = False,
    max_range_span: int = 100,
) -> list[str]:
    """Return literal AC ids plus bounded numeric-range expansion."""

    pattern = NUMERIC_AC_PATTERN if numeric_only else AC_PATTERN
    found = set(pattern.findall(text))
    for match in AC_RANGE_PATTERN.finditer(text):
        start_text, end_text = match.groups()
        start, end = int(start_text), int(end_text)
        if start <= end and end - start <= max_range_span:
            width = max(len(start_text), len(end_text))
            found.update(f"AC-{item:0{width}d}" for item in range(start, end + 1))
    return sorted(found)

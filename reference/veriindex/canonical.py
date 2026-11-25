"""Canonical result encoding and hashing."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(result: dict[str, Any]) -> str:
    """Return the canonical JSON form used for hashing.

    Rules: sorted keys, compact separators, UTF-8, no trailing newline.
    """
    return json.dumps(
        result,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def result_hash(result: dict[str, Any]) -> str:
    """Return the 0x-prefixed SHA-256 hash of the canonical result."""
    digest = hashlib.sha256(canonical_json(result).encode("utf-8")).hexdigest()
    return f"0x{digest}"

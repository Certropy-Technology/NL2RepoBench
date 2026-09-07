"""Canonical serialization shared by every persisted domain record.

Hashes are calculated from UTF-8 JSON with sorted keys and compact separators.
The format is deliberately small and dependency-free so manifests can be
validated by tools outside this package.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel


def canonical_value(value: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
    """Return a JSON-compatible mapping with optional fields removed."""

    if isinstance(value, BaseModel):
        raw = value.model_dump(mode="json", exclude_none=True)
    else:
        raw = dict(value)
    return raw


def canonical_json(value: BaseModel | Mapping[str, Any]) -> bytes:
    """Serialize a record deterministically for storage, diffing, and hashing."""

    return json.dumps(
        canonical_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def content_digest(value: BaseModel | Mapping[str, Any]) -> str:
    """Return a prefixed SHA-256 digest for a canonical record."""

    return f"sha256:{hashlib.sha256(canonical_json(value)).hexdigest()}"


def bytes_digest(data: bytes) -> str:
    """Return a prefixed SHA-256 digest for arbitrary bytes."""

    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def canonical_file_payload(data: bytes) -> bytes:
    """Return the JSON payload from the exact on-disk canonical file format."""

    if not data.endswith(b"\n") or data.endswith(b"\n\n"):
        raise ValueError("canonical JSON files must end with exactly one LF")
    return data[:-1]

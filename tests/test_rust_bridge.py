from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from nl2repobench.verification.rust_bridge import (
    RustBridgeRequest,
    canonical_api_plan_digest,
    canonical_json_bytes,
    load_rust_api_plan,
    validate_rust_value,
)


def _plan_payload() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "package_name": "demo",
        "types": [
            {
                "type_id": "Payload",
                "kind": "struct",
                "scalar": None,
                "item": None,
                "key": None,
                "fields": [{"name": "text", "type": "string"}],
                "variants": [],
            }
        ],
        "functions": [
            {
                "api_id": "summarize",
                "rust_path": "crate::summarize",
                "kind": "sync",
                "receiver": None,
                "state_type": None,
                "args": [{"name": "payload", "type": "Payload"}],
                "returns": "string",
                "error": None,
                "unsafe": False,
                "leaf_ids": ["summarize.basic"],
            }
        ],
        "state_types": [],
        "cli_profiles": [],
        "unsafe_leaf_ids": [],
    }
    payload["api_plan_digest"] = "sha256:" + hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    return payload


def _write_plan(path: Path, payload: dict[str, object]) -> None:
    path.write_bytes(canonical_json_bytes(payload))


def test_api_plan_binds_canonical_plan_and_exact_file_bytes(tmp_path: Path) -> None:
    path = tmp_path / "rust-api-plan.json"
    payload = _plan_payload()
    _write_plan(path, payload)

    plan, exact = load_rust_api_plan(path)

    assert canonical_api_plan_digest(plan) == plan.api_plan_digest
    assert exact == path.read_bytes()


def test_api_plan_rejects_digest_mutation_and_noncanonical_bytes(tmp_path: Path) -> None:
    path = tmp_path / "rust-api-plan.json"
    payload = _plan_payload()
    payload["api_plan_digest"] = "sha256:" + "0" * 64
    _write_plan(path, payload)
    with pytest.raises(ValueError, match="canonical-plan digest"):
        load_rust_api_plan(path)

    payload = _plan_payload()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="canonical JSON bytes"):
        load_rust_api_plan(path)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"schema_version":"1.0","schema_version":"1.0"}\n',
        canonical_json_bytes({**_plan_payload(), "unknown": True}),
        canonical_json_bytes(
            {key: value for key, value in _plan_payload().items() if key != "api_plan_digest"}
        ),
    ],
)
def test_api_plan_rejects_duplicate_unknown_and_missing_fields(
    tmp_path: Path, raw: bytes
) -> None:
    path = tmp_path / "rust-api-plan.json"
    path.write_bytes(raw)

    with pytest.raises((ValueError, ValidationError)):
        load_rust_api_plan(path)


@pytest.mark.parametrize(
    "value",
    [
        {"type": "unit"},
        {"type": "i8", "value": "-128"},
        {"type": "f32", "bits": "3f800000"},
        {"type": "bytes", "base64": "AAE="},
        {
            "type": "map",
            "entries": [
                {"key": "a", "value": {"type": "bool", "value": True}},
                {"key": "b", "value": {"type": "string", "value": "ok"}},
            ],
        },
    ],
)
def test_rust_value_accepts_canonical_serializable_values(value: object) -> None:
    assert validate_rust_value(value) == value


@pytest.mark.parametrize(
    "value",
    [
        {"type": "i8", "value": "128"},
        {"type": "u8", "value": "01"},
        {"type": "bytes", "base64": "AA"},
        {
            "type": "map",
            "entries": [
                {"key": "b", "value": {"type": "unit"}},
                {"key": "a", "value": {"type": "unit"}},
            ],
        },
        {"type": "unit", "extra": True},
    ],
)
def test_rust_value_rejects_noncanonical_or_out_of_range_values(value: object) -> None:
    with pytest.raises(ValueError):
        validate_rust_value(value)


def test_bridge_request_separates_operation_and_leaf_identity() -> None:
    payload = {
        "schema_version": "1.0",
        "request_id": "1" * 32,
        "operations": (
            {
                "operation_id": "op-1",
                "api_id": "summarize",
                "leaf_id": "leaf-1",
                "kind": "call",
                "state_handle": None,
                "args": ({"type": "unit"},),
            },
        ),
    }
    request = RustBridgeRequest.model_validate(payload)
    assert request.operations[0].leaf_id == "leaf-1"

    payload["operations"] = (
        {**payload["operations"][0], "operation_id": "leaf-1"},  # type: ignore[index]
    )
    with pytest.raises(ValidationError, match="distinct"):
        RustBridgeRequest.model_validate(payload)

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from nl2repobench.verification.rust_bridge import (
    MAX_BRIDGE_JSON_BYTES,
    MAX_BRIDGE_RESULTS,
    RustApiPlan,
    RustBridgeRequest,
    RustBridgeResponse,
    _freeze_json,
    canonical_api_plan_digest,
    canonical_json_bytes,
    load_rust_api_plan,
    load_rust_bridge_request,
    load_rust_bridge_response,
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


def _state_plan_payload(*, include_drop: bool = False) -> dict[str, object]:
    payload = _plan_payload()
    payload["types"] = [
        {
            "type_id": "State",
            "kind": "struct",
            "scalar": None,
            "item": None,
            "key": None,
            "fields": [{"name": "value", "type": "string"}],
            "variants": [],
        }
    ]
    functions: list[dict[str, object]] = [
        {
            "api_id": "call",
            "rust_path": "crate::State::value",
            "kind": "instance",
            "receiver": "State",
            "state_type": "State",
            "args": [{"name": "suffix", "type": "string"}],
            "returns": "string",
            "error": None,
            "unsafe": False,
            "leaf_ids": ["state.call"],
        },
        {
            "api_id": "create",
            "rust_path": "crate::State::new",
            "kind": "associated",
            "receiver": None,
            "state_type": None,
            "args": [{"name": "value", "type": "string"}],
            "returns": "State",
            "error": None,
            "unsafe": False,
            "leaf_ids": ["state.create"],
        },
    ]
    if include_drop:
        functions.append(
            {
                "api_id": "drop",
                "rust_path": "crate::State::close",
                "kind": "instance",
                "receiver": "State",
                "state_type": "State",
                "args": [],
                "returns": "unit",
                "error": None,
                "unsafe": False,
                "leaf_ids": ["state.drop"],
            }
        )
    payload["functions"] = sorted(functions, key=lambda item: str(item["api_id"]))
    payload["state_types"] = [
        {
            "state_id": "state",
            "rust_type": "State",
            "create_api_id": "create",
            "methods": [
                {
                    "api_id": "call",
                    "receiver": "&self",
                    "args": [{"name": "suffix", "type": "string"}],
                    "returns": "string",
                    "error": None,
                    "state_type": "State",
                    "leaf_ids": ["state.call"],
                }
            ],
            "drop_api_id": "drop" if include_drop else None,
        }
    ]
    return payload


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


def test_bridge_raw_json_rejects_duplicates_nonfinite_and_noncanonical_bytes() -> None:
    raw = b'{"operations":[],"request_id":"' + b"1" * 32 + b'","schema_version":"1.0"}\n'
    with pytest.raises(ValueError, match="at least 1"):
        load_rust_bridge_request(raw)
    duplicate = (
        b'{"operations":[],"request_id":"' + b"1" * 32
        + b'","request_id":"' + b"2" * 32 + b'","schema_version":"1.0"}\n'
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_rust_bridge_request(duplicate)
    nonfinite = b'{"duration":NaN}\n'
    with pytest.raises(ValueError, match="non-finite"):
        load_rust_bridge_request(nonfinite)

    with pytest.raises(ValueError, match="size limit"):
        load_rust_bridge_request(b" " * (MAX_BRIDGE_JSON_BYTES + 1))


def test_bridge_request_and_response_bind_ids_and_aggregate_value_budget() -> None:
    operation = {
        "operation_id": "op-1",
        "api_id": "summarize",
        "leaf_id": "leaf-1",
        "kind": "call",
        "state_handle": None,
        "args": ({"type": "string", "value": "ok"},),
    }
    request = RustBridgeRequest.model_validate(
        {"schema_version": "1.0", "request_id": "1" * 32, "operations": (operation,)}
    )
    response = RustBridgeResponse.model_validate(
        {
            "schema_version": "1.0",
            "request_id": "1" * 32,
            "results": (
                {
                    "operation_id": "op-1",
                    "status": "ok",
                    "value": {"type": "string", "value": "ok"},
                    "error_type": None,
                    "message": None,
                    "state_handle": None,
                },
            ),
        }
    )
    response_bytes = canonical_json_bytes(response.model_dump(mode="json"))
    assert load_rust_bridge_response(response_bytes, request).request_id == request.request_id
    with pytest.raises(ValueError, match="request_id"):
        load_rust_bridge_response(
            canonical_json_bytes(
                {**response.model_dump(mode="json"), "request_id": "2" * 32}
            ),
            request,
        )

    many_args = tuple({"type": "unit"} for _ in range(2049))
    with pytest.raises(ValidationError, match="argument limit"):
        RustBridgeRequest.model_validate(
            {"schema_version": "1.0", "request_id": "1" * 32,
             "operations": ({**operation, "args": many_args},)}
        )

    oversized_values = tuple(
        {"type": "string", "value": "x" * (256 * 1024)} for _ in range(17)
    )
    with pytest.raises(ValidationError, match="aggregate value-byte"):
        RustBridgeRequest.model_validate(
            {
                "schema_version": "1.0",
                "request_id": "1" * 32,
                "operations": (
                    {
                        **operation,
                        "args": oversized_values,
                    },
                ),
            }
        )

    result = response.results[0].model_dump(mode="json")
    with pytest.raises(ValidationError, match="result limit"):
        RustBridgeResponse.model_validate(
            {
                "schema_version": "1.0",
                "request_id": "1" * 32,
                "results": tuple(
                    {**result, "operation_id": f"result-{index}"}
                    for index in range(MAX_BRIDGE_RESULTS + 1)
                ),
            }
        )


def test_bridge_response_requires_ordered_complete_or_panic_prefix() -> None:
    operations = tuple(
        {
            "operation_id": f"op-{index}",
            "api_id": "summarize",
            "leaf_id": f"leaf-{index}",
            "kind": "call",
            "state_handle": None,
            "args": ({"type": "unit"},),
        }
        for index in range(3)
    )
    request = RustBridgeRequest.model_validate(
        {"schema_version": "1.0", "request_id": "1" * 32, "operations": operations}
    )

    def response_bytes(ids: tuple[str, ...], *, panic_last: bool = False) -> bytes:
        results = []
        for index, operation_id in enumerate(ids):
            panic = panic_last and index == len(ids) - 1
            results.append(
                {
                    "operation_id": operation_id,
                    "status": "panic" if panic else "ok",
                    "value": None if panic else {"type": "unit"},
                    "error_type": "panic" if panic else None,
                    "message": "boom" if panic else None,
                    "state_handle": None,
                }
            )
        response = RustBridgeResponse.model_validate(
            {
                "schema_version": "1.0",
                "request_id": request.request_id,
                "results": tuple(results),
            }
        )
        return canonical_json_bytes(response.model_dump(mode="json"))

    complete = load_rust_bridge_response(
        response_bytes(("op-0", "op-1", "op-2")), request
    )
    aborted = load_rust_bridge_response(
        response_bytes(("op-0", "op-1"), panic_last=True),
        request,
        allow_completed_prefix_on_abort=True,
    )
    assert len(complete.results) == 3
    assert len(aborted.results) == 2
    with pytest.raises(ValueError, match="operation IDs"):
        load_rust_bridge_response(response_bytes(("op-1", "op-0", "op-2")), request)
    with pytest.raises(ValueError, match="operation IDs"):
        load_rust_bridge_response(response_bytes(("op-0", "op-1")), request)
    nonpanic_aborted = load_rust_bridge_response(
        response_bytes(("op-0", "op-1")),
        request,
        allow_completed_prefix_on_abort=True,
    )
    assert len(nonpanic_aborted.results) == 2
    with pytest.raises(ValueError, match="operation IDs"):
        load_rust_bridge_response(response_bytes(()), request)


def test_state_plan_requires_exact_method_descriptor_and_roles() -> None:
    payload = _state_plan_payload()
    RustApiPlan.model_validate(_freeze_json(payload))
    payload["state_types"][0]["methods"][0]["leaf_ids"] = ["state.other"]  # type: ignore[index]
    with pytest.raises(ValidationError, match="exactly match"):
        RustApiPlan.model_validate(_freeze_json(payload))


@pytest.mark.parametrize("create_kind", ["sync", "async", "instance"])
def test_state_create_requires_exact_safe_associated_role(create_kind: str) -> None:
    payload = _state_plan_payload()
    create = next(
        item for item in payload["functions"] if item["api_id"] == "create"  # type: ignore[union-attr]
    )
    create["kind"] = create_kind
    if create_kind == "instance":
        create["receiver"] = "State"
        create["state_type"] = "State"
    with pytest.raises(ValidationError, match="safe associated"):
        RustApiPlan.model_validate(_freeze_json(payload))

    create["kind"] = "associated"
    create["receiver"] = None
    create["state_type"] = None
    create["unsafe"] = True
    payload["unsafe_leaf_ids"] = ["state.create"]
    with pytest.raises(ValidationError, match="safe associated"):
        RustApiPlan.model_validate(_freeze_json(payload))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("args", [], "only a custom state drop"),
        ("leaf_ids", [], "at least 1"),
    ],
)
def test_state_create_requires_arguments_and_leaf_coverage(
    field: str, value: object, message: str
) -> None:
    payload = _state_plan_payload()
    create = next(
        item for item in payload["functions"] if item["api_id"] == "create"  # type: ignore[union-attr]
    )
    create[field] = value
    with pytest.raises(ValidationError, match=message):
        RustApiPlan.model_validate(_freeze_json(payload))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("kind", "associated"),
        ("receiver", "string"),
        ("state_type", "string"),
        ("args", [{"name": "extra", "type": "string"}]),
        ("returns", "string"),
        ("error", "string"),
        ("unsafe", True),
    ],
)
def test_custom_drop_requires_exact_safe_mutable_state_role(
    field: str, value: object
) -> None:
    payload = _state_plan_payload(include_drop=True)
    drop = next(
        item for item in payload["functions"] if item["api_id"] == "drop"  # type: ignore[union-attr]
    )
    drop[field] = value
    if field == "kind":
        drop["receiver"] = None
        drop["state_type"] = None
    if field == "unsafe":
        payload["unsafe_leaf_ids"] = ["state.drop"]
    with pytest.raises(ValidationError, match="invalid descriptor role"):
        RustApiPlan.model_validate(_freeze_json(payload))


def test_custom_drop_requires_leaf_coverage() -> None:
    payload = _state_plan_payload(include_drop=True)
    drop = next(
        item for item in payload["functions"] if item["api_id"] == "drop"  # type: ignore[union-attr]
    )
    drop["leaf_ids"] = []
    with pytest.raises(ValidationError, match="at least 1"):
        RustApiPlan.model_validate(_freeze_json(payload))


def test_state_roles_are_disjoint_and_state_methods_are_safe() -> None:
    payload = _state_plan_payload(include_drop=True)
    state = payload["state_types"][0]  # type: ignore[index]
    state["methods"].append(  # type: ignore[union-attr]
        {
            "api_id": "drop",
            "receiver": "&mut self",
            "args": [],
            "returns": "unit",
            "error": None,
            "state_type": "State",
            "leaf_ids": ["state.drop"],
        }
    )
    state["methods"].sort(key=lambda item: item["api_id"])  # type: ignore[union-attr]
    with pytest.raises(ValidationError, match="roles must be disjoint"):
        RustApiPlan.model_validate(_freeze_json(payload))

    payload = _state_plan_payload()
    call = next(
        item for item in payload["functions"] if item["api_id"] == "call"  # type: ignore[union-attr]
    )
    call["unsafe"] = True
    payload["unsafe_leaf_ids"] = ["state.call"]
    with pytest.raises(ValidationError, match="exactly match"):
        RustApiPlan.model_validate(_freeze_json(payload))


def test_zero_argument_api_is_reserved_for_custom_drop() -> None:
    payload = copy.deepcopy(_plan_payload())
    payload["functions"][0]["args"] = []  # type: ignore[index]
    with pytest.raises(ValidationError, match="only a custom state drop"):
        RustApiPlan.model_validate(_freeze_json(payload))

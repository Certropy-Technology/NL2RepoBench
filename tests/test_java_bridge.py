from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from nl2repobench.verification.java_bridge import (
    JavaBridgeSpec,
    JavaConstructorOperation,
    JavaField,
    JavaInstanceMethodOperation,
    JavaParameter,
    JavaStaticMethodOperation,
    JavaValueType,
    load_java_bridge_spec,
    render_java_bridge,
    validate_java_value,
)


@pytest.mark.parametrize("kind", ["array", "list"])
def test_java_bridge_accepts_valid_sequence_values(kind: str) -> None:
    value_type = JavaValueType(kind=kind, element=JavaValueType(kind="int32"))

    validate_java_value([1, 2, 3], value_type)


def test_java_bridge_rejects_duplicate_set_values() -> None:
    value_type = JavaValueType(kind="set", element=JavaValueType(kind="string"))

    with pytest.raises(ValueError, match="set value is invalid"):
        validate_java_value(["duplicate", "duplicate"], value_type)


def test_java_bridge_loads_canonical_spec_and_renders_descriptors() -> None:
    constructor = JavaConstructorOperation(
        operation_id="new-value",
        class_name="example.Value",
        parameters=(JavaParameter(name="value", value_type=JavaValueType(kind="string")),),
    )
    static = JavaStaticMethodOperation(
        operation_id="parse",
        class_name="example.Value",
        method_name="parse",
        return_type=JavaValueType(kind="int32"),
    )
    instance = JavaInstanceMethodOperation(
        operation_id="size",
        class_name="example.Value",
        constructor_id="new-value",
        method_name="size",
        return_type=JavaValueType(kind="int64"),
    )
    spec = JavaBridgeSpec(operations=(constructor, static, instance))
    data = json.dumps(
        spec.model_dump(mode="json", exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
    ).encode() + b"\n"

    loaded = load_java_bridge_spec(data)
    rendered = render_java_bridge(loaded)

    assert loaded == spec
    assert b'new Operation("new-value", "constructor"' in next(
        value for path, value in rendered.items() if path.suffix == ".java"
    )
    assert any(str(path).endswith("GeneratedBridge.java") for path in rendered)


def test_java_bridge_rejects_noncanonical_and_invalid_operation_graph() -> None:
    spec = JavaBridgeSpec(
        operations=(
            JavaStaticMethodOperation(
                operation_id="parse",
                class_name="example.Value",
                method_name="parse",
                return_type=JavaValueType(kind="string"),
            ),
        )
    )
    noncanonical = json.dumps(spec.model_dump(mode="json", exclude_none=True)).encode()
    with pytest.raises(ValueError, match="not canonical"):
        load_java_bridge_spec(noncanonical)
    with pytest.raises(ValueError, match="invalid Java bridge specification"):
        load_java_bridge_spec(b"not-json")
    with pytest.raises(ValidationError, match="references no constructor"):
        JavaBridgeSpec(
            operations=(
                JavaInstanceMethodOperation(
                    operation_id="size",
                    class_name="example.Value",
                    constructor_id="missing",
                    method_name="size",
                    return_type=JavaValueType(kind="int32"),
                ),
            )
        )


@pytest.mark.parametrize(
    ("kind", "valid", "invalid"),
    [
        ("string", "text", 1),
        ("boolean", True, 1),
        ("int32", 2**31 - 1, 2**31),
        ("int64", -(2**63), -(2**63) - 1),
        ("float64", 1.5, float("inf")),
        ("bytes", "Ynl0ZXM=", "%%%"),
        ("enum", "VALUE", "not-valid!"),
    ],
)
def test_java_bridge_validates_scalar_transport_values(
    kind: str, valid: object, invalid: object
) -> None:
    options = {"enum_name": "example.Kind"} if kind == "enum" else {}
    value_type = JavaValueType(kind=kind, **options)

    validate_java_value(valid, value_type)
    with pytest.raises(ValueError, match=f"{kind} value is invalid"):
        validate_java_value(invalid, value_type)


def test_java_bridge_validates_map_and_value_object() -> None:
    mapping = JavaValueType(kind="string-map", element=JavaValueType(kind="boolean"))
    value_object = JavaValueType(
        kind="value-object",
        class_name="example.Value",
        fields=(JavaField(name="count", value_type=JavaValueType(kind="int32")),),
    )

    validate_java_value({"ready": True}, mapping)
    validate_java_value({"count": 1}, value_object)
    with pytest.raises(ValueError, match="map value is invalid"):
        validate_java_value({1: True}, mapping)
    with pytest.raises(ValueError, match="value-object fields are invalid"):
        validate_java_value({}, value_object)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"kind": "list"},
        {"kind": "string", "element": {"kind": "string"}},
        {"kind": "enum"},
        {"kind": "value-object"},
        {"kind": "enum", "enum_name": "bad-name!"},
    ],
)
def test_java_bridge_rejects_invalid_type_shapes(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        JavaValueType.model_validate(kwargs)


@pytest.mark.parametrize(
    "operation",
    [
        {
            "kind": "constructor",
            "operation_id": "bad id",
            "class_name": "example.Value",
        },
        {
            "kind": "constructor",
            "operation_id": "new",
            "class_name": "bad-name!",
        },
        {
            "kind": "static-method",
            "operation_id": "call",
            "class_name": "example.Value",
            "method_name": "bad-name!",
            "return_type": {"kind": "string"},
        },
        {
            "kind": "instance-method",
            "operation_id": "call",
            "class_name": "example.Value",
            "constructor_id": "bad id",
            "method_name": "call",
            "return_type": {"kind": "string"},
        },
        {
            "kind": "constructor",
            "operation_id": "new",
            "class_name": "example.Value",
            "parameters": [
                {"name": "value", "value_type": {"kind": "string"}},
                {"name": "value", "value_type": {"kind": "string"}},
            ],
        },
        {
            "kind": "constructor",
            "operation_id": "new",
            "class_name": "example.Value",
            "declared_exceptions": ["bad-name!"],
        },
    ],
)
def test_java_bridge_rejects_invalid_operation_fields(
    operation: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        JavaBridgeSpec.model_validate({"operations": [operation]})


def test_java_bridge_rejects_duplicate_ids_and_constructor_class_mismatch() -> None:
    constructor = JavaConstructorOperation(operation_id="new", class_name="example.One")
    with pytest.raises(ValidationError, match="IDs must be unique"):
        JavaBridgeSpec(operations=(constructor, constructor))
    with pytest.raises(ValidationError, match="constructor class does not match"):
        JavaBridgeSpec(
            operations=(
                constructor,
                JavaInstanceMethodOperation(
                    operation_id="call",
                    class_name="example.Two",
                    constructor_id="new",
                    method_name="call",
                    return_type=JavaValueType(kind="string"),
                ),
            )
        )


def test_java_bridge_rejects_oversized_spec_and_excessive_type_depth() -> None:
    with pytest.raises(ValueError, match="size limit"):
        load_java_bridge_spec(b" " * (1024 * 1024 + 1))
    nested = JavaValueType(kind="string")
    for _ in range(8):
        nested = JavaValueType(kind="list", element=nested)
    with pytest.raises(ValidationError, match="depth limit"):
        JavaBridgeSpec(
            operations=(
                JavaStaticMethodOperation(
                    operation_id="deep",
                    class_name="example.Value",
                    method_name="deep",
                    return_type=nested,
                ),
            )
        )

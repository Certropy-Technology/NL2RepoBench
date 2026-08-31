from __future__ import annotations

import json
from pathlib import PurePosixPath

import pytest

from nl2repobench.verification.java_bridge import (
    JavaBridgeSpec,
    JavaConstructorOperation,
    JavaInstanceMethodOperation,
    JavaParameter,
    JavaStaticMethodOperation,
    JavaValueType,
    load_java_bridge_spec,
    render_java_bridge,
    validate_java_value,
)


def _spec() -> JavaBridgeSpec:
    string = JavaValueType(kind="string")
    constructor = JavaConstructorOperation(
        operation_id="new-normalizer",
        class_name="example.api.Normalizer",
        parameters=(JavaParameter(name="prefix", value_type=string),),
        declared_exceptions=("java.lang.IllegalArgumentException",),
    )
    return JavaBridgeSpec(
        operations=(
            constructor,
            JavaInstanceMethodOperation(
                operation_id="normalize",
                constructor_id=constructor.operation_id,
                class_name=constructor.class_name,
                method_name="normalize",
                parameters=(JavaParameter(name="value", value_type=string),),
                return_type=string,
            ),
            JavaStaticMethodOperation(
                operation_id="parse",
                class_name="example.api.Parser",
                method_name="parse",
                parameters=(JavaParameter(name="value", value_type=string),),
                return_type=JavaValueType(kind="int32"),
            ),
        )
    )


def test_java_bridge_round_trip_and_render_are_deterministic() -> None:
    spec = _spec()
    data = json.dumps(
        spec.model_dump(mode="json", exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
    ).encode() + b"\n"
    assert load_java_bridge_spec(data) == spec
    first = render_java_bridge(spec)
    second = render_java_bridge(spec)
    assert first == second
    assert PurePosixPath("bridge-spec.json") in first
    source = next(value for path, value in first.items() if path.suffix == ".java")
    assert b"subprocess" not in source
    assert b"assert" not in source.lower()


def test_java_bridge_rejects_unbound_instance_and_recursive_overflow() -> None:
    string = JavaValueType(kind="string")
    with pytest.raises(ValueError, match="references no constructor"):
        JavaBridgeSpec(
            operations=(
                JavaInstanceMethodOperation(
                    operation_id="call",
                    constructor_id="missing",
                    class_name="example.Api",
                    method_name="call",
                    return_type=string,
                ),
            )
        )
    nested = string
    for _ in range(9):
        nested = JavaValueType(kind="list", element=nested)
    with pytest.raises(ValueError, match="depth limit"):
        JavaBridgeSpec(
            operations=(
                JavaStaticMethodOperation(
                    operation_id="deep",
                    class_name="example.Api",
                    method_name="deep",
                    return_type=nested,
                ),
            )
        )


def test_java_value_validation_is_bounded_and_finite() -> None:
    validate_java_value(42, JavaValueType(kind="int32"))
    validate_java_value(
        ["a", "b"], JavaValueType(kind="list", element=JavaValueType(kind="string"))
    )
    with pytest.raises(ValueError, match="float64"):
        validate_java_value(float("inf"), JavaValueType(kind="float64"))

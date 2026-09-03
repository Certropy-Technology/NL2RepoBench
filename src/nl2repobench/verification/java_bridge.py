"""Bounded Java bridge descriptor and transport-value validation.

The bridge specification describes only reviewed public operations. It never
contains hidden assertions and the renderer emits descriptors, not arbitrary
reflection or candidate-controlled Java code.
"""

# Generated Java descriptor lines are kept stable and compact.
# ruff: noqa: E501

from __future__ import annotations

import json
import math
import re
from base64 import b64decode
from binascii import Error as Base64Error
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_OPERATIONS = 1024
MAX_TYPE_DEPTH = 8
MAX_FIELDS = 256
MAX_COLLECTION_ITEMS = 10_000
MAX_PAYLOAD_BYTES = 1024 * 1024
MAX_GENERATED_BYTES = 4 * 1024 * 1024
SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")
BINARY_NAME = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*$")
MEMBER_NAME = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class JavaValueType(_StrictModel):
    kind: Literal[
        "string",
        "boolean",
        "int32",
        "int64",
        "float64",
        "bytes",
        "array",
        "list",
        "set",
        "string-map",
        "enum",
        "value-object",
    ]
    element: JavaValueType | None = None
    enum_name: str | None = None
    class_name: str | None = None
    fields: tuple[JavaField, ...] = ()

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        collection = self.kind in {"array", "list", "set", "string-map"}
        if collection != (self.element is not None):
            raise ValueError("Java collection/map types require exactly one element type")
        if (self.kind == "enum") != (self.enum_name is not None):
            raise ValueError("Java enum type requires exactly one enum binary name")
        if (self.kind == "value-object") != (self.class_name is not None):
            raise ValueError("Java value object requires exactly one binary class name")
        if self.kind != "value-object" and self.fields:
            raise ValueError("only Java value objects may declare fields")
        if len(self.fields) > MAX_FIELDS or len({field.name for field in self.fields}) != len(
            self.fields
        ):
            raise ValueError("Java value object fields exceed bounds or are duplicated")
        for name in (self.enum_name, self.class_name):
            if name is not None and not BINARY_NAME.fullmatch(name):
                raise ValueError("Java binary name is invalid")
        return self


class JavaField(_StrictModel):
    name: str
    value_type: JavaValueType

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not MEMBER_NAME.fullmatch(value):
            raise ValueError("Java field name is invalid")
        return value


JavaValueType.model_rebuild()


class JavaParameter(_StrictModel):
    name: str
    value_type: JavaValueType

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not MEMBER_NAME.fullmatch(value):
            raise ValueError("Java parameter name is invalid")
        return value


class _Operation(_StrictModel):
    operation_id: str
    class_name: str
    parameters: tuple[JavaParameter, ...] = ()
    declared_exceptions: tuple[str, ...] = ()

    @field_validator("operation_id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not SAFE_ID.fullmatch(value):
            raise ValueError("Java bridge operation ID is invalid")
        return value

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, value: str) -> str:
        if not BINARY_NAME.fullmatch(value):
            raise ValueError("Java binary class name is invalid")
        return value

    @model_validator(mode="after")
    def validate_parameters(self) -> Self:
        if len(self.parameters) > MAX_FIELDS or len({p.name for p in self.parameters}) != len(
            self.parameters
        ):
            raise ValueError("Java operation parameters exceed bounds or are duplicated")
        if len(self.declared_exceptions) > 64 or len(set(self.declared_exceptions)) != len(
            self.declared_exceptions
        ):
            raise ValueError("Java declared exceptions exceed bounds or are duplicated")
        if any(not BINARY_NAME.fullmatch(value) for value in self.declared_exceptions):
            raise ValueError("Java declared exception is invalid")
        return self


class JavaConstructorOperation(_Operation):
    kind: Literal["constructor"] = "constructor"


class JavaStaticMethodOperation(_Operation):
    kind: Literal["static-method"] = "static-method"
    method_name: str
    return_type: JavaValueType

    @field_validator("method_name")
    @classmethod
    def validate_method(cls, value: str) -> str:
        if not MEMBER_NAME.fullmatch(value):
            raise ValueError("Java method name is invalid")
        return value


class JavaInstanceMethodOperation(_Operation):
    kind: Literal["instance-method"] = "instance-method"
    constructor_id: str
    method_name: str
    return_type: JavaValueType

    @field_validator("constructor_id")
    @classmethod
    def validate_constructor_id(cls, value: str) -> str:
        if not SAFE_ID.fullmatch(value):
            raise ValueError("Java constructor operation ID is invalid")
        return value

    @field_validator("method_name")
    @classmethod
    def validate_method(cls, value: str) -> str:
        if not MEMBER_NAME.fullmatch(value):
            raise ValueError("Java instance member name is invalid")
        return value


JavaBridgeOperation = Annotated[
    JavaConstructorOperation | JavaStaticMethodOperation | JavaInstanceMethodOperation,
    Field(discriminator="kind"),
]


def _walk_type(value_type: JavaValueType, depth: int = 1) -> None:
    if depth > MAX_TYPE_DEPTH:
        raise ValueError("Java bridge value type exceeds the depth limit")
    if value_type.element is not None:
        _walk_type(value_type.element, depth + 1)
    for field in value_type.fields:
        _walk_type(field.value_type, depth + 1)


class JavaBridgeSpec(_StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    bridge_class: str = "nl2repobench.bridge.GeneratedBridge"
    operations: tuple[JavaBridgeOperation, ...]
    max_collection_items: Literal[10000] = 10000
    max_payload_bytes: Literal[1048576] = 1048576

    @model_validator(mode="after")
    def validate_operations(self) -> Self:
        if not BINARY_NAME.fullmatch(self.bridge_class):
            raise ValueError("generated Java bridge class name is invalid")
        if not self.operations or len(self.operations) > MAX_OPERATIONS:
            raise ValueError("Java bridge operation count is outside bounds")
        by_id = {operation.operation_id: operation for operation in self.operations}
        if len(by_id) != len(self.operations):
            raise ValueError("Java bridge operation IDs must be unique")
        for operation in self.operations:
            for parameter in operation.parameters:
                _walk_type(parameter.value_type)
            if isinstance(operation, (JavaStaticMethodOperation, JavaInstanceMethodOperation)):
                _walk_type(operation.return_type)
            if isinstance(operation, JavaInstanceMethodOperation):
                constructor = by_id.get(operation.constructor_id)
                if not isinstance(constructor, JavaConstructorOperation):
                    raise ValueError("Java instance operation references no constructor")
                if constructor.class_name != operation.class_name:
                    raise ValueError("Java instance operation constructor class does not match")
        return self


def load_java_bridge_spec(data: bytes) -> JavaBridgeSpec:
    if len(data) > MAX_PAYLOAD_BYTES:
        raise ValueError("Java bridge specification exceeds the size limit")
    try:
        spec = JavaBridgeSpec.model_validate(json.loads(data))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid Java bridge specification: {exc}") from exc
    canonical = (
        json.dumps(
            spec.model_dump(mode="json", exclude_none=True), sort_keys=True, separators=(",", ":")
        ).encode()
        + b"\n"
    )
    if data != canonical:
        raise ValueError("Java bridge specification JSON is not canonical")
    return spec


def render_java_bridge(spec: JavaBridgeSpec) -> dict[PurePosixPath, bytes]:
    """Render an assertion-free public operation descriptor class."""

    package, _, simple_name = spec.bridge_class.rpartition(".")
    rows = []
    for operation in spec.operations:
        member = (
            "<init>" if isinstance(operation, JavaConstructorOperation) else operation.method_name
        )
        rows.append(
            f"        new Operation({json.dumps(operation.operation_id)}, "
            f"{json.dumps(operation.kind)}, {json.dumps(operation.class_name)}, "
            f"{json.dumps(member)})"
        )
    package_line = f"package {package};\n\n" if package else ""
    source = (
        package_line
        + "// Generated public API descriptors. Candidate execution is verifier-owned.\n"
        + f"public final class {simple_name} {{\n"
        + "    public record Operation(String id, String kind, "
        + "String className, String member) {}\n"
        + "    public static final Operation[] OPERATIONS = {\n"
        + ",\n".join(rows)
        + "\n    };\n"
        + f"    private {simple_name}() {{}}\n"
        + "}\n"
    ).encode()
    if len(source) > MAX_GENERATED_BYTES:
        raise ValueError("generated Java bridge source exceeds the size limit")
    path = PurePosixPath("src/main/java", *package.split("."), f"{simple_name}.java")
    return {
        PurePosixPath("bridge-spec.json"): json.dumps(
            spec.model_dump(mode="json", exclude_none=True), sort_keys=True, separators=(",", ":")
        ).encode()
        + b"\n",
        path: source,
    }


def validate_java_value(value: object, value_type: JavaValueType, depth: int = 1) -> None:
    if depth > MAX_TYPE_DEPTH:
        raise ValueError("Java bridge value exceeds the depth limit")
    kind = value_type.kind
    if kind == "string":
        valid = isinstance(value, str) and len(value.encode()) <= MAX_PAYLOAD_BYTES
    elif kind == "boolean":
        valid = isinstance(value, bool)
    elif kind == "int32":
        valid = isinstance(value, int) and not isinstance(value, bool) and -(2**31) <= value < 2**31
    elif kind == "int64":
        valid = isinstance(value, int) and not isinstance(value, bool) and -(2**63) <= value < 2**63
    elif kind == "float64":
        valid = (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        )
    elif kind == "bytes":
        if not isinstance(value, str):
            valid = False
        else:
            try:
                valid = len(b64decode(value, validate=True)) <= MAX_PAYLOAD_BYTES
            except (Base64Error, ValueError):
                valid = False
    elif kind in {"array", "list", "set"}:
        if not isinstance(value, list) or len(value) > MAX_COLLECTION_ITEMS:
            raise ValueError(f"Java bridge {kind} value is invalid")
        if kind == "set" and len({json.dumps(item, sort_keys=True) for item in value}) != len(
            value
        ):
            raise ValueError(f"Java bridge {kind} value is invalid")
        assert value_type.element is not None
        for item in value:
            validate_java_value(item, value_type.element, depth + 1)
        return
    elif kind == "string-map":
        if not isinstance(value, dict) or len(value) > MAX_COLLECTION_ITEMS:
            raise ValueError("Java bridge map value is invalid")
        if not all(isinstance(key, str) for key in value):
            raise ValueError("Java bridge map value is invalid")
        assert value_type.element is not None
        for item in value.values():
            validate_java_value(item, value_type.element, depth + 1)
        return
    elif kind == "enum":
        valid = isinstance(value, str) and MEMBER_NAME.fullmatch(value) is not None
    elif kind == "value-object":
        expected = {field.name: field for field in value_type.fields}
        if not isinstance(value, dict) or set(value) != set(expected):
            raise ValueError("Java bridge value-object fields are invalid")
        for name, field in expected.items():
            validate_java_value(value[name], field.value_type, depth + 1)
        return
    else:
        raise ValueError(f"unsupported Java bridge value type: {kind}")
    if not valid:
        raise ValueError(f"Java bridge {kind} value is invalid")


__all__ = [
    "JavaBridgeSpec",
    "JavaConstructorOperation",
    "JavaField",
    "JavaInstanceMethodOperation",
    "JavaParameter",
    "JavaStaticMethodOperation",
    "JavaValueType",
    "load_java_bridge_spec",
    "render_java_bridge",
    "validate_java_value",
]

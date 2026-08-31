"""Strict Rust API-plan and bridge transport records for R0."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal, Never, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_API_PLAN_BYTES = 4 * 1024 * 1024
MAX_BRIDGE_JSON_BYTES = 8 * 1024 * 1024
MAX_VALUE_DEPTH = 16
MAX_VALUE_NODES = 4096
MAX_VALUE_BYTES = 256 * 1024
MAX_BRIDGE_ARGUMENTS = 2048
MAX_BRIDGE_RESULTS = 64
MAX_BRIDGE_VALUE_BYTES = 4 * 1024 * 1024

_SAFE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_RUST_PATH = re.compile(
    r"^crate::[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*$"
)
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_REQUEST_ID = re.compile(r"^[0-9a-f]{32}$")
_STATE_HANDLE = re.compile(r"^s(?:[0-9]|[12][0-9]|3[01])$")
_LOWER_HEX_8 = re.compile(r"^[0-9a-f]{8}$")
_LOWER_HEX_16 = re.compile(r"^[0-9a-f]{16}$")

PrimitiveType = Literal[
    "unit",
    "bool",
    "i8",
    "i16",
    "i32",
    "i64",
    "isize",
    "u8",
    "u16",
    "u32",
    "u64",
    "usize",
    "f32",
    "f64",
    "char",
    "string",
]
_PRIMITIVES = {
    "unit",
    "bool",
    "i8",
    "i16",
    "i32",
    "i64",
    "isize",
    "u8",
    "u16",
    "u32",
    "u64",
    "usize",
    "f32",
    "f64",
    "char",
    "string",
}


def _utf8_sorted_unique(values: tuple[str, ...], description: str) -> None:
    if tuple(sorted(values, key=lambda value: value.encode("utf-8"))) != values:
        raise ValueError(f"{description} must be sorted by UTF-8 bytes")
    if len(set(values)) != len(values):
        raise ValueError(f"{description} must be unique")


def _safe_id(value: str, description: str) -> str:
    if not _SAFE_ID.fullmatch(value):
        raise ValueError(f"{description} is not a SafeId")
    return value


class RustBridgeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class RustNamedTypeRef(RustBridgeRecord):
    name: str
    type: str

    @model_validator(mode="after")
    def validate_ref(self) -> Self:
        _safe_id(self.name, "descriptor field name")
        _safe_id(self.type, "descriptor type reference")
        return self


class RustVariantRef(RustBridgeRecord):
    name: str
    payload: str

    @model_validator(mode="after")
    def validate_ref(self) -> Self:
        _safe_id(self.name, "variant name")
        _safe_id(self.payload, "variant payload reference")
        return self


class RustTypeDescriptor(RustBridgeRecord):
    type_id: str
    kind: Literal["scalar", "bytes", "list", "map", "struct", "enum"]
    scalar: PrimitiveType | None
    item: str | None
    key: Literal["string"] | None
    fields: tuple[RustNamedTypeRef, ...]
    variants: tuple[RustVariantRef, ...]

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        _safe_id(self.type_id, "type ID")
        if self.item is not None:
            _safe_id(self.item, "item type reference")
        field_names = tuple(item.name for item in self.fields)
        variant_names = tuple(item.name for item in self.variants)
        _utf8_sorted_unique(field_names, f"type {self.type_id} fields")
        _utf8_sorted_unique(variant_names, f"type {self.type_id} variants")
        valid = {
            "scalar": self.scalar is not None
            and self.item is None
            and self.key is None
            and not self.fields
            and not self.variants,
            "bytes": self.scalar is None
            and self.item is None
            and self.key is None
            and not self.fields
            and not self.variants,
            "list": self.scalar is None
            and self.item is not None
            and self.key is None
            and not self.fields
            and not self.variants,
            "map": self.scalar is None
            and self.item is not None
            and self.key == "string"
            and not self.fields
            and not self.variants,
            "struct": self.scalar is None
            and self.item is None
            and self.key is None
            and bool(self.fields)
            and not self.variants,
            "enum": self.scalar is None
            and self.item is None
            and self.key is None
            and not self.fields
            and bool(self.variants),
        }[self.kind]
        if not valid:
            raise ValueError(f"type {self.type_id} has fields inconsistent with {self.kind}")
        return self


class RustArgumentDescriptor(RustBridgeRecord):
    name: str
    type: str

    @model_validator(mode="after")
    def validate_arg(self) -> Self:
        _safe_id(self.name, "argument name")
        _safe_id(self.type, "argument type reference")
        return self


class RustApiDescriptor(RustBridgeRecord):
    api_id: str
    rust_path: str
    kind: Literal["sync", "async", "associated", "instance"]
    receiver: str | None
    state_type: str | None
    args: Annotated[tuple[RustArgumentDescriptor, ...], Field(min_length=1, max_length=32)]
    returns: str
    error: str | None
    unsafe: bool
    leaf_ids: Annotated[tuple[str, ...], Field(min_length=1, max_length=64)]

    @model_validator(mode="after")
    def validate_api(self) -> Self:
        _safe_id(self.api_id, "API ID")
        if not _RUST_PATH.fullmatch(self.rust_path):
            raise ValueError("rust_path is outside the audited crate path grammar")
        for value, description in (
            (self.returns, "return type"),
            (self.error, "error type"),
            (self.receiver, "receiver type"),
            (self.state_type, "state type"),
        ):
            if value is not None:
                _safe_id(value, description)
        instance = self.kind == "instance"
        if instance != (self.receiver is not None and self.state_type is not None):
            raise ValueError("receiver and state_type are non-null exactly for instance APIs")
        argument_names = tuple(item.name for item in self.args)
        if len(set(argument_names)) != len(argument_names):
            raise ValueError("API argument names must be unique")
        _utf8_sorted_unique(self.leaf_ids, f"API {self.api_id} leaf IDs")
        for leaf_id in self.leaf_ids:
            _safe_id(leaf_id, "leaf ID")
        return self


class RustStateMethodDescriptor(RustBridgeRecord):
    api_id: str
    receiver: Literal["&self", "&mut self"]
    args: Annotated[tuple[RustArgumentDescriptor, ...], Field(max_length=32)]
    returns: str
    error: str | None
    state_type: str | None
    leaf_ids: Annotated[tuple[str, ...], Field(min_length=1, max_length=64)]

    @model_validator(mode="after")
    def validate_method(self) -> Self:
        for value, description in (
            (self.api_id, "state method API ID"),
            (self.returns, "state method return type"),
            (self.state_type, "state method state type"),
        ):
            if value is not None:
                _safe_id(value, description)
        if self.error is not None:
            _safe_id(self.error, "state method error type")
        _utf8_sorted_unique(self.leaf_ids, f"state method {self.api_id} leaf IDs")
        return self


class RustStateDescriptor(RustBridgeRecord):
    state_id: str
    rust_type: str
    create_api_id: str
    methods: tuple[RustStateMethodDescriptor, ...]
    drop_api_id: str | None

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        for value, description in (
            (self.state_id, "state ID"),
            (self.rust_type, "state Rust type"),
            (self.create_api_id, "state create API ID"),
            (self.drop_api_id, "state drop API ID"),
        ):
            if value is not None:
                _safe_id(value, description)
        method_ids = tuple(item.api_id for item in self.methods)
        _utf8_sorted_unique(method_ids, f"state {self.state_id} methods")
        return self


class RustCliDescriptor(RustBridgeRecord):
    profile_id: str
    binary_name: str

    @model_validator(mode="after")
    def validate_cli(self) -> Self:
        _safe_id(self.profile_id, "CLI profile ID")
        _safe_id(self.binary_name, "CLI binary name")
        return self


class RustApiPlan(RustBridgeRecord):
    schema_version: Literal["1.0"]
    package_name: str
    api_plan_digest: str
    types: tuple[RustTypeDescriptor, ...]
    functions: tuple[RustApiDescriptor, ...]
    state_types: tuple[RustStateDescriptor, ...]
    cli_profiles: tuple[RustCliDescriptor, ...]
    unsafe_leaf_ids: tuple[str, ...]

    @model_validator(mode="after")
    def validate_plan(self) -> Self:
        _safe_id(self.package_name, "package name")
        if not _DIGEST.fullmatch(self.api_plan_digest):
            raise ValueError("api_plan_digest must be a SHA-256 digest")
        type_ids = tuple(item.type_id for item in self.types)
        api_ids = tuple(item.api_id for item in self.functions)
        state_ids = tuple(item.state_id for item in self.state_types)
        cli_ids = tuple(item.profile_id for item in self.cli_profiles)
        for values, description in (
            (type_ids, "type IDs"),
            (api_ids, "API IDs"),
            (state_ids, "state IDs"),
            (cli_ids, "CLI profile IDs"),
            (self.unsafe_leaf_ids, "unsafe leaf IDs"),
        ):
            _utf8_sorted_unique(values, description)
        known_types = set(type_ids) | _PRIMITIVES

        def require_type(value: str | None) -> None:
            if value is not None and value not in known_types:
                raise ValueError(f"unknown Rust type reference: {value}")

        graph: dict[str, set[str]] = {type_id: set() for type_id in type_ids}
        for descriptor in self.types:
            references = [descriptor.item]
            references.extend(item.type for item in descriptor.fields)
            references.extend(item.payload for item in descriptor.variants)
            for reference in references:
                require_type(reference)
                if reference in graph:
                    graph[descriptor.type_id].add(reference)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(type_id: str) -> None:
            if type_id in visiting:
                raise ValueError("recursive Rust type descriptors are forbidden")
            if type_id in visited:
                return
            visiting.add(type_id)
            for child in graph[type_id]:
                visit(child)
            visiting.remove(type_id)
            visited.add(type_id)

        for type_id in type_ids:
            visit(type_id)

        all_leaf_ids: list[str] = []
        unsafe_leaf_ids: list[str] = []
        for function in self.functions:
            for argument in function.args:
                require_type(argument.type)
            for reference in (
                function.receiver,
                function.state_type,
                function.returns,
                function.error,
            ):
                require_type(reference)
            all_leaf_ids.extend(function.leaf_ids)
            if function.unsafe:
                unsafe_leaf_ids.extend(function.leaf_ids)
        if len(all_leaf_ids) != len(set(all_leaf_ids)):
            raise ValueError("leaf IDs must be unique across APIs")
        if tuple(sorted(unsafe_leaf_ids, key=lambda item: item.encode("utf-8"))) != (
            self.unsafe_leaf_ids
        ):
            raise ValueError("unsafe_leaf_ids must exactly name leaves of unsafe APIs")
        api_map = {item.api_id: item for item in self.functions}
        type_map = {item.type_id: item for item in self.types}
        for state in self.state_types:
            state_type = type_map.get(state.rust_type)
            if state_type is None or state_type.kind not in {"struct", "enum"}:
                raise ValueError("state rust_type must reference a named struct or enum")
            referenced_ids = [state.create_api_id, *(item.api_id for item in state.methods)]
            if state.drop_api_id is not None:
                referenced_ids.append(state.drop_api_id)
            if any(api_id not in api_map for api_id in referenced_ids):
                raise ValueError("state descriptor references an unknown API")
            if api_map[state.create_api_id].returns != state.rust_type:
                raise ValueError("state create API must return the state type")
            create = api_map[state.create_api_id]
            if (
                create.kind == "instance"
                or create.receiver is not None
                or create.state_type is not None
            ):
                raise ValueError("state create API must be an associated, receiver-free API")
            for method in state.methods:
                api = api_map[method.api_id]
                require_type(method.returns)
                require_type(method.error)
                if (
                    api.kind != "instance"
                    or api.receiver != state.rust_type
                    or api.state_type != method.state_type
                    or api.args != method.args
                    or api.returns != method.returns
                    or api.error != method.error
                    or api.leaf_ids != method.leaf_ids
                ):
                    raise ValueError(
                        f"state method {method.api_id} does not exactly match its API descriptor"
                    )
                if method.state_type != state.rust_type:
                    raise ValueError("state method must bind its descriptor state type")
            if state.drop_api_id is not None:
                drop = api_map[state.drop_api_id]
                if (
                    drop.kind != "instance"
                    or drop.receiver != state.rust_type
                    or drop.state_type != state.rust_type
                    or drop.returns != "unit"
                    or drop.error is not None
                ):
                    raise ValueError("state drop API has an invalid descriptor role")
        return self


def _freeze_json(value: object) -> object:
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    if isinstance(value, dict):
        return {key: _freeze_json(item) for key, item in value.items()}
    return value


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_api_plan_digest(plan: RustApiPlan) -> str:
    payload = plan.model_dump(mode="json")
    del payload["api_plan_digest"]
    return f"sha256:{hashlib.sha256(canonical_json_bytes(payload)).hexdigest()}"


def canonical_api_plan_bytes(plan: RustApiPlan) -> bytes:
    return canonical_json_bytes(plan.model_dump(mode="json"))


def load_rust_api_plan(path: Path) -> tuple[RustApiPlan, bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("rust-api-plan.json must be a regular file")
    try:
        if path.stat().st_size > MAX_API_PLAN_BYTES:
            raise ValueError("rust-api-plan.json exceeds the size limit")
        raw = path.read_bytes()
        parsed = json.loads(raw, object_pairs_hook=_no_duplicate_object)
        plan = RustApiPlan.model_validate(_freeze_json(parsed))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid rust-api-plan.json: {exc}") from exc
    if canonical_api_plan_bytes(plan) != raw:
        raise ValueError("rust-api-plan.json must use canonical JSON bytes and one final LF")
    if canonical_api_plan_digest(plan) != plan.api_plan_digest:
        raise ValueError("rust-api-plan.json canonical-plan digest does not match")
    return plan, raw


_INTEGER_RANGES = {
    "i8": (-(2**7), 2**7 - 1),
    "i16": (-(2**15), 2**15 - 1),
    "i32": (-(2**31), 2**31 - 1),
    "i64": (-(2**63), 2**63 - 1),
    "isize": (-(2**63), 2**63 - 1),
    "u8": (0, 2**8 - 1),
    "u16": (0, 2**16 - 1),
    "u32": (0, 2**32 - 1),
    "u64": (0, 2**64 - 1),
    "usize": (0, 2**64 - 1),
}


class _ValueBudget:
    def __init__(self) -> None:
        self.nodes = 0
        self.bytes = 0


def validate_rust_value(
    value: object, *, _budget: _ValueBudget | None = None
) -> dict[str, Any]:
    """Validate the bounded RustValue v1 grammar without coercion."""

    budget = _budget or _ValueBudget()

    def visit(item: object, depth: int) -> dict[str, Any]:
        budget.nodes += 1
        if budget.nodes > MAX_VALUE_NODES or depth > MAX_VALUE_DEPTH:
            raise ValueError("RustValue exceeds depth or node limits")
        if not isinstance(item, dict) or not isinstance(item.get("type"), str):
            raise ValueError("RustValue must be a tagged object")
        kind = item["type"]
        if kind == "unit":
            expected = {"type"}
        elif kind == "bool":
            expected = {"type", "value"}
            if not isinstance(item.get("value"), bool):
                raise ValueError("bool RustValue requires a boolean")
        elif kind in _INTEGER_RANGES:
            expected = {"type", "value"}
            raw = item.get("value")
            if not isinstance(raw, str) or not re.fullmatch(r"(?:0|-[1-9][0-9]*|[1-9][0-9]*)", raw):
                raise ValueError("integer RustValue requires canonical decimal")
            number = int(raw)
            minimum, maximum = _INTEGER_RANGES[kind]
            if number < minimum or number > maximum:
                raise ValueError("integer RustValue is out of range")
        elif kind in {"f32", "f64"}:
            expected = {"type", "bits"}
            bits = item.get("bits")
            pattern = _LOWER_HEX_8 if kind == "f32" else _LOWER_HEX_16
            if not isinstance(bits, str) or not pattern.fullmatch(bits):
                raise ValueError("float RustValue requires fixed lowercase hex bits")
        elif kind == "char":
            expected = {"type", "value"}
            char = item.get("value")
            if not isinstance(char, str) or len(char) != 1 or 0xD800 <= ord(char) <= 0xDFFF:
                raise ValueError("char RustValue requires one Unicode scalar")
        elif kind == "string":
            expected = {"type", "value"}
            text = item.get("value")
            if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_VALUE_BYTES:
                raise ValueError("string RustValue is invalid or oversized")
            budget.bytes += len(text.encode("utf-8"))
        elif kind == "bytes":
            expected = {"type", "base64"}
            encoded = item.get("base64")
            decoded = _decode_canonical_base64(encoded)
            if len(decoded) > MAX_VALUE_BYTES:
                raise ValueError("bytes RustValue exceeds the size limit")
            budget.bytes += len(decoded)
        elif kind == "list":
            expected = {"type", "items"}
            items = item.get("items")
            if not isinstance(items, list):
                raise ValueError("list RustValue requires an array")
            for child in items:
                visit(child, depth + 1)
        elif kind == "map":
            expected = {"type", "entries"}
            entries = item.get("entries")
            if not isinstance(entries, list):
                raise ValueError("map RustValue requires entries")
            keys: list[str] = []
            for entry in entries:
                if not isinstance(entry, dict) or set(entry) != {"key", "value"}:
                    raise ValueError("map entry shape is invalid")
                key = entry["key"]
                if not isinstance(key, str):
                    raise ValueError("map key must be a string")
                keys.append(key)
                visit(entry["value"], depth + 1)
            _utf8_sorted_unique(tuple(keys), "RustValue map keys")
        elif kind == "struct":
            expected = {"type", "name", "fields"}
            struct_name = item.get("name")
            if not isinstance(struct_name, str):
                raise ValueError("RustValue struct name must be a string")
            _safe_id(struct_name, "RustValue struct name")
            fields = item.get("fields")
            if not isinstance(fields, list):
                raise ValueError("struct RustValue requires fields")
            names: list[str] = []
            for field in fields:
                if not isinstance(field, dict) or set(field) != {"name", "value"}:
                    raise ValueError("struct field shape is invalid")
                name = field["name"]
                if not isinstance(name, str):
                    raise ValueError("struct field name must be a string")
                _safe_id(name, "RustValue field name")
                names.append(name)
                visit(field["value"], depth + 1)
            _utf8_sorted_unique(tuple(names), "RustValue struct fields")
        elif kind == "enum":
            expected = {"type", "name", "variant", "payload"}
            enum_name = item.get("name")
            variant = item.get("variant")
            if not isinstance(enum_name, str) or not isinstance(variant, str):
                raise ValueError("RustValue enum name and variant must be strings")
            _safe_id(enum_name, "RustValue enum name")
            _safe_id(variant, "RustValue enum variant")
            payload = item.get("payload")
            validated = visit(payload, depth + 1)
            if validated["type"] not in {"unit", "list", "struct"}:
                raise ValueError("enum payload must be unit, list, or struct")
        else:
            raise ValueError(f"unknown RustValue type: {kind}")
        if set(item) != expected:
            raise ValueError(f"RustValue {kind} fields are invalid")
        return item

    return visit(value, 1)


def _decode_canonical_base64(value: object) -> bytes:
    if not isinstance(value, str):
        raise ValueError("base64 value must be a string")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("base64 value is malformed") from exc
    if base64.b64encode(decoded).decode("ascii") != value:
        raise ValueError("base64 value is not canonical RFC 4648")
    return decoded


class RustOperation(RustBridgeRecord):
    operation_id: str
    api_id: str
    leaf_id: str
    kind: Literal["call", "state-create", "state-call", "state-drop"]
    state_handle: str | None
    args: tuple[dict[str, Any], ...]

    @model_validator(mode="after")
    def validate_operation(self) -> Self:
        for value, description in (
            (self.operation_id, "operation ID"),
            (self.api_id, "operation API ID"),
            (self.leaf_id, "operation leaf ID"),
        ):
            _safe_id(value, description)
        if self.operation_id == self.leaf_id:
            raise ValueError("operation_id must be distinct from leaf_id")
        if self.state_handle is not None and not _STATE_HANDLE.fullmatch(self.state_handle):
            raise ValueError("state handle is invalid")
        if self.kind in {"state-call", "state-drop"} and self.state_handle is None:
            raise ValueError("state call/drop requires a handle")
        if self.kind in {"call", "state-create"} and self.state_handle is not None:
            raise ValueError("call/state-create cannot carry a state handle")
        for argument_value in self.args:
            validate_rust_value(argument_value)
        return self


class RustBridgeRequest(RustBridgeRecord):
    schema_version: Literal["1.0"]
    request_id: str
    operations: Annotated[tuple[RustOperation, ...], Field(min_length=1, max_length=64)]

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if not _REQUEST_ID.fullmatch(self.request_id):
            raise ValueError("request_id must be 32 lowercase hex characters")
        operation_ids = tuple(item.operation_id for item in self.operations)
        leaf_ids = tuple(item.leaf_id for item in self.operations)
        if len(set(operation_ids)) != len(operation_ids):
            raise ValueError("operation IDs must be unique within a request")
        if len(set(leaf_ids)) != len(leaf_ids):
            raise ValueError("leaf IDs must be unique within a request")
        argument_count = sum(len(operation.args) for operation in self.operations)
        if argument_count > MAX_BRIDGE_ARGUMENTS:
            raise ValueError("bridge request exceeds the aggregate argument limit")
        budget = _ValueBudget()
        for operation in self.operations:
            for argument_value in operation.args:
                validate_rust_value(argument_value, _budget=budget)
                budget.bytes += len(canonical_json_bytes(argument_value))
        if budget.bytes > MAX_BRIDGE_VALUE_BYTES:
            raise ValueError("bridge request exceeds the aggregate value-byte limit")
        return self


class RustOperationResult(RustBridgeRecord):
    operation_id: str
    status: Literal["ok", "declared-error", "panic"]
    value: dict[str, Any] | None
    error_type: str | None
    message: Annotated[str | None, Field(max_length=4096)]
    state_handle: str | None

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        _safe_id(self.operation_id, "result operation ID")
        if self.value is not None:
            validate_rust_value(self.value)
        if self.error_type is not None:
            _safe_id(self.error_type, "result error type")
        if self.state_handle is not None and not _STATE_HANDLE.fullmatch(self.state_handle):
            raise ValueError("result state handle is invalid")
        if self.status == "panic" and (
            self.value is not None or self.error_type != "panic" or self.message is None
        ):
            raise ValueError("panic result fields are inconsistent")
        if self.status == "ok" and (self.error_type is not None or self.message is not None):
            raise ValueError("ok result cannot contain error fields")
        if self.status == "declared-error" and (
            self.value is None or self.error_type is None or self.message is not None
        ):
            raise ValueError("declared-error result fields are inconsistent")
        return self


class RustBridgeResponse(RustBridgeRecord):
    schema_version: Literal["1.0"]
    request_id: str
    results: tuple[RustOperationResult, ...]

    @model_validator(mode="after")
    def validate_response(self) -> Self:
        if not _REQUEST_ID.fullmatch(self.request_id):
            raise ValueError("response request_id must be 32 lowercase hex characters")
        operation_ids = tuple(item.operation_id for item in self.results)
        if len(set(operation_ids)) != len(operation_ids):
            raise ValueError("response operation IDs must be unique")
        if len(self.results) > MAX_BRIDGE_RESULTS:
            raise ValueError("bridge response exceeds the result limit")
        budget = _ValueBudget()
        for result in self.results:
            if result.value is not None:
                validate_rust_value(result.value, _budget=budget)
                budget.bytes += len(canonical_json_bytes(result.value))
        if budget.bytes > MAX_BRIDGE_VALUE_BYTES:
            raise ValueError("bridge response exceeds the aggregate value-byte limit")
        return self


def _reject_json_constant(value: str) -> Never:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _load_bridge_json(raw: bytes, model: type[RustBridgeRecord]) -> RustBridgeRecord:
    if len(raw) > MAX_BRIDGE_JSON_BYTES:
        raise ValueError("Rust bridge JSON exceeds the size limit")
    try:
        parsed = json.loads(
            raw,
            object_pairs_hook=_no_duplicate_object,
            parse_constant=_reject_json_constant,
        )
        value = _freeze_json(parsed)
        result = model.model_validate(value)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid Rust bridge JSON: {exc}") from exc
    if canonical_json_bytes(result.model_dump(mode="json")) != raw:
        raise ValueError("Rust bridge JSON must use canonical bytes and one final LF")
    return result


def load_rust_bridge_request(raw: bytes) -> RustBridgeRequest:
    return _load_bridge_json(raw, RustBridgeRequest)  # type: ignore[return-value]


def load_rust_bridge_response(
    raw: bytes, request: RustBridgeRequest | None = None
) -> RustBridgeResponse:
    response = _load_bridge_json(raw, RustBridgeResponse)
    assert isinstance(response, RustBridgeResponse)
    if request is not None:
        if response.request_id != request.request_id:
            raise ValueError("bridge response request_id does not match request")
        expected = {operation.operation_id for operation in request.operations}
        actual = {result.operation_id for result in response.results}
        if actual != expected:
            raise ValueError("bridge response operation IDs do not match request")
    return response


__all__ = [
    "MAX_API_PLAN_BYTES",
    "MAX_BRIDGE_ARGUMENTS",
    "MAX_BRIDGE_JSON_BYTES",
    "MAX_BRIDGE_RESULTS",
    "MAX_BRIDGE_VALUE_BYTES",
    "RustApiPlan",
    "RustBridgeRequest",
    "RustBridgeResponse",
    "canonical_api_plan_bytes",
    "canonical_api_plan_digest",
    "canonical_json_bytes",
    "load_rust_api_plan",
    "load_rust_bridge_request",
    "load_rust_bridge_response",
    "validate_rust_value",
]

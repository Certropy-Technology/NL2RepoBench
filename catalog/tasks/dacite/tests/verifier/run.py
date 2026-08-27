from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from nl2repobench.verification.process_cleanup import terminate_uid_processes


CANDIDATE_UID = 10001
MAX_OUTPUT_BYTES = 1024 * 1024
PER_CASE_TIMEOUT_SEC = 3.0
TOTAL_TIMEOUT_SEC = 150.0
PROBE = Path(__file__).with_name("probe.py").read_text(encoding="utf-8")


def field(name: str, type_spec: Any, **options: Any) -> dict[str, Any]:
    return {"name": name, "type": type_spec, **options}


def cls(name: str, *fields: dict[str, Any], **options: Any) -> dict[str, Any]:
    return {"name": name, "fields": list(fields), **options}


def dc(class_name: str, **fields: Any) -> dict[str, Any]:
    return {"__class__": class_name, "fields": fields}


def tuple_value(*items: Any) -> dict[str, Any]:
    return {"__tuple__": list(items)}


def set_value(*items: Any) -> dict[str, Any]:
    return {"__set__": list(items)}


def success(identifier: str, request: dict[str, Any], value: Any) -> dict[str, Any]:
    return {"id": identifier, "request": request, "expected": {"ok": True, "value": value}}


def failure(
    identifier: str,
    request: dict[str, Any],
    exception_type: str,
    *,
    field_path: str | None = None,
    message_contains: str | None = None,
    keys: list[str] | None = None,
    union_matches: list[str] | None = None,
) -> dict[str, Any]:
    expected: dict[str, Any] = {"ok": False, "type": exception_type}
    if field_path is not None:
        expected["field_path"] = field_path
    if message_contains is not None:
        expected["message_contains"] = message_contains
    if keys is not None:
        expected["keys"] = keys
    if union_matches is not None:
        expected["union_matches"] = union_matches
    return {"id": identifier, "request": request, "expected": expected}


def convert(
    classes: list[dict[str, Any]],
    target: Any,
    data: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
    enums: list[dict[str, Any]] | None = None,
    newtypes: list[dict[str, Any]] | None = None,
    typevars: list[str] | None = None,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "operation": "convert",
        "classes": classes,
        "target": target,
        "data": data,
    }
    if config:
        request["config"] = config
    if enums:
        request["enums"] = enums
    if newtypes:
        request["newtypes"] = newtypes
    if typevars:
        request["typevars"] = typevars
    return request


CASES = [
    success(
        "root-exports",
        {"operation": "exports"},
        {
            "all": [
                "set_cache_size", "get_cache_size", "clear_cache", "Config", "from_dict",
                "DaciteError", "DaciteFieldError", "WrongTypeError", "MissingValueError",
                "UnionMatchError", "StrictUnionMatchError", "ForwardReferenceError",
                "UnexpectedDataError",
            ],
            "module": "dacite.core",
        },
    ),
    success(
        "config-defaults",
        {"operation": "config-defaults"},
        {
            "type_hooks": {}, "cast": [], "forward_references": None,
            "check_types": True, "strict": False, "strict_unions_match": False,
            "convert_key_identity": "some_field",
        },
    ),
    success(
        "distribution-metadata",
        {"operation": "metadata"},
        {"version": "1.9.2", "requires": ['dataclasses; python_version < "3.7"']},
    ),
    success(
        "cache-size",
        {"operation": "cache", "size": 64},
        {"before": 2048, "after": 64},
    ),
    success(
        "exception-hierarchy",
        {"operation": "exception-hierarchy"},
        {
            "DaciteError": ["DaciteError", "Exception", "BaseException", "object"],
            "DaciteFieldError": ["DaciteFieldError", "DaciteError", "Exception", "BaseException"],
            "WrongTypeError": ["WrongTypeError", "DaciteFieldError", "DaciteError", "Exception"],
            "MissingValueError": ["MissingValueError", "DaciteFieldError", "DaciteError", "Exception"],
            "UnionMatchError": ["UnionMatchError", "WrongTypeError", "DaciteFieldError", "DaciteError"],
            "StrictUnionMatchError": ["StrictUnionMatchError", "DaciteFieldError", "DaciteError", "Exception"],
            "ForwardReferenceError": ["ForwardReferenceError", "DaciteError", "Exception", "BaseException"],
            "UnexpectedDataError": ["UnexpectedDataError", "DaciteError", "Exception", "BaseException"],
        },
    ),
    success(
        "basic-dataclass",
        convert([cls("User", field("name", "str"), field("age", "int"), field("active", "bool"))], "User", {"name": "Ada", "age": 37, "active": True}),
        dc("User", name="Ada", age=37, active=True),
    ),
    success(
        "nested-dataclass",
        convert([cls("Address", field("city", "str")), cls("User", field("name", "str"), field("address", {"ref": "Address"}))], "User", {"name": "Ada", "address": {"city": "London"}}),
        dc("User", name="Ada", address=dc("Address", city="London")),
    ),
    success(
        "list-of-dataclasses",
        convert([cls("Item", field("value", "int")), cls("Batch", field("items", {"list": {"ref": "Item"}}))], "Batch", {"items": [{"value": 1}, {"value": 2}]}),
        dc("Batch", items=[dc("Item", value=1), dc("Item", value=2)]),
    ),
    success(
        "mapping-of-dataclasses",
        convert([cls("Item", field("value", "int")), cls("Catalog", field("items", {"dict": ["str", {"ref": "Item"}]}))], "Catalog", {"items": {"one": {"value": 1}}}),
        dc("Catalog", items={"one": dc("Item", value=1)}),
    ),
    success(
        "fixed-tuple",
        convert([cls("Pair", field("value", {"tuple": ["str", "int"]}))], "Pair", {"value": tuple_value("a", 1)}),
        dc("Pair", value=tuple_value("a", 1)),
    ),
    success(
        "variadic-tuple",
        convert([cls("Numbers", field("value", {"tuple_variadic": "int"}))], "Numbers", {"value": tuple_value(1, 2, 3)}),
        dc("Numbers", value=tuple_value(1, 2, 3)),
    ),
    success(
        "set-values",
        convert([cls("Tags", field("value", {"set": "str"}))], "Tags", {"value": set_value("b", "a")}),
        dc("Tags", value=set_value("a", "b")),
    ),
    success(
        "optional-missing",
        convert([cls("Maybe", field("name", "str"), field("count", {"optional": "int"}))], "Maybe", {"name": "x"}),
        dc("Maybe", name="x", count=None),
    ),
    success(
        "optional-null",
        convert([cls("Maybe", field("count", {"optional": "int"}))], "Maybe", {"count": None}),
        dc("Maybe", count=None),
    ),
    success(
        "field-default",
        convert([cls("Defaults", field("name", "str", default="unknown"), field("count", "int", default=3))], "Defaults", {}),
        dc("Defaults", name="unknown", count=3),
    ),
    success(
        "fresh-default-factory",
        convert([cls("Defaults", field("items", {"list": "str"}, default_factory="list"))], "Defaults", {}),
        dc("Defaults", items=[]),
    ),
    failure(
        "missing-required",
        convert([cls("Required", field("name", "str"))], "Required", {}),
        "dacite.exceptions.MissingValueError", field_path="name", message_contains='missing value for field "name"',
    ),
    failure(
        "wrong-primitive-type",
        convert([cls("Typed", field("count", "int"))], "Typed", {"count": "one"}),
        "dacite.exceptions.WrongTypeError", field_path="count", message_contains='should be "int"',
    ),
    success(
        "disabled-type-checking",
        convert([cls("Typed", field("count", "int"))], "Typed", {"count": "one"}, config={"check_types": False}),
        dc("Typed", count="one"),
    ),
    success(
        "extra-data-ignored",
        convert([cls("Loose", field("name", "str"))], "Loose", {"name": "x", "extra": 1}),
        dc("Loose", name="x"),
    ),
    failure(
        "strict-extra-data",
        convert([cls("Strict", field("name", "str"))], "Strict", {"name": "x", "extra": 1}, config={"strict": True}),
        "dacite.exceptions.UnexpectedDataError", message_contains='"extra"', keys=set_value("extra"),
    ),
    success(
        "type-hook",
        convert([cls("Hooked", field("name", "str"))], "Hooked", {"name": "LOUD"}, config={"type_hooks": [{"type": "str", "hook": "lower"}]}),
        dc("Hooked", name="loud"),
    ),
    success(
        "nested-type-hook",
        convert([cls("Hooked", field("items", {"list": "str"}))], "Hooked", {"items": ["A", "B"]}, config={"type_hooks": [{"type": "str", "hook": "lower"}]}),
        dc("Hooked", items=["a", "b"]),
    ),
    success(
        "primitive-cast",
        convert([cls("Cast", field("count", "int"))], "Cast", {"count": "7"}, config={"cast": ["int"]}),
        dc("Cast", count=7),
    ),
    success(
        "enum-base-cast",
        convert([cls("Paint", field("color", {"enum": "Color"}))], "Paint", {"color": "red"}, config={"cast": ["enum.Enum"]}, enums=[{"name": "Color", "members": {"RED": "red", "BLUE": "blue"}}]),
        dc("Paint", color={"__enum__": "Color.RED", "value": "red"}),
    ),
    success(
        "mixed-tuple-cast-from-list",
        convert([cls("Pair", field("value", {"tuple": ["str", "int"]}))], "Pair", {"value": ["a", "1"]}, config={"cast": ["int", "tuple"]}),
        dc("Pair", value=tuple_value("a", 1)),
    ),
    success(
        "convert-key",
        convert([cls("Person", field("first_name", "str"), field("last_name", "str"))], "Person", {"firstName": "Ada", "lastName": "Lovelace"}, config={"convert_key": "camel"}),
        dc("Person", first_name="Ada", last_name="Lovelace"),
    ),
    success(
        "union-first-match",
        convert([cls("Value", field("item", {"union": ["int", "str"]}))], "Value", {"item": 3}),
        dc("Value", item=3),
    ),
    success(
        "union-dataclass-match",
        convert([cls("Left", field("left", "int")), cls("Right", field("right", "str")), cls("Choice", field("value", {"union": [{"ref": "Left"}, {"ref": "Right"}]}))], "Choice", {"value": {"right": "ok"}}),
        dc("Choice", value=dc("Right", right="ok")),
    ),
    failure(
        "union-no-match",
        convert([cls("Choice", field("value", {"union": ["int", "float"]}))], "Choice", {"value": "bad"}),
        "dacite.exceptions.UnionMatchError", field_path="value", message_contains="can not match type",
    ),
    failure(
        "strict-union-ambiguity",
        convert([cls("Left", field("value", "int")), cls("Right", field("value", "int")), cls("Choice", field("item", {"union": [{"ref": "Left"}, {"ref": "Right"}]}))], "Choice", {"item": {"value": 1}}, config={"strict_unions_match": True}),
        "dacite.exceptions.StrictUnionMatchError", field_path="item", message_contains="Left, Right", union_matches=["__main__.Left", "__main__.Right"],
    ),
    success(
        "strict-union-single-match",
        convert([cls("Left", field("value", "str")), cls("Right", field("value", "int")), cls("Choice", field("item", {"union": [{"ref": "Left"}, {"ref": "Right"}]}))], "Choice", {"item": {"value": 1}}, config={"strict_unions_match": True}),
        dc("Choice", item=dc("Right", value=1)),
    ),
    success(
        "forward-reference",
        convert([cls("Target", field("text", "str")), cls("Holder", field("target", {"forward": "Target"}))], "Holder", {"target": {"text": "ok"}}, config={"forward_references": {"Target": {"ref": "Target"}}}),
        dc("Holder", target=dc("Target", text="ok")),
    ),
    failure(
        "missing-forward-reference",
        convert([cls("Holder", field("target", {"forward": "Missing"}))], "Holder", {"target": {"text": "no"}}),
        "dacite.exceptions.ForwardReferenceError", message_contains="name 'Missing' is not defined",
    ),
    success(
        "new-type",
        convert([cls("Identifier", field("value", {"newtype": "UserId"}))], "Identifier", {"value": "abc"}, newtypes=[{"name": "UserId", "type": "str"}]),
        dc("Identifier", value="abc"),
    ),
    success(
        "literal-value",
        convert([cls("Mode", field("value", {"literal": ["A", "B"]}))], "Mode", {"value": "A"}),
        dc("Mode", value="A"),
    ),
    failure(
        "literal-wrong-value",
        convert([cls("Mode", field("value", {"literal": ["A", "B"]}))], "Mode", {"value": "C"}),
        "dacite.exceptions.WrongTypeError", field_path="value", message_contains="Literal",
    ),
    success(
        "non-init-field",
        convert([cls("Computed", field("name", "str"), field("hidden", "int", init=False, default=9))], "Computed", {"name": "x", "hidden": 4}),
        dc("Computed", name="x", hidden=4),
    ),
    success(
        "frozen-default",
        convert([cls("Frozen", field("name", "str", default="fixed"), frozen=True)], "Frozen", {}),
        dc("Frozen", name="fixed"),
    ),
    success(
        "post-init-derived-field",
        convert([cls("Total", field("left", "int"), field("right", "int"), field("total", "int", init=False, default=0), frozen=True, post_init="sum-total")], "Total", {"left": 2, "right": 3}),
        dc("Total", left=2, right=3, total=5),
    ),
    success(
        "init-var",
        convert([cls("Prepared", field("raw", {"initvar": "int"}), field("value", "int", init=False, default=0), frozen=True, post_init="copy-raw")], "Prepared", {"raw": 7}),
        dc("Prepared", value=7),
    ),
    success(
        "type-field",
        convert([cls("Typed", field("kind", {"type": "int"}))], "Typed", {"kind": {"__type__": "int"}}),
        dc("Typed", kind={"__type__": "builtins.int"}),
    ),
    success(
        "generic-dataclass",
        convert([cls("Box", field("value", {"typevar": "T"}), generic=["T"])], {"generic": {"ref": "Box", "args": ["int"]}}, {"value": 9}, typevars=["T"]),
        dc("Box", value=9),
    ),
    success(
        "nested-generic-dataclass",
        convert([cls("Item", field("name", "str")), cls("Box", field("value", {"typevar": "T"}), generic=["T"]), cls("Holder", field("box", {"generic": {"ref": "Box", "args": [{"ref": "Item"}]}}))], "Holder", {"box": {"value": {"name": "inside"}}}, typevars=["T"]),
        dc("Holder", box=dc("Box", value=dc("Item", name="inside"))),
    ),
    success(
        "any-value",
        convert([cls("Open", field("value", "Any"))], "Open", {"value": {"nested": [1, "two"]}}),
        dc("Open", value={"nested": [1, "two"]}),
    ),
]


def _run_probe(request: dict[str, Any], deadline: float) -> dict[str, Any]:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("candidate cumulative execution budget exhausted")
    timeout = min(PER_CASE_TIMEOUT_SEC, remaining)
    environment = [
        "HOME=/home/candidate",
        "PYTHONDONTWRITEBYTECODE=1",
    ]
    dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    if dependency_root:
        environment.append(f"NL2REPO_CANDIDATE_DEPENDENCIES={dependency_root}")
    command = [
        "runuser", "-u", "candidate", "--", "env", *environment,
        "prlimit", "--as=536870912", "--cpu=8", "--fsize=1048576",
        "--nofile=64", "--nproc=32", "--",
        sys.executable, "-I", "-B", "-c", PROBE,
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(
            json.dumps(request, ensure_ascii=False, separators=(",", ":")),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        raise TimeoutError(f"candidate case exceeded {timeout:.1f}s") from None
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        terminate_uid_processes(CANDIDATE_UID)
    if len(stdout.encode("utf-8")) > MAX_OUTPUT_BYTES or len(stderr.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise RuntimeError("candidate output exceeds size limit")
    if process.returncode != 0:
        raise RuntimeError((stderr or stdout or "candidate probe failed")[-2000:])
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("candidate probe produced an invalid response count")
    payload = json.loads(lines[0])
    if not isinstance(payload, dict) or payload.get("ok") not in {True, False}:
        raise RuntimeError("candidate probe response has invalid shape")
    return payload


def _matches(payload: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, str]:
    if payload.get("ok") is not expected["ok"]:
        return False, f"expected ok={expected['ok']}, got {payload!r}"
    if expected["ok"]:
        if payload.get("value") != expected["value"]:
            return False, f"value mismatch: expected {expected['value']!r}, got {payload.get('value')!r}"
        return True, ""
    exception = payload.get("exception")
    if not isinstance(exception, dict):
        return False, f"missing exception payload: {payload!r}"
    if exception.get("type") != expected["type"]:
        return False, f"exception type mismatch: {exception!r}"
    for name in ("field_path", "keys", "union_matches"):
        if name in expected and exception.get(name) != expected[name]:
            return False, f"exception {name} mismatch: expected {expected[name]!r}, got {exception.get(name)!r}"
    if "message_contains" in expected and expected["message_contains"] not in exception.get("message", ""):
        return False, f"exception message mismatch: {exception.get('message')!r}"
    return True, ""


deadline = time.monotonic() + TOTAL_TIMEOUT_SEC
leaves: list[dict[str, str]] = []
for case in CASES:
    try:
        payload = _run_probe(case["request"], deadline)
        passed, message = _matches(payload, case["expected"])
    except BaseException as error:
        passed, message = False, f"{type(error).__name__}: {error}"
    leaf = {"id": case["id"], "status": "passed" if passed else "failed"}
    if message:
        leaf["message"] = message[:2000]
    leaves.append(leaf)

print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))

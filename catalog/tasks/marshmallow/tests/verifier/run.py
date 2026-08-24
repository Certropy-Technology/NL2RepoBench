"""Trusted marshmallow verifier: declarative JSON scenarios over a subprocess boundary."""

import json
import os
import subprocess
import sys
from pathlib import Path

EXPECTED = 33
ADAPTER = Path(__file__).with_name("adapter.py")


def field(kind, **spec):
    return dict(spec, type=kind)


def schema(fields, name="ScenarioSchema", meta=None):
    value = {"fields": fields, "name": name}
    if meta is not None:
        value["meta"] = meta
    return value


PERSON = {
    "name": field("String", args={"required": True}),
    "age": field("Integer", validate=[{"kind": "Range", "args": {"min": 0, "max": 150}}]),
}

CASES = [
    {
        "id": "api-surface",
        "request": {"operation": "api"},
        "expected": {
            "root": [
                "EXCLUDE",
                "INCLUDE",
                "RAISE",
                "Schema",
                "SchemaOpts",
                "ValidationError",
                "fields",
                "missing",
                "post_dump",
                "post_load",
                "pre_dump",
                "pre_load",
                "validates",
                "validates_schema",
            ],
            "fields": [
                "AwareDateTime",
                "Bool",
                "Boolean",
                "Constant",
                "Date",
                "DateTime",
                "Decimal",
                "Dict",
                "Email",
                "Enum",
                "Field",
                "Float",
                "Function",
                "IP",
                "IPInterface",
                "IPv4",
                "IPv4Interface",
                "IPv6",
                "IPv6Interface",
                "Int",
                "Integer",
                "List",
                "Mapping",
                "Method",
                "NaiveDateTime",
                "Nested",
                "Number",
                "Pluck",
                "Raw",
                "Str",
                "String",
                "Time",
                "TimeDelta",
                "Tuple",
                "URL",
                "UUID",
                "Url",
            ],
            "validators": [
                "And",
                "ContainsNoneOf",
                "ContainsOnly",
                "Email",
                "Equal",
                "Length",
                "NoneOf",
                "OneOf",
                "Predicate",
                "Range",
                "Regexp",
                "URL",
                "Validator",
            ],
            "unknown_options": ["raise", "exclude", "include"],
        },
    },
    {
        "id": "dump-scalars",
        "request": {"operation": "dump", "schema": schema(PERSON), "payload": {"name": "Ada", "age": 36}},
        "expected": {"name": "Ada", "age": 36},
    },
    {
        "id": "load-coerces-string-to-integer",
        "request": {"operation": "load", "schema": schema(PERSON), "payload": {"name": "Ada", "age": "36"}},
        "expected": {"name": "Ada", "age": 36},
    },
    {
        "id": "load-missing-required-field",
        "request": {"operation": "load_error", "schema": schema(PERSON), "payload": {"age": 3}},
        "expected": {
            "messages": {"name": ["Missing data for required field."]},
            "valid_data": {"age": 3},
            "field_name": "_schema",
        },
    },
    {
        "id": "load-range-validator-message",
        "request": {"operation": "load_error", "schema": schema(PERSON), "payload": {"name": "Ada", "age": -1}},
        "expected": {
            "messages": {"age": ["Must be greater than or equal to 0 and less than or equal to 150."]},
            "valid_data": {"name": "Ada"},
            "field_name": "_schema",
        },
    },
    {
        "id": "validate-returns-messages",
        "request": {"operation": "validate", "schema": schema(PERSON), "payload": {"age": "abc"}},
        "expected": {"name": ["Missing data for required field."], "age": ["Not a valid integer."]},
    },
    {
        "id": "load-unknown-field-raises",
        "request": {"operation": "load_error", "schema": schema(PERSON), "payload": {"name": "Ada", "extra": 1}},
        "expected": {
            "messages": {"extra": ["Unknown field."]},
            "valid_data": {"name": "Ada"},
            "field_name": "_schema",
        },
    },
    {
        "id": "load-unknown-exclude",
        "request": {
            "operation": "load",
            "schema": schema(PERSON),
            "init": {"unknown": "exclude"},
            "payload": {"name": "Ada", "extra": 1},
        },
        "expected": {"name": "Ada"},
    },
    {
        "id": "load-unknown-include",
        "request": {
            "operation": "load",
            "schema": schema(PERSON),
            "payload": {"name": "Ada", "extra": 1},
            "call": {"unknown": "include"},
        },
        "expected": {"name": "Ada", "extra": 1},
    },
    {
        "id": "load-partial-skips-required",
        "request": {
            "operation": "load",
            "schema": schema(PERSON),
            "payload": {"age": 5},
            "call": {"partial": True},
        },
        "expected": {"age": 5},
    },
    {
        "id": "load-partial-field-tuple",
        "request": {
            "operation": "load",
            "schema": schema(PERSON),
            "payload": {"age": 5},
            "call": {"partial": ["name"]},
        },
        "expected": {"age": 5},
    },
    {
        "id": "dump-many",
        "request": {
            "operation": "dump",
            "schema": schema(PERSON),
            "payload": [{"name": "Ada", "age": 1}, {"name": "Bob", "age": 2}],
            "call": {"many": True},
        },
        "expected": [{"name": "Ada", "age": 1}, {"name": "Bob", "age": 2}],
    },
    {
        "id": "load-many-index-errors",
        "request": {
            "operation": "load_error",
            "schema": schema(PERSON),
            "payload": [{"name": "Ada"}, {"age": 2}],
            "call": {"many": True},
        },
        "expected": {
            "messages": {"1": {"name": ["Missing data for required field."]}},
            "valid_data": [{"name": "Ada"}, {"age": 2}],
            "field_name": "_schema",
        },
    },
    {
        "id": "only-and-exclude-field-selection",
        "request": {
            "operation": "field_names",
            "schema": schema(
                {
                    "a": field("String"),
                    "b": field("Integer"),
                    "c": field("Boolean"),
                }
            ),
            "init": {"only": ["a", "c"]},
        },
        "expected": ["a", "c"],
    },
    {
        "id": "exclude-removes-field",
        "request": {
            "operation": "field_names",
            "schema": schema({"a": field("String"), "b": field("Integer")}),
            "init": {"exclude": ["b"]},
        },
        "expected": ["a"],
    },
    {
        "id": "dump-only-field-not-loaded",
        "request": {
            "operation": "load",
            "schema": schema(
                {"a": field("String"), "b": field("Integer", args={"dump_only": True})}
            ),
            "payload": {"a": "x"},
        },
        "expected": {"a": "x"},
    },
    {
        "id": "load-only-field-not-dumped",
        "request": {
            "operation": "dump",
            "schema": schema(
                {"a": field("String"), "b": field("String", args={"load_only": True})}
            ),
            "payload": {"a": "x", "b": "secret"},
        },
        "expected": {"a": "x"},
    },
    {
        "id": "data-key-renames-external-name",
        "request": {
            "operation": "load",
            "schema": schema({"created": field("String", args={"data_key": "created_at"})}),
            "payload": {"created_at": "now"},
        },
        "expected": {"created": "now"},
    },
    {
        "id": "load-default-fills-missing",
        "request": {
            "operation": "load",
            "schema": schema({"a": field("Integer", args={"load_default": 7})}),
            "payload": {},
        },
        "expected": {"a": 7},
    },
    {
        "id": "dump-default-fills-missing",
        "request": {
            "operation": "dump",
            "schema": schema({"a": field("Integer", args={"dump_default": 9})}),
            "payload": {},
        },
        "expected": {"a": 9},
    },
    {
        "id": "allow-none-accepts-null",
        "request": {
            "operation": "load",
            "schema": schema({"a": field("String", args={"allow_none": True})}),
            "payload": {"a": None},
        },
        "expected": {"a": None},
    },
    {
        "id": "none-rejected-without-allow-none",
        "request": {
            "operation": "load_error",
            "schema": schema({"a": field("String")}),
            "payload": {"a": None},
        },
        "expected": {
            "messages": {"a": ["Field may not be null."]},
            "valid_data": {},
            "field_name": "_schema",
        },
    },
    {
        "id": "nested-schema-load",
        "request": {
            "operation": "load",
            "schema": schema(
                {
                    "title": field("String"),
                    "author": field("Nested", schema=PERSON, name="AuthorSchema"),
                }
            ),
            "payload": {"title": "Book", "author": {"name": "Ada", "age": "5"}},
        },
        "expected": {"title": "Book", "author": {"name": "Ada", "age": 5}},
    },
    {
        "id": "nested-error-nests-messages",
        "request": {
            "operation": "load_error",
            "schema": schema(
                {"author": field("Nested", schema=PERSON, name="AuthorSchema")}
            ),
            "payload": {"author": {"age": 1}},
        },
        "expected": {
            "messages": {"author": {"name": ["Missing data for required field."]}},
            "valid_data": {"author": {"age": 1}},
            "field_name": "_schema",
        },
    },
    {
        "id": "pluck-extracts-single-field",
        "request": {
            "operation": "dump",
            "schema": schema(
                {
                    "author": field(
                        "Pluck", schema=PERSON, field_name="name", name="AuthorSchema"
                    )
                }
            ),
            "payload": {"author": {"name": "Ada", "age": 3}},
        },
        "expected": {"author": "Ada"},
    },
    {
        "id": "list-of-integers-load",
        "request": {
            "operation": "load",
            "schema": schema({"values": field("List", inner=field("Integer"))}),
            "payload": {"values": ["1", "2", "3"]},
        },
        "expected": {"values": [1, 2, 3]},
    },
    {
        "id": "list-error-keyed-by-index",
        "request": {
            "operation": "load_error",
            "schema": schema({"values": field("List", inner=field("Integer"))}),
            "payload": {"values": [1, "bad", 3]},
        },
        "expected": {
            "messages": {"values": {"1": ["Not a valid integer."]}},
            "valid_data": {"values": [1, 3]},
            "field_name": "_schema",
        },
    },
    {
        "id": "tuple-preserves-positional-types",
        "request": {
            "operation": "load",
            "schema": schema(
                {
                    "pair": field(
                        "Tuple", tuple_fields=[field("String"), field("Integer")]
                    )
                }
            ),
            "payload": {"pair": ["x", "2"]},
        },
        "expected": {"pair": {"__type__": "tuple", "value": ["x", 2]}},
    },
    {
        "id": "dict-typed-keys-and-values",
        "request": {
            "operation": "load",
            "schema": schema(
                {
                    "counts": field(
                        "Dict", keys=field("String"), values=field("Integer")
                    )
                }
            ),
            "payload": {"counts": {"a": "1", "b": "2"}},
        },
        "expected": {"counts": {"a": 1, "b": 2}},
    },
    {
        "id": "domain-types-round-trip",
        "request": {
            "operation": "load",
            "schema": schema(
                {
                    "when": field("DateTime"),
                    "day": field("Date"),
                    "span": field("TimeDelta"),
                    "amount": field("Decimal", args={"as_string": True}),
                    "token": field("UUID"),
                    "host": field("IPv4"),
                    "color": field("Enum", enum=True),
                }
            ),
            "payload": {
                "when": "2026-08-08T10:26:10",
                "day": "2026-08-08",
                "span": 90,
                "amount": "1.25",
                "token": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "host": "192.0.2.10",
                "color": "GREEN",
            },
        },
        "expected": {
            "when": {"__type__": "datetime", "value": "2026-08-08T10:26:10"},
            "day": {"__type__": "date", "value": "2026-08-08"},
            "span": {"__type__": "timedelta", "value": 90.0},
            "amount": {"__type__": "decimal", "value": "1.25"},
            "token": {"__type__": "uuid", "value": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"},
            "host": {"__type__": "IPv4Address", "value": "192.0.2.10"},
            "color": {"__type__": "enum", "name": "GREEN", "value": 2},
        },
    },
    {
        "id": "domain-types-dump-native-forms",
        "request": {
            "operation": "dump",
            "schema": schema(
                {
                    "when": field("DateTime"),
                    "amount": field("Decimal", args={"as_string": True}),
                    "color": field("Enum", enum=True),
                }
            ),
            "payload": {
                "when": {"__type__": "datetime", "value": "2026-08-08T10:26:10"},
                "amount": {"__type__": "decimal", "value": "1.25"},
                "color": {"__type__": "enum", "name": "GREEN", "value": 2},
            },
        },
        "expected": {"when": "2026-08-08T10:26:10", "amount": "1.25", "color": "GREEN"},
    },
    {
        "id": "dumps-and-loads-use-render-module",
        "request": {
            "operation": "dumps",
            "schema": schema({"a": field("Integer"), "b": field("String")}),
            "payload": {"a": 1, "b": "x"},
        },
        "expected": '{"a": 1, "b": "x"}',
    },
    {
        "id": "meta-fields-and-validators-compose",
        "request": {
            "operation": "load_error",
            "schema": schema(
                {
                    "code": field(
                        "String",
                        validate=[
                            {"kind": "Length", "args": {"min": 2, "max": 4}},
                            {"kind": "OneOf", "args": {"choices": ["ab", "abc"]}},
                        ],
                    )
                }
            ),
            "payload": {"code": "zzz"},
        },
        "expected": {
            "messages": {"code": ["Must be one of: ab, abc."]},
            "valid_data": {},
            "field_name": "_schema",
        },
    },
]


def invoke(request):
    payload = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    command = [
        sys.executable,
        "-I",
        "-B",
        "-",
        "--candidate-site",
        os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--request",
        payload,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") != "1":
        command = [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "HOME=/home/candidate",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTHONHASHSEED=0",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            *command,
        ]
    try:
        result = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"ok": False, "exception_type": "VerifierProcessError", "exception_message": str(error)}
    lines = [line for line in result.stdout.decode("utf-8", "replace").splitlines() if line.strip()]
    if result.returncode != 0 or len(lines) != 1:
        detail = result.stderr.decode("utf-8", "replace") or result.stdout.decode("utf-8", "replace")
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": detail[-2000:]}
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(error)}


def normalize(value):
    """Sort mapping keys so hash-order-dependent error dictionaries compare stably."""
    if isinstance(value, dict):
        return {key: normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def main():
    leaves = []
    for case in CASES:
        result = invoke(case["request"])
        if "expected_error" in case:
            passed = result.get("ok") is False and result.get("exception_type") == case["expected_error"]
        else:
            passed = result.get("ok") is True and normalize(result.get("value")) == normalize(case["expected"])
        leaf = {"id": "marshmallow/" + case["id"], "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps(
                {"expected": case.get("expected", case.get("expected_error")), "actual": result},
                ensure_ascii=False,
                sort_keys=True,
            )[:1000]
        leaves.append(leaf)
    print(
        json.dumps(
            {"schema_version": "1.0", "leaves": leaves},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()

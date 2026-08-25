#!/usr/bin/env python3
"""Child-side observations for the bounded schema 0.7.8 contract."""
from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
import re
import sys


def _configure_candidate(candidate_site: str) -> None:
    while candidate_site in sys.path:
        sys.path.remove(candidate_site)
    sys.path.insert(0, candidate_site)


def _error(callable_):
    try:
        return {"ok": True, "value": callable_()}
    except BaseException as error:
        result = {
            "ok": False,
            "type": type(error).__name__,
            "message": str(error),
        }
        for name in ("autos", "errors", "code"):
            if hasattr(error, name):
                result[name] = getattr(error, name)
        return result


def api_surface():
    import schema

    names = [
        "Schema",
        "And",
        "Or",
        "Regex",
        "Optional",
        "Use",
        "Forbidden",
        "Const",
        "Literal",
        "SchemaError",
        "SchemaWrongKeyError",
        "SchemaMissingKeyError",
        "SchemaForbiddenKeyError",
        "SchemaUnexpectedTypeError",
        "SchemaOnlyOneAllowedError",
    ]
    return {
        "version": schema.__version__,
        "all": list(schema.__all__),
        "exports": {name: hasattr(schema, name) for name in names},
        "hook_available": hasattr(schema, "Hook"),
        "exception_bases": {
            name: [base.__name__ for base in getattr(schema, name).__mro__[1:3]]
            for name in names[9:]
        },
    }


def schema_properties():
    from schema import Schema

    value = Schema(
        {"name": str},
        error="bad payload",
        ignore_extra_keys=True,
        name="Person",
        description="A person",
    )
    return {
        "repr": repr(value),
        "schema": repr(value.schema),
        "name": value.name,
        "description": value.description,
        "ignore_extra_keys": value.ignore_extra_keys,
        "reference_without_name": _error(lambda: Schema(str, as_reference=True)),
    }


def primitive_validation():
    from schema import Schema

    cases = [
        ("literal-ok", lambda: Schema(1).validate(1)),
        ("literal-bad", lambda: Schema(1).validate(9)),
        ("int-ok", lambda: Schema(int).validate(3)),
        ("int-string", lambda: Schema(int).validate("3")),
        ("int-bool", lambda: Schema(int).validate(True)),
        ("str-ok", lambda: Schema(str).validate("hai")),
        ("object", lambda: Schema(object).validate([1, 2])),
    ]
    return {name: _error(callable_) for name, callable_ in cases}


def callable_validation():
    from schema import Schema

    class Positive:
        def __call__(self, value):
            return value > 0

        def __str__(self):
            return "positive-check"

    def explode(_value):
        raise ValueError("boom")

    return {
        "true": _error(lambda: Schema(lambda n: 0 < n < 5).validate(3)),
        "false": _error(lambda: Schema(lambda n: 0 < n < 5).validate(-1)),
        "object": _error(lambda: Schema(Positive()).validate(2)),
        "object-false": _error(lambda: Schema(Positive()).validate(-2)),
        "raises": _error(lambda: Schema(explode).validate("x")),
    }


def use_and_const():
    from schema import And, Const, Schema, Use

    return {
        "int": _error(lambda: Schema(Use(int)).validate("7")),
        "lower": _error(lambda: Schema(Use(str.lower)).validate("MiXeD")),
        "bad": _error(lambda: Schema(Use(int)).validate("seven")),
        "const": Schema(
            And(Const(And(Use(int), lambda n: n > 0)), Use(lambda raw: {"raw": raw}))
        ).validate("7"),
        "noncallable": _error(lambda: Use(3)),
    }


def and_or():
    from schema import And, Or, Use

    conjunction = And(Use(int), lambda n: 0 < n < 5)
    choice = Or(int, dict)
    return {
        "and": _error(lambda: conjunction.validate("3")),
        "and-fail": _error(lambda: conjunction.validate("7")),
        "and-args": [
            repr(conjunction.args[0]),
            getattr(conjunction.args[1], "__name__", type(conjunction.args[1]).__name__),
        ],
        "or-int": _error(lambda: choice.validate(5)),
        "or-dict": _error(lambda: choice.validate({"a": 1})),
        "or-fail": _error(lambda: Or(int, dict).validate("hai")),
        "or-empty": _error(lambda: Or().validate(2)),
    }


def regex_validation():
    from schema import Regex

    value = Regex(r"^[a-z]+$", flags=re.I)
    return {
        "repr": repr(value),
        "pattern": value.pattern_str,
        "match": _error(lambda: value.validate("Letters")),
        "mismatch": _error(lambda: value.validate("letters + spaces")),
        "wrong-type": _error(lambda: value.validate(3)),
        "bad-pattern": _error(lambda: Regex(None)),
    }


def iterable_validation():
    from schema import Schema

    return {
        "list": _error(lambda: Schema([int, str]).validate([1, "two", 3])),
        "empty": _error(lambda: Schema([int]).validate([])),
        "list-bad": _error(lambda: Schema([int]).validate([1, "2"])),
        "tuple": list(Schema((int, str)).validate((1, "two"))),
        "set": sorted(Schema({int}).validate({3, 1, 2})),
        "frozenset": sorted(Schema(frozenset([int])).validate(frozenset([2, 1]))),
        "wrong-container": _error(lambda: Schema((int,)).validate([1, 2])),
    }


def mapping_validation():
    from schema import Schema, Use

    dynamic = Schema({Use(str): Use(int)}).validate({1: 3.14, 3.14: 1})
    nested = Schema(
        {"name": str, "items": [{"id": Use(int), "active": bool}]}
    ).validate(
        {"name": "sample", "items": [{"id": "4", "active": True}]}
    )
    return {"dynamic": dynamic, "nested": nested}


def mapping_errors():
    from schema import Schema

    return {
        "missing-one": _error(lambda: Schema({"key": int}).validate({})),
        "missing-two": _error(
            lambda: Schema({"key": int, "other": str}).validate({"bad": 1})
        ),
        "wrong-one": _error(lambda: Schema({}).validate({"bad": 1})),
        "wrong-two": _error(lambda: Schema({}).validate({"a": 1, "b": 2})),
        "nested-type": _error(
            lambda: Schema({"outer": {"value": int}}).validate(
                {"outer": {"value": "x"}}
            )
        ),
    }


def ignore_extra_keys():
    from schema import Schema

    schema = Schema(
        {"key": 5, "nested": {"keep": str}}, ignore_extra_keys=True
    )
    return {
        "dropped": schema.validate(
            {"key": 5, "bad": 4, "nested": {"keep": "yes", "bad": "no"}}
        ),
        "retained": Schema(
            {"key": 5, object: object}, ignore_extra_keys=True
        ).validate({"key": 5, "bad": 4}),
    }


def optional_keys():
    from schema import Optional, Schema

    configured = Schema({"a": 1, Optional("b"): 2})
    return {
        "absent": configured.validate({"a": 1}),
        "present": configured.validate({"a": 1, "b": 2}),
        "priority": Schema({str: 1, Optional("b"): 2}).validate(
            {"a": 1, "b": 2}
        ),
        "deduplicated": len({Optional("a"): 1, Optional("a"): 2, Optional("b"): 3}),
    }


def defaults_static():
    from schema import Literal, Optional, Schema

    return {
        "filled": Schema(
            {Optional("a", default=1): 11, Optional("b", default=2): 22}
        ).validate({"a": 11}),
        "verbatim": Schema({Optional("count", default="not-an-int"): int}).validate(
            {}
        ),
        "literal-key": Schema(
            {Optional(Literal("data", description="payload"), default={}): dict}
        ).validate({}),
    }


def defaults_callable():
    from schema import Optional, Schema

    def empty_default():
        return {"created": True}

    def named_default(**kwargs):
        return "Hello, " + kwargs["name"]

    return {
        "no-args": Schema({Optional("data", default=empty_default): dict}).validate({}),
        "kwargs": Schema({Optional("message", default=named_default): str}).validate(
            {}, name="World"
        ),
        "fresh": Schema({Optional("data", default=lambda: {}): dict}).validate({}),
    }


def defaults_invalid():
    from schema import And, Optional, Use

    return {
        "complex-key": _error(lambda: Optional(And(str, Use(int)), default=7)),
        "simple-type-key": _error(lambda: Optional(str, default="x")),
    }


def forbidden_keys():
    from schema import Forbidden, Optional, Schema

    return {
        "match": _error(
            lambda: Schema({Forbidden("secret"): object}).validate({"secret": 1})
        ),
        "value-mismatch": _error(
            lambda: Schema({Forbidden("age"): str}).validate({"age": 50})
        ),
        "fallback": _error(
            lambda: Schema(
                {Forbidden("age"): str, Optional("age"): int}
            ).validate({"age": 50})
        ),
        "priority": _error(
            lambda: Schema(
                {Forbidden("age"): object, Optional(str): object}
            ).validate({"age": 50})
        ),
    }


def custom_hook():
    from schema import Hook, Optional, Schema

    calls = []

    def handler(key, scope, error):
        calls.append({"key": key, "scope": dict(scope), "error": error})

    hook = Hook("deprecated", handler=handler)
    first = Schema({hook: str, Optional("deprecated"): object}).validate(
        {"deprecated": "value"}
    )
    second = Schema({hook: int, Optional("deprecated"): object}).validate(
        {"deprecated": "value"}
    )
    return {"first": first, "second": second, "calls": calls, "key": hook.key}


def only_one_key():
    import copy
    from schema import Optional, Or, Schema

    either = Or("left", "right", only_one=True)
    configured = Schema(
        {either: str, Optional("nested"): {Optional(copy.deepcopy(either)): str}}
    )
    return {
        "left": _error(lambda: configured.validate({"left": "x"})),
        "right": _error(lambda: configured.validate({"right": "y"})),
        "both": _error(lambda: configured.validate({"left": "x", "right": "y"})),
        "nested": _error(
            lambda: configured.validate({"left": "x", "nested": {"right": "y"}})
        ),
    }


def literal_metadata():
    from schema import Literal, Schema

    value = Literal("productId", title="Product ID", description="Identifier")
    return {
        "str": str(value),
        "repr": repr(value),
        "schema": value.schema,
        "title": value.title,
        "description": value.description,
        "valid": _error(lambda: Schema(value).validate("productId")),
        "invalid": _error(lambda: Schema(value).validate("other")),
    }


def schema_error_code():
    from schema import SchemaError

    error = SchemaError(
        ["auto one", None, "auto one", "auto two"],
        [None, "public", "public", "second"],
    )
    automatic = SchemaError(["auto one", None, "auto one", "auto two"])
    return {
        "autos": error.autos,
        "errors": error.errors,
        "code": error.code,
        "str": str(error),
        "automatic": automatic.code,
    }


def custom_errors():
    from schema import And, Optional, Or, Schema, Use

    return {
        "schema": _error(lambda: Schema(int, error="must be int").validate("x")),
        "use": _error(lambda: Use(int, error="bad integer: {}").validate("x")),
        "nested": _error(
            lambda: Schema(
                {Optional("count"): Use(int, error="count is invalid")},
                error="payload invalid",
            ).validate({"count": "x"})
        ),
        "or": _error(
            lambda: Or(int, float, error="not numeric: {}").validate("x")
        ),
        "and": _error(
            lambda: And(int, lambda n: n > 0, error="not positive").validate(-1)
        ),
    }


def callable_errors():
    from schema import Schema, SchemaError, Use

    def value_error(_value):
        raise ValueError("bad")

    def schema_error(_value):
        raise SchemaError("inner auto", "inner public")

    return {
        "use-value": _error(lambda: Use(value_error).validate("x")),
        "use-schema": _error(lambda: Use(schema_error).validate("x")),
        "schema-use": _error(lambda: Schema(Use(schema_error)).validate("x")),
        "predicate-value": _error(lambda: Schema(value_error).validate("x")),
        "predicate-schema": _error(lambda: Schema(schema_error).validate("x")),
    }


def named_errors_and_validity():
    from schema import Schema

    named = Schema({"key": int}, name="Settings")
    return {
        "nested": _error(lambda: named.validate({"key": "x"})),
        "type": _error(lambda: Schema(int, name="Count").validate("x")),
        "valid": Schema(int).is_valid(2),
        "invalid": Schema(int).is_valid("2"),
    }


def json_input():
    from schema import And, Optional, Schema, Use

    configured = Schema(
        And(
            Use(json.loads),
            {
                Optional("description"): str,
                "public": bool,
                "files": {str: {"content": str}},
            },
        )
    )
    valid = json.dumps(
        {
            "description": "sample",
            "public": True,
            "files": {"one.txt": {"content": "hello"}},
        },
        ensure_ascii=False,
    )
    return {
        "valid": _error(lambda: configured.validate(valid)),
        "bad-json": _error(lambda: configured.validate("{")),
        "bad-shape": _error(lambda: configured.validate('["not", "an", "object"]')),
    }


def json_schema_basic():
    from schema import Schema

    return Schema(
        {"name": str, "age": int}, name="Person", description="A person"
    ).json_schema("https://example.test/person.json")


def json_schema_types():
    from schema import Regex, Schema

    schemas = {
        "int": Schema(int).json_schema("int-id"),
        "float": Schema(float).json_schema("float-id"),
        "bool": Schema(bool).json_schema("bool-id"),
        "null": Schema(None).json_schema("null-id"),
        "array": Schema([str]).json_schema("array-id"),
        "regex": Schema(Regex(r"^v\d+$")).json_schema("regex-id"),
    }
    return schemas


def json_schema_combinators():
    from schema import And, Or, Schema

    return {
        "enum": Schema({"mode": Or("read", "write")}).json_schema("enum-id"),
        "any-of": Schema({"value": Or(str, int)}).json_schema("any-id"),
        "all-of": Schema({"value": And(str, "exact")}).json_schema("all-id"),
        "single": Schema({"value": Or(True)}).json_schema("single-id"),
    }


def json_schema_metadata_defaults():
    from schema import Literal, Optional, Schema

    return Schema(
        {
            Literal("productId", title="Product ID", description="Identifier"): int,
            Optional("tags", default=("one", "two")): list,
            Optional("enabled", default=False): bool,
            Optional("note", default=None): str,
        },
        name="Product",
        description="Catalog product",
    ).json_schema("product-id")


def json_schema_additional_properties():
    from schema import Forbidden, Optional, Schema

    return {
        "closed": Schema({Optional("known"): str}).json_schema("closed-id"),
        "dynamic": Schema({str: int}).json_schema("dynamic-id"),
        "ignored": Schema({}, ignore_extra_keys=True).json_schema("ignored-id"),
        "forbidden": Schema(
            {Forbidden("secret"): object, "name": str}
        ).json_schema("forbidden-id"),
    }


def json_schema_definitions():
    from schema import Schema

    address = Schema(
        {"city": str, "zip": int},
        name="Address",
        description="Postal address",
        as_reference=True,
    )
    return Schema({"home": address, "work": address}).json_schema("person-id")


SCENARIOS = {
    "api-surface": api_surface,
    "schema-properties": schema_properties,
    "primitive-validation": primitive_validation,
    "callable-validation": callable_validation,
    "use-and-const": use_and_const,
    "and-or": and_or,
    "regex-validation": regex_validation,
    "iterable-validation": iterable_validation,
    "mapping-validation": mapping_validation,
    "mapping-errors": mapping_errors,
    "ignore-extra-keys": ignore_extra_keys,
    "optional-keys": optional_keys,
    "defaults-static": defaults_static,
    "defaults-callable": defaults_callable,
    "defaults-invalid": defaults_invalid,
    "forbidden-keys": forbidden_keys,
    "custom-hook": custom_hook,
    "only-one-key": only_one_key,
    "literal-metadata": literal_metadata,
    "schema-error-code": schema_error_code,
    "custom-errors": custom_errors,
    "callable-errors": callable_errors,
    "named-errors-and-validity": named_errors_and_validity,
    "json-input": json_input,
    "json-schema-basic": json_schema_basic,
    "json-schema-types": json_schema_types,
    "json-schema-combinators": json_schema_combinators,
    "json-schema-metadata-defaults": json_schema_metadata_defaults,
    "json-schema-additional-properties": json_schema_additional_properties,
    "json-schema-definitions": json_schema_definitions,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _configure_candidate(args.candidate_site)
    try:
        value = SCENARIOS[args.scenario]()
        report = {
            "schema_version": "1.0",
            "scenario": args.scenario,
            "ok": True,
            "value": value,
        }
    except BaseException as error:
        report = {
            "schema_version": "1.0",
            "scenario": args.scenario,
            "ok": False,
            "exception_type": type(error).__module__ + "." + type(error).__qualname__,
            "exception_message": str(error),
        }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

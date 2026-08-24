"""Candidate-side adapter: declarative JSON scenario -> normalized observation.

The adapter runs inside the untrusted candidate process. It builds every schema,
field, validator, and hook from a JSON scenario so no schema object, callable, or
process-local registry state ever crosses the process boundary.
"""

import argparse
import datetime as dt
import decimal
import enum
import ipaddress
import json
import sys
import uuid


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


TAGGED = "__type__"


def encode(value):
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, enum.Enum):
        return {TAGGED: "enum", "name": value.name, "value": encode(value.value)}
    if isinstance(value, dt.datetime):
        return {TAGGED: "datetime", "value": value.isoformat()}
    if isinstance(value, dt.date):
        return {TAGGED: "date", "value": value.isoformat()}
    if isinstance(value, dt.time):
        return {TAGGED: "time", "value": value.isoformat()}
    if isinstance(value, dt.timedelta):
        return {TAGGED: "timedelta", "value": value.total_seconds()}
    if isinstance(value, decimal.Decimal):
        return {TAGGED: "decimal", "value": str(value)}
    if isinstance(value, uuid.UUID):
        return {TAGGED: "uuid", "value": str(value)}
    if isinstance(
        value,
        (
            ipaddress.IPv4Address,
            ipaddress.IPv6Address,
            ipaddress.IPv4Interface,
            ipaddress.IPv6Interface,
        ),
    ):
        return {TAGGED: type(value).__name__, "value": str(value)}
    if isinstance(value, bytes):
        return {TAGGED: "bytes", "value": value.decode("utf-8", "replace")}
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return {TAGGED: "tuple", "value": [encode(item) for item in value]}
    if isinstance(value, (set, frozenset)):
        return {TAGGED: "set", "value": sorted(json.dumps(encode(x), sort_keys=True) for x in value)}
    if isinstance(value, (list,)):
        return [encode(item) for item in value]
    return {TAGGED: "repr", "value": repr(value)}


def decode(value):
    if isinstance(value, dict):
        tag = value.get(TAGGED)
        if tag is None:
            return {key: decode(item) for key, item in value.items()}
        raw = value.get("value")
        if tag == "datetime":
            return dt.datetime.fromisoformat(raw)
        if tag == "date":
            return dt.date.fromisoformat(raw)
        if tag == "time":
            return dt.time.fromisoformat(raw)
        if tag == "timedelta":
            return dt.timedelta(seconds=raw)
        if tag == "decimal":
            return decimal.Decimal(raw)
        if tag == "uuid":
            return uuid.UUID(raw)
        if tag == "enum":
            return Color[value["name"]]
        if tag == "bytes":
            return raw.encode("utf-8")
        if tag == "ip":
            return ipaddress.ip_address(raw)
        if tag == "tuple":
            return tuple(decode(item) for item in raw)
        if tag == "set":
            return {decode(item) for item in raw}
        if tag == "missing":
            from marshmallow import missing

            return missing
        raise ValueError("unsupported tag: " + str(tag))
    if isinstance(value, list):
        return [decode(item) for item in value]
    return value


def build_validator(spec):
    from marshmallow import validate

    kind = spec["kind"]
    arguments = {key: decode(item) for key, item in spec.get("args", {}).items()}
    if kind == "And":
        return validate.And(*[build_validator(item) for item in spec["validators"]])
    return getattr(validate, kind)(**arguments)


FIELD_CHILD_KEYS = ("inner", "keys", "values")


def build_field(spec):
    from marshmallow import Schema, fields

    kind = spec["type"]
    arguments = {}
    for key, item in spec.get("args", {}).items():
        arguments[key] = decode(item)
    if "validate" in spec:
        validators = [build_validator(item) for item in spec["validate"]]
        arguments["validate"] = validators if len(validators) > 1 else validators[0]
    for key in FIELD_CHILD_KEYS:
        if key in spec:
            arguments[key] = build_field(spec[key])
    if "enum" in spec:
        arguments["enum"] = Color
    positional = []
    if kind in ("Nested", "Pluck"):
        positional.append(Schema.from_dict(build_fields(spec["schema"]), name=spec.get("name", "InlineSchema")))
        if kind == "Pluck":
            positional.append(spec["field_name"])
    elif kind == "List":
        positional.append(arguments.pop("inner"))
    elif kind == "Tuple":
        positional.append([build_field(item) for item in spec["tuple_fields"]])
    elif kind in ("Dict", "Mapping"):
        arguments.setdefault("keys", None)
        arguments.setdefault("values", None)
    elif kind == "Constant":
        positional.append(decode(spec["constant"]))
    elif kind == "Enum":
        positional.append(arguments.pop("enum"))
    return getattr(fields, kind)(*positional, **arguments)


def build_fields(spec):
    return {name: build_field(field) for name, field in spec.items()}


def build_schema_class(spec):
    from marshmallow import Schema

    declared = build_fields(spec.get("fields", {}))
    meta = spec.get("meta")
    if meta:
        namespace = dict(declared)
        options = {}
        for key, item in meta.items():
            options[key] = tuple(item) if isinstance(item, list) else item
        namespace["Meta"] = type("Meta", (), options)
        return type(spec.get("name", "ScenarioSchema"), (Schema,), namespace)
    return Schema.from_dict(declared, name=spec.get("name", "ScenarioSchema"))


def instantiate(spec):
    arguments = {}
    for key, item in spec.get("init", {}).items():
        arguments[key] = tuple(item) if isinstance(item, list) and key != "partial" else item
        if key == "partial" and isinstance(item, list):
            arguments[key] = tuple(item)
    return build_schema_class(spec.get("schema", {}))(**arguments)


def observe_error(error):
    return {
        "messages": encode(error.messages),
        "valid_data": encode(error.valid_data),
        "field_name": error.field_name,
    }


def handle(request):
    operation = request["operation"]
    if operation == "api":
        import marshmallow
        from marshmallow import fields, validate

        probe = (
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
        )
        return {
            "root": sorted(marshmallow.__all__),
            "fields": sorted(fields.__all__),
            "validators": sorted(name for name in probe if hasattr(validate, name)),
            "unknown_options": [marshmallow.RAISE, marshmallow.EXCLUDE, marshmallow.INCLUDE],
        }

    schema = instantiate(request)
    call = {key: (tuple(item) if isinstance(item, list) else item) for key, item in request.get("call", {}).items()}
    payload = decode(request["payload"]) if "payload" in request else None

    if operation == "dump":
        return encode(schema.dump(payload, **call))
    if operation == "dumps":
        return schema.dumps(payload, **call)
    if operation == "load":
        return encode(schema.load(payload, **call))
    if operation == "loads":
        return encode(schema.loads(payload, **call))
    if operation == "validate":
        return encode(schema.validate(payload, **call))
    if operation == "load_error":
        from marshmallow import ValidationError

        try:
            schema.load(payload, **call)
        except ValidationError as error:
            return observe_error(error)
        raise AssertionError("ValidationError was not raised")
    if operation == "field_names":
        return sorted(schema.fields)
    raise ValueError("unsupported operation: " + operation)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    arguments = parser.parse_args()
    sys.path.insert(0, arguments.candidate_site)
    try:
        value = handle(json.loads(arguments.request))
    except BaseException as error:  # noqa: BLE001 - reported as a candidate observation
        module = type(error).__module__
        name = type(error).__qualname__
        payload = {
            "ok": False,
            "exception_type": name if module in ("builtins", None) else module + "." + name,
            "exception_message": str(error)[:2000],
        }
    else:
        payload = {"ok": True, "value": value}
    sys.stdout.write(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    )


if __name__ == "__main__":
    main()

"""Candidate-side adapter for the allowlisted offline PyMongo scenarios."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from typing import Any


def _error_type(call: Callable[[], Any]) -> str | None:
    try:
        call()
    except Exception as exc:
        return f"{type(exc).__module__}.{type(exc).__qualname__}"
    return None


def _version_scenario(_identifier: str) -> str:
    import pymongo

    return pymongo.__version__


def _json_scenario(identifier: str) -> Any:
    from bson import json_util

    if identifier == "json-dumps-order-unicode":
        return json_util.dumps({"second": 2, "first": "caf\u00e9"})
    if identifier == "json-dumps-nested":
        return json_util.dumps({"items": [True, None, 3, "x"]})
    if identifier == "json-loads-whitespace":
        return json_util.loads('  {"name":"Ada","enabled":true} \n')
    if identifier == "json-loads-array":
        return json_util.loads('[1,"two",null,false]')
    if identifier == "json-loads-numbers":
        value = json_util.loads('{"integer":4,"float":1.25}')
        return [value, type(value["integer"]).__name__, type(value["float"]).__name__]
    if identifier == "json-roundtrip":
        value = {"nested": [{"x": 1}], "text": "\u2603"}
        return json_util.loads(json_util.dumps(value))
    if identifier == "json-invalid":
        return _error_type(lambda: json_util.loads('{"broken":]'))
    raise KeyError(identifier)


def _objectid_scenario(identifier: str) -> bool:
    from bson.objectid import ObjectId

    values: dict[str, Any] = {
        "objectid-lower": "0123456789abcdefabcdef01",
        "objectid-upper": "0123456789ABCDEFABCDEF01",
        "objectid-short": "0123456789abcdefabcdef0",
        "objectid-long": "0123456789abcdefabcdef012",
        "objectid-nonhex": "0123456789abcdefabcdef0z",
        "objectid-text12": "abcdefghijkl",
        "objectid-none": None,
    }
    return ObjectId.is_valid(values[identifier])


def _host_scenario(identifier: str) -> Any:
    from pymongo.uri_parser import parse_host

    values = {
        "host-default": "localhost",
        "host-explicit": "localhost:27018",
        "host-case-normalized": "LOCALHOST:7",
        "host-ipv4": "127.0.0.1:27019",
        "host-ipv6-default": "[::1]",
        "host-ipv6-explicit": "[2001:db8::1]:42",
    }
    if identifier in values:
        return parse_host(values[identifier])
    invalid = {
        "host-port-zero": "localhost:0",
        "host-port-high": "localhost:65536",
        "host-port-text": "localhost:not-a-port",
    }
    return _error_type(lambda: parse_host(invalid[identifier]))


def _split_scenario(identifier: str) -> Any:
    from pymongo.uri_parser import split_hosts

    values = {
        "split-single": "localhost",
        "split-two": "a:1,B",
        "split-ipv6": "[::1]:27018,example.com:4",
    }
    if identifier in values:
        return split_hosts(values[identifier])
    invalid = {
        "split-empty-middle": "a:1,,b:2",
        "split-empty-trailing": "a:1,",
    }
    return _error_type(lambda: split_hosts(invalid[identifier]))


def _uri_scenario(identifier: str) -> Any:
    from pymongo.uri_parser import parse_uri

    values = {
        "uri-minimal": "mongodb://localhost",
        "uri-host-list": "mongodb://a:1,B:27018",
        "uri-credentials": "mongodb://u%40ser:p%3Aass@localhost",
        "uri-database": "mongodb://localhost/example_db",
        "uri-collection": "mongodb://localhost/example_db.items",
        "uri-options-ampersand": (
            "mongodb://localhost/?retryWrites=true&connectTimeoutMS=2500"
        ),
        "uri-options-semicolon": "mongodb://localhost/?tls=true;retryWrites=false",
        "uri-ipv6": "mongodb://[::1]:27018/db",
    }
    if identifier in values:
        return parse_uri(values[identifier])
    invalid = {
        "uri-invalid-scheme": "http://localhost/db",
        "uri-invalid-port": "mongodb://localhost:70000/db",
    }
    return _error_type(lambda: parse_uri(invalid[identifier]))


def _validator_scenario(identifier: str) -> Any:
    from pymongo import common

    valid: dict[str, Callable[[], Any]] = {
        "validator-boolean-true": lambda: common.validate_boolean("enabled", True),
        "validator-boolean-false": lambda: common.validate_boolean("enabled", False),
        "validator-integer": lambda: common.validate_integer("count", 4),
        "validator-string": lambda: common.validate_string("name", "Ada"),
        "validator-string-or-none-string": lambda: common.validate_string_or_none(
            "name", "Ada"
        ),
        "validator-string-or-none-none": lambda: common.validate_string_or_none(
            "name", None
        ),
        "validator-mapping": lambda: common.validate_is_mapping("options", {"x": 1}),
    }
    if identifier in valid:
        return valid[identifier]()
    invalid: dict[str, Callable[[], Any]] = {
        "validator-boolean-invalid": lambda: common.validate_boolean("enabled", "true"),
        "validator-integer-invalid": lambda: common.validate_integer("count", 1.5),
        "validator-string-invalid": lambda: common.validate_string("name", b"Ada"),
        "validator-string-or-none-invalid": lambda: common.validate_string_or_none(
            "name", 1
        ),
        "validator-mapping-invalid": lambda: common.validate_is_mapping("options", []),
    }
    return _error_type(invalid[identifier])


SCENARIOS: dict[str, Callable[[str], Any]] = {}
SCENARIOS["package-version"] = _version_scenario
for _identifier in (
    "json-dumps-order-unicode",
    "json-dumps-nested",
    "json-loads-whitespace",
    "json-loads-array",
    "json-loads-numbers",
    "json-roundtrip",
    "json-invalid",
):
    SCENARIOS[_identifier] = _json_scenario
for _identifier in (
    "objectid-lower",
    "objectid-upper",
    "objectid-short",
    "objectid-long",
    "objectid-nonhex",
    "objectid-text12",
    "objectid-none",
):
    SCENARIOS[_identifier] = _objectid_scenario
for _identifier in (
    "host-default",
    "host-explicit",
    "host-case-normalized",
    "host-ipv4",
    "host-ipv6-default",
    "host-ipv6-explicit",
    "host-port-zero",
    "host-port-high",
    "host-port-text",
):
    SCENARIOS[_identifier] = _host_scenario
for _identifier in (
    "split-single",
    "split-two",
    "split-ipv6",
    "split-empty-middle",
    "split-empty-trailing",
):
    SCENARIOS[_identifier] = _split_scenario
for _identifier in (
    "uri-minimal",
    "uri-host-list",
    "uri-credentials",
    "uri-database",
    "uri-collection",
    "uri-options-ampersand",
    "uri-options-semicolon",
    "uri-ipv6",
    "uri-invalid-scheme",
    "uri-invalid-port",
):
    SCENARIOS[_identifier] = _uri_scenario
for _identifier in (
    "validator-boolean-true",
    "validator-boolean-false",
    "validator-boolean-invalid",
    "validator-integer",
    "validator-integer-invalid",
    "validator-string",
    "validator-string-invalid",
    "validator-string-or-none-string",
    "validator-string-or-none-none",
    "validator-string-or-none-invalid",
    "validator-mapping",
    "validator-mapping-invalid",
):
    SCENARIOS[_identifier] = _validator_scenario


def evaluate(identifier: str) -> dict[str, Any]:
    try:
        value = SCENARIOS[identifier](identifier)
    except BaseException as exc:
        return {
            "ok": False,
            "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "exception_message": str(exc),
        }
    return {"ok": True, "value": value}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    site = os.path.realpath(args.candidate_site)
    if site != "/tmp/candidate-site" or not os.path.isdir(site):
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, site)
    request = json.loads(args.request)
    if set(request) != {"schema_version", "scenario"}:
        raise ValueError("invalid scenario request fields")
    if request["schema_version"] != "1.0":
        raise ValueError("unsupported scenario schema")
    identifier = request["scenario"]
    if identifier not in SCENARIOS:
        raise ValueError("scenario is not allowlisted")
    print(json.dumps(evaluate(identifier), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
                    "exception_message": str(exc),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )

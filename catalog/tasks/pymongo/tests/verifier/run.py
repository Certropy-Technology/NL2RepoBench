from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import call, get


def main() -> None:
    leaves: list[dict[str, str]] = []

    def check_call(
        leaf_id: str,
        module: str,
        attribute: str,
        args: list[object],
        expected: object,
    ) -> None:
        result = call(module, attribute, *args)
        if result.ok and result.value == expected:
            leaves.append({"id": leaf_id, "status": "passed"})
        else:
            leaves.append(
                {
                    "id": leaf_id,
                    "status": "failed",
                    "message": f"expected={expected!r} result={result!r}",
                }
            )

    def check_get(leaf_id: str, module: str, attribute: str, expected: object) -> None:
        result = get(module, attribute)
        if result.ok and result.value == expected:
            leaves.append({"id": leaf_id, "status": "passed"})
        else:
            leaves.append(
                {
                    "id": leaf_id,
                    "status": "failed",
                    "message": f"expected={expected!r} result={result!r}",
                }
            )

    def check_error(
        leaf_id: str,
        module: str,
        attribute: str,
        args: list[object],
        exception_suffix: str,
        message_fragment: str,
    ) -> None:
        result = call(module, attribute, *args)
        if (
            not result.ok
            and (result.exception_type or "").endswith(exception_suffix)
            and message_fragment in (result.exception_message or "")
        ):
            leaves.append({"id": leaf_id, "status": "passed"})
        else:
            leaves.append(
                {
                    "id": leaf_id,
                    "status": "failed",
                    "message": f"expected={exception_suffix} result={result!r}",
                }
            )

    check_get("version", "pymongo", "__version__", "4.18.0.dev0")
    check_call("json-dumps-simple", "bson.json_util", "dumps", [{"a": 1, "b": "x"}], '{"a": 1, "b": "x"}')
    check_call("json-dumps-array", "bson.json_util", "dumps", [[1, "x", None]], '[1, "x", null]')
    check_call("json-dumps-nested", "bson.json_util", "dumps", [{"nested": {"ok": True}, "items": [1, 2]}], '{"items": [1, 2], "nested": {"ok": true}}')
    check_call("json-dumps-unicode", "bson.json_util", "dumps", [{"text": "café 中文"}], '{"text": "caf\\u00e9 \\u4e2d\\u6587"}')
    check_call("json-dumps-booleans", "bson.json_util", "dumps", [{"true": True, "false": False, "none": None}], '{"false": false, "none": null, "true": true}')
    check_call("json-dumps-empty-object", "bson.json_util", "dumps", [{}], "{}")
    check_call("json-dumps-empty-array", "bson.json_util", "dumps", [[]], "[]")
    check_call("json-loads-simple", "bson.json_util", "loads", ['{"a": 1, "b": "x"}'], {"a": 1, "b": "x"})
    check_call("json-loads-whitespace", "bson.json_util", "loads", [' { "a" : 1 } '], {"a": 1})
    check_call("json-loads-array", "bson.json_util", "loads", ['[1, "x", null]'], [1, "x", None])
    check_call("json-loads-booleans", "bson.json_util", "loads", ['{"true": true, "none": null}'], {"true": True, "none": None})
    check_call("json-loads-number", "bson.json_util", "loads", ['{"integer": 42, "fraction": 1.5}'], {"integer": 42, "fraction": 1.5})
    check_call("json-loads-escaped", "bson.json_util", "loads", ['{"text": "caf\\u00e9"}'], {"text": "café"})

    for leaf_id, value, expected in (
        ("objectid-valid-hex", "507f1f77bcf86cd799439011", True),
        ("objectid-valid-upper", "507F1F77BCF86CD799439011", True),
        ("objectid-invalid-12-text", "123456789012", False),
        ("objectid-invalid-short", "507f1f77bcf86cd79943901", False),
        ("objectid-invalid-text", "not-an-objectid", False),
        ("objectid-invalid-empty", "", False),
        ("objectid-invalid-type", 123, False),
    ):
        check_call(leaf_id, "bson.objectid", "ObjectId.is_valid", [value], expected)

    check_call("host-lowercase", "pymongo.uri_parser", "parse_host", ["LOCALHOST:27018"], ["localhost", 27018])
    check_call("host-default-port", "pymongo.uri_parser", "parse_host", ["example.com"], ["example.com", 27017])
    check_call("host-ipv6", "pymongo.uri_parser", "parse_host", ["[::1]:27018"], ["::1", 27018])
    check_call("hosts-two", "pymongo.uri_parser", "split_hosts", ["localhost:27018,example.com"], [["localhost", 27018], ["example.com", 27017]])
    check_call("hosts-defaults", "pymongo.uri_parser", "split_hosts", ["localhost,example.com:27018"], [["localhost", 27017], ["example.com", 27018]])
    check_call("uri-basic", "pymongo.uri_parser", "parse_uri", ["mongodb://localhost/testdb"], {"nodelist": [["localhost", 27017]], "username": None, "password": None, "database": "testdb", "collection": None, "options": {}, "fqdn": None})
    check_call("uri-auth", "pymongo.uri_parser", "parse_uri", ["mongodb://fred:foobar@localhost/testdb"], {"nodelist": [["localhost", 27017]], "username": "fred", "password": "foobar", "database": "testdb", "collection": None, "options": {}, "fqdn": None})
    check_call("uri-encoded-auth", "pymongo.uri_parser", "parse_uri", ["mongodb://user%40domain.com:pass%20word@localhost"], {"nodelist": [["localhost", 27017]], "username": "user@domain.com", "password": "pass word", "database": None, "collection": None, "options": {}, "fqdn": None})
    check_call("uri-options", "pymongo.uri_parser", "parse_uri", ["mongodb://localhost/?readPreference=secondary"], {"nodelist": [["localhost", 27017]], "username": None, "password": None, "database": None, "collection": None, "options": {"readPreference": "secondary"}, "fqdn": None})
    check_call("uri-multiple-hosts", "pymongo.uri_parser", "parse_uri", ["mongodb://localhost,example.com:27018/mydb"], {"nodelist": [["localhost", 27017], ["example.com", 27018]], "username": None, "password": None, "database": "mydb", "collection": None, "options": {}, "fqdn": None})
    check_call("uri-collection", "pymongo.uri_parser", "parse_uri", ["mongodb://localhost/mydb.events"], {"nodelist": [["localhost", 27017]], "username": None, "password": None, "database": "mydb", "collection": "events", "options": {}, "fqdn": None})
    check_call("uri-semicolon-options", "pymongo.uri_parser", "parse_uri", ["mongodb://localhost/?w=1;connectTimeoutMS=500"], {"nodelist": [["localhost", 27017]], "username": None, "password": None, "database": None, "collection": None, "options": {"w": 1, "connectTimeoutMS": 0.5}, "fqdn": None})
    check_call("uri-option-ampersand", "pymongo.uri_parser", "parse_uri", ["mongodb://localhost/?retryWrites=true&appName=bench"], {"nodelist": [["localhost", 27017]], "username": None, "password": None, "database": None, "collection": None, "options": {"retryWrites": True, "appname": "bench"}, "fqdn": None})

    check_call("boolean-true", "pymongo.common", "validate_boolean", ["tls", True], True)
    check_call("boolean-false", "pymongo.common", "validate_boolean", ["tls", False], False)
    check_call("integer", "pymongo.common", "validate_integer", ["port", 27017], 27017)
    check_call("string", "pymongo.common", "validate_string", ["name", "value"], "value")
    check_call("string-or-none", "pymongo.common", "validate_string_or_none", ["name", None], None)
    check_call("mapping", "pymongo.common", "validate_is_mapping", ["options", {"w": 1}], None)

    check_error("bad-json", "bson.json_util", "loads", ["{bad}"], "JSONDecodeError", "Expecting property name")
    check_error("bad-host-port", "pymongo.uri_parser", "parse_host", ["localhost:65536"], "ValueError", "between 0 and 65535")
    check_error("zero-host-port", "pymongo.uri_parser", "parse_host", ["localhost:0"], "ValueError", "between 0 and 65535")
    check_error("empty-host", "pymongo.uri_parser", "split_hosts", ["localhost:27017,"], "ConfigurationError", "Empty host")
    check_error("bad-scheme", "pymongo.uri_parser", "parse_uri", ["http://localhost"], "InvalidURI", "Invalid URI scheme")
    check_error("bad-uri-port", "pymongo.uri_parser", "parse_uri", ["mongodb://localhost:65536"], "ValueError", "between 0 and 65535")
    check_error("bad-boolean", "pymongo.common", "validate_boolean", ["tls", 1], "TypeError", "must be True or False")
    check_error("bad-integer", "pymongo.common", "validate_integer", ["port", 1.5], "TypeError", "must be an integer")
    check_error("bad-string", "pymongo.common", "validate_string", ["name", 1], "TypeError", "must be an instance of str")
    check_error("bad-string-none", "pymongo.common", "validate_string_or_none", ["name", 1], "TypeError", "must be an instance of str")
    check_error("bad-mapping", "pymongo.common", "validate_is_mapping", ["options", []], "TypeError", "must be an instance of dict")

    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()

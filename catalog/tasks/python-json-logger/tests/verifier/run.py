from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


LEAF_IDS = [
    "metadata",
    "availability-flags",
    "module-surface",
    "reserved-attributes",
    "merge-record-extra",
    "default-message",
    "percent-format",
    "brace-format",
    "template-format",
    "comma-format",
    "sequence-format",
    "defaults-precedence",
    "rename-fields",
    "rename-keep-missing",
    "rename-once-order",
    "static-fields",
    "dictionary-message",
    "dictionary-not-mutated",
    "extra-fields",
    "prefix",
    "timestamp",
    "invalid-style",
    "unknown-format-field",
    "no-exception-field",
    "exception-string",
    "exception-array",
    "stack-array",
    "process-hook",
    "unicode-ascii",
    "unicode-native",
    "bytes-encoding",
    "bytearray-encoding",
    "datetime-encoding",
    "uuid-encoding",
    "exception-encoding",
    "dataclass-encoding",
    "enum-value-encoding",
    "enum-class-encoding",
    "type-encoding",
    "unknown-object",
    "broken-object",
    "custom-default",
    "json-indent",
    "package-available",
    "missing-package",
    "missing-package-extra",
    "legacy-module-warning",
    "reserved-attrs-warning",
    "base-jsonify-abstract",
    "serializer-call-contract",
]


SCENARIO = r'''
import dataclasses
import datetime
import enum
import importlib
import importlib.metadata
import io
import json
import logging
import uuid
import warnings

import pythonjsonlogger
from pythonjsonlogger import defaults
from pythonjsonlogger.core import BaseJsonFormatter, RESERVED_ATTRS, merge_record_extra
from pythonjsonlogger.exception import MissingPackageError
from pythonjsonlogger.json import JsonEncoder, JsonFormatter
from pythonjsonlogger.utils import package_is_available


outcomes = []


def record(identifier, check):
    try:
        check()
    except BaseException as exc:
        outcomes.append({
            "id": identifier,
            "status": "failed",
            "message": f"{type(exc).__module__}.{type(exc).__qualname__}: {exc}"[:1000],
        })
    else:
        outcomes.append({"id": identifier, "status": "passed"})


def ensure(condition, message="assertion failed"):
    if not condition:
        raise AssertionError(message)


def raises(expected, operation, contains=None):
    try:
        operation()
    except expected as exc:
        if contains is not None:
            ensure(contains in str(exc), str(exc))
        return
    except BaseException as exc:
        raise AssertionError(f"expected {expected.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"expected {expected.__name__}")


def make_record(message="hello", *, args=(), extra=None, exc_info=None, stack_info=None):
    record = logging.LogRecord("contract", logging.INFO, "sample.py", 17, message, args, exc_info, "fn")
    if extra:
        record.__dict__.update(extra)
    if stack_info is not None:
        record.stack_info = stack_info
    return record


def formatted(formatter, message="hello", **kwargs):
    return formatter.format(make_record(message, **kwargs))


def decoded(formatter, message="hello", **kwargs):
    return json.loads(formatted(formatter, message, **kwargs))


def test_metadata():
    ensure(importlib.metadata.version("python-json-logger") == "4.2.0")
    ensure(importlib.metadata.metadata("python-json-logger")["Name"] == "python-json-logger")
    ensure(importlib.metadata.requires("python-json-logger") is None)


def test_availability_flags():
    ensure(pythonjsonlogger.ORJSON_AVAILABLE is False)
    ensure(pythonjsonlogger.MSGSPEC_AVAILABLE is False)


def test_module_surface():
    for name in ["core", "defaults", "exception", "json", "jsonlogger", "utils"]:
        ensure(importlib.import_module(f"pythonjsonlogger.{name}"))
    ensure(issubclass(JsonFormatter, BaseJsonFormatter))


def test_reserved_attributes():
    ensure("message" in RESERVED_ATTRS and "taskName" in RESERVED_ATTRS)
    ensure(RESERVED_ATTRS == sorted(RESERVED_ATTRS))


def test_merge_record_extra():
    item = make_record("x", extra={"visible": 4, "_hidden": 5, 7: "numeric"})
    target = {"existing": True}
    returned = merge_record_extra(item, target, ["msg"], {"visible": "shown"})
    ensure(returned is target)
    ensure(target["shown"] == 4 and target[7] == "numeric")
    ensure("msg" not in target and "_hidden" not in target)


def test_default_message():
    ensure(decoded(JsonFormatter())["message"] == "hello")


def test_percent_format():
    data = decoded(JsonFormatter("%(levelname)s %(message)s %(lineno)d"))
    ensure(list(data) == ["levelname", "message", "lineno"])
    ensure(data == {"levelname": "INFO", "message": "hello", "lineno": 17})


def test_brace_format():
    data = decoded(JsonFormatter("{levelname} {message}", style="{"))
    ensure(data == {"levelname": "INFO", "message": "hello"})


def test_template_format():
    data = decoded(JsonFormatter("$$literal $levelname ${message}", style="$"))
    ensure(data == {"levelname": "INFO", "message": "hello"})


def test_comma_format():
    data = decoded(JsonFormatter("levelname,,message,lineno,", style=","))
    ensure(data == {"levelname": "INFO", "message": "hello", "lineno": 17})


def test_sequence_format():
    ensure(decoded(JsonFormatter(["levelname", "message"])) == {"levelname": "INFO", "message": "hello"})
    ensure(decoded(JsonFormatter(("message", "lineno"))) == {"message": "hello", "lineno": 17})


def test_defaults_precedence():
    data = decoded(JsonFormatter(defaults={"first": 1, "second": 2}), extra={"first": 9})
    ensure(data["first"] == 9 and data["second"] == 2)


def test_rename_fields():
    data = decoded(JsonFormatter(rename_fields={"message": "@message"}))
    ensure(data == {"@message": "hello"})


def test_rename_keep_missing():
    data = decoded(JsonFormatter(rename_fields={"missing": "new"}, rename_fields_keep_missing=True))
    ensure(data["message"] == "hello" and data["new"] is None and "missing" not in data)


def test_rename_once_order():
    formatter = JsonFormatter(
        "{levelname}{message}", style="{",
        rename_fields={"levelname": "LEVEL", "message": "levelname"},
    )
    data = decoded(formatter)
    ensure(list(data) == ["LEVEL", "levelname"])
    ensure(data == {"LEVEL": "INFO", "levelname": "hello"})


def test_static_fields():
    data = decoded(JsonFormatter(static_fields={"stream": "audit"}))
    ensure(data == {"stream": "audit", "message": "hello"})


def test_dictionary_message():
    message = {"text": "hello", "nested": {"n": 1}, 5: "five"}
    data = decoded(JsonFormatter(), message)
    ensure(data == {"text": "hello", "nested": {"n": 1}, "5": "five", "message": ""})


def test_dictionary_not_mutated():
    message = {"text": "hello"}
    JsonFormatter().format(make_record(message, stack_info="Stack info"))
    ensure(message == {"text": "hello"})


def test_extra_fields():
    data = decoded(JsonFormatter(), extra={"text": "extra", "nested": {"n": 2}})
    ensure(data["message"] == "hello" and data["text"] == "extra" and data["nested"] == {"n": 2})


def test_prefix():
    ensure(formatted(JsonFormatter(prefix="P:")) == 'P:{"message": "hello"}')


def test_timestamp():
    item = make_record()
    item.created = 1_500_000_000.0
    data = json.loads(JsonFormatter(timestamp=True).format(item))
    ensure(data["timestamp"] == "2017-07-14T02:40:00+00:00")
    data = json.loads(JsonFormatter(timestamp="@timestamp").format(item))
    ensure(data["@timestamp"] == "2017-07-14T02:40:00+00:00")


def test_invalid_style():
    raises(ValueError, lambda: JsonFormatter("message", style="!"), "Style must be one of")


def test_unknown_format_field():
    data = decoded(JsonFormatter("%(unknown)s %(message)s"))
    ensure(data == {"unknown": None, "message": "hello"})


def test_no_exception_field():
    ensure("exc_info" not in decoded(JsonFormatter(exc_info_as_array=True)))


def capture_exception(formatter):
    try:
        raise ValueError("bad value")
    except ValueError:
        import sys
        return json.loads(formatter.format(make_record("failed", exc_info=sys.exc_info())))


def test_exception_string():
    value = capture_exception(JsonFormatter())["exc_info"]
    ensure(isinstance(value, str) and "ValueError: bad value" in value)


def test_exception_array():
    value = capture_exception(JsonFormatter(exc_info_as_array=True))["exc_info"]
    ensure(isinstance(value, list) and "ValueError: bad value" in "\n".join(value))


def test_stack_array():
    value = decoded(JsonFormatter(stack_info_as_array=True), stack_info="Stack (most recent call last):\n  frame")["stack_info"]
    ensure(value == ["Stack (most recent call last):", "  frame"])


def test_process_hook():
    class Custom(JsonFormatter):
        def process_log_record(self, log_data):
            log_data["custom"] = "yes"
            return super().process_log_record(log_data)
    ensure(decoded(Custom())["custom"] == "yes")


def test_unicode_ascii():
    text = formatted(JsonFormatter(), "Привет")
    ensure("\\u041f" in text and "Привет" not in text)


def test_unicode_native():
    text = formatted(JsonFormatter(json_ensure_ascii=False), "Привет")
    ensure("Привет" in text)


def encoded_extra(value):
    return decoded(JsonFormatter(), extra={"value": value})["value"]


def test_bytes_encoding():
    ensure(encoded_extra(b"some-bytes") == "c29tZS1ieXRlcw==")


def test_bytearray_encoding():
    ensure(encoded_extra(bytearray(b"abc")) == "YWJj")


def test_datetime_encoding():
    ensure(encoded_extra(datetime.time(16, 45, 30, 100)) == "16:45:30.000100")
    ensure(encoded_extra(datetime.date(2024, 5, 5)) == "2024-05-05")
    ensure(encoded_extra(datetime.datetime(2024, 5, 5, 16, 45, 30, 100)) == "2024-05-05T16:45:30.000100")


def test_uuid_encoding():
    value = uuid.UUID("12345678-1234-5678-1234-567812345678")
    ensure(encoded_extra(value) == str(value))


def test_exception_encoding():
    ensure(encoded_extra(ValueError("oops")) == "ValueError: oops")


def test_dataclass_encoding():
    @dataclasses.dataclass
    class Item:
        name: str
        count: int
    ensure(encoded_extra(Item("a", 2)) == {"name": "a", "count": 2})


def test_enum_value_encoding():
    class Choice(enum.Enum):
        NONE = None
        NUMBER = 4
    ensure(encoded_extra(Choice.NONE) is None and encoded_extra(Choice.NUMBER) == 4)


def test_enum_class_encoding():
    class Choice(enum.Enum):
        FIRST = "a"
        SECOND = b"b"
    ensure(encoded_extra(Choice) == ["a", "Yg=="])


def test_type_encoding():
    class Item: pass
    ensure(encoded_extra(Item) == "Item")


def test_unknown_object():
    class Item:
        def __str__(self): return "item-text"
    ensure(encoded_extra(Item()) == "item-text")


def test_broken_object():
    class Item:
        def __str__(self): raise ValueError("broken")
        def __repr__(self): raise ValueError("broken")
    ensure(encoded_extra(Item()) == "__could_not_encode__")


def test_custom_default():
    formatter = JsonFormatter(json_default=lambda value: [value.real, value.imag] if isinstance(value, complex) else None)
    ensure(decoded(formatter, extra={"value": 3 + 8j})["value"] == [3.0, 8.0])


def test_json_indent():
    text = formatted(JsonFormatter(json_indent=2))
    ensure("\n  \"message\": \"hello\"\n" in text)


def test_package_available():
    ensure(package_is_available("json") is True)
    ensure(package_is_available("package_that_does_not_exist_anywhere") is False)


def test_missing_package():
    raises(MissingPackageError, lambda: package_is_available("missing_contract_package", throw_error=True), "missing_contract_package")


def test_missing_package_extra():
    try:
        package_is_available("missing_contract_package", throw_error=True, extras_name="speedups")
    except MissingPackageError as exc:
        ensure("missing_contract_package" in exc.msg and "speedups" in exc.msg)
        return
    raise AssertionError("MissingPackageError not raised")


def test_legacy_module_warning():
    import sys
    sys.modules.pop("pythonjsonlogger.jsonlogger", None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        module = importlib.import_module("pythonjsonlogger.jsonlogger")
    ensure(module.JsonFormatter is JsonFormatter)
    ensure(any(item.category is DeprecationWarning for item in caught))


def test_reserved_attrs_warning():
    import pythonjsonlogger.json as module
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = module.RESERVED_ATTRS
    ensure(value is RESERVED_ATTRS)
    ensure(any(item.category is DeprecationWarning for item in caught))


def test_base_jsonify_abstract():
    formatter = BaseJsonFormatter()
    raises(NotImplementedError, lambda: formatter.jsonify_log_record({"message": "x"}))


def test_serializer_call_contract():
    calls = []
    def serializer(value, **kwargs):
        calls.append((value, kwargs))
        return "SERIALIZED"
    formatter = JsonFormatter(json_serializer=serializer, json_indent="\t", json_ensure_ascii=False)
    ensure(formatter.format(make_record()) == "SERIALIZED")
    ensure(calls[0][0] == {"message": "hello"})
    ensure(calls[0][1]["indent"] == "\t" and calls[0][1]["ensure_ascii"] is False)


checks = [
    ("metadata", test_metadata),
    ("availability-flags", test_availability_flags),
    ("module-surface", test_module_surface),
    ("reserved-attributes", test_reserved_attributes),
    ("merge-record-extra", test_merge_record_extra),
    ("default-message", test_default_message),
    ("percent-format", test_percent_format),
    ("brace-format", test_brace_format),
    ("template-format", test_template_format),
    ("comma-format", test_comma_format),
    ("sequence-format", test_sequence_format),
    ("defaults-precedence", test_defaults_precedence),
    ("rename-fields", test_rename_fields),
    ("rename-keep-missing", test_rename_keep_missing),
    ("rename-once-order", test_rename_once_order),
    ("static-fields", test_static_fields),
    ("dictionary-message", test_dictionary_message),
    ("dictionary-not-mutated", test_dictionary_not_mutated),
    ("extra-fields", test_extra_fields),
    ("prefix", test_prefix),
    ("timestamp", test_timestamp),
    ("invalid-style", test_invalid_style),
    ("unknown-format-field", test_unknown_format_field),
    ("no-exception-field", test_no_exception_field),
    ("exception-string", test_exception_string),
    ("exception-array", test_exception_array),
    ("stack-array", test_stack_array),
    ("process-hook", test_process_hook),
    ("unicode-ascii", test_unicode_ascii),
    ("unicode-native", test_unicode_native),
    ("bytes-encoding", test_bytes_encoding),
    ("bytearray-encoding", test_bytearray_encoding),
    ("datetime-encoding", test_datetime_encoding),
    ("uuid-encoding", test_uuid_encoding),
    ("exception-encoding", test_exception_encoding),
    ("dataclass-encoding", test_dataclass_encoding),
    ("enum-value-encoding", test_enum_value_encoding),
    ("enum-class-encoding", test_enum_class_encoding),
    ("type-encoding", test_type_encoding),
    ("unknown-object", test_unknown_object),
    ("broken-object", test_broken_object),
    ("custom-default", test_custom_default),
    ("json-indent", test_json_indent),
    ("package-available", test_package_available),
    ("missing-package", test_missing_package),
    ("missing-package-extra", test_missing_package_extra),
    ("legacy-module-warning", test_legacy_module_warning),
    ("reserved-attrs-warning", test_reserved_attrs_warning),
    ("base-jsonify-abstract", test_base_jsonify_abstract),
    ("serializer-call-contract", test_serializer_call_contract),
]

for identifier, check in checks:
    record(identifier, check)

result = outcomes
'''


def main() -> None:
    response = execute_script(SCENARIO, timeout_sec=60.0)
    if response.ok and isinstance(response.value, list):
        by_id = {
            item.get("id"): item
            for item in response.value
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        leaves = []
        for identifier in LEAF_IDS:
            item = by_id.get(identifier)
            if item is None or item.get("status") not in {"passed", "failed"}:
                leaves.append({"id": identifier, "status": "failed", "message": "candidate omitted a valid leaf outcome"})
            else:
                leaf = {"id": identifier, "status": str(item["status"])}
                if leaf["status"] == "failed":
                    leaf["message"] = str(item.get("message", "scenario failed"))[:1000]
                leaves.append(leaf)
    else:
        message = (
            f"{response.exception_type}: {response.exception_message}"
            if not response.ok
            else "candidate scenario returned an invalid report"
        )
        leaves = [{"id": identifier, "status": "failed", "message": message[:1000]} for identifier in LEAF_IDS]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()

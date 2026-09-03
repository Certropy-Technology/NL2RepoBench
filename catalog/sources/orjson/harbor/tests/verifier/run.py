from __future__ import annotations

import inspect
import json
from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from nl2repobench.verification.candidate_client import (
    CandidateCallResult,
    execute_script,
    metadata_requires,
)


def script(source: str) -> CandidateCallResult:
    return execute_script(source, timeout_sec=12.0)


def equal(result: CandidateCallResult, expected: Any) -> bool:
    return result.ok and result.value == expected


def encoded_equal(result: CandidateCallResult, expected: str) -> bool:
    return result.ok and result.value == [True, expected]


def exception_name(source: str) -> str | None:
    result = script(source)
    if not result.ok:
        return None
    return result.value if isinstance(result.value, str) else None


def main() -> None:
    leaves: list[dict[str, object]] = []

    def check(identifier: str, passed: bool, message: str = "") -> None:
        leaves.append(
            {"id": identifier, "status": "passed" if passed else "failed", "message": message}
        )

    check(
        "packaging-surface",
        equal(
            script(
                "import orjson\nresult = [orjson.__version__, sorted(orjson.__all__)]"
            ),
            [
                "3.12.0",
                [
                    "Fragment",
                    "JSONDecodeError",
                    "JSONEncodeError",
                    "OPT_APPEND_NEWLINE",
                    "OPT_INDENT_2",
                    "OPT_NAIVE_UTC",
                    "OPT_NON_STR_KEYS",
                    "OPT_OMIT_MICROSECONDS",
                    "OPT_PASSTHROUGH_DATACLASS",
                    "OPT_PASSTHROUGH_DATETIME",
                    "OPT_PASSTHROUGH_SUBCLASS",
                    "OPT_SERIALIZE_DATACLASS",
                    "OPT_SERIALIZE_NUMPY",
                    "OPT_SERIALIZE_UUID",
                    "OPT_SORT_KEYS",
                    "OPT_STRICT_INTEGER",
                    "OPT_UTC_Z",
                    "__version__",
                    "dumps",
                    "loads",
                ],
            ],
            ),
        ),
    metadata = metadata_requires("orjson")
    check("metadata-dependencies", metadata.ok and metadata.value in (None, []))
    check(
        "simple-dumps",
        encoded_equal(script("import orjson\nvalue = orjson.dumps({'a': 1, 'ok': True, 'n': None})\nresult = [isinstance(value, bytes), value.decode()]"),
                      '{"a":1,"ok":true,"n":null}'),
    )
    check(
        "simple-loads",
        equal(script("import orjson\nresult = orjson.loads(b'{\"a\": [1, true, null]}')"),
              {"a": [1, True, None]}),
    )
    check(
        "round-trip",
        equal(script("import orjson\nvalue = {'x': [1, 'two', False]}\nresult = orjson.loads(orjson.dumps(value))"),
              {"x": [1, "two", False]}),
    )
    check(
        "buffer-input",
        equal(script("import orjson\nresult = [orjson.loads(bytearray(b'[1]')), orjson.loads(memoryview(b'{\"x\":2}'))]"),
              [[1], {"x": 2}]),
    )
    check(
        "unicode",
        encoded_equal(script("import orjson\nvalue = orjson.dumps({'text': 'café ☕'})\nresult = [isinstance(value, bytes), value.decode()]"),
                      '{"text":"café ☕"}'),
    )
    check(
        "nested-values",
        encoded_equal(script("import orjson\nvalue = orjson.dumps((1, 2, {'z': 3}))\nresult = [isinstance(value, bytes), value.decode()]"),
                      '[1,2,{"z":3}]'),
    )
    check(
        "indent",
        encoded_equal(script("import orjson\nvalue = orjson.dumps({'a': [1, 2]}, option=orjson.OPT_INDENT_2)\nresult = [isinstance(value, bytes), value.decode()]"),
                      '{\n  "a": [\n    1,\n    2\n  ]\n}'),
    )
    check(
        "sort-keys",
        encoded_equal(script("import orjson\nvalue = orjson.dumps({'b': 1, 'a': 2}, option=orjson.OPT_SORT_KEYS)\nresult = [isinstance(value, bytes), value.decode()]"),
                      '{"a":2,"b":1}'),
    )
    check(
        "append-newline",
        encoded_equal(script("import orjson\nvalue = orjson.dumps([1], option=orjson.OPT_APPEND_NEWLINE)\nresult = [isinstance(value, bytes), value.decode()]"), "[1]\n"),
    )
    check(
        "non-finite-floats",
        encoded_equal(script("import orjson\nvalue = orjson.dumps([float('nan'), float('inf'), float('-inf')])\nresult = [isinstance(value, bytes), value.decode()]"), "[null,null,null]"),
    )
    check(
        "strict-integer",
        exception_name("import orjson\ntry:\n orjson.dumps(2**53 + 1, option=orjson.OPT_STRICT_INTEGER)\n result = 'missing'\nexcept Exception as exc:\n result = type(exc).__module__ + '.' + type(exc).__qualname__")
        == "builtins.TypeError",
    )
    check(
        "option-validation",
        exception_name("import orjson\ntry:\n orjson.dumps(True, option=-1)\n result = 'missing'\nexcept Exception as exc:\n result = type(exc).__module__ + '.' + type(exc).__qualname__")
        == "builtins.TypeError",
    )
    check(
        "datetime",
        encoded_equal(script("from datetime import datetime\nimport orjson\nvalue = orjson.dumps(datetime(2020, 1, 2, 3, 4, 5))\nresult = [isinstance(value, bytes), value.decode()]"),
                      '"2020-01-02T03:04:05"'),
    )
    check(
        "date",
        encoded_equal(script("from datetime import date\nimport orjson\nvalue = orjson.dumps(date(2020, 1, 2))\nresult = [isinstance(value, bytes), value.decode()]"), '"2020-01-02"'),
    )
    check(
        "uuid",
        encoded_equal(script("from uuid import UUID\nimport orjson\nvalue = orjson.dumps(UUID('00000000-0000-0000-0000-000000000001'), option=orjson.OPT_SERIALIZE_UUID)\nresult = [isinstance(value, bytes), value.decode()]"),
                      '"00000000-0000-0000-0000-000000000001"'),
    )
    check(
        "dataclass",
        encoded_equal(script("from dataclasses import dataclass\nimport orjson\n@dataclass\nclass Item:\n a: int\nvalue = orjson.dumps(Item(7), option=orjson.OPT_SERIALIZE_DATACLASS)\nresult = [isinstance(value, bytes), value.decode()]"), '{"a":7}'),
    )
    check(
        "default-callback",
        encoded_equal(script("import orjson\nclass Value: pass\nvalue = orjson.dumps(Value(), default=lambda value: {'kind': 'value'})\nresult = [isinstance(value, bytes), value.decode()]"), '{"kind":"value"}'),
    )
    check(
        "fragment",
        encoded_equal(script("import orjson\nvalue = orjson.dumps([orjson.Fragment(b'{\"x\":1}')])\nresult = [isinstance(value, bytes), value.decode()]"), '[{"x":1}]'),
    )
    check(
        "decode-errors",
        exception_name("import orjson\ntry:\n orjson.loads(b'{')\n result = 'missing'\nexcept Exception as exc:\n result = type(exc).__module__ + '.' + type(exc).__qualname__")
        == "orjson.JSONDecodeError",
    )
    check(
        "encode-errors",
        exception_name("import orjson\ntry:\n orjson.dumps(object())\n result = 'missing'\nexcept Exception as exc:\n result = type(exc).__module__ + '.' + type(exc).__qualname__")
        == "builtins.TypeError",
    )
    check(
        "signature-contract",
        equal(script("import inspect, orjson\nresult = [str(inspect.signature(orjson.dumps)), str(inspect.signature(orjson.loads))]"),
              ["(obj, /, default=None, option=None)", "(obj, /)"]),
    )
    check(
        "positional-only",
        equal(script("import orjson\ntry:\n orjson.dumps(obj=1)\n result = 'missing'\nexcept TypeError:\n result = 'TypeError'"), "TypeError"),
    )
    check(
        "non-str-keys",
        encoded_equal(script("import orjson\nvalue = orjson.dumps({1: 'one', True: 'bool'}, option=orjson.OPT_NON_STR_KEYS)\nresult = [isinstance(value, bytes), value.decode()]"), '{"1":"bool"}'),
    )
    check(
        "recursion-error",
        exception_name("import orjson\ntry:\n orjson.loads(b'[' * 1025 + b']' * 1025)\n result = 'missing'\nexcept Exception as exc:\n result = type(exc).__module__ + '.' + type(exc).__qualname__")
        == "orjson.JSONDecodeError",
    )

    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()

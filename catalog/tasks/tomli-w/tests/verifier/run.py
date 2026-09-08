"""Private deterministic scenarios for the tomli-w public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction. The candidate runner executes
the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    (
        'api-dumps-empty',
        'import tomli_w\nresult = tomli_w.dumps({})',
        {"ok": True, "value": ""},
    ),
    (
        'api-dumps-single-string',
        'import tomli_w\nresult = tomli_w.dumps({"key": "value"})',
        {"ok": True, "value": "key = \"value\"\n"},
    ),
    (
        'api-dumps-single-int',
        'import tomli_w\nresult = tomli_w.dumps({"num": 42})',
        {"ok": True, "value": "num = 42\n"},
    ),
    (
        'api-dumps-multiple',
        'import tomli_w\nresult = tomli_w.dumps({"a": 1, "b": "two", "c": True})',
        {"ok": True, "value": "a = 1\nb = \"two\"\nc = true\n"},
    ),
    (
        'api-dump-file',
        'import tomli_w\nfrom io import BytesIO\nfp = BytesIO()\ntomli_w.dump({"key": "value"}, fp)\nresult = fp.getvalue().decode()',
        {"ok": True, "value": "key = \"value\"\n"},
    ),
    (
        'type-bool-true',
        'import tomli_w\nresult = tomli_w.dumps({"flag": True})',
        {"ok": True, "value": "flag = true\n"},
    ),
    (
        'type-bool-false',
        'import tomli_w\nresult = tomli_w.dumps({"flag": False})',
        {"ok": True, "value": "flag = false\n"},
    ),
    (
        'type-int-zero',
        'import tomli_w\nresult = tomli_w.dumps({"n": 0})',
        {"ok": True, "value": "n = 0\n"},
    ),
    (
        'type-int-negative',
        'import tomli_w\nresult = tomli_w.dumps({"n": -42})',
        {"ok": True, "value": "n = -42\n"},
    ),
    (
        'type-int-large',
        'import tomli_w\nresult = tomli_w.dumps({"n": 999999999999})',
        {"ok": True, "value": "n = 999999999999\n"},
    ),
    (
        'type-float-simple',
        'import tomli_w\nresult = tomli_w.dumps({"f": 3.14})',
        {"ok": True, "value": "f = 3.14\n"},
    ),
    (
        'type-float-zero',
        'import tomli_w\nresult = tomli_w.dumps({"f": 0.0})',
        {"ok": True, "value": "f = 0.0\n"},
    ),
    (
        'type-float-negative',
        'import tomli_w\nresult = tomli_w.dumps({"f": -1.5})',
        {"ok": True, "value": "f = -1.5\n"},
    ),
    (
        'type-float-exp',
        'import tomli_w\nresult = tomli_w.dumps({"f": 1e10})',
        {"ok": True, "value": "f = 10000000000.0\n"},
    ),
    (
        'type-float-nan',
        'import tomli_w\nresult = tomli_w.dumps({"f": float("nan")})',
        {"ok": True, "value": "f = nan\n"},
    ),
    (
        'type-float-inf',
        'import tomli_w\nresult = tomli_w.dumps({"f": float("inf")})',
        {"ok": True, "value": "f = inf\n"},
    ),
    (
        'type-float-neginf',
        'import tomli_w\nresult = tomli_w.dumps({"f": float("-inf")})',
        {"ok": True, "value": "f = -inf\n"},
    ),
    (
        'type-decimal-simple',
        'import tomli_w\nimport decimal\nfrom decimal import Decimal\nresult = tomli_w.dumps({"d": Decimal("3.14159")})',
        {"ok": True, "value": "d = 3.14159\n"},
    ),
    (
        'type-decimal-integer',
        'import tomli_w\nimport decimal\nfrom decimal import Decimal\nresult = tomli_w.dumps({"d": Decimal("42")})',
        {"ok": True, "value": "d = 42.0\n"},
    ),
    (
        'type-decimal-zero',
        'import tomli_w\nimport decimal\nfrom decimal import Decimal\nresult = tomli_w.dumps({"d": Decimal("0")})',
        {"ok": True, "value": "d = 0.0\n"},
    ),
    (
        'type-decimal-exp',
        'import tomli_w\nimport decimal\nfrom decimal import Decimal\nresult = tomli_w.dumps({"d": Decimal("2e3")})',
        {"ok": True, "value": "d = 2e+3\n"},
    ),
    (
        'type-decimal-nan',
        'import tomli_w\nimport decimal\nfrom decimal import Decimal\nresult = tomli_w.dumps({"d": Decimal("nan")})',
        {"ok": True, "value": "d = nan\n"},
    ),
    (
        'type-decimal-inf',
        'import tomli_w\nimport decimal\nfrom decimal import Decimal\nresult = tomli_w.dumps({"d": Decimal("inf")})',
        {"ok": True, "value": "d = inf\n"},
    ),
    (
        'string-empty',
        'import tomli_w\nresult = tomli_w.dumps({"s": ""})',
        {"ok": True, "value": "s = \"\"\n"},
    ),
    (
        'string-quote',
        'import tomli_w\nresult = tomli_w.dumps({"s": "quote\\"here"})',
        {"ok": True, "value": "s = \"quote\\\"here\"\n"},
    ),
    (
        'string-backslash',
        'import tomli_w\nresult = tomli_w.dumps({"s": "back\\\\slash"})',
        {"ok": True, "value": "s = \"back\\\\slash\"\n"},
    ),
    (
        'string-newline-default',
        'import tomli_w\nresult = tomli_w.dumps({"s": "line1\\nline2"})',
        {"ok": True, "value": "s = \"line1\\nline2\"\n"},
    ),
    (
        'string-newline-multiline',
        'import tomli_w\nresult = tomli_w.dumps({"s": "line1\\nline2"}, multiline_strings=True)',
        {"ok": True, "value": "s = \"\"\"\nline1\nline2\"\"\"\n"},
    ),
    (
        'string-tab',
        'import tomli_w\nresult = tomli_w.dumps({"s": "tab\\there"})',
        {"ok": True, "value": "s = \"tab\there\"\n"},
    ),
    (
        'string-carriage-return',
        'import tomli_w\nresult = tomli_w.dumps({"s": "cr\\rhere"})',
        {"ok": True, "value": "s = \"cr\\rhere\"\n"},
    ),
    (
        'string-unicode',
        'import tomli_w\nresult = tomli_w.dumps({"s": "Hello 世界"})',
        {"ok": True, "value": "s = \"Hello 世界\"\n"},
    ),
    (
        'string-emoji',
        'import tomli_w\nresult = tomli_w.dumps({"s": "emoji 🎉"})',
        {"ok": True, "value": "s = \"emoji 🎉\"\n"},
    ),
    (
        'string-backspace',
        'import tomli_w\nresult = tomli_w.dumps({"s": "back\\bspace"})',
        {"ok": True, "value": "s = \"back\\bspace\"\n"},
    ),
    (
        'string-formfeed',
        'import tomli_w\nresult = tomli_w.dumps({"s": "form\\ffeed"})',
        {"ok": True, "value": "s = \"form\\ffeed\"\n"},
    ),
    (
        'key-bare-simple',
        'import tomli_w\nresult = tomli_w.dumps({"simple": "v"})',
        {"ok": True, "value": "simple = \"v\"\n"},
    ),
    (
        'key-bare-underscore',
        'import tomli_w\nresult = tomli_w.dumps({"under_score": "v"})',
        {"ok": True, "value": "under_score = \"v\"\n"},
    ),
    (
        'key-bare-dash',
        'import tomli_w\nresult = tomli_w.dumps({"with-dash": "v"})',
        {"ok": True, "value": "with-dash = \"v\"\n"},
    ),
    (
        'key-bare-numeric',
        'import tomli_w\nresult = tomli_w.dumps({"key123": "v"})',
        {"ok": True, "value": "key123 = \"v\"\n"},
    ),
    (
        'key-quoted-space',
        'import tomli_w\nresult = tomli_w.dumps({"key with space": "v"})',
        {"ok": True, "value": "\"key with space\" = \"v\"\n"},
    ),
    (
        'key-quoted-dot',
        'import tomli_w\nresult = tomli_w.dumps({"key.with.dot": "v"})',
        {"ok": True, "value": "\"key.with.dot\" = \"v\"\n"},
    ),
    (
        'key-quoted-special',
        'import tomli_w\nresult = tomli_w.dumps({"key@special": "v"})',
        {"ok": True, "value": "\"key@special\" = \"v\"\n"},
    ),
    (
        'array-empty',
        'import tomli_w\nresult = tomli_w.dumps({"arr": []})',
        {"ok": True, "value": "arr = []\n"},
    ),
    (
        'array-int',
        'import tomli_w\nresult = tomli_w.dumps({"arr": [1, 2, 3]})',
        {"ok": True, "value": "arr = [\n    1,\n    2,\n    3,\n]\n"},
    ),
    (
        'array-string',
        'import tomli_w\nresult = tomli_w.dumps({"arr": ["a", "b"]})',
        {"ok": True, "value": "arr = [\n    \"a\",\n    \"b\",\n]\n"},
    ),
    (
        'array-mixed',
        'import tomli_w\nresult = tomli_w.dumps({"arr": [1, "two", True]})',
        {"ok": True, "value": "arr = [\n    1,\n    \"two\",\n    true,\n]\n"},
    ),
    (
        'array-nested',
        'import tomli_w\nresult = tomli_w.dumps({"arr": [[1, 2], [3, 4]]})',
        {"ok": True, "value": "arr = [\n    [\n        1,\n        2,\n    ],\n    [\n        3,\n        4,\n    ],\n]\n"},
    ),
    (
        'array-indent-2',
        'import tomli_w\nresult = tomli_w.dumps({"arr": [1, 2]}, indent=2)',
        {"ok": True, "value": "arr = [\n  1,\n  2,\n]\n"},
    ),
    (
        'array-indent-0',
        'import tomli_w\nresult = tomli_w.dumps({"arr": [1, 2]}, indent=0)',
        {"ok": True, "value": "arr = [\n1,\n2,\n]\n"},
    ),
    (
        'array-tuple-empty',
        'import tomli_w\nresult = tomli_w.dumps({"t": ()})',
        {"ok": True, "value": "t = []\n"},
    ),
    (
        'array-tuple',
        'import tomli_w\nresult = tomli_w.dumps({"t": (1, 2, 3)})',
        {"ok": True, "value": "t = [\n    1,\n    2,\n    3,\n]\n"},
    ),
    (
        'table-simple',
        'import tomli_w\nresult = tomli_w.dumps({"table": {"key": "value"}})',
        {"ok": True, "value": "[table]\nkey = \"value\"\n"},
    ),
    (
        'table-nested',
        'import tomli_w\nresult = tomli_w.dumps({"parent": {"child": {"value": 1}}})',
        {"ok": True, "value": "[parent.child]\nvalue = 1\n"},
    ),
    (
        'table-multiple',
        'import tomli_w\nresult = tomli_w.dumps({"t1": {"a": 1}, "t2": {"b": 2}})',
        {"ok": True, "value": "[t1]\na = 1\n\n[t2]\nb = 2\n"},
    ),
    (
        'table-mixed-literals',
        'import tomli_w\nresult = tomli_w.dumps({"literal": 1, "table": {"nested": 2}})',
        {"ok": True, "value": "literal = 1\n\n[table]\nnested = 2\n"},
    ),
    (
        'aot-simple',
        'import tomli_w\nresult = tomli_w.dumps({"items": [{"a": 1}, {"a": 2}]})',
        {"ok": True, "value": "items = [\n    { a = 1 },\n    { a = 2 },\n]\n"},
    ),
    (
        'aot-complex',
        'import tomli_w\nresult = tomli_w.dumps({"products": [{"name": "A", "price": 10}, {"name": "B", "price": 20}]})',
        {"ok": True, "value": "products = [\n    { name = \"A\", price = 10 },\n    { name = \"B\", price = 20 },\n]\n"},
    ),
    (
        'aot-large',
        'import tomli_w\nresult = tomli_w.dumps({"items": [{"key": "very_long_value_that_exceeds_100_chars_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "other": 1}]})',
        {"ok": True, "value": "[[items]]\nkey = \"very_long_value_that_exceeds_100_chars_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\"\nother = 1\n"},
    ),
    (
        'order-preserved',
        'import tomli_w\nresult = tomli_w.dumps({"z": 1, "a": 2, "m": 3})',
        {"ok": True, "value": "z = 1\na = 2\nm = 3\n"},
    ),
    (
        'datetime-date',
        'import tomli_w\nimport datetime\nfrom datetime import date\nresult = tomli_w.dumps({"d": date(2024, 1, 15)})',
        {"ok": True, "value": "d = 2024-01-15\n"},
    ),
    (
        'datetime-time',
        'import tomli_w\nimport datetime\nfrom datetime import time\nresult = tomli_w.dumps({"t": time(12, 30, 45)})',
        {"ok": True, "value": "t = 12:30:45\n"},
    ),
    (
        'datetime-datetime',
        'import tomli_w\nfrom datetime import datetime\nresult = tomli_w.dumps({"dt": datetime(2024, 1, 15, 12, 30, 45)})',
        {"ok": True, "value": "dt = 2024-01-15 12:30:45\n"},
    ),
    (
        'datetime-datetime-micro',
        'import tomli_w\nfrom datetime import datetime\nresult = tomli_w.dumps({"dt": datetime(2024, 1, 15, 12, 30, 45, 123456)})',
        {"ok": True, "value": "dt = 2024-01-15 12:30:45.123456\n"},
    ),
    (
        'error-invalid-key-int',
        'import tomli_w\ntry:\n  tomli_w.dumps({1: "v"})\n  result = False\nexcept TypeError as e:\n  result = ["TypeError" in str(type(e)), "int" in str(e)]',
        {"ok": True, "value": [True, True]},
    ),
    (
        'error-invalid-key-none',
        'import tomli_w\ntry:\n  tomli_w.dumps({None: "v"})\n  result = False\nexcept TypeError as e:\n  result = ["TypeError" in str(type(e)), "NoneType" in str(e)]',
        {"ok": True, "value": [True, True]},
    ),
    (
        'error-negative-indent',
        'import tomli_w\ntry:\n  tomli_w.dumps({}, indent=-1)\n  result = False\nexcept ValueError:\n  result = True',
        {"ok": True, "value": True},
    ),
    (
        'error-invalid-type',
        'import tomli_w\ntry:\n  tomli_w.dumps({"obj": object()})\n  result = False\nexcept TypeError as e:\n  result = "not TOML serializable" in str(e)',
        {"ok": True, "value": True},
    ),
    (
        'error-bytearray',
        'import tomli_w\ntry:\n  tomli_w.dumps({"ba": bytearray()})\n  result = False\nexcept TypeError as e:\n  result = "bytearray" in str(e)',
        {"ok": True, "value": True},
    ),
    (
        'error-time-with-tz',
        'import tomli_w\nimport datetime\nfrom datetime import time, timezone\ntry:\n  tomli_w.dumps({"t": time(12, 0, tzinfo=timezone.utc)})\n  result = False\nexcept ValueError:\n  result = True',
        {"ok": True, "value": True},
    ),
    (
        'roundtrip-simple',
        'import tomli_w\nimport tomli\nobj = {"a": 1, "b": "two"}\ntoml_str = tomli_w.dumps(obj)\nresult = tomli.loads(toml_str) == obj',
        {"ok": True, "value": True},
    ),
    (
        'roundtrip-nested',
        'import tomli_w\nimport tomli\nobj = {"t": {"nested": {"deep": 42}}}\ntoml_str = tomli_w.dumps(obj)\nresult = tomli.loads(toml_str) == obj',
        {"ok": True, "value": True},
    ),
    (
        'roundtrip-array',
        'import tomli_w\nimport tomli\nobj = {"arr": [1, 2, [3, 4]]}\ntoml_str = tomli_w.dumps(obj)\nresult = tomli.loads(toml_str) == obj',
        {"ok": True, "value": True},
    ),
    (
        'attr-all',
        'import tomli_w\nresult = list(tomli_w.__all__)',
        {"ok": True, "value": ["dumps", "dump"]},
    ),
    (
        'attr-version',
        'import tomli_w\nresult = isinstance(tomli_w.__version__, str) and len(tomli_w.__version__) > 0',
        {"ok": True, "value": True},
    ),
    (
        'attr-has-dumps',
        'import tomli_w\nresult = hasattr(tomli_w, "dumps") and callable(tomli_w.dumps)',
        {"ok": True, "value": True},
    ),
    (
        'attr-has-dump',
        'import tomli_w\nresult = hasattr(tomli_w, "dump") and callable(tomli_w.dump)',
        {"ok": True, "value": True},
    ),
    (
        'complex-config',
        'import tomli_w\nobj = {\n    "title": "Config",\n    "version": 1,\n    "database": {"host": "localhost", "port": 5432},\n    "servers": [{"ip": "10.0.0.1"}, {"ip": "10.0.0.2"}]\n}\ntoml_str = tomli_w.dumps(obj)\nresult = "title" in toml_str and "[database]" in toml_str and "servers" in toml_str',
        {"ok": True, "value": True},
    ),
    (
        'complex-multiline',
        'import tomli_w\nobj = {"text": "line1\\nline2\\nline3"}\nresult = \'"""\' in tomli_w.dumps(obj, multiline_strings=True)',
        {"ok": True, "value": True},
    ),
    (
        'edge-large-number',
        'import tomli_w\nresult = tomli_w.dumps({"n": 99999999999999999})',
        {"ok": True, "value": "n = 99999999999999999\n"},
    ),
    (
        'edge-negative-zero-float',
        'import tomli_w\nresult = tomli_w.dumps({"f": -0.0})',
        {"ok": True, "value": "f = -0.0\n"},
    ),
    (
        'edge-empty-nested-table',
        'import tomli_w\nresult = tomli_w.dumps({"t": {}})',
        {"ok": True, "value": "[t]\n"},
    ),
    (
        'edge-many-keys',
        'import tomli_w\nobj = {f"key{i}": i for i in range(10)}\nresult = len(tomli_w.dumps(obj).split("\\n")) > 10',
        {"ok": True, "value": True},
    ),
    (
        'edge-deep-nesting',
        'import tomli_w\nobj = {"a": {"b": {"c": {"d": {"e": 5}}}}}\nresult = "[a.b.c.d]" in tomli_w.dumps(obj)',
        {"ok": True, "value": True},
    ),
    (
        'dump-bytesio',
        'import tomli_w\nfrom io import BytesIO\nfp = BytesIO()\ntomli_w.dump({"key": "value"}, fp)\nresult = fp.getvalue() == b\'key = "value"\\n\' ',
        {"ok": True, "value": True},
    ),
    (
        'dump-multiline',
        'import tomli_w\nfrom io import BytesIO\nfp = BytesIO()\ntomli_w.dump({"text": "line1\\nline2"}, fp, multiline_strings=True)\nresult = b\'"""\' in fp.getvalue()',
        {"ok": True, "value": True},
    ),
    (
        'dump-indent',
        'import tomli_w\nfrom io import BytesIO\nfp = BytesIO()\ntomli_w.dump({"arr": [1, 2]}, fp, indent=2)\nresult = b\'  1,\' in fp.getvalue()',
        {"ok": True, "value": True},
    ),
    (
        'multiline-crlf',
        'import tomli_w\nresult = tomli_w.dumps({"s": "line1\\r\\nline2"}, multiline_strings=True)',
        {"ok": True, "value": "s = \"\"\"\nline1\nline2\"\"\"\n"},
    ),
    (
        'key-empty-string',
        'import tomli_w\nresult = tomli_w.dumps({"": "empty-key"})',
        {"ok": True, "value": "\"\" = \"empty-key\"\n"},
    ),
    (
        'float-very-small',
        'import tomli_w\nresult = tomli_w.dumps({"f": 1e-100})',
        {"ok": True, "value": "f = 1e-100\n"},
    ),
    (
        'table-then-literal',
        'import tomli_w\nresult = "[section]" in tomli_w.dumps({"section": {"a": 1}, "literal": 2})',
        {"ok": True, "value": True},
    ),
    (
        'array-of-arrays',
        'import tomli_w\nresult = tomli_w.dumps({"matrix": [[1, 2], [3, 4], [5, 6]]})',
        {"ok": True, "value": "matrix = [\n    [\n        1,\n        2,\n    ],\n    [\n        3,\n        4,\n    ],\n    [\n        5,\n        6,\n    ],\n]\n"},
    ),
]

assert len(CASES) == 90, f"Expected 90 cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

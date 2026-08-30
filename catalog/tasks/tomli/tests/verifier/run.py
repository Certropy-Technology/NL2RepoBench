# Embedded candidate-side scenario strings are intentionally kept readable;
# their generated source lines are not subject to the repository line limit.
# ruff: noqa: E501
from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import (
    call,
    execute_script,
    get,
    metadata_requires,
)

LEAVES: list[dict[str, str]] = []


def record(leaf_id: str, passed: bool, detail: str = "") -> None:
    item = {"id": leaf_id, "status": "passed" if passed else "failed"}
    if detail and not passed:
        item["message"] = detail[:500]
    LEAVES.append(item)


def value(leaf_id: str, observed: object, expected: object) -> None:
    record(leaf_id, observed == expected, f"expected {expected!r}, got {observed!r}")


def call_value(leaf_id: str, attribute: str, *args: object, expected: object, **kwargs: object) -> None:
    result = call("tomli", attribute, *args, timeout_sec=2.0, **kwargs)
    value(leaf_id, result.value if result.ok else result.exception_message, expected)


def script_value(leaf_id: str, source: str, expected: object) -> None:
    result = execute_script(source, timeout_sec=2.0)
    value(leaf_id, result.value if result.ok else result.exception_message, expected)


def call_error(
    leaf_id: str,
    attribute: str,
    *args: object,
    exception_type: str,
    message: str | None = None,
) -> None:
    result = call("tomli", attribute, *args, timeout_sec=2.0)
    passed = (
        not result.ok
        and result.exception_type == exception_type
        and (message is None or result.exception_message == message)
    )
    record(
        leaf_id,
        passed,
        f"expected {exception_type} {message!r}, got {result.exception_type} {result.exception_message!r}",
    )


script_value(
    "root-exports",
    "import tomli\nresult = {'all': list(tomli.__all__), 'version': tomli.__version__}",
    {"all": ["loads", "load", "TOMLDecodeError"], "version": "2.4.1"},
)
installed_version = get("tomli", "__version__")
value(
    "installed-version",
    installed_version.value if installed_version.ok else installed_version.exception_message,
    "2.4.1",
)

metadata = metadata_requires("tomli")
record(
    "metadata-requires",
    metadata.ok and metadata.value in (None, []),
    f"unexpected installed requirements: {metadata.value!r}",
)

call_value(
    "scalar-values",
    "loads",
    'title = "TOML"\nactive = true\ncount = 42\nratio = 1.5',
    expected={"title": "TOML", "active": True, "count": 42, "ratio": 1.5},
)
call_value(
    "nested-tables",
    "loads",
    "[owner]\nname = \"Tom\"\n[database]\nserver = \"192.0.2.1\"\nports = [8000, 8001]",
    expected={
        "owner": {"name": "Tom"},
        "database": {"server": "192.0.2.1", "ports": [8000, 8001]},
    },
)
call_value(
    "arrays-inline",
    "loads",
    "products = [{name = \"Hammer\", sku = 738}, {name = \"Nail\", sku = 284}]",
    expected={
        "products": [
            {"name": "Hammer", "sku": 738},
            {"name": "Nail", "sku": 284},
        ]
    },
)
call_value(
    "basic-strings",
    "loads",
    'basic = "line\\nnext\\t\\u03bb\\\""\nliteral = \'C:/tmp\'',
    expected={"basic": 'line\nnext\tλ"', "literal": "C:/tmp"},
)
call_value(
    "multiline-literal",
    "loads",
    'basic = """hello\nworld"""\nliteral = \'\'\'raw\ntext\'\'\'',
    expected={"basic": "hello\nworld", "literal": "raw\ntext"},
)
call_value(
    "numbers",
    "loads",
    "hex = 0xDEAD_BEEF\nbin = 0b1101\noct = 0o755\nlarge = 1_000_000\nnegative = -42",
    expected={"hex": 3735928559, "bin": 13, "oct": 493, "large": 1000000, "negative": -42},
)
script_value(
    "dates-times",
    "import tomli\ndata = tomli.loads('date = 1979-05-27\\ndt = 1979-05-27T07:32:00Z\\ntime = 07:32:00.999999')\nresult = {key: [type(item).__name__, item.isoformat()] for key, item in data.items()}",
    {
        "date": ["date", "1979-05-27"],
        "dt": ["datetime", "1979-05-27T07:32:00+00:00"],
        "time": ["time", "07:32:00.999999"],
    },
)
script_value(
    "custom-float",
    "from decimal import Decimal\nimport tomli\ndata = tomli.loads('value = 1.2300\\nother = -inf', parse_float=Decimal)\nresult = {key: [type(item).__name__, str(item)] for key, item in data.items()}",
    {"value": ["Decimal", "1.2300"], "other": ["Decimal", "-Infinity"]},
)
script_value(
    "load-binary",
    "import io\nimport tomli\nresult = tomli.load(io.BytesIO(b\"one = 1\\ntwo = 'two'\\n\"))",
    {"one": 1, "two": "two"},
)
script_value(
    "load-empty",
    "import io\nimport tomli\nresult = tomli.load(io.BytesIO(b''))",
    {},
)
script_value(
    "load-text-reject",
    "import io\nimport tomli\ntry:\n    tomli.load(io.StringIO('one = 1'))\nexcept Exception as exc:\n    result = [type(exc).__name__, str(exc)]\nelse:\n    result = None",
    ["TypeError", "File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`"],
)
script_value(
    "loads-nonstr-reject",
    "import tomli\ntry:\n    tomli.loads(None)\nexcept Exception as exc:\n    result = [type(exc).__name__, str(exc)]\nelse:\n    result = None",
    ["TypeError", "Expected str object, not 'NoneType'"],
)
script_value(
    "loads-bytes-reject",
    "import tomli\ntry:\n    tomli.loads(b'one = 1')\nexcept Exception as exc:\n    result = [type(exc).__name__, str(exc)]\nelse:\n    result = None",
    ["TypeError", "Expected str object, not 'bytes'"],
)

call_error(
    "error-location",
    "loads",
    "val=.",
    exception_type="tomli._parser.TOMLDecodeError",
    message="Invalid value (at line 1, column 5)",
)
call_error(
    "error-statement",
    "loads",
    ".",
    exception_type="tomli._parser.TOMLDecodeError",
    message="Invalid statement (at line 1, column 1)",
)
call_error(
    "error-end",
    "loads",
    "\n\nfwfw=",
    exception_type="tomli._parser.TOMLDecodeError",
    message="Invalid value (at end of document)",
)
script_value(
    "error-escape",
    "import tomli\ntry:\n    tomli.loads(\"v = '\\n'\")\nexcept Exception as exc:\n    result = [type(exc).__name__, '\\\\n' in str(exc)]\nelse:\n    result = None",
    ["TOMLDecodeError", True],
)
script_value(
    "error-attrs",
    "import tomli\ndoc = 'v=1\\n[table]\\nv=\\\'val\\\''\ne = tomli.TOMLDecodeError('error parsing', doc, 13)\nresult = {'args': list(e.args), 'msg': e.msg, 'doc': e.doc, 'pos': e.pos, 'lineno': e.lineno, 'colno': e.colno, 'value_error': isinstance(e, ValueError)}",
    {
        "args": ["error parsing (at line 3, column 2)"],
        "msg": "error parsing",
        "doc": "v=1\n[table]\nv='val'",
        "pos": 13,
        "lineno": 3,
        "colno": 2,
        "value_error": True,
    },
)
script_value(
    "error-deprecated",
    "import warnings\nimport tomli\nwith warnings.catch_warnings(record=True) as caught:\n    warnings.simplefilter('always')\n    error = tomli.TOMLDecodeError('legacy')\nresult = [list(error.args), len(caught), caught[0].category.__name__ if caught else None]",
    [["legacy"], 1, "DeprecationWarning"],
)
script_value(
    "parse-float-reject",
    "import tomli\ndef invalid(value):\n    return {}\ntry:\n    tomli.loads('value = 1.0', parse_float=invalid)\nexcept Exception as exc:\n    result = [type(exc).__name__, str(exc)]\nelse:\n    result = None",
    ["ValueError", "parse_float must not return dicts or lists"],
)
call_error(
    "invalid-duplicate",
    "loads",
    "key = 1\nkey = 2",
    exception_type="tomli._parser.TOMLDecodeError",
)
call_error(
    "invalid-date",
    "loads",
    "date = 2021-02-29",
    exception_type="tomli._parser.TOMLDecodeError",
)
call_error(
    "invalid-inline",
    "loads",
    "value = { key = 1, key = 2 }",
    exception_type="tomli._parser.TOMLDecodeError",
)
call_value(
    "crlf-comments",
    "loads",
    "# heading\r\n[section]\r\nvalue = 1 # trailing\r\n",
    expected={"section": {"value": 1}},
)
call_value(
    "quoted-unicode",
    "loads",
    '"quoted key" = "café"\n"unicode" = "значение"',
    expected={"quoted key": "café", "unicode": "значение"},
)
script_value(
    "deepcopy",
    "import copy\nimport tomli\nvalue = tomli.loads('[table]\\nitems = [1, 2]')\nclone = copy.deepcopy(value)\nresult = clone == value and clone is not value and clone['table']['items'] is not value['table']['items']",
    True,
)
script_value(
    "recursion",
    "import tomli\ndocument = 'arr = ' + ('[' * 80) + (']' * 80)\nvalue = tomli.loads(document)['arr']\nresult = isinstance(value, list) and len(value) == 1 and isinstance(value[0], list)",
    True,
)
script_value(
    "types-module",
    "import importlib\nmodule = importlib.import_module('tomli._types')\nresult = hasattr(module, 'ParseFloat') and hasattr(module, 'Key')",
    True,
)
script_value(
    "class-inheritance",
    "import tomli\nresult = issubclass(tomli.TOMLDecodeError, ValueError) and tomli.TOMLDecodeError.__module__ == 'tomli._parser'",
    True,
)

print(json.dumps({"schema_version": "1.0", "leaves": LEAVES}, separators=(",", ":"), sort_keys=True))

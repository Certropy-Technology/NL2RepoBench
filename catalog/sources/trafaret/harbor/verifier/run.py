"""Private deterministic scenarios for the trafaret public contract.

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
    ("int-valid", "import trafaret as t\nresult = t.Int().check(42)", {"ok": True, "value": 42}),
    ("int-invalid-string", "import trafaret as t\ntry:\n    result = t.Int().check('not_int')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("int-invalid-float", "import trafaret as t\ntry:\n    result = t.Int().check(3.14)\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("int-negative", "import trafaret as t\nresult = t.Int().check(-42)", {"ok": True, "value": -42}),
    ("toint-from-string", "import trafaret as t\nresult = t.ToInt().check('42')", {"ok": True, "value": 42}),
    ("toint-from-int", "import trafaret as t\nresult = t.ToInt().check(42)", {"ok": True, "value": 42}),
    ("toint-invalid", "import trafaret as t\ntry:\n    result = t.ToInt().check('not_a_number')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("float-valid", "import trafaret as t\nresult = t.Float().check(3.14)", {"ok": True, "value": 3.14}),
    ("float-from-int", "import trafaret as t\nresult = t.Float().check(42)", {"ok": True, "value": 42.0}),
    ("float-invalid", "import trafaret as t\ntry:\n    result = t.Float().check('text')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("tofloat-from-string", "import trafaret as t\nresult = t.ToFloat().check('3.14')", {"ok": True, "value": 3.14}),
    ("tofloat-from-int", "import trafaret as t\nresult = t.ToFloat().check(42)", {"ok": True, "value": 42.0}),
    ("string-valid", "import trafaret as t\nresult = t.String().check('hello')", {"ok": True, "value": "hello"}),
    ("string-invalid-int", "import trafaret as t\ntry:\n    result = t.String().check(123)\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("string-max-length", "import trafaret as t\nresult = t.String(max_length=5).check('hello')", {"ok": True, "value": "hello"}),
    ("string-max-length-exceeded", "import trafaret as t\ntry:\n    result = t.String(max_length=3).check('hello')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("string-min-length", "import trafaret as t\nresult = t.String(min_length=3).check('hello')", {"ok": True, "value": "hello"}),
    ("string-min-length-fail", "import trafaret as t\ntry:\n    result = t.String(min_length=10).check('hi')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("string-empty", "import trafaret as t\ntry:\n    result = t.String().check('')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("bool-true", "import trafaret as t\nresult = t.Bool().check(True)", {"ok": True, "value": True}),
    ("bool-false", "import trafaret as t\nresult = t.Bool().check(False)", {"ok": True, "value": False}),
    ("bool-invalid", "import trafaret as t\ntry:\n    result = t.Bool().check('yes')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("bool-invalid-int", "import trafaret as t\ntry:\n    result = t.Bool().check(1)\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("tobool-yes", "import trafaret as t\nresult = t.ToBool().check('yes')", {"ok": True, "value": True}),
    ("tobool-no", "import trafaret as t\nresult = t.ToBool().check('no')", {"ok": True, "value": False}),
    ("tobool-true", "import trafaret as t\nresult = t.ToBool().check('true')", {"ok": True, "value": True}),
    ("tobool-false", "import trafaret as t\nresult = t.ToBool().check('false')", {"ok": True, "value": False}),
    ("tobool-1", "import trafaret as t\nresult = t.ToBool().check('1')", {"ok": True, "value": True}),
    ("tobool-0", "import trafaret as t\nresult = t.ToBool().check('0')", {"ok": True, "value": False}),
    ("list-int", "import trafaret as t\nresult = t.List(t.Int).check([1, 2, 3])", {"ok": True, "value": [1, 2, 3]}),
    ("list-string", "import trafaret as t\nresult = t.List(t.String).check(['a', 'b', 'c'])", {"ok": True, "value": ["a", "b", "c"]}),
    ("list-mixed-error", "import trafaret as t\ntry:\n    result = t.List(t.Int).check([1, 'two', 3])\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("list-empty", "import trafaret as t\nresult = t.List(t.Int).check([])", {"ok": True, "value": []}),
    ("dict-simple", "import trafaret as t\nschema = t.Dict({t.Key('name'): t.String, t.Key('age'): t.Int})\nresult = schema.check({'name': 'John', 'age': 30})", {"ok": True, "value": {"name": "John", "age": 30}}),
    ("dict-missing-key", "import trafaret as t\nschema = t.Dict({t.Key('name'): t.String, t.Key('age'): t.Int})\ntry:\n    result = schema.check({'name': 'John'})\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("dict-wrong-type", "import trafaret as t\nschema = t.Dict({t.Key('age'): t.Int})\ntry:\n    result = schema.check({'age': 'thirty'})\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("dict-key-default", "import trafaret as t\nschema = t.Dict({t.Key('name'): t.String, t.Key('age', default=0): t.Int})\nresult = schema.check({'name': 'John'})", {"ok": True, "value": {"name": "John", "age": 0}}),
    ("dict-key-optional", "import trafaret as t\nschema = t.Dict({t.Key('name'): t.String, t.Key('age', optional=True): t.Int})\nresult = schema.check({'name': 'John'})", {"ok": True, "value": {"name": "John"}}),
    ("dict-ignore-extra", "import trafaret as t\nschema = t.Dict({t.Key('name'): t.String}).ignore_extra('*')\nresult = schema.check({'name': 'John', 'extra': 'data'})", {"ok": True, "value": {"name": "John"}}),
    ("dict-allow-extra", "import trafaret as t\nschema = t.Dict({t.Key('name'): t.String}).allow_extra('*')\nresult = schema.check({'name': 'John', 'extra': 'data'})", {"ok": True, "value": {"name": "John", "extra": "data"}}),
    ("dict-nested", "import trafaret as t\nschema = t.Dict({t.Key('user'): t.Dict({t.Key('id'): t.Int})})\nresult = schema.check({'user': {'id': 42}})", {"ok": True, "value": {"user": {"id": 42}}}),
    ("enum-valid", "import trafaret as t\nresult = t.Enum('apple', 'banana', 'cherry').check('apple')", {"ok": True, "value": "apple"}),
    ("enum-invalid", "import trafaret as t\ntry:\n    result = t.Enum('apple', 'banana').check('orange')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("enum-numbers", "import trafaret as t\nresult = t.Enum(1, 2, 3).check(2)", {"ok": True, "value": 2}),
    ("any-dict", "import trafaret as t\nresult = t.Any().check({'key': 'value'})", {"ok": True, "value": {"key": "value"}}),
    ("any-list", "import trafaret as t\nresult = t.Any().check([1, 'two', 3.0])", {"ok": True, "value": [1, "two", 3.0]}),
    ("any-none", "import trafaret as t\nresult = t.Any().check(None)", {"ok": True, "value": None}),
    ("null-valid", "import trafaret as t\nresult = t.Null().check(None)", {"ok": True, "value": None}),
    ("null-invalid", "import trafaret as t\ntry:\n    result = t.Null().check('not_none')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("or-first-match", "import trafaret as t\nresult = t.Or(t.Int, t.String).check(42)", {"ok": True, "value": 42}),
    ("or-second-match", "import trafaret as t\nresult = t.Or(t.Int, t.String).check('hello')", {"ok": True, "value": "hello"}),
    ("or-no-match", "import trafaret as t\ntry:\n    result = t.Or(t.Int, t.String).check([])\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("and-chain", "import trafaret as t\nresult = (t.Int() & (lambda x: x > 0)).check(5)", {"ok": True, "value": True}),
    ("and-chain-fail", "import trafaret as t\nresult = (t.Int() & (lambda x: x > 0)).check(-5)", {"ok": True, "value": False}),
    ("transform-upper", "import trafaret as t\nresult = (t.String() >> (lambda s: s.upper())).check('hello')", {"ok": True, "value": "HELLO"}),
    ("transform-multiply", "import trafaret as t\nresult = (t.Int() >> (lambda x: x * 2)).check(21)", {"ok": True, "value": 42}),
    ("type-int", "import trafaret as t\nresult = t.Type(int).check(42)", {"ok": True, "value": 42}),
    ("type-str", "import trafaret as t\nresult = t.Type(str).check('hello')", {"ok": True, "value": "hello"}),
    ("type-fail", "import trafaret as t\ntry:\n    result = t.Type(int).check('not_int')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("callable-check-function", "import trafaret as t\ndef f(): pass\ntry:\n    t.Callable().check(f)\n    result = 'passed'\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "passed"}),
    ("callable-check-lambda", "import trafaret as t\ntry:\n    t.Callable().check(lambda: None)\n    result = 'passed'\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "passed"}),
    ("callable-fail", "import trafaret as t\ntry:\n    t.Callable().check(42)\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("call-custom", "import trafaret as t\ndef double(x):\n    return x * 2\nresult = t.Call(double).check(21)", {"ok": True, "value": 42}),
    ("call-error", "import trafaret as t\ndef check_positive(x):\n    if x > 0:\n        return x\n    return t.DataError('must be positive')\ntry:\n    result = t.Call(check_positive).check(-5)\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("mapping-string-int", "import trafaret as t\nresult = t.Mapping(t.String, t.Int).check({'a': 1, 'b': 2})", {"ok": True, "value": {"a": 1, "b": 2}}),
    ("mapping-key-error", "import trafaret as t\ntry:\n    result = t.Mapping(t.String, t.Int).check({123: 1})\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("mapping-value-error", "import trafaret as t\ntry:\n    result = t.Mapping(t.String, t.Int).check({'a': 'not_int'})\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("tuple-simple", "import trafaret as t\nresult = t.Tuple(t.String, t.Int, t.Float).check(('hello', 42, 3.14))", {"ok": True, "value": ["hello", 42, 3.14]}),
    ("tuple-wrong-type", "import trafaret as t\ntry:\n    result = t.Tuple(t.String, t.Int).check(('hello', 'world'))\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("tuple-wrong-length", "import trafaret as t\ntry:\n    result = t.Tuple(t.String, t.Int).check(('hello',))\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("regexp-match", "import trafaret as t\nresult = t.Regexp(r'^[a-z]+$').check('hello')", {"ok": True, "value": "hello"}),
    ("regexp-no-match", "import trafaret as t\ntry:\n    result = t.Regexp(r'^[a-z]+$').check('Hello123')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("regexpraw-extract", "import trafaret as t\nresult = (t.RegexpRaw(r'name=(\\w+)') >> (lambda m: m.group(1))).check('name=Alice')", {"ok": True, "value": "Alice"}),
    ("email-valid", "import trafaret as t\nresult = t.Email.check('user@example.com')", {"ok": True, "value": "user@example.com"}),
    ("email-invalid", "import trafaret as t\ntry:\n    result = t.Email.check('not_an_email')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("url-valid", "import trafaret as t\nresult = t.URL.check('https://example.com/path')", {"ok": True, "value": "https://example.com/path"}),
    ("url-invalid", "import trafaret as t\ntry:\n    result = t.URL.check('not a url')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("ipv4-valid", "import trafaret as t\nresult = t.IPv4.check('192.168.1.1')", {"ok": True, "value": "192.168.1.1"}),
    ("ipv4-invalid", "import trafaret as t\ntry:\n    result = t.IPv4.check('999.999.999.999')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("forward-recursive", "import trafaret as t\nnode = t.Forward()\nnode << t.Dict({t.Key('value'): t.Int, t.Key('next', optional=True): node})\nresult = node.check({'value': 1, 'next': {'value': 2}})", {"ok": True, "value": {"value": 1, "next": {"value": 2}}}),
    ("iterable-list", "import trafaret as t\nresult = t.Iterable(t.Int).check([1, 2, 3])", {"ok": True, "value": [1, 2, 3]}),
    ("iterable-tuple", "import trafaret as t\nresult = t.Iterable(t.String).check(('a', 'b', 'c'))", {"ok": True, "value": ["a", "b", "c"]}),
    ("guard-valid", "import trafaret as t\n@t.guard(x=t.Int, y=t.String)\ndef func(x, y):\n    return f'{y}: {x}'\nresult = func(x=42, y='answer')", {"ok": True, "value": "answer: 42"}),
    ("guard-invalid", "import trafaret as t\n@t.guard(x=t.Int)\ndef func(x):\n    return x * 2\ntry:\n    result = func(x='not_int')\nexcept t.DataError:\n    result = 'DataError'", {"ok": True, "value": "DataError"}),
    ("dataerror-as-dict", "import trafaret as t\ntry:\n    t.Dict({t.Key('age'): t.Int}).check({'age': 'invalid'})\nexcept t.DataError as e:\n    result = list(e.as_dict().keys())", {"ok": True, "value": ["age"]}),
]

assert len(CASES) == 85, f"Expected 85 cases, got {len(CASES)}"


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

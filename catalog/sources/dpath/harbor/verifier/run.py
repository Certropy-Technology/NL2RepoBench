"""Private deterministic scenarios for the dpath public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (dpath-python 2.2.0,
immutable revision a8169a93b4561cd6c5fe58dbe484bd3b37845fe2). The
candidate runner executes the script and reads the ``result`` binding.
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
    # Basic get operations
    (
        "get-simple",
        "import dpath\nobj = {'a': {'b': {'c': 1}}}\nresult = dpath.get(obj, 'a/b/c')",
        {"ok": True, "value": 1},
    ),
    (
        "get-root",
        "import dpath\nobj = {'a': 1}\nresult = dpath.get(obj, '/')",
        {"ok": True, "value": {"a": 1}},
    ),
    (
        "get-empty-list",
        "import dpath\nobj = {'a': 1}\nresult = dpath.get(obj, [])",
        {"ok": True, "value": {"a": 1}},
    ),
    (
        "get-list-path",
        "import dpath\nobj = {'a': {'b': 2}}\nresult = dpath.get(obj, ['a', 'b'])",
        {"ok": True, "value": 2},
    ),
    (
        "get-with-default",
        "import dpath\nobj = {'a': 1}\nresult = dpath.get(obj, 'x/y', default=42)",
        {"ok": True, "value": 42},
    ),
    (
        "get-missing-no-default",
        "import dpath\nobj = {'a': 1}\ntry:\n    dpath.get(obj, 'x/y')\n    result = 'no-error'\nexcept KeyError:\n    result = 'KeyError'",
        {"ok": True, "value": "KeyError"},
    ),
    (
        "get-glob-single-match",
        "import dpath\nobj = {'a': {'b': {'c': 42}}}\nresult = dpath.get(obj, 'a/*/c')",
        {"ok": True, "value": 42},
    ),
    (
        "get-glob-multiple-matches",
        "import dpath\nobj = {'a': {'b': {'d': 1}, 'c': {'d': 2}}}\ntry:\n    dpath.get(obj, 'a/*/d')\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "get-none-value",
        "import dpath\nobj = {'a': {'b': None}}\nresult = dpath.get(obj, 'a/b')",
        {"ok": True, "value": None},
    ),
    
    # Search operations
    (
        "search-simple-glob",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2}}\nresult = dpath.search(obj, 'a/*')",
        {"ok": True, "value": {"a": {"b": 1, "c": 2}}},
    ),
    (
        "search-star-star",
        "import dpath\nobj = {'a': {'b': {'c': 1}}}\nresult = dpath.search(obj, '**')",
        {"ok": True, "value": {"a": {"b": {"c": 1}}}},
    ),
    (
        "search-no-match",
        "import dpath\nobj = {'a': 1}\nresult = dpath.search(obj, 'x/*')",
        {"ok": True, "value": {}},
    ),
    (
        "search-yielded",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2}}\nresult = list(dpath.search(obj, 'a/*', yielded=True))\nresult = sorted(result)",
        {"ok": True, "value": [["a/b", 1], ["a/c", 2]]},
    ),
    (
        "search-with-filter",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2, 'd': 3}}\ntry:\n    r = dpath.search(obj, 'a/*', afilter=lambda x: x > 1)\n    result = (_wrapped := None)\nexcept TypeError as e:\n    result = 'typeerror'",
        {"ok": True, "value": "typeerror"},
    ),
    (
        "search-dirs-false",
        "import dpath\nobj = {'a': {'b': {'c': 1}}}\nresult = dpath.search(obj, '**', dirs=False)",
        {"ok": True, "value": {"a": {"b": {"c": 1}}}},
    ),
    (
        "search-list-path",
        "import dpath\nobj = {'a': {'b': 1}}\nresult = dpath.search(obj, ['a', '*'])",
        {"ok": True, "value": {"a": {"b": 1}}},
    ),
    (
        "search-custom-separator",
        "import dpath\nobj = {'a': {'b': 1}}\nresult = dpath.search(obj, 'a.b', separator='.')",
        {"ok": True, "value": {"a": {"b": 1}}},
    ),
    
    # Values operations
    (
        "values-simple",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2, 'd': 3}}\nresult = sorted(dpath.values(obj, 'a/*'))",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "values-empty",
        "import dpath\nobj = {'a': 1}\nresult = dpath.values(obj, 'x/*')",
        {"ok": True, "value": []},
    ),
    (
        "values-from-list",
        "import dpath\nobj = {'a': [1, 2, 3]}\nresult = dpath.values(obj, 'a/*')",
        {"ok": True, "value": [1, 2, 3]},
    ),
    
    # New operations
    (
        "new-simple",
        "import dpath\nobj = {}\ndpath.new(obj, 'a/b/c', 42)\nresult = obj",
        {"ok": True, "value": {"a": {"b": {"c": 42}}}},
    ),
    (
        "new-nested",
        "import dpath\nobj = {'a': {'x': 1}}\ndpath.new(obj, 'a/b/c', 99)\nresult = obj",
        {"ok": True, "value": {"a": {"x": 1, "b": {"c": 99}}}},
    ),
    (
        "new-list-path",
        "import dpath\nobj = {}\ndpath.new(obj, ['a', 'b'], 5)\nresult = obj",
        {"ok": True, "value": {"a": {"b": 5}}},
    ),
    (
        "new-custom-separator",
        "import dpath\nobj = {}\ndpath.new(obj, 'a.b.c', 7, separator='.')\nresult = obj",
        {"ok": True, "value": {"a": {"b": {"c": 7}}}},
    ),
    (
        "new-with-creator",
        "import dpath\ndef creator(current, segments, i, hints=()):\n    current[segments[i]] = {}\nobj = {}\ndpath.new(obj, 'a/b', 1, creator=creator)\nresult = obj",
        {"ok": True, "value": {"a": {"b": 1}}},
    ),
    (
        "new-empty-string-key",
        "import dpath\nobj = {}\ndpath.new(obj, 'a//b', 1)\nresult = obj",
        {"ok": True, "value": {"a": {"": {"b": 1}}}},
    ),
    
    # Delete operations
    (
        "delete-simple",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2}}\ncount = dpath.delete(obj, 'a/b')\nresult = [count, obj]",
        {"ok": True, "value": [1, {"a": {"c": 2}}]},
    ),
    (
        "delete-glob",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2, 'd': 3}}\ncount = dpath.delete(obj, 'a/[bc]')\nresult = [count, obj]",
        {"ok": True, "value": [2, {"a": {"d": 3}}]},
    ),
    (
        "delete-not-found",
        "import dpath\nfrom dpath.exceptions import PathNotFound\nobj = {'a': 1}\ntry:\n    dpath.delete(obj, 'x/y')\n    result = 'no-error'\nexcept PathNotFound:\n    result = 'PathNotFound'",
        {"ok": True, "value": "PathNotFound"},
    ),
    (
        "delete-with-filter",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2, 'd': 3}}\ncount = dpath.delete(obj, 'a/*', afilter=lambda x: x > 1)\nresult = [count, obj]",
        {"ok": True, "value": [2, {"a": {"b": 1}}]},
    ),
    (
        "delete-from-list",
        "import dpath\nobj = {'a': [1, 2, 3]}\ncount = dpath.delete(obj, 'a/1')\nresult = [count, obj]",
        {"ok": True, "value": [1, {"a": [1, None, 3]}]},
    ),
    (
        "delete-list-middle",
        "import dpath\nobj = {'a': [1, 2, 3, 4]}\ndpath.delete(obj, 'a/1')\nresult = obj",
        {"ok": True, "value": {"a": [1, None, 3, 4]}},
    ),
    (
        "delete-list-last",
        "import dpath\nobj = {'a': [1, 2, 3]}\ndpath.delete(obj, 'a/2')\nresult = obj",
        {"ok": True, "value": {"a": [1, 2]}},
    ),
    
    # Set operations
    (
        "set-simple",
        "import dpath\nobj = {'a': {'b': 1}}\ncount = dpath.set(obj, 'a/b', 99)\nresult = [count, obj]",
        {"ok": True, "value": [1, {"a": {"b": 99}}]},
    ),
    (
        "set-glob",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2}}\ncount = dpath.set(obj, 'a/*', 5)\nresult = [count, obj]",
        {"ok": True, "value": [2, {"a": {"b": 5, "c": 5}}]},
    ),
    (
        "set-no-match",
        "import dpath\nobj = {'a': 1}\ncount = dpath.set(obj, 'x/y', 99)\nresult = count",
        {"ok": True, "value": 0},
    ),
    (
        "set-with-filter",
        "import dpath\nobj = {'a': {'b': 1, 'c': 2, 'd': 3}}\ncount = dpath.set(obj, 'a/*', 0, afilter=lambda x: x > 1)\nresult = [count, obj]",
        {"ok": True, "value": [2, {"a": {"b": 1, "c": 0, "d": 0}}]},
    ),
    
    # Merge operations
    (
        "merge-simple",
        "import dpath\ndst = {'a': {'b': 1}}\nsrc = {'a': {'c': 2}}\ndpath.merge(dst, src)\nresult = dst",
        {"ok": True, "value": {"a": {"b": 1, "c": 2}}},
    ),
    (
        "merge-deep",
        "import dpath\ndst = {'a': {'b': {'x': 1}}}\nsrc = {'a': {'b': {'y': 2}}}\ndpath.merge(dst, src)\nresult = dst",
        {"ok": True, "value": {"a": {"b": {"x": 1, "y": 2}}}},
    ),
    (
        "merge-list-additive",
        "import dpath\nfrom dpath import MergeType\ndst = {'a': [1, 2]}\nsrc = {'a': [3, 4]}\ndpath.merge(dst, src, flags=MergeType.ADDITIVE)\nresult = dst",
        {"ok": True, "value": {"a": [1, 2, 3, 4]}},
    ),
    (
        "merge-list-replace",
        "import dpath\nfrom dpath import MergeType\ndst = {'a': [1, 2]}\nsrc = {'a': [3, 4]}\ndpath.merge(dst, src, flags=MergeType.REPLACE)\nresult = dst",
        {"ok": True, "value": {"a": [3, 4]}},
    ),
    (
        "merge-typesafe-ok",
        "import dpath\nfrom dpath import MergeType\ndst = {'a': 1}\nsrc = {'a': 2}\ndpath.merge(dst, src, flags=MergeType.TYPESAFE)\nresult = dst",
        {"ok": True, "value": {"a": 2}},
    ),
    (
        "merge-typesafe-fail",
        "import dpath\nfrom dpath import MergeType\ndst = {'a': 1}\nsrc = {'a': 'str'}\ntry:\n    dpath.merge(dst, src, flags=MergeType.TYPESAFE)\n    result = 'no-error'\nexcept TypeError:\n    result = 'TypeError'",
        {"ok": True, "value": "TypeError"},
    ),
    (
        "merge-with-filter",
        "import dpath\ndst = {'a': {'b': 1}}\nsrc = {'a': {'c': 2, 'd': 3}}\ntry:\n    dpath.merge(dst, src, afilter=lambda x: x > 2)\n    result = 'no-error'\nexcept TypeError as e:\n    result = 'typeerror'",
        {"ok": True, "value": "typeerror"},
    ),
    
    # Segments module tests
    (
        "segments-get",
        "import dpath.segments as seg\nobj = {'a': {'b': 1}}\nresult = seg.get(obj, ['a', 'b'])",
        {"ok": True, "value": 1},
    ),
    (
        "segments-has-true",
        "import dpath.segments as seg\nobj = {'a': {'b': 1}}\nresult = seg.has(obj, ['a', 'b'])",
        {"ok": True, "value": True},
    ),
    (
        "segments-has-false",
        "import dpath.segments as seg\nobj = {'a': 1}\nresult = seg.has(obj, ['x', 'y'])",
        {"ok": True, "value": False},
    ),
    (
        "segments-set",
        "import dpath.segments as seg\nobj = {}\nseg.set(obj, ['a', 'b'], 42)\nresult = obj",
        {"ok": True, "value": {"a": {"b": 42}}},
    ),
    (
        "segments-leaf-true",
        "import dpath.segments as seg\nresult = [seg.leaf(1), seg.leaf('str'), seg.leaf(None), seg.leaf(True)]",
        {"ok": True, "value": [True, True, True, True]},
    ),
    (
        "segments-leaf-false",
        "import dpath.segments as seg\nresult = [seg.leaf({}), seg.leaf([]), seg.leaf((1,))]",
        {"ok": True, "value": [False, False, False]},
    ),
    (
        "segments-walk",
        "import dpath.segments as seg\nobj = {'a': {'b': 1}}\nresult = list(seg.walk(obj))\nresult = sorted([(tuple(p), v) for p, v in result])",
        {"ok": True, "value": [[["a"], {"b": 1}], [["a", "b"], 1]]},
    ),
    (
        "segments-match-simple",
        "import dpath.segments as seg\nresult = seg.match(['a', 'b'], ['a', 'b'])",
        {"ok": True, "value": True},
    ),
    (
        "segments-match-glob",
        "import dpath.segments as seg\nresult = seg.match(['a', 'b'], ['a', '*'])",
        {"ok": True, "value": True},
    ),
    (
        "segments-match-star-star",
        "import dpath.segments as seg\nresult = [seg.match(['a', 'b', 'c'], ['**']), seg.match(['a', 'b'], ['a', '**', 'b'])]",
        {"ok": True, "value": [True, True]},
    ),
    
    # Exception tests
    (
        "pathnotfound-exception-type",
        "from dpath.exceptions import PathNotFound\ntry:\n    raise PathNotFound('test')\nexcept PathNotFound:\n    result = 'caught'",
        {"ok": True, "value": "caught"},
    ),
    (
        "invalidkeyname-exception-type",
        "from dpath.exceptions import InvalidKeyName\ntry:\n    raise InvalidKeyName('test')\nexcept InvalidKeyName:\n    result = 'caught'",
        {"ok": True, "value": "caught"},
    ),
    
    # MergeType enum tests
    (
        "mergetype-flags",
        "from dpath import MergeType\nresult = [bool(MergeType.ADDITIVE), bool(MergeType.REPLACE), bool(MergeType.TYPESAFE)]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "mergetype-combined",
        "from dpath import MergeType\nflags = MergeType.ADDITIVE | MergeType.TYPESAFE\nresult = bool(flags & MergeType.ADDITIVE)",
        {"ok": True, "value": True},
    ),
    
    # Edge cases
    (
        "empty-dict-search",
        "import dpath\nresult = dpath.search({}, '**')",
        {"ok": True, "value": {}},
    ),
    (
        "nested-list-access",
        "import dpath\nobj = {'a': {'b': [10, 20, 30]}}\nresult = dpath.get(obj, 'a/b/1')",
        {"ok": True, "value": 20},
    ),
    (
        "list-index-string",
        "import dpath\nobj = {'a': [1, 2, 3]}\nresult = dpath.get(obj, ['a', '1'])",
        {"ok": True, "value": 2},
    ),
    (
        "list-negative-index",
        "import dpath\nobj = {'a': [1, 2, 3]}\nresult = dpath.get(obj, ['a', -1])",
        {"ok": True, "value": 3},
    ),
    (
        "glob-character-class",
        "import dpath\nobj = {'a': {'b1': 1, 'b2': 2, 'c': 3}}\nresult = dpath.search(obj, 'a/b[12]')",
        {"ok": True, "value": {"a": {"b1": 1, "b2": 2}}},
    ),
    (
        "separator-in-value",
        "import dpath\nobj = {'a/b': 1}\nresult = dpath.get(obj, ['a/b'])",
        {"ok": True, "value": 1},
    ),
    (
        "unicode-key",
        "import dpath\nobj = {'中文': {'キー': 42}}\nresult = dpath.get(obj, '中文/キー')",
        {"ok": True, "value": 42},
    ),
    (
        "numeric-string-key",
        "import dpath\nobj = {'123': {'456': 'value'}}\nresult = dpath.get(obj, '123/456')",
        {"ok": True, "value": "value"},
    ),
    (
        "boolean-value",
        "import dpath\nobj = {'a': {'b': True, 'c': False}}\nresult = [dpath.get(obj, 'a/b'), dpath.get(obj, 'a/c')]",
        {"ok": True, "value": [True, False]},
    ),
    (
        "empty-list-leaf",
        "import dpath\nobj = {'a': {'b': []}}\nresult = dpath.get(obj, 'a/b')",
        {"ok": True, "value": []},
    ),
    (
        "empty-dict-leaf",
        "import dpath\nobj = {'a': {'b': {}}}\nresult = dpath.get(obj, 'a/b')",
        {"ok": True, "value": {}},
    ),
    (
        "mixed-nesting",
        "import dpath\nobj = {'a': [{'b': 1}, {'b': 2}]}\nresult = [dpath.get(obj, 'a/0/b'), dpath.get(obj, 'a/1/b')]",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "search-question-mark-glob",
        "import dpath\nobj = {'a': {'b1': 1, 'b2': 2, 'bb': 3}}\nresult = dpath.search(obj, 'a/b?')",
        {"ok": True, "value": {"a": {"b1": 1, "b2": 2, "bb": 3}}},
    ),
    (
        "custom-separator-multiple",
        "import dpath\nobj = {}\ndpath.new(obj, 'a::b::c', 7, separator='::')\nresult = obj",
        {"ok": True, "value": {"a": {"b": {"c": 7}}}},
    ),
    (
        "get-callable-value",
        "import dpath\ndef func(): return 42\nobj = {'a': func}\nresult = dpath.get(obj, 'a')() == 42",
        {"ok": True, "value": True},
    ),
    (
        "segments-int-str",
        "import dpath.segments as seg\nresult = [seg.int_str(123), seg.int_str('abc')]",
        {"ok": True, "value": ["123", "abc"]},
    ),
    (
        "segments-leafy-true",
        "import dpath.segments as seg\nresult = [seg.leafy(1), seg.leafy(''), seg.leafy([]), seg.leafy({})]",
        {"ok": True, "value": [True, True, True, True]},
    ),
    (
        "segments-leafy-false",
        "import dpath.segments as seg\nresult = [seg.leafy([1]), seg.leafy({'a': 1})]",
        {"ok": True, "value": [False, False]},
    ),
    (
        "types-module-import",
        "from dpath.types import MergeType, PathSegment, Filter, Glob, Path\nresult = True",
        {"ok": True, "value": True},
    ),
    (
        "options-module-access",
        "import dpath.options\nresult = isinstance(dpath.options.ALLOW_EMPTY_STRING_KEYS, bool)",
        {"ok": True, "value": True},
    ),
]

# Assert we have the expected number of scenarios
assert len(CASES) == 78, f"Expected 78 scenarios, got {len(CASES)}"


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

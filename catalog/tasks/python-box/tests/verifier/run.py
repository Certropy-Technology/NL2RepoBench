"""Private deterministic scenarios for the python-box public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/cdgriffith/Box,
v7.4.1, immutable revision a4c10e977b574114613431394b30412b50aaacce). The
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
    (
        "box-create-empty",
        "from box import Box\nresult = len(Box())",
        {"ok": True, "value": 0},
    ),
    (
        "box-create-dict",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\nresult = (b['a'], b['b'])",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "box-create-kwargs",
        "from box import Box\nb = Box(x=10, y=20)\nresult = (b.x, b.y)",
        {"ok": True, "value": [10, 20]},
    ),
    (
        "box-attr-access",
        "from box import Box\nb = Box({'key': 'value'})\nresult = b.key",
        {"ok": True, "value": "value"},
    ),
    (
        "box-bracket-access",
        "from box import Box\nb = Box({'key': 'value'})\nresult = b['key']",
        {"ok": True, "value": "value"},
    ),
    (
        "box-nested-dict",
        "from box import Box\nb = Box({'outer': {'inner': 'value'}})\nresult = b.outer.inner",
        {"ok": True, "value": "value"},
    ),
    (
        "box-nested-list",
        "from box import Box\nb = Box({'data': [{'a': 1}, {'b': 2}]})\nresult = (type(b['data']).__name__, b['data'][0].a, b['data'][1].b)",
        {"ok": True, "value": ["BoxList", 1, 2]},
    ),
    (
        "box-setitem",
        "from box import Box\nb = Box()\nb['key'] = 'value'\nresult = b.key",
        {"ok": True, "value": "value"},
    ),
    (
        "box-setattr",
        "from box import Box\nb = Box()\nb.key = 'value'\nresult = b['key']",
        {"ok": True, "value": "value"},
    ),
    (
        "box-contains",
        "from box import Box\nb = Box({'a': 1})\nresult = ('a' in b, 'b' in b)",
        {"ok": True, "value": [True, False]},
    ),
    (
        "box-get-exists",
        "from box import Box\nb = Box({'a': 1})\nresult = b.get('a')",
        {"ok": True, "value": 1},
    ),
    (
        "box-get-default",
        "from box import Box\nb = Box({'a': 1})\nresult = b.get('missing', 'default')",
        {"ok": True, "value": "default"},
    ),
    (
        "box-get-none",
        "from box import Box\nb = Box({'a': 1})\nresult = b.get('missing')",
        {"ok": True, "value": None},
    ),
    (
        "box-to-dict",
        "from box import Box\nb = Box({'a': 1, 'nested': {'b': 2}})\nd = b.to_dict()\nresult = (type(d).__name__, d['a'], type(d['nested']).__name__, d['nested']['b'])",
        {"ok": True, "value": ["dict", 1, "dict", 2]},
    ),
    (
        "box-update",
        "from box import Box\nb = Box({'a': 1})\nb.update({'b': 2, 'c': 3})\nresult = (b.a, b.b, b.c)",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "box-merge-update",
        "from box import Box\nb = Box({'a': {'x': 1, 'y': 2}})\nb.merge_update({'a': {'y': 3, 'z': 4}})\nresult = (b.a.x, b.a.y, b.a.z)",
        {"ok": True, "value": [1, 3, 4]},
    ),
    (
        "box-setdefault-new",
        "from box import Box\nb = Box()\nresult = b.setdefault('key', 'default')",
        {"ok": True, "value": "default"},
    ),
    (
        "box-setdefault-exists",
        "from box import Box\nb = Box({'key': 'original'})\nresult = b.setdefault('key', 'default')",
        {"ok": True, "value": "original"},
    ),
    (
        "box-pop",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\nval = b.pop('a')\nresult = (val, 'a' in b)",
        {"ok": True, "value": [1, False]},
    ),
    (
        "box-pop-default",
        "from box import Box\nb = Box({'a': 1})\nresult = b.pop('missing', 'default')",
        {"ok": True, "value": "default"},
    ),
    (
        "box-clear",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\nb.clear()\nresult = len(b)",
        {"ok": True, "value": 0},
    ),
    (
        "box-copy",
        "from box import Box\nb1 = Box({'a': 1})\nb2 = b1.copy()\nb2.a = 2\nresult = (b1.a, b2.a)",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "box-keys",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\nresult = sorted(list(b.keys()))",
        {"ok": True, "value": ["a", "b"]},
    ),
    (
        "box-items",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\nresult = sorted([(k, v) for k, v in b.items()])",
        {"ok": True, "value": [["a", 1], ["b", 2]]},
    ),
    (
        "box-default-box",
        "from box import Box\nb = Box(default_box=True)\nb.missing.nested.key = 'value'\nresult = b.missing.nested.key",
        {"ok": True, "value": "value"},
    ),
    (
        "box-no-default-error",
        "from box import Box, BoxKeyError\nb = Box()\ntry:\n    _ = b.missing\n    result = 'no-error'\nexcept BoxKeyError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "box-frozen-no-modify",
        "from box import Box, BoxError\nb = Box({'a': 1}, frozen_box=True)\ntry:\n    b.a = 2\n    result = 'no-error'\nexcept BoxError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "box-frozen-no-add",
        "from box import Box, BoxError\nb = Box({'a': 1}, frozen_box=True)\ntry:\n    b.new = 2\n    result = 'no-error'\nexcept BoxError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "box-frozen-no-delete",
        "from box import Box, BoxError\nb = Box({'a': 1}, frozen_box=True)\ntry:\n    del b.a\n    result = 'no-error'\nexcept BoxError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "box-frozen-read",
        "from box import Box\nb = Box({'a': 1}, frozen_box=True)\nresult = b.a",
        {"ok": True, "value": 1},
    ),
    (
        "box-camel-killer-set",
        "from box import Box\nb = Box(camel_killer_box=True)\nb.CamelCase = 'value'\nresult = b.camel_case",
        {"ok": True, "value": "value"},
    ),
    (
        "box-camel-killer-get",
        "from box import Box\nb = Box(camel_killer_box=True)\nb['BigKey'] = 'value'\nresult = b.big_key",
        {"ok": True, "value": "value"},
    ),
    (
        "box-conversion-spaces",
        "from box import Box\nb = Box({'key with spaces': 'value'})\nresult = b.key_with_spaces",
        {"ok": True, "value": "value"},
    ),
    (
        "box-conversion-numeric",
        "from box import Box\nb = Box({'123': 'value'})\nresult = b.x123",
        {"ok": True, "value": "value"},
    ),
    (
        "box-conversion-special",
        "from box import Box\nb = Box({'key!@#': 'value'})\nresult = b.key",
        {"ok": True, "value": "value"},
    ),
    (
        "boxlist-create",
        "from box import BoxList\nbl = BoxList([1, 2, 3])\nresult = (len(bl), bl[0], bl[2])",
        {"ok": True, "value": [3, 1, 3]},
    ),
    (
        "boxlist-dict-conversion",
        "from box import BoxList\nbl = BoxList([{'a': 1}, {'b': 2}])\nresult = (bl[0].a, bl[1].b)",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "boxlist-append",
        "from box import BoxList\nbl = BoxList([1, 2])\nbl.append({'c': 3})\nresult = (len(bl), bl[2].c)",
        {"ok": True, "value": [3, 3]},
    ),
    (
        "boxlist-extend",
        "from box import BoxList\nbl = BoxList([1])\nbl.extend([2, {'a': 3}])\nresult = (len(bl), bl[2].a)",
        {"ok": True, "value": [3, 3]},
    ),
    (
        "boxlist-insert",
        "from box import BoxList\nbl = BoxList([1, 3])\nbl.insert(1, {'b': 2})\nresult = (len(bl), bl[1].b)",
        {"ok": True, "value": [3, 2]},
    ),
    (
        "ddbox-create",
        "from box import DDBox\ndb = DDBox()\ndb.missing.nested = 'value'\nresult = db.missing.nested",
        {"ok": True, "value": "value"},
    ),
    (
        "box-to-json",
        "from box import Box\nimport json\nb = Box({'a': 1, 'b': 2})\njson_str = b.to_json()\nresult = json.loads(json_str)",
        {"ok": True, "value": {"a": 1, "b": 2}},
    ),
    (
        "box-from-json-string",
        "from box import Box\nb = Box.from_json('{\"a\": 1, \"b\": 2}')\nresult = (b.a, b.b)",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "box-from-json-nested",
        "from box import Box\nb = Box.from_json('{\"outer\": {\"inner\": \"value\"}}')\nresult = b.outer.inner",
        {"ok": True, "value": "value"},
    ),
    (
        "box-from-string-json",
        "from box import box_from_string\nb = box_from_string('{\"a\": 1}')\nresult = b.a",
        {"ok": True, "value": 1},
    ),
    (
        "box-none-value",
        "from box import Box\nb = Box({'key': None})\nresult = b.key",
        {"ok": True, "value": None},
    ),
    (
        "box-empty-string",
        "from box import Box\nb = Box({'key': ''})\nresult = b.key",
        {"ok": True, "value": ""},
    ),
    (
        "box-unicode",
        "from box import Box\nb = Box({'中文': '汉字'})\nresult = b['中文']",
        {"ok": True, "value": "汉字"},
    ),
    (
        "box-nested-empty",
        "from box import Box\nb = Box({'a': {}})\nresult = len(b.a)",
        {"ok": True, "value": 0},
    ),
    (
        "box-list-nested",
        "from box import Box\nb = Box({'data': [{'id': 1}, {'id': 2}, {'id': 3}]})\nresult = [item.id for item in b['data']]",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "box-update-nested",
        "from box import Box\nb = Box({'a': {'b': 1}})\nb.a.b = 2\nresult = b.a.b",
        {"ok": True, "value": 2},
    ),
    (
        "box-pop-missing",
        "from box import Box\nb = Box({'a': 1})\ntry:\n    b.pop('missing')\n    result = 'no-error'\nexcept KeyError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "box-delitem",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\ndel b['a']\nresult = 'a' in b",
        {"ok": True, "value": False},
    ),
    (
        "box-delattr",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\ndel b.a\nresult = 'a' in b",
        {"ok": True, "value": False},
    ),
    (
        "box-bool-empty",
        "from box import Box\nresult = bool(Box())",
        {"ok": True, "value": False},
    ),
    (
        "box-bool-nonempty",
        "from box import Box\nresult = bool(Box({'a': 1}))",
        {"ok": True, "value": True},
    ),
    (
        "box-len",
        "from box import Box\nb = Box({'a': 1, 'b': 2, 'c': 3})\nresult = len(b)",
        {"ok": True, "value": 3},
    ),
    (
        "box-equality",
        "from box import Box\nb1 = Box({'a': 1})\nb2 = Box({'a': 1})\nresult = b1 == b2",
        {"ok": True, "value": True},
    ),
    (
        "box-inequality",
        "from box import Box\nb1 = Box({'a': 1})\nb2 = Box({'a': 2})\nresult = b1 != b2",
        {"ok": True, "value": True},
    ),
    (
        "box-default-attr-none",
        "from box import Box\nb = Box(default_box=True, default_box_attr=None)\nresult = b.missing is None",
        {"ok": True, "value": True},
    ),
    (
        "box-tuple-key",
        "from box import Box\nb = Box({(1, 2): 'value'})\nresult = b[(1, 2)]",
        {"ok": True, "value": "value"},
    ),
    (
        "box-nested-boxlist",
        "from box import Box\nb = Box({'data': [[{'a': 1}], [{'b': 2}]]})\nresult = b.data[1][0].b",
        {"ok": True, "value": 2},
    ),
    (
        "box-update-kwargs",
        "from box import Box\nb = Box({'a': 1})\nb.update(b=2, c=3)\nresult = (b.a, b.b, b.c)",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "box-merge-deep",
        "from box import Box\nb = Box({'a': {'b': {'c': 1}}})\nb.merge_update({'a': {'b': {'d': 2}}})\nresult = (b.a.b.c, b.a.b.d)",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "box-popitem",
        "from box import Box\nb = Box({'a': 1})\nk, v = b.popitem()\nresult = (k, v, len(b))",
        {"ok": True, "value": ["a", 1, 0]},
    ),
    (
        "boxlist-slice",
        "from box import BoxList\nbl = BoxList([1, 2, 3, 4, 5])\nresult = bl[1:3]",
        {"ok": True, "value": [2, 3]},
    ),
    (
        "box-from-tuples",
        "from box import Box\nb = Box([('a', 1), ('b', 2)])\nresult = (b.a, b.b)",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "box-setdefault-stores",
        "from box import Box\nb = Box()\nb.setdefault('key', 'value')\nresult = b.key",
        {"ok": True, "value": "value"},
    ),
    (
        "box-iter",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\nresult = sorted(list(b))",
        {"ok": True, "value": ["a", "b"]},
    ),
    (
        "box-values",
        "from box import Box\nb = Box({'a': 1, 'b': 2})\nresult = sorted(list(b.values()))",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "boxlist-modify",
        "from box import BoxList\nbl = BoxList([{'a': 1}])\nbl[0].a = 2\nresult = bl[0].a",
        {"ok": True, "value": 2},
    ),
    (
        "box-mixed-types",
        "from box import Box\nb = Box({'str': 'text', 'int': 42, 'float': 3.14, 'lst': [1, 2], 'dct': {'nested': True}})\nresult = (b.str, b.int, b.float, len(b.lst), b.dct.nested)",
        {"ok": True, "value": ["text", 42, 3.14, 2, True]},
    ),
    (
        "box-repr",
        "from box import Box\nb = Box({'a': 1})\nresult = 'Box' in repr(b)",
        {"ok": True, "value": True},
    ),
    (
        "box-str",
        "from box import Box\nb = Box({'a': 1})\nresult = 'a' in str(b)",
        {"ok": True, "value": True},
    ),
    (
        "box-nested-assign",
        "from box import Box\nb = Box()\nb.nested = {'key': 'value'}\nresult = (type(b.nested).__name__, b.nested.key)",
        {"ok": True, "value": ["Box", "value"]},
    ),
    (
        "box-list-assign",
        "from box import Box\nb = Box()\nb.lst = [{'a': 1}]\nresult = (type(b.lst).__name__, b.lst[0].a)",
        {"ok": True, "value": ["BoxList", 1]},
    ),
    (
        "box-merge-preserve",
        "from box import Box\nb = Box({'a': {'b': 1, 'c': 2}})\nb.merge_update({'a': {'c': 3}})\nresult = (b.a.b, b.a.c)",
        {"ok": True, "value": [1, 3]},
    ),
    (
        "box-get-nested",
        "from box import Box\nb = Box({'a': {'b': {'c': 'value'}}})\nresult = b.a.b.get('c')",
        {"ok": True, "value": "value"},
    ),
    (
        "box-in-top-level",
        "from box import Box\nb = Box({'a': {'b': 1}})\nresult = ('a' in b, 'b' in b)",
        {"ok": True, "value": [True, False]},
    ),
    (
        "box-update-nested-convert",
        "from box import Box\nb = Box()\nb.update({'outer': {'inner': 'value'}})\nresult = b.outer.inner",
        {"ok": True, "value": "value"},
    ),
    (
        "box-nested-deep-four",
        "from box import Box\nb = Box({'a': {'b': {'c': {'d': 'value'}}}})\nresult = b.a.b.c.d",
        {"ok": True, "value": "value"},
    ),
    (
        "box-list-mixed-nested",
        "from box import Box\nb = Box({'data': [1, {'a': 2}, [3, 4]]})\nresult = (b['data'][0], b['data'][1].a, b['data'][2])",
        {"ok": True, "value": [1, 2, [3, 4]]},
    ),
    (
        "boxlist-remove",
        "from box import BoxList\nbl = BoxList([1, 2, 3])\nbl.remove(2)\nresult = list(bl)",
        {"ok": True, "value": [1, 3]},
    ),
    (
        "box-clear-then-add",
        "from box import Box\nb = Box({'a': 1})\nb.clear()\nb.b = 2\nresult = ('a' in b, b.b)",
        {"ok": True, "value": [False, 2]},
    ),
    (
        "box-popitem-order",
        "from box import Box\nb = Box()\nb.a = 1\nb.b = 2\nk, v = b.popitem()\nresult = k in ['a', 'b']",
        {"ok": True, "value": True},
    ),
    (
        "box-fromkeys-class",
        "from box import Box\nb = Box.fromkeys(['a', 'b', 'c'], 0)\nresult = (b.a, b.b, b.c)",
        {"ok": True, "value": [0, 0, 0]},
    ),
    (
        "box-to-dict-deep",
        "from box import Box\nb = Box({'a': {'b': {'c': [{'d': 1}]}}})\nd = b.to_dict()\nresult = type(d['a']['b']['c'][0]).__name__",
        {"ok": True, "value": "dict"},
    ),
    (
        "box-json-roundtrip",
        "from box import Box\nb1 = Box({'a': {'b': [1, 2, 3]}})\njson_str = b1.to_json()\nb2 = Box.from_json(json_str)\nresult = (b2.a.b[0], b2.a.b[2])",
        {"ok": True, "value": [1, 3]},
    ),
    (
        "box-default-box-attr-custom",
        "from box import Box\nb = Box(default_box=True, default_box_attr={})\nresult = type(b.missing).__name__",
        {"ok": True, "value": "Box"},
    ),
    (
        "box-copy-nested-independence",
        "from box import Box\nb1 = Box({'a': {'b': 1}})\nb2 = b1.copy()\nb2.a.b = 2\nresult = b1.a.b",
        {"ok": True, "value": 1},
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

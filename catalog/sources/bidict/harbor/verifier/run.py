"""Private deterministic scenarios for the bidict public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (bidict 0.24.1). The candidate
runner executes the script and reads the ``result`` binding.
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
        'empty_construction',
        "from bidict import bidict\nr = dict(bidict())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {}},
    ),
    (
        'dict_construction',
        "from bidict import bidict\nr = dict(bidict({'a': 1, 'b': 2}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "b": 2}},
    ),
    (
        'kwargs_construction',
        "from bidict import bidict\nr = dict(bidict(x=10, y=20))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"x": 10, "y": 20}},
    ),
    (
        'pairs_construction',
        "from bidict import bidict\nr = dict(bidict([('k1', 'v1'), ('k2', 'v2')]))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"k1": "v1", "k2": "v2"}},
    ),
    (
        'mixed_construction',
        "from bidict import bidict\nr = dict(bidict({'a': 1}, b=2))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "b": 2}},
    ),
    (
        'single_pair',
        "from bidict import bidict\nr = dict(bidict({'key': 'value'}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"key": "value"}},
    ),
    (
        'int_keys',
        "from bidict import bidict\nr = dict(bidict({1: 'a', 2: 'b'}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"1": "a", "2": "b"}},
    ),
    (
        'str_values',
        "from bidict import bidict\nr = dict(bidict({'x': 'foo', 'y': 'bar'}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"x": "foo", "y": "bar"}},
    ),
    (
        'mixed_types',
        "from bidict import bidict\nr = dict(bidict({'a': 1, 'b': 'two', 'c': 3.0}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "b": "two", "c": 3.0}},
    ),
    (
        'access_key',
        "from bidict import bidict\nr = bidict({'a': 1, 'b': 2})['a']\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'access_int_key',
        "from bidict import bidict\nr = bidict({1: 'one', 2: 'two'})[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": "one"},
    ),
    (
        'inverse_access',
        "from bidict import bidict\nr = bidict({'a': 1, 'b': 2}).inverse[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": "a"},
    ),
    (
        'inverse_access_str',
        "from bidict import bidict\nr = bidict({1: 'one', 2: 'two'}).inverse['one']\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'double_inverse_access',
        "from bidict import bidict\nr = bidict({'x': 10}).inverse.inverse['x']\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 10},
    ),
    (
        'get_present',
        "from bidict import bidict\nr = bidict({'a': 1}).get('a')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'get_absent',
        "from bidict import bidict\nr = bidict({'a': 1}).get('z')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": None},
    ),
    (
        'get_with_default',
        "from bidict import bidict\nr = bidict({'a': 1}).get('z', -1)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": -1},
    ),
    (
        'get_zero_default',
        "from bidict import bidict\nr = bidict({'a': 1}).get('z', 0)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'inverse_get',
        "from bidict import bidict\nr = bidict({'a': 1}).inverse.get(1)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": "a"},
    ),
    (
        'inverse_dict',
        "from bidict import bidict\nr = dict(bidict({'a': 1, 'b': 2}).inverse)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"1": "a", "2": "b"}},
    ),
    (
        'inverse_len',
        "from bidict import bidict\nr = len(bidict({'a': 1, 'b': 2}).inverse)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 2},
    ),
    (
        'inverse_keys',
        "from bidict import bidict\nr = sorted(bidict({'a': 1, 'b': 2}).inverse.keys())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": [1, 2]},
    ),
    (
        'inverse_values',
        "from bidict import bidict\nr = sorted(bidict({'a': 1, 'b': 2}).inverse.values())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": ["a", "b"]},
    ),
    (
        'inverse_items',
        "from bidict import bidict\nr = sorted(bidict({'a': 1, 'b': 2}).inverse.items())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": [[1, "a"], [2, "b"]]},
    ),
    (
        'inverse_contains',
        "from bidict import bidict\nr = 1 in bidict({'a': 1}).inverse\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'inverse_not_contains',
        "from bidict import bidict\nr = 99 in bidict({'a': 1}).inverse\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": False},
    ),
    (
        'inverse_inverse',
        "from bidict import bidict\nr = dict(bidict({'a': 1}).inverse.inverse)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1}},
    ),
    (
        'inverse_empty',
        "from bidict import bidict\nr = dict(bidict().inverse)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {}},
    ),
    (
        'setdefault_new',
        "from bidict import bidict\nr = (lambda b: (b.setdefault('b', 2), dict(b)))(bidict({'a': 1}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "b": 2}},
    ),
    (
        'setdefault_existing',
        "from bidict import bidict\nr = (lambda b: (b.setdefault('a', 99), dict(b)))(bidict({'a': 1}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1}},
    ),
    (
        'setdefault_return_new',
        "from bidict import bidict\nr = bidict({'a': 1}).setdefault('b', 2)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 2},
    ),
    (
        'setdefault_return_existing',
        "from bidict import bidict\nr = bidict({'a': 1}).setdefault('a', 99)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'setdefault_zero',
        "from bidict import bidict\nr = bidict().setdefault('x', 0)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'setdefault_none',
        "from bidict import bidict\nr = bidict().setdefault('x', None)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": None},
    ),
    (
        'update_dict',
        "from bidict import bidict\nr = (lambda b: (b.update({'c': 3}), dict(b)))(bidict({'a': 1}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "c": 3}},
    ),
    (
        'update_pairs',
        "from bidict import bidict\nr = (lambda b: (b.update([('x', 10)]), dict(b)))(bidict({'a': 1}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "x": 10}},
    ),
    (
        'update_kwargs',
        "from bidict import bidict\nr = (lambda b: (b.update(z=26), dict(b)))(bidict({'a': 1}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "z": 26}},
    ),
    (
        'update_empty',
        "from bidict import bidict\nr = (lambda b: (b.update({}), dict(b)))(bidict({'a': 1}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1}},
    ),
    (
        'update_overwrite',
        "from bidict import bidict\nr = (lambda b: (b.update({'a': 99}), dict(b)))(bidict({'a': 1}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 99}},
    ),
    (
        'assignment_new',
        "from bidict import bidict\nr = (lambda b: (b.__setitem__('c', 3), dict(b)))(bidict({'a': 1, 'b': 2}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"a": 1, "b": 2, "c": 3}},
    ),
    (
        'del_key',
        "from bidict import bidict\nr = (lambda b: (b.__delitem__('a'), dict(b)))(bidict({'a': 1, 'b': 2}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"b": 2}},
    ),
    (
        'pop_key',
        "from bidict import bidict\nr = (lambda b: (b.pop('a'), dict(b)))(bidict({'a': 1, 'b': 2}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": {"b": 2}},
    ),
    (
        'pop_return',
        "from bidict import bidict\nr = bidict({'a': 1, 'b': 2}).pop('a')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'pop_default',
        "from bidict import bidict\nr = bidict({'a': 1}).pop('z', 'default')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": "default"},
    ),
    (
        'popitem_return',
        "from bidict import bidict\nr = list(bidict({'a': 1}).popitem())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": ["a", 1]},
    ),
    (
        'clear_result',
        "from bidict import bidict\nr = (lambda b: (b.clear(), len(b)))(bidict({'a': 1, 'b': 2}))[1]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'keys_list',
        "from bidict import bidict\nr = sorted(bidict({'b': 2, 'a': 1}).keys())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": ["a", "b"]},
    ),
    (
        'values_list',
        "from bidict import bidict\nr = sorted(bidict({'a': 2, 'b': 1}).values())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": [1, 2]},
    ),
    (
        'items_list',
        "from bidict import bidict\nr = sorted(bidict({'b': 2, 'a': 1}).items())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": [["a", 1], ["b", 2]]},
    ),
    (
        'keys_len',
        "from bidict import bidict\nr = len(bidict({'a': 1, 'b': 2}).keys())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 2},
    ),
    (
        'values_contains',
        "from bidict import bidict\nr = 1 in bidict({'a': 1, 'b': 2}).values()\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'items_contains',
        "from bidict import bidict\nr = ('a', 1) in bidict({'a': 1}).items()\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'len_empty',
        "from bidict import bidict\nr = len(bidict())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'len_one',
        "from bidict import bidict\nr = len(bidict({'a': 1}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'len_many',
        "from bidict import bidict\nr = len(bidict({'a': 1, 'b': 2, 'c': 3}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'contains_true',
        "from bidict import bidict\nr = 'a' in bidict({'a': 1, 'b': 2})\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'contains_false',
        "from bidict import bidict\nr = 'z' in bidict({'a': 1, 'b': 2})\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": False},
    ),
    (
        'bool_empty',
        "from bidict import bidict\nr = bool(bidict())\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": False},
    ),
    (
        'bool_nonempty',
        "from bidict import bidict\nr = bool(bidict({'a': 1}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'copy_independent',
        "from bidict import bidict\nr = (lambda: (lambda b, c: (c.__setitem__('b', 2), dict(b)))(bidict({'a': 1}), bidict({'a': 1}).copy()))()\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": [None, {"a": 1}]},
    ),
    (
        'eq_same',
        "from bidict import bidict\nr = bidict({'a': 1}) == bidict({'a': 1})\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'eq_different',
        "from bidict import bidict\nr = bidict({'a': 1}) == bidict({'b': 2})\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": False},
    ),
    (
        'eq_empty',
        "from bidict import bidict\nr = bidict() == bidict()\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'ne_different',
        "from bidict import bidict\nr = bidict({'a': 1}) != bidict({'b': 2})\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'ne_same',
        "from bidict import bidict\nr = bidict({'a': 1}) != bidict({'a': 1})\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": False},
    ),
    (
        'eq_dict',
        "from bidict import bidict\nr = bidict({'a': 1}) == {'a': 1}\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": True, "value": True},
    ),
    (
        'duplicate_value_error',
        "from bidict import bidict\nr = bidict({'a': 1}).__setitem__('b', 1)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "bidict.ValueDuplicationError", "exception_message": "1"},
    ),
    (
        'keyerror_access',
        "from bidict import bidict\nr = bidict({'a': 1})['z']\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "builtins.KeyError", "exception_message": "'z'"},
    ),
    (
        'keyerror_del',
        "from bidict import bidict\nr = bidict({'a': 1}).__delitem__('z')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "builtins.KeyError", "exception_message": "'z'"},
    ),
    (
        'keyerror_pop',
        "from bidict import bidict\nr = bidict({'a': 1}).pop('z')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "builtins.KeyError", "exception_message": "'z'"},
    ),
    (
        'empty_popitem',
        "from bidict import bidict\nr = bidict().popitem()\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "builtins.KeyError", "exception_message": "'popitem(): dictionary is empty'"},
    ),
    (
        'inverse_keyerror',
        "from bidict import bidict\nr = bidict({'a': 1}).inverse[99]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "builtins.KeyError", "exception_message": "99"},
    ),
    (
        'inverse_duplicate_value',
        "from bidict import bidict\nr = bidict({1: 'a', 2: 'b'}).inverse.__setitem__('c', 1)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "bidict.ValueDuplicationError", "exception_message": "1"},
    ),
    (
        'update_dup_value',
        "from bidict import bidict\nr = (lambda b: b.update({'b': 1}))(bidict({'a': 1}))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nif 'bidict' in str(type(r)):\n    r = dict(r)\nresult = r",
        {"ok": False, "value": None, "exception_type": "bidict.ValueDuplicationError", "exception_message": "1"},
    ),
]

assert len(CASES) == 74, f"Expected 74 cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True, default=repr)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

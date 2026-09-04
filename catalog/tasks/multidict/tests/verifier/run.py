from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ADAPTER = Path(__file__).with_name("adapter.py")
PREFIX = "NL2REPO_MULTIDICT_RESULT="
SCENARIOS = [
    "surface-metadata", "abc-generics", "constructor-duplicates", "mapping-constructor",
    "get-contract", "get-errors", "contains-nonstring", "add-setitem", "delete-clear",
    "setdefault", "extend", "update", "merge", "popone", "popall", "popitem",
    "case-insensitive", "case-update-key", "istr-contract", "copy-contract", "proxy-live",
    "proxy-readonly", "proxy-validation", "ci-proxy", "views", "view-sets",
    "view-mutation-guard", "equality", "version", "constructor-errors", "repr-recursion",
]

EXPECTED = {
    "surface-metadata": {"all": ["CIMultiDict", "CIMultiDictProxy", "MultiDict", "MultiDictProxy", "MultiMapping", "MutableMultiMapping", "getversion", "istr", "upstr"], "distribution_version": "6.7.2.dev0", "py_typed": True, "version": "6.7.2.dev0"},
    "abc-generics": {"mapping": True, "mutable": True, "multi": True, "proxy": True, "alias": "multidict.MultiDict[int]"},
    "constructor-duplicates": {"items": [["a", 1], ["a", 2], ["b", 3], ["c", 4]], "keys": ["a", "a", "b", "c"], "len": 4, "source": [["a", 1], ["a", 2], ["b", 3], ["z", 9]], "values": [1, 2, 3, 4]},
    "mapping-constructor": {"copy": [["a", 1], ["b", 2]], "different": True, "items": [["a", 1], ["b", 2]]},
    "get-contract": {"get": 1, "get_default": 8, "getall": [1, 2], "getall_default": [], "getitem": 1, "getone": 1, "getone_default": 9},
    "get-errors": {"getall": {"message": "\"Key not found: 'missing'\"", "type": "builtins.KeyError"}, "getitem": {"message": "\"Key not found: 'missing'\"", "type": "builtins.KeyError"}, "getone": {"message": "\"Key not found: 'missing'\"", "type": "builtins.KeyError"}},
    "contains-nonstring": {"integer": False, "missing": False, "string": True},
    "add-setitem": {"add_result": None, "all_a": [5], "items": [["a", 5], ["b", 3], ["c", 6]]},
    "delete-clear": {"after_clear": [], "after_delete": [["b", 3]], "clear_result": None, "missing": {"message": "'z'", "type": "builtins.KeyError"}},
    "setdefault": {"existing": 1, "items": [["a", 1], ["a", 2], ["b", 3], ["c", None]], "new": 3, "none": None},
    "extend": {"items": [["a", 1], ["a", 2], ["b", 3], ["c", 4]], "result": None},
    "update": {"items": [["a", 4], ["a", 5], ["b", 3], ["c", 6], ["d", 7]], "result": None},
    "merge": {"items": [["a", 1], ["a", 2], ["b", 3], ["c", 5], ["c", 6], ["d", 7]], "result": None},
    "popone": {"default": 8, "error": {"message": "'z'", "type": "builtins.KeyError"}, "first": 1, "remaining": [["a", 2], ["b", 3]]},
    "popall": {"all": [1, 2], "default": [], "error": {"message": "'z'", "type": "builtins.KeyError"}, "remaining": [["b", 3]]},
    "popitem": {"error": {"message": "'empty multidict'", "type": "builtins.KeyError"}, "first": ["b", 2], "second": ["a", 1]},
    "case-insensitive": {"all": ["text/plain", "json"], "contains": True, "first": "text/plain", "items": [["Content-Type", "text/plain"], ["content-type", "json"], ["X", "y"]]},
    "case-update-key": {"items": [["header", 4], ["Other", 3]], "keys": ["header", "Other"]},
    "istr-contract": {"is_str": True, "lookup": 1, "repr": "'AbC'", "text": "AbC", "upstr_same": True},
    "copy-contract": {"copy_items": [["a", []], ["a", 2]], "different": True, "shared": True, "source_items": [["a", []], ["a", 2], ["b", 3]]},
    "proxy-live": {"all": [1, 2], "copy_items": [["a", 1], ["a", 2], ["b", 3]], "copy_type": "MultiDict", "items": [["a", 1], ["a", 2], ["b", 3]]},
    "proxy-readonly": {"add": False, "dict": False, "set": {"message": "'MultiDictProxy' object has no attribute '__setitem__'", "type": "builtins.AttributeError"}},
    "proxy-validation": {"ci_plain": {"message": "ctor requires CIMultiDict or CIMultiDictProxy instance, not <class 'dict'>", "type": "builtins.TypeError"}, "cross": {"message": "ctor requires CIMultiDict or CIMultiDictProxy instance, not <class 'multidict._multidict_py.MultiDict'>", "type": "builtins.TypeError"}, "plain": {"message": "ctor requires MultiDict or MultiDictProxy instance, not <class 'dict'>", "type": "builtins.TypeError"}},
    "ci-proxy": {"all": [1, 2], "copy_type": "CIMultiDict", "items": [["A", 1], ["a", 2]]},
    "views": {"items": [["a", 1], ["a", 2], ["b", 3]], "items_type": True, "keys": ["a", "a", "b"], "keys_type": True, "values": [1, 2, 3], "values_type": True},
    "view-sets": {"disjoint": True, "items_and": [["a", 2]], "keys_and": ["a"], "keys_or": ["a", "b", "z"]},
    "view-mutation-guard": {"first": ["a", 1], "next": {"message": "Dictionary changed during iteration", "type": "builtins.RuntimeError"}},
    "equality": {"not_mapping": False, "order": False, "plain": True, "same": True},
    "version": {"bad": {"message": "Parameter should be multidict or proxy", "type": "builtins.TypeError"}, "increased": True, "integer": True, "proxy": True},
    "constructor-errors": {"key": {"message": "MultiDict keys should be either str or subclasses of str", "type": "builtins.TypeError"}, "length": {"message": "multidict update sequence element #0 has length 3; 2 is required", "type": "builtins.ValueError"}, "scalar": {"message": "object of type 'int' has no len()", "type": "builtins.TypeError"}},
    "repr-recursion": {"duplicate": "<MultiDict('a': 1, 'a': 2)>", "empty": "<MultiDict()>", "recursive": "<MultiDict('self': ...)>"},
}


def invoke(scenario: str) -> dict[str, object]:
    command = [sys.executable, "-I", str(ADAPTER), "--candidate-site", "/tmp/candidate-site", "--scenario", scenario]
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/tmp", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    completed = subprocess.run(
        command,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
        preexec_fn=_drop_candidate_privileges,
    )
    lines = [line for line in completed.stdout.splitlines() if line.startswith(PREFIX)]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "error": completed.stderr[-1000:]}
    try:
        value = json.loads(lines[0][len(PREFIX):])
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": str(exc)}
    return value if isinstance(value, dict) else {"ok": False, "error": "invalid result"}


def _drop_candidate_privileges() -> None:
    os.setgroups([])
    os.setgid(10001)
    os.setuid(10001)


def main() -> int:
    leaves = []
    for scenario in SCENARIOS:
        result = invoke(scenario)
        actual = result.get("value") if result.get("ok") is True else {"exception": result.get("error")}
        expected = EXPECTED[scenario]
        passed = actual == expected
        leaves.append({"id": f"multidict/{scenario}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:2000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

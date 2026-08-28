from __future__ import annotations

import argparse
import copy
import importlib.metadata
import json
import os
import resource
import sys
from collections.abc import MutableSequence
from pathlib import Path
from typing import Any

RESULT_PREFIX = "NL2REPO_FROZENLIST_RESULT="


def _limits() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))


def _error(action: Any) -> dict[str, Any]:
    try:
        action()
    except BaseException as exc:
        return {
            "message": str(exc),
            "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
        }
    return {"message": None, "type": None}


def exercise(name: str) -> Any:
    import frozenlist
    from frozenlist import FrozenList, PyFrozenList

    if name == "exports-version-metadata":
        package = Path(frozenlist.__file__).resolve().parent
        return {
            "all": list(frozenlist.__all__),
            "distribution_version": next(
                distribution.version
                for distribution in importlib.metadata.distributions(
                    path=["/tmp/candidate-site"]
                )
                if distribution.metadata.get("Name", "").casefold() == "frozenlist"
            ),
            "py_typed": (package / "py.typed").is_file(),
            "stub": (package / "__init__.pyi").is_file(),
            "version": frozenlist.__version__,
        }

    if name == "generic-mutable-sequence":
        frozen_alias = FrozenList[int]
        py_alias = PyFrozenList[str]
        return {
            "frozen_args": [item.__name__ for item in frozen_alias.__args__],
            "frozen_origin": frozen_alias.__origin__.__name__,
            "frozen_subclass": issubclass(FrozenList, MutableSequence),
            "py_args": [item.__name__ for item in py_alias.__args__],
            "py_origin": py_alias.__origin__.__name__,
            "py_subclass": issubclass(PyFrozenList, MutableSequence),
        }

    if name == "constructor-copy-iteration":
        source = [1, 2]
        value = FrozenList(source)
        source.append(3)
        empty = FrozenList()
        generated = FrozenList(item for item in (4, 5))
        return {
            "empty": [list(empty), empty.frozen],
            "generated": list(generated),
            "iterated": list(iter(value)),
            "source": source,
            "stored": list(value),
        }

    if name == "index-slice-reversed":
        value = FrozenList([0, 1, 2, 3])
        value[1:3] = [7, 8, 9]
        selected = value[1:4]
        del value[::2]
        return {
            "after": list(value),
            "index": selected[0],
            "reversed": list(reversed(selected)),
            "slice": list(selected),
            "slice_type": type(selected).__name__,
        }

    if name == "comparisons":
        value = FrozenList([1, 2])
        return {
            "eq": value == [1, 2],
            "ge": value >= [1, 2],
            "gt": value > [1, 1],
            "le": value <= [1, 2],
            "lt": value < [2],
            "ne": value != [2, 1],
        }

    if name == "insert-append-extend-iadd":
        value = FrozenList([2])
        value.insert(0, 1)
        append_result = value.append(3)
        value.extend((4, 5))
        original_id = id(value)
        value += [6]
        return {
            "append_result": append_result,
            "items": list(value),
            "same_after_iadd": id(value) == original_id,
        }

    if name == "remove-clear-reverse-pop":
        value = FrozenList([1, 2, 3, 2])
        value.remove(2)
        first = value.pop(0)
        last = value.pop()
        value.extend([4, 5])
        value.reverse()
        reversed_items = list(value)
        value.clear()
        return {
            "cleared": list(value),
            "first": first,
            "last": last,
            "reversed": reversed_items,
        }

    if name == "count-index-contains":
        value = FrozenList(["a", "b", "a"])
        return {
            "contains": "b" in value,
            "count": value.count("a"),
            "index": value.index("a"),
            "missing": "z" in value,
        }

    if name == "freeze-idempotent-repr":
        value = FrozenList([1])
        before = repr(value)
        first = value.freeze()
        second = value.freeze()
        return {
            "after": repr(value),
            "before": before,
            "first": first,
            "frozen": value.frozen,
            "second": second,
        }

    if name == "frozen-setitem":
        value = FrozenList([1, 2])
        value.freeze()
        error = _error(lambda: value.__setitem__(0, 9))
        return {"error": error, "items": list(value)}

    if name == "frozen-delitem":
        value = FrozenList([1, 2])
        value.freeze()
        error = _error(lambda: value.__delitem__(slice(None)))
        return {"error": error, "items": list(value)}

    if name == "frozen-insert":
        value = FrozenList([1])
        value.freeze()
        error = _error(lambda: value.insert(0, 0))
        return {"error": error, "items": list(value)}

    if name == "frozen-append-extend-iadd":
        value = FrozenList([1])
        value.freeze()

        def iadd() -> None:
            nonlocal value
            value += [4]

        return {
            "append": _error(lambda: value.append(2)),
            "extend": _error(lambda: value.extend([3])),
            "iadd": _error(iadd),
            "items": list(value),
        }

    if name == "frozen-remove-clear-reverse-pop":
        value = FrozenList([1, 2])
        value.freeze()
        return {
            "clear": _error(value.clear),
            "items": list(value),
            "pop": _error(value.pop),
            "remove": _error(lambda: value.remove(1)),
            "reverse": _error(value.reverse),
        }

    if name == "hash-contract":
        value = FrozenList([1, 2])
        before = _error(lambda: hash(value))
        value.freeze()
        return {
            "after_matches_tuple": hash(value) == hash((1, 2)),
            "before": before,
            "dict_lookup": {value: "ok"}[value],
        }

    if name == "shallow-copy":
        inner = [1]
        original = FrozenList([inner, 2])
        duplicate = copy.copy(original)
        original.append(3)
        duplicate_frozen = FrozenList([4])
        duplicate_frozen.freeze()
        frozen_copy = copy.copy(duplicate_frozen)
        return {
            "different": duplicate is not original,
            "frozen_copy": [list(frozen_copy), frozen_copy.frozen],
            "lengths": [len(original), len(duplicate)],
            "shared_item": duplicate[0] is inner,
        }

    if name == "deepcopy-nested":
        inner = FrozenList([[1]])
        original = FrozenList([inner, 2])
        duplicate = copy.deepcopy(original)
        duplicate[0][0].append(3)
        frozen = FrozenList([inner])
        frozen.freeze()
        frozen_copy = copy.deepcopy(frozen)
        return {
            "different_inner": duplicate[0] is not inner,
            "frozen": frozen_copy.frozen,
            "nested_copy": duplicate[0][0],
            "nested_original": original[0][0],
        }

    if name == "deepcopy-circular":
        original = FrozenList([1])
        original.append(original)
        duplicate = copy.deepcopy(original)
        return {
            "different": duplicate is not original,
            "items": duplicate[0],
            "self_cycle": duplicate[1] is duplicate,
        }

    if name == "deepcopy-shared-reference":
        shared = FrozenList([1])
        original = FrozenList([shared, shared])
        duplicate = copy.deepcopy(original)
        duplicate[0].append(2)
        return {
            "copy_items": list(duplicate[1]),
            "new_shared": duplicate[0] is not shared,
            "original_items": list(shared),
            "same_reference": duplicate[0] is duplicate[1],
        }

    if name == "pyfrozenlist-parity":
        value = PyFrozenList([1, 2])
        value.append(3)
        before = repr(value)
        value.freeze()
        return {
            "append_error": _error(lambda: value.append(4)),
            "before": before,
            "frozen": value.frozen,
            "hash_matches": hash(value) == hash((1, 2, 3)),
            "items": list(value),
        }

    if name == "pure-python-selection":
        return {
            "disabled": os.environ.get("FROZENLIST_NO_EXTENSIONS"),
            "same": FrozenList is PyFrozenList,
            "module": FrozenList.__module__,
        }

    raise ValueError(f"unknown scenario: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    _limits()
    if Path(args.candidate_site).resolve() != Path("/tmp/candidate-site"):
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    payload: dict[str, Any]
    try:
        payload = {"ok": True, "value": exercise(args.scenario)}
    except BaseException as exc:
        payload = {
            "exception_message": str(exc),
            "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "ok": False,
        }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    os.write(1, RESULT_PREFIX.encode() + encoded + b"\n")


if __name__ == "__main__":
    main()

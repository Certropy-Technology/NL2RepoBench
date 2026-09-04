from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import resource
import sys
from collections.abc import ItemsView, KeysView, Mapping, MutableMapping, ValuesView
from pathlib import Path
from typing import Any

RESULT_PREFIX = "NL2REPO_MULTIDICT_RESULT="


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
        return {"message": str(exc), "type": f"{type(exc).__module__}.{type(exc).__qualname__}"}
    return {"message": None, "type": None}


def exercise(name: str) -> Any:
    import multidict
    from multidict import (
        CIMultiDict,
        CIMultiDictProxy,
        MultiDict,
        MultiDictProxy,
        MultiMapping,
        MutableMultiMapping,
        getversion,
        istr,
        upstr,
    )

    if name == "surface-metadata":
        package = Path(multidict.__file__).resolve().parent
        distributions = importlib.metadata.distributions(path=[str(package.parent)])
        version = next(d.version for d in distributions if d.metadata.get("Name", "").casefold() == "multidict")
        return {"all": list(multidict.__all__), "py_typed": (package / "py.typed").is_file(), "version": multidict.__version__, "distribution_version": version}
    if name == "abc-generics":
        return {"mapping": issubclass(MultiDict, Mapping), "mutable": issubclass(MultiDict, MutableMapping), "multi": issubclass(MultiDict, MutableMultiMapping), "proxy": issubclass(MultiDictProxy, MultiMapping), "alias": str(MultiDict[int]).replace("multidict._multidict_py.", "multidict.")}
    if name == "constructor-duplicates":
        source = [("a", 1), ("a", 2), ("b", 3)]
        value = MultiDict(source, c=4)
        source.append(("z", 9))
        return {"items": list(value.items()), "keys": list(value.keys()), "values": list(value.values()), "len": len(value), "source": source}
    if name == "mapping-constructor":
        value = MultiDict({"a": 1, "b": 2})
        duplicate = MultiDict(value)
        return {"items": list(value.items()), "copy": list(duplicate.items()), "different": duplicate is not value}
    if name == "get-contract":
        value = MultiDict([("a", 1), ("a", 2)])
        return {"getitem": value["a"], "get": value.get("a"), "get_default": value.get("z", 8), "getall": value.getall("a"), "getall_default": value.getall("z", []), "getone": value.getone("a"), "getone_default": value.getone("z", 9)}
    if name == "get-errors":
        value = MultiDict()
        return {"getitem": _error(lambda: value["missing"]), "getall": _error(lambda: value.getall("missing")), "getone": _error(lambda: value.getone("missing"))}
    if name == "contains-nonstring":
        value = MultiDict([("1", "x")])
        return {"string": "1" in value, "integer": 1 in value, "missing": "x" in value}
    if name == "add-setitem":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        add_result = value.add("a", 4)
        value["a"] = 5
        value["c"] = 6
        return {"add_result": add_result, "items": list(value.items()), "all_a": value.getall("a")}
    if name == "delete-clear":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        del value["a"]
        after_delete = list(value.items())
        clear_result = value.clear()
        return {"after_delete": after_delete, "after_clear": list(value.items()), "clear_result": clear_result, "missing": _error(lambda: value.__delitem__("z"))}
    if name == "setdefault":
        value = MultiDict([("a", 1), ("a", 2)])
        return {"existing": value.setdefault("a", 9), "new": value.setdefault("b", 3), "none": value.setdefault("c"), "items": list(value.items())}
    if name == "extend":
        value = MultiDict([("a", 1)])
        result = value.extend([("a", 2), ("b", 3)], c=4)
        return {"result": result, "items": list(value.items())}
    if name == "update":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        result = value.update([("a", 4), ("a", 5), ("c", 6)], d=7)
        return {"result": result, "items": list(value.items())}
    if name == "merge":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        result = value.merge([("a", 4), ("c", 5), ("c", 6)], d=7)
        return {"result": result, "items": list(value.items())}
    if name == "popone":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        return {"first": value.popone("a"), "remaining": list(value.items()), "default": value.popone("z", 8), "error": _error(lambda: value.popone("z"))}
    if name == "popall":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        return {"all": value.popall("a"), "remaining": list(value.items()), "default": value.popall("z", []), "error": _error(lambda: value.popall("z"))}
    if name == "popitem":
        value = MultiDict([("a", 1), ("b", 2)])
        first = value.popitem()
        second = value.popitem()
        return {"first": first, "second": second, "error": _error(value.popitem)}
    if name == "case-insensitive":
        value = CIMultiDict([("Content-Type", "text/plain"), ("content-type", "json"), ("X", "y")])
        return {"all": value.getall("CONTENT-TYPE"), "first": value["content-TYPE"], "contains": "CONTENT-type" in value, "items": list(value.items())}
    if name == "case-update-key":
        value = CIMultiDict([("Header", 1), ("HEADER", 2), ("Other", 3)])
        value["header"] = 4
        return {"items": list(value.items()), "keys": list(value.keys())}
    if name == "istr-contract":
        key = istr("AbC")
        value = CIMultiDict([(key, 1)])
        return {"is_str": isinstance(key, str), "text": str(key), "repr": repr(key), "lookup": value["abc"], "upstr_same": upstr is istr}
    if name == "copy-contract":
        inner = []
        value = MultiDict([("a", inner), ("a", 2)])
        duplicate = value.copy()
        value.add("b", 3)
        return {"different": duplicate is not value, "copy_items": list(duplicate.items()), "source_items": list(value.items()), "shared": duplicate["a"] is inner}
    if name == "proxy-live":
        value = MultiDict([("a", 1), ("a", 2)])
        proxy = MultiDictProxy(value)
        value.add("b", 3)
        return {"items": list(proxy.items()), "all": proxy.getall("a"), "copy_type": type(proxy.copy()).__name__, "copy_items": list(proxy.copy().items())}
    if name == "proxy-readonly":
        proxy = MultiDictProxy(MultiDict([("a", 1)]))
        return {"set": _error(lambda: proxy.__setitem__("a", 2)), "add": hasattr(proxy, "add"), "dict": isinstance(proxy, dict)}
    if name == "proxy-validation":
        return {"plain": _error(lambda: MultiDictProxy({"a": 1})), "ci_plain": _error(lambda: CIMultiDictProxy({"a": 1})), "cross": _error(lambda: CIMultiDictProxy(MultiDict()))}
    if name == "ci-proxy":
        value = CIMultiDict([("A", 1)])
        proxy = CIMultiDictProxy(value)
        value.add("a", 2)
        return {"all": proxy.getall("a"), "copy_type": type(proxy.copy()).__name__, "items": list(proxy.items())}
    if name == "views":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        return {"keys_type": isinstance(value.keys(), KeysView), "items_type": isinstance(value.items(), ItemsView), "values_type": isinstance(value.values(), ValuesView), "keys": list(value.keys()), "items": list(value.items()), "values": list(value.values())}
    if name == "view-sets":
        value = MultiDict([("a", 1), ("a", 2), ("b", 3)])
        return {"keys_and": sorted(value.keys() & {"a", "z"}), "keys_or": sorted(value.keys() | {"z"}), "items_and": sorted(value.items() & {("a", 2), ("z", 9)}), "disjoint": value.keys().isdisjoint({"x", "y"})}
    if name == "view-mutation-guard":
        value = MultiDict([("a", 1), ("b", 2)])
        iterator = iter(value.items())
        first = next(iterator)
        value.add("c", 3)
        return {"first": first, "next": _error(lambda: next(iterator))}
    if name == "equality":
        one = MultiDict([("a", 1), ("a", 2)])
        two = MultiDict([("a", 1), ("a", 2)])
        reordered = MultiDict([("a", 2), ("a", 1)])
        return {"same": one == two, "order": one == reordered, "plain": MultiDict([("a", 1)]) == {"a": 1}, "not_mapping": one == [("a", 1)]}
    if name == "version":
        value = MultiDict([("a", 1)])
        v1 = getversion(value)
        value.add("b", 2)
        v2 = getversion(value)
        proxy = MultiDictProxy(value)
        return {"integer": isinstance(v1, int), "increased": v2 > v1, "proxy": getversion(proxy) == v2, "bad": _error(lambda: getversion({}))}
    if name == "constructor-errors":
        return {"key": _error(lambda: MultiDict([(1, 2)])), "length": _error(lambda: MultiDict([("a", 1, 2)])), "scalar": _error(lambda: MultiDict([1]))}
    if name == "repr-recursion":
        value = MultiDict()
        value.add("self", value)
        return {"empty": repr(MultiDict()), "duplicate": repr(MultiDict([("a", 1), ("a", 2)])), "recursive": repr(value)}
    raise ValueError(f"unknown scenario: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    _limits()
    sys.path.insert(0, str(Path(args.candidate_site).resolve()))
    try:
        payload = {"ok": True, "value": exercise(args.scenario)}
    except BaseException as exc:
        payload = {"ok": False, "exception_message": str(exc), "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    os.write(1, RESULT_PREFIX.encode() + encoded + b"\n")


if __name__ == "__main__":
    main()

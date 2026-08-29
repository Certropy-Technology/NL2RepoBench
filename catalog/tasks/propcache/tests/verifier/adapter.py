from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any


def type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def module_for(variant: str):
    if variant == "public":
        return importlib.import_module("propcache")
    return importlib.import_module(f"propcache._helpers_{variant}")


def run_scenario(scenario: str) -> Any:
    import propcache
    from propcache import api

    if scenario == "metadata/version":
        return propcache.__version__
    if scenario == "metadata/exports":
        return {
            "api": list(api.__all__),
            "helpers": list(importlib.import_module("propcache._helpers").__all__),
            "same": propcache.cached_property is api.cached_property
            and propcache.under_cached_property is api.under_cached_property,
        }
    if scenario == "metadata/dir":
        return "cached_property" in dir(propcache) and "under_cached_property" in dir(propcache)
    if scenario == "metadata/invalid-attr":
        try:
            getattr(propcache, "invalid_attr")
        except AttributeError as exc:
            return {"type": type_name(exc), "message": str(exc)}
        return None
    if scenario == "api/identity":
        helpers = importlib.import_module("propcache._helpers")
        return {
            "cached": api.cached_property is helpers.cached_property,
            "under": api.under_cached_property is helpers.under_cached_property,
        }
    if scenario == "cached/class-access":
        cls = module_for("public").cached_property

        class A:
            @cls
            def prop(self):
                return 1

        return A.prop is A.__dict__["prop"]
    if scenario == "cached/cache-hit":
        calls = 0

        class A:
            @propcache.cached_property
            def prop(self):
                nonlocal calls
                calls += 1
                return []

        item = A()
        first = item.prop
        second = item.prop
        return {"calls": calls, "same": first is second, "stored": item.__dict__["prop"] is first}
    if scenario == "cached/docstring":
        class A:
            @propcache.cached_property
            def prop(self):
                """descriptor documentation."""
                return 1

        return A.prop.__doc__
    if scenario == "cached/wrapped-callable":
        class A:
            @propcache.cached_property
            def prop(self):
                return 7

        return A.prop.func(A())
    if scenario == "cached/delete-recompute":
        calls = 0

        class A:
            @propcache.cached_property
            def prop(self):
                nonlocal calls
                calls += 1
                return calls

        item = A()
        values = [item.prop]
        del item.__dict__["prop"]
        values.append(item.prop)
        return {"calls": calls, "values": values}
    if scenario == "cached/set-name-guard":
        descriptor = propcache.cached_property(lambda self: 1)

        class A:
            pass

        descriptor.__set_name__(A, "prop")
        try:
            descriptor.__set_name__(A, "other")
        except TypeError as exc:
            return type_name(exc)
        return None
    if scenario == "cached/missing-set-name":
        descriptor = propcache.cached_property(lambda self: 1)

        class A:
            pass

        A.prop = descriptor
        try:
            A().prop
        except Exception as exc:
            return type_name(exc)
        return None
    if scenario == "cached/no-dict":
        class A:
            __slots__ = ()

            @propcache.cached_property
            def prop(self):
                return 1

        try:
            A().prop
        except Exception as exc:
            return type_name(exc)
        return None
    if scenario == "cached/generic-alias":
        return type(propcache.cached_property[int]).__name__
    if scenario == "under/class-access":
        class A:
            def __init__(self):
                self._cache = {}

            @propcache.under_cached_property
            def prop(self):
                return 1

        return A.prop is A.__dict__["prop"]
    if scenario == "under/cache-hit":
        calls = 0

        class A:
            def __init__(self):
                self._cache = {}

            @propcache.under_cached_property
            def prop(self):
                nonlocal calls
                calls += 1
                return object()

        item = A()
        first = item.prop
        second = item.prop
        return {"calls": calls, "same": first is second, "stored": item._cache["prop"] is first}
    if scenario == "under/docstring":
        class A:
            def __init__(self):
                self._cache = {}

            @propcache.under_cached_property
            def prop(self):
                """under documentation."""
                return 1

        return A.prop.__doc__
    if scenario == "under/wrapped-callable":
        class A:
            def __init__(self):
                self._cache = {}

            @propcache.under_cached_property
            def prop(self):
                return 9

        item = A()
        value = A.prop.wrapped(item)
        item.prop
        return {"value": value, "cache-key": "prop" if "prop" in item._cache else None}
    if scenario == "under/readonly":
        class A:
            def __init__(self):
                self._cache = {}

            @propcache.under_cached_property
            def prop(self):
                return 1

        try:
            A().prop = 2
        except AttributeError as exc:
            return {"type": type_name(exc), "message": str(exc)}
        return None
    if scenario == "under/missing-cache":
        class A:
            @propcache.under_cached_property
            def prop(self):
                return 1

        try:
            A().prop
        except Exception as exc:
            return type_name(exc)
        return None
    if scenario == "under/cache-preserves-none":
        class A:
            def __init__(self):
                self._cache = {"prop": None}

            @propcache.under_cached_property
            def prop(self):
                raise AssertionError("cache miss")

        return A().prop is None
    if scenario == "under/generic-alias":
        return type(propcache.under_cached_property[int]).__name__
    if scenario == "fallback/cached":
        module = module_for("py")
        calls = 0

        class A:
            @module.cached_property
            def prop(self):
                nonlocal calls
                calls += 1
                return calls

        item = A()
        return [item.prop, item.prop, calls]
    if scenario == "fallback/under":
        module = module_for("py")
        calls = 0

        class A:
            def __init__(self):
                self._cache = {}

            @module.under_cached_property
            def prop(self):
                nonlocal calls
                calls += 1
                return calls

        item = A()
        return [item.prop, item.prop, calls]
    if scenario == "extension/import":
        try:
            module = module_for("c")
        except ImportError:
            return {"ok": False}
        return {"ok": True, "cached": module.cached_property.__name__, "under": module.under_cached_property.__name__}
    if scenario == "extension/cached":
        module = module_for("c")
        calls = 0

        class A:
            @module.cached_property
            def prop(self):
                nonlocal calls
                calls += 1
                return calls

        item = A()
        return [item.prop, item.prop, calls]
    if scenario == "extension/under":
        module = module_for("c")
        calls = 0

        class A:
            def __init__(self):
                self._cache = {}

            @module.under_cached_property
            def prop(self):
                nonlocal calls
                calls += 1
                return calls

        item = A()
        return [item.prop, item.prop, calls]
    if scenario == "metadata/no-wildcard":
        return list(propcache.__all__)
    raise ValueError(f"unknown scenario: {scenario}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    try:
        value = run_scenario(args.scenario)
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": type_name(exc), "exception_message": str(exc)}, sort_keys=True))
    else:
        print(json.dumps({"ok": True, "value": value}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

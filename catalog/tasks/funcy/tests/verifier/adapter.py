"""Unprivileged child adapter for the bounded funcy 2.0 contract."""

from __future__ import annotations

import argparse
from collections.abc import Iterator, Mapping
from importlib import metadata
from itertools import islice
import json
from pathlib import Path
import sys


def _increment(value):
    return value + 1


def _double(value):
    return value * 2


def _square(value):
    return value * value


def _add(left, right):
    return left + right


def _even(value):
    return value % 2 == 0


def _odd(value):
    return value % 2 == 1


def _modulo_two(value):
    return value % 2


def _modulo_three(value):
    return value % 3


def _pair_value_double(pair):
    key, value = pair
    return key, value * 2


def _key_upper(value):
    return value.upper()


def _second_gt_one(pair):
    return pair[1] > 1


def _ternary_concat(left, middle, right):
    return f"{left}{middle}{right}"


def _affine(value, scale=1, offset=0):
    return value * scale + offset


def _length(value):
    return len(value)


CALLBACKS = {
    "add": _add,
    "affine": _affine,
    "double": _double,
    "even": _even,
    "increment": _increment,
    "key-upper": _key_upper,
    "length": _length,
    "list-values": list,
    "modulo-2": _modulo_two,
    "modulo-3": _modulo_three,
    "odd": _odd,
    "pair-value-double": _pair_value_double,
    "second-gt-one": _second_gt_one,
    "square": _square,
    "sum-values": sum,
    "ternary-concat": _ternary_concat,
}

INVOKE_APIS = {
    "chunks",
    "compact",
    "distinct",
    "flatten",
    "get_in",
    "group_by",
    "keep",
    "lfilter",
    "lmap",
    "merge",
    "merge_with",
    "pairwise",
    "partition_by",
    "reductions",
    "select",
    "split",
    "take",
    "walk",
    "walk_keys",
    "walk_values",
}


class TrackingIterator:
    def __init__(self, values):
        self._values = iter(values)
        self.seen = []

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self._values)
        self.seen.append(value)
        return value


def _decode(value, *, source=None):
    if isinstance(value, list):
        return [_decode(item, source=source) for item in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {"$callback"}:
        return CALLBACKS[value["$callback"]]
    if set(value) == {"$iterator"}:
        return iter(_decode(value["$iterator"], source=source))
    if set(value) == {"$set"}:
        return set(_decode(value["$set"], source=source))
    if set(value) == {"$tuple"}:
        return tuple(_decode(value["$tuple"], source=source))
    if set(value) == {"$source"} and value["$source"] is True:
        if source is None:
            raise ValueError("tracking source is unavailable")
        return source
    return {key: _decode(item, source=source) for key, item in value.items()}


def _observe(value):
    if isinstance(value, Mapping):
        return {
            "kind": "mapping",
            "type": type(value).__name__,
            "items": [[_observe(key), _observe(item)] for key, item in value.items()],
        }
    if isinstance(value, Iterator):
        return {
            "kind": "iterator",
            "items": [_observe(item) for item in value],
        }
    if isinstance(value, tuple):
        return {"kind": "tuple", "items": [_observe(item) for item in value]}
    if isinstance(value, (set, frozenset)):
        items = [_observe(item) for item in value]
        return {"kind": type(value).__name__, "items": sorted(items, key=repr)}
    if isinstance(value, list):
        return [_observe(item) for item in value]
    return value


def _api_surface(candidate_site: Path):
    import funcy

    modules = (
        "calc",
        "colls",
        "decorators",
        "debug",
        "flow",
        "funcolls",
        "funcmakers",
        "funcs",
        "objects",
        "primitives",
        "seqs",
        "strings",
        "tree",
        "types",
    )
    required = (
        "autocurry",
        "cache",
        "cached_property",
        "chunks",
        "compact",
        "compose",
        "curry",
        "distinct",
        "drop",
        "flatten",
        "group_by",
        "keep",
        "lfilter",
        "lmap",
        "memoize",
        "merge",
        "merge_with",
        "once",
        "pairwise",
        "select",
        "take",
        "update_in",
        "walk",
    )
    origin = Path(funcy.__file__).resolve()
    return {
        "all_unique": len(funcy.__all__) == len(set(funcy.__all__)),
        "candidate_origin": origin.is_relative_to(candidate_site.resolve()),
        "exports": {name: name in funcy.__all__ and hasattr(funcy, name) for name in required},
        "modules": {name: hasattr(__import__(f"funcy.{name}"), name) for name in modules},
        "version": metadata.version("funcy"),
    }


def _invoke(request):
    import funcy

    api = request["api"]
    if api not in INVOKE_APIS:
        raise ValueError("unsupported invoke API")
    function = getattr(funcy, api)
    args = _decode(request.get("args", []))
    kwargs = _decode(request.get("kwargs", {}))
    value = function(*args, **kwargs)
    return {"is_iterator": isinstance(value, Iterator), "value": _observe(value)}


def _lazy_trace(request):
    import funcy

    api = request["api"]
    if api not in {"drop", "walk"}:
        raise ValueError("unsupported lazy trace API")
    source = TrackingIterator(_decode(request["source"]))
    args = _decode(request.get("args", []), source=source)
    value = getattr(funcy, api)(*args)
    before = list(source.seen)
    prefix = list(islice(value, request["count"]))
    after_prefix = list(source.seen)
    remainder = list(value)
    return {
        "after_prefix": after_prefix,
        "before": before,
        "is_iterator": isinstance(value, Iterator),
        "prefix": _observe(prefix),
        "remainder": _observe(remainder),
        "source_seen": source.seen,
    }


def _prefix(request):
    import funcy

    api = request["api"]
    if api != "iterate":
        raise ValueError("unsupported prefix API")
    value = funcy.iterate(CALLBACKS[request["callback"]], _decode(request["initial"]))
    return {
        "is_iterator": isinstance(value, Iterator),
        "value": _observe(list(islice(value, request["count"]))),
    }


def _compose(request):
    import funcy

    api = request["api"]
    if api not in {"compose", "rcompose"}:
        raise ValueError("unsupported composition API")
    callbacks = [CALLBACKS[name] for name in request.get("callbacks", [])]
    combined = getattr(funcy, api)(*callbacks)
    value = combined(*_decode(request.get("args", [])), **_decode(request.get("kwargs", {})))
    return _observe(value)


def _staged_call(request):
    import funcy

    api = request["api"]
    if api not in {"autocurry", "curry", "rcurry"}:
        raise ValueError("unsupported staged-call API")
    value = getattr(funcy, api)(CALLBACKS[request["callback"]])
    for stage in request["stages"]:
        value = value(*_decode(stage.get("args", [])), **_decode(stage.get("kwargs", {})))
    return _observe(value)


def _juxt(request):
    import funcy

    api = request["api"]
    if api not in {"juxt", "ljuxt"}:
        raise ValueError("unsupported juxt API")
    function = getattr(funcy, api)(*(CALLBACKS[name] for name in request["callbacks"]))
    value = function(*_decode(request.get("args", [])))
    return {"is_iterator": isinstance(value, Iterator), "value": _observe(value)}


def _memoize_trace(request):
    import funcy

    calls = []

    def counted_affine(value, scale=1, offset=0):
        calls.append([value, scale, offset])
        return value * scale + offset

    def skip_negative(value, scale=1, offset=0):
        calls.append([value, scale, offset])
        if value < 0:
            raise funcy.memoize.skip("not-cached")
        return value * scale + offset

    recipes = {"counted-affine": counted_affine, "skip-negative": skip_negative}
    key_name = request.get("key_callback")
    decorator = funcy.memoize if key_name is None else funcy.memoize(key_func=CALLBACKS[key_name])
    wrapped = decorator(recipes[request["recipe"]])
    results = []
    for step in request["steps"]:
        operation = step["operation"]
        if operation == "call":
            results.append(_observe(wrapped(*_decode(step.get("args", [])), **_decode(step.get("kwargs", {})))))
        elif operation == "invalidate":
            wrapped.invalidate(*_decode(step.get("args", [])), **_decode(step.get("kwargs", {})))
        elif operation == "invalidate-all":
            wrapped.invalidate_all()
        else:
            raise ValueError("unsupported memoize step")
    return {
        "calls": calls,
        "memory_size": len(wrapped.memory),
        "name": wrapped.__name__,
        "results": results,
    }


def _cache_trace(request):
    import funcy
    import funcy.calc

    now = [0.0]
    original_time = funcy.calc.time.time
    funcy.calc.time.time = lambda: now[0]
    calls = []

    @funcy.cache(request["timeout"])
    def counted_affine(value, scale=1, offset=0):
        calls.append([value, scale, offset])
        return value * scale + offset

    results = []
    try:
        for step in request["steps"]:
            operation = step["operation"]
            if operation == "time":
                now[0] = float(step["value"])
            elif operation == "call":
                results.append(counted_affine(*step.get("args", []), **step.get("kwargs", {})))
            elif operation == "invalidate":
                counted_affine.invalidate(*step.get("args", []), **step.get("kwargs", {}))
            else:
                raise ValueError("unsupported cache step")
    finally:
        funcy.calc.time.time = original_time
    return {"calls": calls, "memory_size": len(counted_affine.memory), "results": results}


def _nested_update(request):
    import funcy

    original = _decode(request["value"])
    result = funcy.update_in(
        original,
        _decode(request["path"]),
        CALLBACKS[request["callback"]],
        request.get("default"),
    )
    return {
        "inner_identity": result[request["path"][0]] is original.get(request["path"][0]),
        "original": _observe(original),
        "result": _observe(result),
        "root_identity": result is original,
    }


def _cached_property(request):
    import funcy

    if request["callback"] != "computed-seven":
        raise ValueError("unsupported property callback")
    calls = []

    class Holder:
        @funcy.cached_property
        def value(self):
            """computed value"""
            calls.append(True)
            return 7

    holder = Holder()
    values = [holder.value, holder.value]
    holder.value = 9
    values.append(holder.value)
    del holder.value
    values.append(holder.value)
    return {"calls": len(calls), "doc": Holder.value.__doc__, "values": values}


def _once_trace(request):
    import funcy

    if request["callback"] != "record-affine":
        raise ValueError("unsupported once callback")
    calls = []

    @funcy.once
    def record(value, scale=1):
        calls.append([value, scale])
        return value * scale

    results = [record(*step.get("args", []), **step.get("kwargs", {})) for step in request["calls"]]
    return {"calls": calls, "name": record.__name__, "results": results}


ACTIONS = {
    "api-surface": _api_surface,
    "cache-trace": _cache_trace,
    "cached-property": _cached_property,
    "compose": _compose,
    "invoke": _invoke,
    "juxt": _juxt,
    "lazy-trace": _lazy_trace,
    "memoize-trace": _memoize_trace,
    "nested-update": _nested_update,
    "once-trace": _once_trace,
    "prefix": _prefix,
    "staged-call": _staged_call,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", type=Path, required=True)
    parser.add_argument("--request", required=True)
    arguments = parser.parse_args()
    try:
        request = json.loads(arguments.request)
        if request.get("schema_version") != "funcy-scenarios-v1":
            raise ValueError("unsupported request schema")
        sys.path.insert(0, str(arguments.candidate_site))
        action = request["action"]
        if action == "api-surface":
            value = ACTIONS[action](arguments.candidate_site)
        else:
            value = ACTIONS[action](request)
        response = {"ok": True, "value": value}
    except BaseException as error:
        response = {
            "exception_message": str(error),
            "exception_type": type(error).__name__,
            "ok": False,
        }
    print(json.dumps(response, ensure_ascii=False, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()

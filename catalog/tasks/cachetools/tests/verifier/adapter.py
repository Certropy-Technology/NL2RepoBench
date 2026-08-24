"""Unprivileged child adapter for deterministic cachetools scenarios."""

from __future__ import annotations

import argparse
import json
import pickle
import sys
import threading
from collections.abc import MutableMapping
from datetime import datetime, timedelta, timezone
from pathlib import Path


class Clock:
    def __init__(self, value=0):
        self.value = value

    def __call__(self):
        return self.value

    def set(self, value):
        self.value = value


class AdvancingClock:
    def __init__(self):
        self.value = 0

    def __call__(self):
        value = self.value
        self.value += 1
        return value


def error_name(callback):
    try:
        callback()
    except Exception as error:  # The exception type is the observation.
        return type(error).__name__
    return None


def api_surface(candidate_site: Path):
    import cachetools
    import cachetools.func as func
    import cachetools.keys as keys

    cache_types = (
        cachetools.Cache,
        cachetools.FIFOCache,
        cachetools.LFUCache,
        cachetools.LRUCache,
        cachetools.RRCache,
        cachetools.TLRUCache,
        cachetools.TTLCache,
    )
    origin = Path(cachetools.__file__).resolve()
    return {
        "candidate_origin": origin.is_relative_to(candidate_site.resolve()),
        "func_all": sorted(func.__all__),
        "keys_all": sorted(keys.__all__),
        "mutable_mappings": all(issubclass(value, MutableMapping) for value in cache_types),
        "py_typed": origin.with_name("py.typed").is_file(),
        "root_all": sorted(cachetools.__all__),
        "version": cachetools.__version__,
    }


def cache_sizing(_candidate_site: Path):
    from cachetools import Cache

    cache = Cache(5, getsizeof=len)
    cache["a"] = "xx"
    cache["b"] = "yyy"
    initial_size = cache.currsize
    cache["a"] = "x"
    replaced_size = cache.currsize
    oversized = error_name(lambda: cache.__setitem__("c", "123456"))
    negative = Cache(2, getsizeof=lambda _value: -1)
    negative_error = error_name(lambda: negative.__setitem__("x", "value"))
    zero = Cache(0)
    zero_error = error_name(lambda: zero.__setitem__("x", 1))
    popped = cache.pop("b")
    before_clear = {"currsize": cache.currsize, "items": sorted(cache.items())}
    cache.clear()
    return {
        "before_clear": before_clear,
        "cleared": {"currsize": cache.currsize, "length": len(cache)},
        "default_size": Cache.getsizeof(object()),
        "initial_size": initial_size,
        "maxsize": cache.maxsize,
        "negative_error": negative_error,
        "oversized_error": oversized,
        "popped": popped,
        "replaced_size": replaced_size,
        "zero_error": zero_error,
    }


def missing_mapping(_candidate_site: Path):
    from cachetools import Cache

    class MissingCache(Cache):
        def __init__(self):
            super().__init__(4)
            self.misses = []

        def __missing__(self, key):
            self.misses.append(key)
            return f"generated:{key}"

    cache = MissingCache()
    subscription = cache["one"]
    get_value = cache.get("two", "fallback")
    pop_value = cache.pop("three", "fallback")
    default_value = cache.setdefault("four", 4)
    return {
        "default_value": default_value,
        "get_value": get_value,
        "items": sorted(cache.items()),
        "misses": cache.misses,
        "pop_value": pop_value,
        "subscription": subscription,
    }


def fifo_policy(_candidate_site: Path):
    from cachetools import FIFOCache

    cache = FIFOCache(3)
    cache.update(a=1, b=2, c=3)
    _ = cache["a"]
    cache["b"] = 20
    victims = [list(cache.popitem()), list(cache.popitem()), list(cache.popitem())]
    return {"empty_error": error_name(cache.popitem), "victims": victims}


def lru_mru_policy(_candidate_site: Path):
    from cachetools import LRUCache

    cache = LRUCache(3)
    cache.update(a=1, b=2, c=3)
    _ = cache["a"]
    _ = cache["c"]
    first = cache.popitem()
    cache["d"] = 4
    _ = cache["a"]
    second = cache.popitem()
    cache["d"] = 40
    third = cache.popitem()
    return {
        "remaining": sorted(cache.items()),
        "victims": [list(first), list(second), list(third)],
    }


def lfu_policy(_candidate_site: Path):
    from cachetools import LFUCache

    cache = LFUCache(3)
    cache.update(a=1, b=2, c=3)
    _ = cache["a"]
    _ = cache["a"]
    _ = cache["b"]
    cache["d"] = 4
    after_first = sorted(cache)
    _ = cache["d"]
    _ = cache["d"]
    cache["e"] = 5
    return {
        "after_first_eviction": after_first,
        "final_items": sorted(cache.items()),
    }


def rr_policy(_candidate_site: Path):
    from cachetools import RRCache

    calls = []

    def choose_last(values):
        calls.append(list(values))
        return values[-1]

    cache = RRCache(2, choice=choose_last)
    cache.update(a=1, b=2)
    cache["c"] = 3
    popped = cache.popitem()
    return {
        "calls": calls,
        "choice_identity": cache.choice is choose_last,
        "popped": list(popped),
        "remaining": sorted(cache.items()),
    }


def ttl_expiration(_candidate_site: Path):
    from cachetools import TTLCache

    clock = Clock()
    cache = TTLCache(3, ttl=3, timer=clock)
    cache["a"] = 1
    clock.set(1)
    cache["b"] = 2
    clock.set(2)
    cache["c"] = 3
    expired_at_three = [list(item) for item in cache.expire(3)]
    expired_at_four = [list(item) for item in cache.expire(4)]
    clock.set(5)
    contains_c = "c" in cache
    get_c_error = error_name(lambda: cache["c"])
    expired_at_five = [list(item) for item in cache.expire()]
    return {
        "contains_c_at_deadline": contains_c,
        "expired_at_five": expired_at_five,
        "expired_at_four": expired_at_four,
        "expired_at_three": expired_at_three,
        "get_c_error": get_c_error,
        "length": len(cache),
        "timer_identity": cache.timer() == clock(),
        "ttl": cache.ttl,
    }


def ttl_lru_and_timer(_candidate_site: Path):
    from cachetools import TTLCache

    clock = Clock()
    cache = TTLCache(2, ttl=10, timer=clock)
    cache.update(a=1, b=2)
    _ = cache["a"]
    cache["c"] = 3

    advancing = AdvancingClock()
    timed = TTLCache(1, ttl=100, timer=advancing)
    with timed.timer as observed:
        frozen = [observed, timed.timer(), timed.timer()]
    outside = timed.timer()
    return {
        "frozen_timer_values": frozen,
        "lru_items": sorted(cache.items()),
        "outside_timer_value": outside,
    }


def ttl_datetime_domain(_candidate_site: Path):
    from cachetools import TTLCache

    origin = datetime(2030, 1, 1, tzinfo=timezone.utc)
    clock = Clock(origin)
    cache = TTLCache(2, ttl=timedelta(days=2), timer=clock)
    cache["dated"] = 7
    before = [list(item) for item in cache.expire(origin + timedelta(days=1))]
    exact = [list(item) for item in cache.expire(origin + timedelta(days=2))]
    return {"before_deadline": before, "exact_deadline": exact, "length": len(cache)}


def tlru_expiration(_candidate_site: Path):
    from cachetools import TLRUCache

    clock = Clock()

    def ttu(_key, value, now):
        return now + value

    cache = TLRUCache(3, ttu=ttu, timer=clock)
    cache["long"] = 5
    cache["short"] = 1
    cache["medium"] = 3
    first = [list(item) for item in cache.expire(1)]
    cache["long"] = 0
    after_dead_on_arrival = sorted(cache.items())
    clock.set(2)
    cache["fresh"] = 2
    second = [list(item) for item in cache.expire(3)]
    return {
        "after_dead_on_arrival": after_dead_on_arrival,
        "expires_at_one": first,
        "expires_at_three": second,
        "final_items": sorted(cache.items()),
        "ttu_result": cache.ttu("x", 4, 2),
    }


def key_functions(_candidate_site: Path):
    from cachetools import keys

    ordered = keys.hashkey(1, z=2, a=3)
    reordered = keys.hashkey(1, a=3, z=2)
    typed_int = keys.typedkey(1, value=2)
    typed_float = keys.typedkey(1.0, value=2.0)
    concatenated = keys.hashkey("a") + ("b",)
    return {
        "concatenated": list(concatenated),
        "concatenated_type": type(concatenated).__name__,
        "method_ignores_self": keys.methodkey(object(), 1, x=2) == keys.hashkey(1, x=2),
        "ordered_kwargs": ordered == reordered,
        "pickle_roundtrip": pickle.loads(pickle.dumps(ordered)) == ordered,
        "typed_distinct": typed_int != typed_float,
        "typed_method_ignores_self": keys.typedmethodkey(object(), 1) == keys.typedkey(1),
        "unhashable_error": error_name(lambda: hash(keys.hashkey([]))),
        "untyped_numeric_equal": keys.hashkey(1) == keys.hashkey(1.0),
    }


def cached_function(_candidate_site: Path):
    from cachetools import Cache, LRUCache, cached

    calls = []
    cache = LRUCache(2)

    @cached(cache, info=True)
    def compute(value, scale=1):
        """Multiply a value."""
        calls.append([value, scale])
        return value * scale

    results = [compute(2, scale=3), compute(2, scale=3), compute(4)]
    info_before = list(compute.cache_info())
    metadata = {
        "cache_identity": compute.cache is cache,
        "doc": compute.__doc__,
        "name": compute.__name__,
        "wrapped_name": compute.__wrapped__.__name__,
    }
    compute.cache_clear()
    info_after = list(compute.cache_info())

    oversized_calls = []
    tiny = Cache(1, getsizeof=len)

    @cached(tiny)
    def oversized():
        oversized_calls.append(True)
        return "large"

    oversized_results = [oversized(), oversized()]
    return {
        "calls": calls,
        "info_after_clear": info_after,
        "info_before_clear": info_before,
        "metadata": metadata,
        "oversized_cache_length": len(tiny),
        "oversized_call_count": len(oversized_calls),
        "oversized_results": oversized_results,
        "results": results,
    }


def cached_method(_candidate_site: Path):
    from cachetools import LRUCache, cachedmethod

    class Service:
        def __init__(self, label):
            self.label = label
            self.cache = LRUCache(2)
            self.calls = 0

        @cachedmethod(lambda self: self.cache, info=True)
        def value(self, number):
            """Return a labeled value."""
            self.calls += 1
            return f"{self.label}:{number}"

    first = Service("first")
    second = Service("second")
    results = [first.value(2), first.value(2), second.value(2)]

    shared_cache = LRUCache(2)

    class Shared:
        def __init__(self, label):
            self.label = label
            self.calls = 0

        @cachedmethod(lambda _self: shared_cache)
        def value(self, number):
            self.calls += 1
            return f"{self.label}:{number}"

    left = Shared("left")
    right = Shared("right")
    shared_results = [left.value(1), right.value(1)]
    return {
        "bound_cache_identity": first.value.cache is first.cache,
        "calls": [first.calls, second.calls],
        "first_info": list(first.value.cache_info()),
        "metadata": [first.value.__name__, first.value.__doc__, first.value.__wrapped__.__name__],
        "results": results,
        "second_info": list(second.value.cache_info()),
        "shared_calls": [left.calls, right.calls],
        "shared_results": shared_results,
    }


def convenience_lru(_candidate_site: Path):
    from cachetools.func import lru_cache

    untyped_calls = []

    @lru_cache(maxsize=2)
    def untyped(value):
        untyped_calls.append(type(value).__name__)
        return type(value).__name__

    typed_calls = []

    @lru_cache(maxsize=2, typed=True)
    def typed(value):
        typed_calls.append(type(value).__name__)
        return type(value).__name__

    untyped_results = [untyped(1), untyped(1.0)]
    typed_results = [typed(1), typed(1.0)]
    parameters = typed.cache_parameters()
    parameters["maxsize"] = 99

    zero_calls = []

    @lru_cache(maxsize=0)
    def zero(value):
        zero_calls.append(value)
        return value

    zero(1)
    zero(1)
    return {
        "parameters_after_mutation": typed.cache_parameters(),
        "typed_calls": typed_calls,
        "typed_info": list(typed.cache_info()),
        "typed_results": typed_results,
        "untyped_calls": untyped_calls,
        "untyped_info": list(untyped.cache_info()),
        "untyped_results": untyped_results,
        "zero_call_count": len(zero_calls),
        "zero_info": list(zero.cache_info()),
    }


def convenience_ttl(_candidate_site: Path):
    from cachetools.func import ttl_cache

    clock = Clock()
    calls = []

    @ttl_cache(maxsize=2, ttl=2, timer=clock)
    def compute(value):
        calls.append(value)
        return value * 10

    results = [compute(3), compute(3)]
    before = list(compute.cache_info())
    clock.set(2)
    results.append(compute(3))
    return {
        "after_deadline": list(compute.cache_info()),
        "before_deadline": before,
        "calls": calls,
        "parameters": compute.cache_parameters(),
        "results": results,
    }


def condition_stampede(_candidate_site: Path):
    from cachetools import LRUCache, cached

    entered = threading.Event()
    release = threading.Event()
    second_started = threading.Event()
    calls = []
    results = []

    @cached(LRUCache(2), condition=threading.Condition(), info=True)
    def compute(value):
        calls.append(value)
        entered.set()
        if not release.wait(5):
            raise RuntimeError("release timeout")
        return value * 2

    def invoke(mark_started=False):
        if mark_started:
            second_started.set()
        results.append(compute(5))

    first = threading.Thread(target=invoke)
    first.start()
    if not entered.wait(5):
        raise RuntimeError("first call did not enter")
    second = threading.Thread(target=invoke, args=(True,))
    second.start()
    if not second_started.wait(5):
        raise RuntimeError("second call did not start")
    release.set()
    first.join(5)
    second.join(5)
    return {
        "alive": [first.is_alive(), second.is_alive()],
        "call_count": len(calls),
        "info": list(compute.cache_info()),
        "results": sorted(results),
    }


OPERATIONS = {
    "api_surface": api_surface,
    "cache_sizing": cache_sizing,
    "cached_function": cached_function,
    "cached_method": cached_method,
    "condition_stampede": condition_stampede,
    "convenience_lru": convenience_lru,
    "convenience_ttl": convenience_ttl,
    "fifo_policy": fifo_policy,
    "key_functions": key_functions,
    "lfu_policy": lfu_policy,
    "lru_mru_policy": lru_mru_policy,
    "missing_mapping": missing_mapping,
    "rr_policy": rr_policy,
    "tlru_expiration": tlru_expiration,
    "ttl_datetime_domain": ttl_datetime_domain,
    "ttl_expiration": ttl_expiration,
    "ttl_lru_and_timer": ttl_lru_and_timer,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", type=Path, required=True)
    parser.add_argument("--request", required=True)
    arguments = parser.parse_args()
    try:
        request = json.loads(arguments.request)
        if request.get("schema_version") != "cachetools-scenarios-v1":
            raise ValueError("unsupported request schema")
        operation = request["operation"]
        callback = OPERATIONS[operation]
        sys.path.insert(0, str(arguments.candidate_site))
        value = callback(arguments.candidate_site)
        response = {"ok": True, "value": value}
    except Exception as error:
        response = {
            "exception_message": str(error),
            "exception_type": type(error).__name__,
            "ok": False,
        }
    print(json.dumps(response, ensure_ascii=False, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import textwrap

from nl2repobench.verification.candidate_client import CandidateCallResult, execute_script


def leaf(leaf_id: str, source: str) -> dict[str, object]:
    result: CandidateCallResult = execute_script(textwrap.dedent(source), timeout_sec=2.0)
    if result.ok:
        return {"id": leaf_id, "status": "passed", "details": "scenario completed"}
    detail = result.exception_message or result.exception_type or "candidate scenario failed"
    return {"id": leaf_id, "status": "failed", "message": detail[-2000:]}


SCENARIOS: tuple[tuple[str, str], ...] = (
    ("wrapt/version", """
        import wrapt
        assert wrapt.__version__ == "2.4.0rc5"
        result = wrapt.__version_info__
    """),
    ("wrapt/exports", """
        import wrapt
        expected = {"ObjectProxy", "CallableObjectProxy", "FunctionWrapper", "decorator",
                    "wrap_object", "unwrap_object", "lru_cache", "synchronized", "MISSING"}
        assert expected.issubset(set(wrapt.__all__))
        assert len(wrapt.__all__) == len(set(wrapt.__all__))
        result = list(wrapt.__all__)
    """),
    ("proxy/operations", """
        import wrapt
        proxy = wrapt.ObjectProxy([1, 2, 3])
        assert len(proxy) == 3 and list(proxy) == [1, 2, 3]
        assert 2 in proxy and proxy + [4] == [1, 2, 3, 4]
        assert proxy.__wrapped__ == [1, 2, 3]
        result = str(proxy)
    """),
    ("proxy/attribute-delegation", """
        import wrapt
        class Target:
            value = 3
        target = Target()
        proxy = wrapt.ObjectProxy(target)
        assert proxy.value == 3
        proxy.value = 7
        assert target.value == 7
        proxy._self_note = "private"
        assert proxy._self_note == "private" and not hasattr(target, "_self_note")
        result = proxy.value
    """),
    ("proxy/self-dict", """
        import wrapt
        class Target:
            def __init__(self): self.visible = 1
        target = Target()
        proxy = wrapt.ObjectProxy(target)
        proxy._self_hidden = 2
        assert proxy.__self_dict__["_self_hidden"] == 2
        assert "visible" not in proxy.__self_dict__
        result = dict(proxy.__self_dict__)
    """),
    ("proxy/repr-str", """
        import wrapt
        value = "hello"
        proxy = wrapt.ObjectProxy(value)
        assert str(proxy) == "hello" and repr(proxy).startswith("<ObjectProxy ")
        result = repr(proxy)
    """),
    ("proxy/equality-hash", """
        import wrapt
        value = ("a", 1)
        proxy = wrapt.ObjectProxy(value)
        assert proxy == value and value == proxy
        assert hash(proxy) == hash(value)
        assert proxy != ("b", 1)
        result = True
    """),
    ("proxy/context", """
        import wrapt
        class CM:
            def __enter__(self): return "entered"
            def __exit__(self, *args): return False
        proxy = wrapt.ObjectProxy(CM())
        with proxy as value:
            assert value == "entered"
        result = True
    """),
    ("proxy/auto-lazy", """
        import wrapt
        calls = []
        proxy = wrapt.LazyObjectProxy(lambda: calls.append(1) or {"x": 4})
        assert calls == []
        assert proxy["x"] == 4
        assert calls == [1]
        result = calls
    """),
    ("proxy/callable", """
        import wrapt
        def add(a, b): return a + b
        proxy = wrapt.CallableObjectProxy(add)
        assert proxy(2, 5) == 7
        assert proxy.__wrapped__ is add
        result = proxy(1, 1)
    """),
    ("proxy/fspath", """
        import os
        import wrapt
        from pathlib import Path
        path = Path("/tmp/example")
        proxy = wrapt.ObjectProxy(path)
        try:
            os.fspath(proxy)
        except TypeError:
            pass
        else:
            raise AssertionError("ObjectProxy unexpectedly implements os.fspath")
        result = True
    """),
    ("wrapper/call-contract", """
        import wrapt
        events = []
        def target(a, b=0): return a + b
        def around(wrapped, instance, args, kwargs):
            events.append((instance, args, kwargs))
            return wrapped(*args, **kwargs) * 2
        wrapped = wrapt.FunctionWrapper(target, around)
        assert wrapped(2, b=3) == 10
        assert events == [(None, (2,), {"b": 3})]
        result = wrapped(1)
    """),
    ("wrapper/metadata", """
        import inspect
        import wrapt
        def target(x: int) -> int:
            "target-doc"
            return x
        wrapped = wrapt.FunctionWrapper(target, lambda w, i, a, k: w(*a, **k))
        assert wrapped.__name__ == "target" and wrapped.__doc__ == "target-doc"
        assert wrapped.__module__ == target.__module__
        assert inspect.signature(wrapped) == inspect.signature(target)
        result = wrapped(4)
    """),
    ("wrapper/method-binding", """
        import wrapt
        class C:
            def __init__(self, n): self.n = n
            def value(self, x): return self.n + x
        def around(wrapped, instance, args, kwargs):
            assert instance is not None
            return wrapped(*args, **kwargs) * 2
        C.value = wrapt.FunctionWrapper(C.value, around)
        assert C(3).value(4) == 14
        result = C(1).value(2)
    """),
    ("wrapper/partial", """
        import wrapt
        def add(a, b, c=0): return a + b + c
        partial = wrapt.partial(add, 2, c=5)
        assert partial(3) == 10
        result = partial(1)
    """),
    ("wrapper/self-state", """
        import wrapt
        def target(): return 1
        wrapper = wrapt.FunctionWrapper(target, lambda w, i, a, k: w(*a, **k))
        wrapper._self_count = 3
        assert wrapper._self_count == 3 and not hasattr(target, "_self_count")
        result = wrapper()
    """),
    ("wrapper/classmethod", """
        import wrapt
        class C:
            @classmethod
            def value(cls, amount): return amount + 1
        def around(wrapped, instance, args, kwargs):
            assert instance is C
            return wrapped(*args, **kwargs) * 2
        C.value = wrapt.FunctionWrapper(C.value, around)
        assert C.value(4) == 10
        result = True
    """),
    ("decorator/basic", """
        import wrapt
        calls = []
        @wrapt.decorator
        def traced(wrapped, instance, args, kwargs):
            calls.append(args)
            return wrapped(*args, **kwargs) + 1
        @traced
        def f(x): return x * 2
        assert f(4) == 9 and calls == [(4,)]
        result = f(2)
    """),
    ("decorator/disabled", """
        import wrapt
        calls = []
        @wrapt.decorator(enabled=False)
        def traced(wrapped, instance, args, kwargs):
            calls.append(1)
            return wrapped(*args, **kwargs)
        @traced
        def f(): return 8
        assert f() == 8 and calls == []
        result = True
    """),
    ("decorator/enabled-predicate", """
        import wrapt
        calls = []
        @wrapt.decorator(enabled=lambda: False)
        def traced(wrapped, instance, args, kwargs):
            calls.append(1)
            return wrapped(*args, **kwargs) + 1
        @traced
        def f(): return 8
        assert f() == 8 and calls == []
        result = True
    """),
    ("decorator/adapter-signature", """
        import inspect
        import wrapt
        def prototype(a, b=2): pass
        @wrapt.decorator(adapter=prototype)
        def traced(wrapped, instance, args, kwargs): return wrapped(*args, **kwargs)
        @traced
        def f(value): return value
        signature = inspect.signature(f)
        assert list(signature.parameters) == ["a", "b"]
        assert signature.parameters["b"].default == 2
        assert f(6) == 6
        result = True
    """),
    ("signature/overlay", """
        import inspect
        import wrapt
        def prototype(a, b: int = 3): pass
        def target(value): return value
        viewed = wrapt.with_signature(target, prototype=prototype)
        signature = inspect.signature(viewed)
        assert list(signature.parameters) == ["a", "b"]
        assert signature.parameters["b"].default == 3
        assert viewed(9) == 9
        result = True
    """),
    ("patch/wrap-function", """
        import wrapt
        class Box:
            def get(self, value): return value + 1
        box = Box()
        def around(wrapped, instance, args, kwargs): return wrapped(*args, **kwargs) * 3
        handle = wrapt.wrap_function_wrapper(box, "get", around)
        assert box.get(2) == 9
        assert wrapt.is_wrapped_by(box.get, handle)
        result = True
    """),
    ("patch/wrap-object", """
        import wrapt
        class Box:
            value = 4
        box = Box()
        handle = wrapt.wrap_object(box, "value", lambda x: x + 2)
        assert box.value == 6
        assert wrapt.is_wrapped_by(box.value, handle)
        result = box.value
    """),
    ("patch/chain", """
        import wrapt
        def f(): return "ok"
        def around(w, i, a, k): return w(*a, **k)
        outer = wrapt.FunctionWrapper(wrapt.FunctionWrapper(f, around), around)
        chain = list(wrapt.wrapper_chain(outer))
        assert len(chain) == 3 and wrapt.unwrapped(outer) is f
        result = len(chain)
    """),
    ("patch/find-wrapper", """
        import wrapt
        def f(): return 1
        def around(w, i, a, k): return w(*a, **k)
        wrapped = wrapt.FunctionWrapper(f, around)
        assert wrapt.find_wrapper(wrapped, predicate=lambda item: item is wrapped) is wrapped
        assert wrapt.is_wrapped_by(wrapped, wrapped)
        result = True
    """),
    ("patch/unwrap-restore", """
        import wrapt
        class Box:
            def get(self): return 4
        box = Box()
        original = box.get
        handle = wrapt.wrap_function_wrapper(box, "get", lambda w, i, a, k: 9)
        assert box.get() == 9
        wrapt.unwrap_object(box, "get", handle)
        assert box.get() == 4
        result = original() == 4
    """),
    ("patch/transient", """
        import wrapt
        class Box:
            def get(self): return 4
        box = Box()
        with wrapt.scoped_function_wrapper(box, "get", lambda w, i, a, k: w(*a, **k) + 5):
            assert box.get() == 9
        assert box.get() == 4
        result = True
    """),
    ("patch/resolve-path", """
        import os
        import wrapt
        owner, name, original = wrapt.resolve_path("os", "path.join")
        assert owner is os.path and name == "join" and original is os.path.join
        result = name
    """),
    ("patch/resolve-owner", """
        import wrapt
        class Base:
            value = 3
        class Child(Base):
            pass
        owner, name, original = wrapt.resolve_owner(Child, "value")
        assert owner is Base and name == "value" and original == 3
        result = name
    """),
    ("cache/value-and-info", """
        import wrapt
        calls = []
        @wrapt.lru_cache(maxsize=2)
        def f(x): calls.append(x); return x * 2
        assert f(3) == 6 and f(3) == 6 and calls == [3]
        info = f.cache_info()
        assert info.hits == 1 and info.misses == 1
        result = info.currsize
    """),
    ("cache/clear", """
        import wrapt
        @wrapt.lru_cache()
        def f(x): return x
        f(1); f(1); f.cache_clear()
        assert f.cache_info().hits == 0 and f.cache_info().misses == 0
        result = f(2)
    """),
    ("sync/synchronized", """
        import wrapt
        class Counter:
            def __init__(self): self.value = 0
            @wrapt.synchronized
            def inc(self, amount):
                self.value += amount
                return self.value
        counter = Counter()
        assert counter.inc(2) == 2 and counter.inc(3) == 5
        result = counter.value
    """),
    ("sync/sync-to-async", """
        import asyncio
        import wrapt
        def add(a, b): return a + b
        async_add = wrapt.sync_to_async(add)
        assert asyncio.run(async_add(2, 4)) == 6
        result = True
    """),
    ("sync/async-to-sync", """
        import asyncio
        import wrapt
        async def add(a, b): return a + b
        sync_add = wrapt.async_to_sync(add)
        assert sync_add(2, 4) == 6
        result = True
    """),
    ("sync/markers", """
        import inspect
        import wrapt
        async def coro(): return 1
        marked = wrapt.mark_as_sync(coro)
        assert not inspect.iscoroutinefunction(marked)
        def plain(): return 2
        marked_async = wrapt.mark_as_async(plain)
        assert inspect.iscoroutinefunction(marked_async)
        result = True
    """),
    ("sync/async-lock", """
        import asyncio
        import wrapt
        class Counter:
            def __init__(self): self.value = 0
            @wrapt.synchronized
            async def inc(self):
                old = self.value
                await asyncio.sleep(0)
                self.value = old + 1
                return self.value
        async def main():
            c = Counter()
            values = await asyncio.gather(*(c.inc() for _ in range(5)))
            assert values == [1, 2, 3, 4, 5] and c.value == 5
        asyncio.run(main())
        result = True
    """),
    ("import/lazy-module", """
        import math
        import wrapt
        value = wrapt.lazy_import("math", "sqrt")
        assert value(16) == 4
        assert value.__wrapped__ is math.sqrt
        result = True
    """),
    ("import/notify-hook", """
        import types
        import wrapt
        seen = []
        module = types.ModuleType("synthetic_wrapt_module")
        wrapt.register_post_import_hook(lambda m: seen.append(m.__name__), module.__name__)
        wrapt.notify_module_loaded(module)
        assert seen == [module.__name__]
        result = seen
    """),
    ("errors/missing-wrapper", """
        import wrapt
        from wrapt.exceptions import WrapperNotFoundError
        def f(): return 1
        try:
            wrapt.unwrap_object(f, "missing", object())
        except (WrapperNotFoundError, AttributeError):
            result = True
        else:
            raise AssertionError("missing wrapper did not fail")
    """),
)


def main() -> None:
    leaves = [leaf(leaf_id, source) for leaf_id, source in SCENARIOS]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys


def _type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def compose_case():
    from jaraco.functools import compose

    return {
        "values": [
            compose(lambda x: x + 1, lambda x: x * 2)(3),
            compose(lambda x: x + 1, lambda x, y: x + y)(2, 3),
        ]
    }


def compose_empty_case():
    from jaraco.functools import compose

    try:
        compose()
    except Exception as exc:
        failure = [_type_name(exc)]
    return {"failure": failure}


def once_case():
    from jaraco.functools import once

    calls = []

    @once
    def get(value):
        calls.append(value)
        return value * 2

    first = get(2)
    second = get(9)
    del get.saved_result
    third = get(4)
    return {"calls": calls, "values": [first, second, third], "saved": get.saved_result}


def once_reset_case():
    from jaraco.functools import once

    calls = []

    @once
    def get(value):
        calls.append(value)
        return value * 2

    first = get(1)
    second = get(2)
    get.reset()
    third = get(3)
    return {"calls": calls, "values": [first, second, third], "saved": get.saved_result}


def method_cache_case():
    from jaraco.functools import method_cache

    class Counter:
        def __init__(self):
            self.calls = 0

        @method_cache
        def value(self, item):
            self.calls += 1
            return item * 10

    first, second = Counter(), Counter()
    values = [first.value(2), first.value(2), second.value(2)]
    return {"calls": [first.calls, second.calls], "values": values}


def method_cache_clear_case():
    from jaraco.functools import method_cache

    class Counter:
        def __init__(self):
            self.calls = 0

        @method_cache
        def value(self, item):
            self.calls += 1
            return item * 10

    Counter.value.cache_clear()
    counter = Counter()
    first = counter.value(2)
    second = counter.value(2)
    counter.value.cache_clear()
    third = counter.value(2)
    return {"calls": counter.calls, "values": [first, second, third]}


def special_cache_case():
    from jaraco.functools import method_cache

    class Box:
        def __init__(self):
            self.getitem_calls = 0
            self.getattr_calls = 0

        @method_cache
        def __getitem__(self, key):
            self.getitem_calls += 1
            return key

        @method_cache
        def __getattr__(self, name):
            self.getattr_calls += 1
            return name

    box = Box()
    values = [box[3], box[3], box.answer, box.answer]
    return {"calls": [box.getitem_calls, box.getattr_calls], "values": values}


def decorators_case():
    from jaraco.functools import apply, passthrough, result_invoke

    events = []

    @apply(str.upper)
    def text():
        "kept"
        return "hello"

    @result_invoke(events.append)
    def number():
        return 7

    kept = passthrough(events.append)("value")
    return {
        "apply": text(),
        "doc": text.__doc__,
        "invoke": number(),
        "events": events,
        "passthrough": kept,
    }


def invoke_case():
    from jaraco.functools import invoke

    events = []

    def action():
        events.append("called")

    returned = invoke(action)
    return {"events": events, "same": returned is action, "count": len(events)}


def method_caller_case():
    import warnings

    from jaraco.functools import method_caller

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        result = method_caller("upper")("hello")
    warning = recorded[0]
    return {
        "result": result,
        "warning_category": warning.category.__name__,
        "warning_message": str(warning.message),
    }


def throttler_case():
    from jaraco.functools import Throttler

    wrapped = Throttler(lambda value: value + 1, float("inf"))
    wrapped_again = Throttler(wrapped, 4)
    wrapped.reset()
    return {
        "value": wrapped(2),
        "func_unwrapped": wrapped_again.func is wrapped.func,
        "rate": wrapped_again.max_rate,
        "last_called": wrapped.last_called > 0,
    }


def throttler_descriptor_case():
    from jaraco.functools import Throttler

    class Echo:
        @Throttler
        def value(self, item):
            return item

    result = Echo().value("ok")
    descriptor = Echo.__dict__["value"]
    return {"value": result, "last_called": descriptor.last_called > 0}


def first_invoke_case():
    from jaraco.functools import first_invoke

    events = []
    call = first_invoke(
        lambda: events.append("first"), lambda value: (events.append(value), value)[1]
    )
    return {"value": call("second"), "events": events}


def retry_call_case():
    from jaraco.functools import retry_call

    attempts = [0]
    cleanup = []

    def action():
        attempts[0] += 1
        if attempts[0] < 3:
            raise ValueError("try again")
        return "ok"

    result = retry_call(
        action, cleanup=lambda: cleanup.append(attempts[0]), retries=2, trap=ValueError
    )
    return {"attempts": attempts[0], "cleanup": cleanup, "result": result}


def retry_failure_case():
    from jaraco.functools import retry_call

    attempts = [0]

    def action():
        attempts[0] += 1
        raise KeyError("bad")

    try:
        retry_call(action, retries=2, trap=KeyError)
    except Exception as exc:
        failure = [_type_name(exc), str(exc), attempts[0]]
    return {"failure": failure}


def retry_infinite_case():
    from jaraco.functools import retry_call

    attempts = [0]
    cleanup = []

    def action():
        attempts[0] += 1
        if attempts[0] < 4:
            raise ValueError("again")
        return "ok"

    result = retry_call(
        action,
        cleanup=lambda: cleanup.append(attempts[0]),
        retries=float("inf"),
        trap=ValueError,
    )
    return {"attempts": attempts[0], "cleanup": cleanup, "result": result}


def retry_defaults_case():
    from jaraco.functools import retry_call

    calls = [0]

    def action():
        calls[0] += 1
        raise ValueError("untrapped")

    try:
        retry_call(action, retries=3)
    except Exception as exc:
        failure = [_type_name(exc), str(exc)]
    return {"calls": calls[0], "failure": failure}


def retry_decorator_case():
    from jaraco.functools import retry

    attempts = [0]

    @retry(retries=1, trap=ValueError)
    def action(value):
        attempts[0] += 1
        if attempts[0] == 1:
            raise ValueError("once")
        return value

    result = action("done")
    return {"attempts": attempts[0], "result": result, "doc": action.__name__}


def print_yielded_case():
    from jaraco.functools import print_yielded

    @print_yielded
    def values():
        yield 2
        yield None
        yield "three"

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        result = values()
    return {"output": output.getvalue().splitlines(), "result": result}


def simple_helpers_case():
    from jaraco.functools import none_as, pass_none, signed

    calls = []
    wrapped = pass_none(calls.append)
    return {
        "none": wrapped(None),
        "value": wrapped("x"),
        "calls": calls,
        "signed": [
            signed("{:.1f}".format)(3.5),
            signed("{:.1f}".format)(-3.5),
            signed("{:.1f}".format)(0),
        ],
        "none_as": [none_as(None, "fallback"), none_as("value", "fallback")],
    }


def assign_params_case():
    from jaraco.functools import assign_params

    def func(required, optional=3):
        return [required, optional]

    assigned = assign_params(func, {"required": 8, "optional": 5, "ignored": 9})
    return {"value": assigned(), "partial_name": assigned.func.__name__}


def assign_missing_case():
    from jaraco.functools import assign_params

    def func(required):
        return required

    assigned = assign_params(func, {"ignored": 1})
    try:
        assigned()
    except Exception as exc:
        failure = [_type_name(exc)]
    return {"failure": failure}


def save_method_args_case():
    from jaraco.functools import save_method_args

    class Recorder:
        @save_method_args
        def record(self, *args, **kwargs):
            return len(args) + len(kwargs)

    item = Recorder()
    result = item.record(1, 2, label="x")
    saved = item._saved_record
    return {"result": result, "args": list(saved.args), "kwargs": saved.kwargs}


def except_replace_case():
    from jaraco.functools import except_

    safe = except_(ValueError, replace=0)(int)
    return {"invalid": safe("bad"), "valid": safe("7")}


def except_use_case():
    from jaraco.functools import except_

    safe = except_(ValueError, use="args[0]")(int)
    return {"invalid": safe("bad"), "valid": safe("7")}


def except_untrapped_case():
    from jaraco.functools import except_

    @except_(ValueError, replace=0)
    def fail():
        raise KeyError("nope")

    try:
        fail()
    except Exception as exc:
        failure = [_type_name(exc), str(exc)]
    return {"failure": failure}


def identity_case():
    from jaraco.functools import identity

    value = object()
    return {"same": identity(value) is value, "text": identity("x")}


def bypass_when_case():
    from jaraco.functools import bypass_when

    enabled = []

    @bypass_when(enabled)
    def double(value):
        return value * 2

    before = double(3)
    enabled.append(True)
    after = double(3)
    return {"before": before, "after": after}


def bypass_callable_case():
    from jaraco.functools import bypass_when

    state = {"enabled": False}

    @bypass_when(lambda: state["enabled"])
    def double(value):
        return value * 2

    before = double(4)
    state["enabled"] = True
    after = double(4)
    return {"before": before, "after": after}


def bypass_unless_case():
    from jaraco.functools import bypass_unless

    enabled = [True]

    @bypass_unless(enabled)
    def double(value):
        return value * 2

    first = double(3)
    enabled.clear()
    second = double(3)
    return {"first": first, "second": second}


def splat_case():
    from jaraco.functools import splat

    def join(left, right):
        return f"{left}:{right}"

    return {"tuple": splat(join)(("a", "b")), "mapping": splat(join)({"left": "c", "right": "d"})}


def chainable_case():
    from jaraco.functools import chainable

    class Builder:
        def __init__(self):
            self.values = []

        @chainable
        def add(self, value):
            self.values.append(value)

    builder = Builder()
    returned = builder.add(1).add(2)
    return {"same": returned is builder, "values": builder.values}


def chainable_error_case():
    from jaraco.functools import chainable

    class Bad:
        @chainable
        def add(self):
            return 1

    try:
        Bad().add()
    except Exception as exc:
        failure = [_type_name(exc), str(exc)]
    return {"failure": failure}


def noop_case():
    from jaraco.functools import noop

    return {"value": noop(1, 2, label="x")}


def metadata_case():
    from jaraco.functools import apply, once, retry

    @apply(str.strip)
    @once
    @retry()
    def sample(value):
        "sample documentation"
        return value

    return {"name": sample.__name__, "doc": sample.__doc__}


CASES = {
    "compose": compose_case,
    "compose-empty": compose_empty_case,
    "once": once_case,
    "once-reset": once_reset_case,
    "method-cache": method_cache_case,
    "method-cache-clear": method_cache_clear_case,
    "special-cache": special_cache_case,
    "decorators": decorators_case,
    "invoke": invoke_case,
    "method-caller": method_caller_case,
    "throttler": throttler_case,
    "throttler-descriptor": throttler_descriptor_case,
    "first-invoke": first_invoke_case,
    "retry-call": retry_call_case,
    "retry-failure": retry_failure_case,
    "retry-infinite": retry_infinite_case,
    "retry-defaults": retry_defaults_case,
    "retry-decorator": retry_decorator_case,
    "print-yielded": print_yielded_case,
    "simple-helpers": simple_helpers_case,
    "assign-params": assign_params_case,
    "assign-missing": assign_missing_case,
    "save-method-args": save_method_args_case,
    "except-replace": except_replace_case,
    "except-use": except_use_case,
    "except-untrapped": except_untrapped_case,
    "identity": identity_case,
    "bypass-when": bypass_when_case,
    "bypass-callable": bypass_callable_case,
    "bypass-unless": bypass_unless_case,
    "splat": splat_case,
    "chainable": chainable_case,
    "chainable-error": chainable_error_case,
    "noop": noop_case,
    "metadata": metadata_case,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True, choices=sorted(CASES))
    args = parser.parse_args()
    sys.path.insert(0, args.candidate_site)
    dependency_site = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    if dependency_site:
        sys.path.insert(1, dependency_site)
    try:
        value = CASES[args.scenario]()
        print(json.dumps({"ok": True, "value": value}, sort_keys=True, separators=(",", ":")))
    except BaseException as exc:
        print(
            json.dumps(
                {"ok": False, "exception_type": _type_name(exc), "exception_message": str(exc)},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

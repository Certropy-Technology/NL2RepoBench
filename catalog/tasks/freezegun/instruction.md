# Project Description

Build `freezegun` 1.5.5, a Python library for tests that temporarily replaces
the standard date, datetime, and time views with values controlled by a
`freeze_time` object. The implementation must be installable from an empty
workspace and must restore all patched standard-library objects when a freeze
ends.

The assessed contract is intentionally bounded to deterministic freezing,
manual movement, timezone offsets, and synchronous function decoration. It
does not require real-time ticking, asyncio integration, ignore-list
configuration, framework plugins, static typing parity, or the upstream test
suite.

# Supports

- Python 3.12 on Debian 13, installed as the distribution `freezegun==1.5.5`.
- The package must expose `freeze_time` from `freezegun` and report
  `freezegun.__version__ == "1.5.5"`.
- Runtime date-string parsing may use the preinstalled
  `python-dateutil==2.9.0.post0`; `six==1.17.0`, `setuptools==80.10.2`, and
  `wheel==0.45.1` are also preinstalled.
- Verification runs without network access. Do not fetch source code or
  dependencies at runtime.
- Keep all implementation code in the submitted repository. The project must
  support an isolated non-editable installation without requiring Git.

# API Usage Guide

## `freezegun.freeze_time`

```python
freeze_time(
    time_to_freeze=None,
    tz_offset=0,
    ignore=None,
    tick=False,
    as_arg=False,
    as_kwarg="",
    auto_tick_seconds=0,
    real_asyncio=False,
)
```

Return an object that is both a context manager and a decorator.

`time_to_freeze` accepts a date string understood by `python-dateutil`, a
`datetime.date`, or a `datetime.datetime`. Dates freeze at midnight. Unsupported
values raise `TypeError`. Within an active freeze:

- `datetime.datetime.now()` and `datetime.datetime.utcnow()` return the frozen
  instant, with `now()` shifted by `tz_offset` and `utcnow()` remaining at the
  unshifted instant.
- `datetime.date.today()` returns the date of the shifted local value.
- `time.time()` and `time.time_ns()` return the Unix timestamp of the unshifted
  frozen instant.
- `time.gmtime()`, `time.localtime()`, and `time.strftime()` observe the frozen
  value. The required environment uses UTC as its system timezone.
- Ordinary date/datetime construction, arithmetic, `combine`, and
  `isinstance` compatibility continue to work.
- `datetime.datetime.now(tz)` returns an aware value representing the frozen
  instant in the supplied fixed-offset `datetime.tzinfo`.

`tz_offset` accepts either a numeric number of hours or a
`datetime.timedelta`. It affects local `now()` and `today()` but not `utcnow()`
or the Unix timestamp.

The returned context value is a callable time factory with:

```python
factory() -> datetime.datetime
factory.tick(delta=1) -> datetime.datetime
factory.move_to(target_datetime) -> None
```

`tick` advances the frozen instant and returns its new value. `delta` accepts
numeric seconds or a `datetime.timedelta`, including fractional seconds and
date-boundary crossings. `move_to` accepts the same string, date, and datetime
forms as `freeze_time`; subsequent date, datetime, and time calls immediately
observe the target.

When `auto_tick_seconds` is nonzero, each read from the frozen clock advances
the value by exactly that many seconds. Real elapsed-time behavior from
`tick=True` is outside this contract.

The object also provides explicit lifecycle methods:

```python
freezer = freeze_time("2030-01-02 03:04:05")
factory = freezer.start()
freezer.stop()
```

Nested freezes restore the enclosing frozen value when the inner context
exits. Exiting a context or calling `stop()` restores the exact date, datetime,
and time callables that were present before activation.

As a synchronous function decorator, `freeze_time(...)` preserves the wrapped
function metadata and arguments. With `as_arg=True`, the active factory is
inserted as the first positional argument. With a nonempty `as_kwarg`, it is
injected under that keyword name. The factory passed to a decorated function
supports `tick` and `move_to` as described above.

# Implementation Notes

- Freezing is process-global while active. Use a stack so nested contexts and
  explicit `start()`/`stop()` restore state in last-in, first-out order.
- Patch already imported references consistently, not only future imports of
  `datetime` or `time`.
- Preserve microseconds exactly for fixed values, timestamps, `tick`, and
  `move_to`.
- Context and decorator cleanup must run even when user code raises.
- All assessed ticking is driven by explicit calls or deterministic
  `auto_tick_seconds`; no assertion depends on the machine wall clock.

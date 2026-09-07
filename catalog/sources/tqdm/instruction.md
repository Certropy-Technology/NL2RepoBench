## Project Description

Build `tqdm`, a Python library for adding progress state to ordinary iterables
and rendering that state as text. Its users are programs that process a finite
sequence, stream, or manually counted workload and need to expose current
count, total, rate, and elapsed interval without changing the values produced
by the workload.

The candidate must provide an installable package named `tqdm`. It must expose
the core class from both `tqdm` and `tqdm.std`, the `trange` convenience
function, deterministic numeric and meter-formatting helpers, display-width
helpers, and iterator wrappers in `tqdm.contrib`. An iterable wrapper must be
lazy, preserve values and order, and maintain the documented counter state. A
manual bar must support `update`, `reset`, and `close`.

This task covers text-oriented progress state and formatting only. Terminal
refresh cadence, TTY detection, terminal dimensions, cursor movement, current
wall-clock values, and exact output produced by a live refresh are outside the
deterministic contract. Jupyter widgets, tkinter, rich, pandas, dask, keras,
asyncio, multiprocessing, notifications, and network services are out of
scope; importing the core package must not require those optional libraries.

## Natural Language Instruction

Create the project from an empty workspace and implement these capabilities:

1. Make `tqdm` a normal Python package with the root exports documented below.
   `from tqdm import tqdm, trange` and `from tqdm.std import tqdm` must work,
   and the two class objects must be identical.
2. Implement one progress-bar class that accepts either an iterable or a
   manual `total`. It must infer a total from a sized iterable when possible,
   defer iteration until the caller asks for values, preserve iteration order,
   and expose `n` and `total` state.
3. Implement deterministic format helpers. Explicit `elapsed`, `rate`,
   `prefix`, `ascii`, `unit`, `ncols`, and `bar_format` arguments must be
   reflected by `format_meter`; the numeric helpers must use the forms below.
4. Implement `tqdm.utils.disp_len` and `disp_trim` for text containing ANSI
   control sequences, plus lazy `tenumerate`, `tzip`, and `tmap` in
   `tqdm.contrib`.

Do not add a second incompatible progress class, change values or ordering of
wrapped iterables, consume a generator during construction, or make the
documented deterministic examples depend on sleeping or terminal state.

## Supports

- Runtime: CPython 3.12 on 64-bit Debian 12 Linux.
- Package manager and build: `pip` with the setuptools build backend. The
  project must contain `pyproject.toml` and install with
  `python -m pip install .` or `python -m pip install -e .` from its root.
- Build dependency: setuptools is installed by the image build from the
  locked environment. The package has no required runtime dependency beyond
  the Python standard library.
- Runtime network: no network access is available. The agent, candidate,
  verifier, Oracle, and controls must not contact GitHub, PyPI, DNS, or any
  external service while running. Installation and imports must not fetch
  packages; optional integrations must remain optional imports.
- Harness setup: installation is run from `workspace/`; subsequent imports
  happen in a separate Python process. Tests provide `io.StringIO` streams and
  `disable=True` when they need output-independent behavior.

### Project Directory Structure

The minimum public structure is:

```text
workspace/
├── pyproject.toml
└── tqdm/
    ├── __init__.py
    ├── std.py
    ├── utils.py
    └── contrib/
        └── __init__.py
```

`tqdm/__init__.py` is the package entry point and must export `tqdm` and
`trange` (and may expose version metadata). `tqdm/std.py` owns the core class
and static formatting methods. `tqdm/utils.py` owns the two display-width
helpers. `tqdm/contrib/__init__.py` owns the three finite-input iterator
helpers. Extra optional modules are permitted only when they do not alter this
layout or require unavailable dependencies. No CLI entry point is part of
this bounded contract; `python -m tqdm` need not be implemented.

## API Usage Guide

The following is the public deterministic API for this task. Signatures use
Python notation and include defaults. Other names an upstream release may
contain are not required unless needed to implement these behaviors.

### Package exports: `tqdm` and `trange`

Import the core class and range shortcut as follows:

```python
from tqdm import tqdm, trange
from tqdm.std import tqdm as std_tqdm

assert tqdm is std_tqdm
list(trange(3, disable=True))       # [0, 1, 2]
```

`tqdm` is a class and `trange` is the callable `trange(*args, **kwargs)`
described below. Importing these names must not initialize Jupyter, GUI,
network, or data-science integrations. A missing optional dependency must not
prevent these imports.

### `tqdm.std.tqdm.__init__`

Construct the class with this shape:

```python
tqdm(
    iterable=None, desc=None, total=None, leave=True, file=None,
    ncols=None, mininterval=0.1, maxinterval=10.0, miniters=None,
    ascii=None, disable=False, unit='it', unit_scale=False,
    dynamic_ncols=False, smoothing=0.3, bar_format=None, initial=0,
    position=None, postfix=None, unit_divisor=1000, write_bytes=False,
    lock_args=None, nrows=None, colour=None, delay=0.0, gui=False,
    **kwargs
)
```

`iterable` may be any iterable, including a one-shot generator. If omitted,
the object is a manually updated bar. `total` is an integer or float count, or
`None`; when omitted and the iterable implements `__len__`, that length becomes
`total`. `initial` sets the starting `n`. `file` is a text-like object with
`write` and optionally `flush`; its default is standard error. `disable=True`
suppresses all progress output and is the required mode for output-independent
examples. The remaining formatting and refresh parameters are accepted with
the defaults shown and must not change values yielded by iteration.

Construction stores the iterable without consuming it. It creates no required
files, network connections, or external process. A non-`None` unknown keyword
is invalid and must raise the package's argument error (`TqdmKeyError` in
implementations that expose it), except for explicitly supported compatibility
keywords. A non-iterable supplied as `iterable` may fail when iteration begins.

```python
bar = tqdm(["read", "write"], disable=True)
assert bar.total == 2
assert list(bar) == ["read", "write"]
```

The empty and manual forms are both valid:

```python
from io import StringIO

empty = tqdm([], disable=True)
assert list(empty) == [] and empty.total == 0
manual = tqdm(total=5, file=StringIO(), mininterval=10**9, miniters=1)
```

### `tqdm.std.tqdm.__iter__`

The instance is itself iterable and has callable shape
`__iter__(self) -> Iterator[object]`. Iteration is lazy: construction does not
call `iter(iterable)` or consume a generator. Each `next()` yields the original
object unchanged and preserves source order. For an enabled bar, the internal
counter advances as values are consumed and the bar is closed when normal
iteration finishes or exits through an exception. For a disabled bar, values
are passed through and no output is written; the disabled fast path does not
advance `n` beyond its initial value.

```python
seen = []

def source():
    seen.append("started")
    yield from (4, 5)

bar = tqdm(source(), disable=True)
assert seen == []
assert next(iter(bar)) == 4
assert seen == ["started"]
```

An empty iterable yields no values. If iteration raises, the original
exception propagates after normal cleanup; it must not be silently converted
into a progress result.

### `tqdm.std.tqdm.__len__`

`__len__(self) -> int | float` returns the iterable length when the wrapped
object is sized, or the configured `total` for a manual bar. Objects with a
`shape[0]` or `__length_hint__` may supply that size. An unsized iterable with
no total has no meaningful length and may raise `TypeError` rather than
inventing a value.

```python
assert len(tqdm((x for x in range(3)), total=3, disable=True)) == 3
assert len(tqdm([10, 20], disable=True)) == 2
```

### `tqdm.std.tqdm.update`

Use `update(self, n=1) -> bool | None` to add a numeric delta to the manual
counter. The default increments by one; negative and fractional deltas are
accepted when the caller uses a numeric counter. With an enabled bar, a call
may trigger a refresh according to `mininterval` and `miniters`, returning
`True` when it does and otherwise `None`. That timing-dependent return value
and emitted control text are not deterministic requirements. With
`disable=True`, the call is a no-op and does not write output.

```python
bar = tqdm(total=3, file=StringIO(), mininterval=10**9, miniters=1)
bar.update(2)
assert bar.n == 2
bar.update(-1)
assert bar.n == 1
```

The argument must support the numeric comparisons and addition required by
the counter; unrelated objects raise their normal `TypeError`. `update` does
not consume or modify an iterable.

### `tqdm.std.tqdm.reset`

`reset(self, total=None) -> None` starts the counter state over at zero. If
`total` is supplied, it replaces the current total; when omitted, the
existing total remains unchanged. The enabled-bar timer and rate bookkeeping
are also restarted, while disabled bars still receive the deterministic
counter and total reset.

```python
bar = tqdm(total=5, file=StringIO(), mininterval=10**9, miniters=1)
bar.update(2)
bar.reset(total=3)
assert [bar.n, bar.total] == [0, 3]
bar.update(1)
assert [bar.n, bar.total] == [1, 3]
```

An empty reset, `reset()`, is valid. A total of `float('inf')` is treated as
an unknown total for meter purposes, as in the constructor.

### `tqdm.std.tqdm.close`

`close(self) -> None` finalizes a bar and marks it disabled. It is safe to call
more than once, including after normal iteration or partial iteration. It may
perform stream cleanup or a final refresh for an enabled bar, but must not
raise merely because it was already closed. It does not close a file object
supplied by the caller.

```python
bar = tqdm(total=1, file=StringIO())
bar.close()
bar.close()
assert bar.disable is True
```

### Context-manager methods

The class provides `__enter__(self) -> tqdm` and
`__exit__(self, exc_type, exc_value, traceback) -> None`. Entering returns the
same object. Exiting calls `close`, including when the body raises, and the
body's exception is not suppressed.

```python
with tqdm(range(2), disable=True) as bar:
    values = list(bar)
assert values == [0, 1]
assert bar.disable is True
```

### `tqdm.std.tqdm.format_sizeof`

`format_sizeof(num, suffix='', divisor=1000) -> str` is a static method that
formats a numeric magnitude using compact SI-style units (`k`, `M`, `G`, and
so on) and appends `suffix` after the unit. `divisor` controls the step between
units. Values below the first unit retain appropriate decimal places.

```python
assert tqdm.format_sizeof(1024) == "1.02k"
assert tqdm.format_sizeof(1024, suffix="B") == "1.02kB"
```

Zero, negative, and non-finite numeric values are accepted according to normal
numeric formatting; callers must not pass a zero divisor. Non-numeric values
or a zero divisor raise the underlying arithmetic/type exception.

### `tqdm.std.tqdm.format_interval`

`format_interval(t) -> str` converts seconds to a clock string in `[H:]MM:SS`
form. Fractional seconds are truncated to whole seconds. Hours are included
only when nonzero; negative values follow Python's integer `divmod` result.

```python
assert tqdm.format_interval(3661) == "1:01:01"
assert tqdm.format_interval(0) == "00:00"
assert tqdm.format_interval(-1) == "-1:59:59"
```

Values that are not numeric enough for comparison and integer conversion raise
the normal exception.

### `tqdm.std.tqdm.format_num`

`format_num(n) -> str` returns a compact representation of an integer, float,
or other numeric value. It uses a short three-significant-digit form when that
form is shorter than the original string representation, while retaining the
ordinary representation when shortening would not be more compact.

```python
assert tqdm.format_num(12.3456) == "12.3"
assert tqdm.format_num(0) == "0"
```

The return type is always `str`. Values that cannot be formatted with numeric
formatting raise their normal formatting exception.

### `tqdm.std.tqdm.format_meter`

`format_meter(n, total, elapsed, ncols=None, prefix='', ascii=False,
unit='it', unit_scale=False, rate=None, bar_format=None, postfix=None,
unit_divisor=1000, initial=0, colour=None, **extra_kwargs) -> str` is a static
method that renders a meter from explicit state. `n` is completed work,
`total` is expected work or `None`, and `elapsed` is seconds. `rate` is an
optional explicit iterations-per-second override; supplying it and a fixed
`elapsed` makes the result independent of the clock. `prefix` supplies the
description, `unit` labels counts, `ascii` selects ASCII bar characters,
`unit_scale` and `unit_divisor` scale numeric values, and `postfix` adds
trailing statistics. `ncols` constrains the complete line; zero suppresses the
bar.

`bar_format` may reference `desc`, `bar`, `n_fmt`, `total_fmt`, `elapsed`,
`rate_fmt`, `percentage`, `unit`, `postfix`, and corresponding raw values.
The function returns text and has no stream or file side effect. With
`total=None`, it omits percentage and ETA information that cannot be computed.
Invalid format fields or incompatible numeric values raise the normal
formatting exception.

```python
meter = tqdm.format_meter(
    3, 10, 2.0, rate=1.5, prefix="run", ascii=True, unit="item",
    bar_format="{desc}|{bar}|{n_fmt}/{total_fmt}|{elapsed}|{rate_fmt}",
)
assert meter == "run|###       |3/10|00:02| 1.50item/s"
```

The width-constrained and unknown-total cases are valid:

```python
assert tqdm.format_meter(0, None, 0.0, prefix="idle", ascii=True).startswith("idle")
short = tqdm.format_meter(2, 4, 0.0, ncols=20, rate=4.0,
                          prefix="x", ascii=True, unit="it")
assert short == "x:  50%|5| 2/4 [00:0"
```

### `trange`

`trange(*args, **kwargs) -> tqdm` is exactly the convenience form
`tqdm(range(*args), **kwargs)`. It accepts the same keyword options as the
class and follows Python `range` rules for one, two, or three positional
arguments.

```python
assert list(trange(3, disable=True)) == [0, 1, 2]
assert list(trange(2, 0, -1, disable=True)) == [2, 1]
```

As with `range`, an empty interval yields an empty iterator, and invalid
argument counts or non-integer range arguments raise Python's normal
`TypeError`.

### `tqdm.utils.disp_len`

`disp_len(data) -> int` returns the terminal display width of a string. ANSI
control sequences matching the package's supported escape-sequence form do not
contribute width; ordinary characters count as one and East Asian wide
characters count as two. The input is text, not bytes, and the function has no
side effect.

```python
assert disp_len("a\x1b[31mred\x1b[0m") == 4
assert disp_len("abc") == 3
```

An empty string has width zero. Non-string input raises the regular type error
from the text/regular-expression operation rather than being silently coerced.

### `tqdm.utils.disp_trim`

`disp_trim(data, length) -> str` trims text to the requested display width while
preserving supported ANSI sequences when present. For plain text it returns
the leading slice; for coloured text it avoids counting escape bytes and adds
an ANSI reset when trimming leaves an active sequence. It does not write to a
stream.

```python
assert disp_trim("abcdef", 4) == "abcd"
coloured = "a\x1b[31mred\x1b[0m"
trimmed = disp_trim(coloured, 2)
assert disp_len(trimmed) <= 2 or trimmed.endswith("\x1b[0m")
```

An empty input returns an empty string. A non-negative integer `length` is the
supported domain; other values produce the normal comparison or slicing
error.

### `tqdm.contrib.tenumerate`

`tenumerate(iterable, start=0, total=None,
tqdm_class=tqdm.auto.tqdm, **tqdm_kwargs) -> Iterator[tuple[int, object]]`
is the progress-aware equivalent of `enumerate`. It yields `(index, value)`
pairs in source order, beginning at `start`. `total` and keyword arguments are
passed to the selected progress class. `disable=True` makes finite local
examples silent and deterministic.

```python
assert list(tenumerate("ab", start=2, disable=True)) == [(2, "a"), (3, "b")]
assert list(tenumerate([], disable=True)) == []
```

The helper is lazy and does not evaluate a generator until iteration. It uses
normal `enumerate` behavior for invalid `start`; an exception from the
underlying iterable propagates unchanged.

### `tqdm.contrib.tzip`

`tzip(iter1, *iter2plus, **tqdm_kwargs) -> Iterator[tuple[object, ...]]`
is the progress-aware equivalent of `zip`. It yields tuples in normal `zip`
order and stops when the first exhausted input is reached. Progress keyword
arguments apply to the first iterable's bar; `tqdm_class` may select a class.

```python
assert list(tzip([1, 2], [3, 4], disable=True)) == [(1, 3), (2, 4)]
assert list(tzip([], [1], disable=True)) == []
```

Inputs are consumed lazily. With one iterable it yields one-element tuples;
with no second iterable it still follows `zip` semantics. Normal iterator
errors propagate.

### `tqdm.contrib.tmap`

`tmap(function, *sequences, **tqdm_kwargs) -> Iterator[object]` is the
progress-aware equivalent of `map`. It applies `function` lazily to each tuple
of corresponding sequence values and yields results in normal `map` order.
Progress keyword arguments are forwarded to `tzip`.

```python
assert list(tmap(lambda value: value * 2, [1, 2, 3], disable=True)) == [2, 4, 6]
assert list(tmap(str, [], disable=True)) == []
```

The function is not called until the result iterator is consumed. Python's
normal `TypeError` for a missing function or incompatible callable propagates,
as does an exception raised by the callable or input sequence.

## Implementation Notes

Keep the implementation split along the directory boundaries above, but share
one `tqdm.std.tqdm` class between all supported imports. Root imports must be
usable in a clean Python process with only the standard library and build
dependency available. Do not vendor third-party packages or require internet
during installation, import, or use.

State transitions must be deterministic wherever the caller supplies inputs:
construction records `iterable`, `total`, and `initial`; iteration preserves
values and order; `update` changes `n` only for an enabled bar; `reset` sets
`n` to zero; and `close` is idempotent. A disabled iterable remains lazy and
silent, including when its source is a generator. Context-manager exit closes
the bar without swallowing an exception from the managed block.

Formatting code may use current time only for live refresh bookkeeping. Static
formatting examples must derive output from explicit arguments, especially
`elapsed` and `rate`. Do not introduce behavior based on the host TTY,
terminal-width discovery, sleep duration, cursor escapes, or scheduling.
`disp_len` and `disp_trim` must treat ANSI bytes as control sequences rather
than visible characters and must not corrupt a reset sequence when trimming
coloured text.

The three `contrib` helpers preserve Python iterator semantics and avoid
eagerly materializing finite or one-shot inputs. They may accept a replacement
`tqdm_class` through their documented keyword path, but default local use must
work without optional integrations. Empty iterables, unknown totals, manual
bars, Unicode text, negative intervals, and repeated `close()` calls are valid
cases and must not be replaced with invented sentinel values.

The following small checks summarize the required composition without
prescribing an algorithm:

```python
from io import StringIO
from tqdm import tqdm

bar = tqdm(total=3, file=StringIO(), mininterval=10**9, miniters=1)
bar.update(1)
bar.reset()
assert (bar.n, bar.total) == (0, 3)
bar.close()
bar.close()
```

```python
from tqdm import trange
from tqdm.contrib import tmap, tenumerate, tzip

assert list(trange(0, disable=True)) == []
assert list(tenumerate([], start=7, disable=True)) == []
assert list(tzip([1], [], disable=True)) == []
assert list(tmap(lambda x: x + 1, [1, 2], disable=True)) == [2, 3]
```

```python
from tqdm.utils import disp_len, disp_trim

text = "\x1b[32mready\x1b[0m"
assert disp_len(text) == 5
assert disp_trim("abcdef", 0) == ""
```

```python
from tqdm import tqdm

assert tqdm.format_sizeof(1024) == "1.02k"
assert tqdm.format_interval(-1) == "-1:59:59"
assert tqdm.format_num(12.3456) == "12.3"
```

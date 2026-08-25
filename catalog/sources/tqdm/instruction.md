# Project Description

Build the `tqdm` Python package from an empty workspace. It is a reusable
progress-bar and iterator toolkit: callers can wrap an iterable, update a
manual counter, reset a bar, and format progress text for a text stream.

The task evaluates deterministic library behavior. Wall-clock refresh cadence,
terminal cursor movement, terminal width detection, and terminal escape output
are outside the contract because they are inherently environment-dependent.

# Supports

- Python 3.12 on 64-bit Debian Linux.
- An installable project named `tqdm` with a normal `pyproject.toml`.
- No runtime network access or external services.
- Core implementation in `tqdm.std`, with the public `tqdm` and `trange`
  exports available from the package root.

# API Usage Guide

## Core class and fixed formatting

`from tqdm import tqdm, trange` and `from tqdm.std import tqdm as std_tqdm`
must refer to the core progress class. The class accepts an iterable or a
manual `total`, and supports `disable=True` for deterministic, silent use.
When disabled, wrapping an iterable must preserve its values and update the
bar's `n` counter without writing progress output.

The following static methods are part of the contract:

- `tqdm.format_sizeof(num, suffix="", divisor=1000)` returns a compact SI
  representation.
- `tqdm.format_interval(seconds)` returns `[H:]MM:SS`.
- `tqdm.format_num(number)` returns the compact numeric representation used by
  the progress meter.
- `tqdm.format_meter(n, total, elapsed, ...)` returns a text meter. Calls with
  explicit `elapsed` and `rate` are deterministic and must honor `prefix`,
  `ascii`, `unit`, `ncols`, and a custom `bar_format`.

Do not make test-visible behavior depend on `time.monotonic()`, terminal width,
or whether a stream is a TTY. A disabled bar may still maintain counters and
state, but tests will not assert terminal refresh timing.

## Iteration and state

Constructing `tqdm(iterable, disable=True)` must be lazy: it must not consume
the iterable until iteration begins. Iteration yields each original value in
order and increments `n`. `len(bar)` uses the iterable length when one is
available. `update(delta)` changes `n` by the requested delta. `reset(total)`
sets `n` to zero and optionally replaces `total`; a subsequent update uses the
new state. `close()` is safe to call more than once.

The class must support context-manager use and `trange(n, **kwargs)` must be a
convenient equivalent of `tqdm(range(n), **kwargs)`.

## Deterministic utility helpers

Expose the standard utility functions needed by callers:

- `tqdm.utils.disp_len(text)` counts visible characters while ignoring ANSI
  escape sequences.
- `tqdm.utils.disp_trim(text, length)` trims text to a display width.
- `tqdm.contrib.tenumerate`, `tzip`, and `tmap` preserve the normal iterator
  semantics and return the expected values for finite local inputs.

# Implementation Notes

Keep imports local and optional integrations importable without requiring
Jupyter, pandas, dask, rich, GUI toolkits, or notification services. The
verifier only exercises the deterministic core and utility surface above; it
does not require those optional integrations. Do not add tests or verifier
files that alter the candidate's source tree. The package must be installable
from its root without downloading dependencies during the run.

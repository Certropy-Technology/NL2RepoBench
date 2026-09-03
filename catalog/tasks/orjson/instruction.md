# Build `orjson`

Create a complete, installable Python distribution named `orjson` from an
empty workspace. The frozen upstream package is a fast JSON encoder and
decoder with a native implementation, but this task evaluates a deterministic
JSON-safe compatibility contract. A standard-library implementation is
acceptable when every specified observable behavior matches.

## Project Description

`orjson` exposes `dumps` and `loads` for compact UTF-8 JSON bytes. It supports
common Python data types, selected date/time and UUID values, a custom default
callback, formatting options, JSON fragments, and typed exceptions. The
library is local and deterministic: it must not open sockets, read files,
spawn processes, or contact a service during normal API use.

## Supports

- Provide an installable project named `orjson`, version `3.12.0`, supporting
  CPython 3.10 and newer. `pip install .` and editable installation must work
  after the build backend is already available.
- Provide an `orjson` package with `__version__`, `dumps`, `loads`,
  `Fragment`, `JSONDecodeError`, `JSONEncodeError`, all option constants below,
  and `py.typed` package data. `orjson.__all__` must contain exactly the
  documented public names and no private helpers.
- Runtime dependencies must be empty. Use only the Python standard library;
  build metadata may require a pinned setuptools backend.
- `dumps` returns `bytes` encoded as UTF-8 and `loads` accepts `str`, `bytes`,
  `bytearray`, and one-dimensional `memoryview` inputs. Runtime behavior must
  be offline and bounded for ordinary inputs.

## API Usage Guide

### `orjson.dumps`

Import path: `orjson.dumps`

Signature: `dumps(obj, /, default=None, option=None) -> bytes`. `obj` may be a
JSON-compatible scalar, list, tuple, or dictionary. Strings use compact JSON
escaping and UTF-8 output. `None`, booleans, integers, finite floats, strings,
lists, tuples, and dictionaries have their normal JSON meanings. Non-finite
floats serialize as `null`. Unsupported values raise `TypeError` (the exported
`JSONEncodeError` name is a TypeError-compatible public alias) unless
`default` is a callable; the callable receives the unsupported object and its
return value is serialized recursively. Exceptions from `default` propagate
with the normal exception context.

Dictionary keys are strings by default. With `OPT_NON_STR_KEYS`, integer,
float, boolean, `None`, date/time, UUID, and enum keys use the same scalar
conversion rules as values. Unsupported keys raise `TypeError`.

`option` is an integer bit mask or `None`. Implement these constants:
`OPT_APPEND_NEWLINE`, `OPT_INDENT_2`, `OPT_NAIVE_UTC`,
`OPT_NON_STR_KEYS`, `OPT_OMIT_MICROSECONDS`,
`OPT_PASSTHROUGH_DATACLASS`, `OPT_PASSTHROUGH_DATETIME`,
`OPT_PASSTHROUGH_SUBCLASS`, `OPT_SERIALIZE_DATACLASS`,
`OPT_SERIALIZE_NUMPY`, `OPT_SERIALIZE_UUID`, `OPT_SORT_KEYS`,
`OPT_STRICT_INTEGER`, and `OPT_UTC_Z`. `OPT_INDENT_2` uses two-space
  indentation, `OPT_SORT_KEYS` sorts dictionary keys by their UTF-8 encoded
  representation, and `OPT_APPEND_NEWLINE` appends one byte newline after the
  complete document. `OPT_STRICT_INTEGER` rejects integers outside the safe
JavaScript range `[-2**53, 2**53]`. Unsupported option values raise
  `TypeError`.

Naive `datetime.datetime` values use ISO-8601 without an offset unless
`OPT_NAIVE_UTC` is set, in which case `+00:00` is used. Aware datetimes retain
their offset. `OPT_UTC_Z` uses `Z` for UTC offsets. Dates and times use the
corresponding ISO-8601 forms, and `OPT_OMIT_MICROSECONDS` removes fractional
seconds. UUID values serialize as their canonical string when
`OPT_SERIALIZE_UUID` is set. Dataclass instances serialize their fields when
`OPT_SERIALIZE_DATACLASS` is set; `OPT_PASSTHROUGH_*` sends the value to
`default` instead.

### `orjson.loads`

Import path: `orjson.loads`

Signature: `loads(obj, /) -> object`. Parse one complete JSON document and
return Python `dict`, `list`, scalar, or `None` values. Leading and trailing
JSON whitespace is accepted, but any other trailing bytes, malformed UTF-8,
invalid escapes, NaN/Infinity spellings, and excessive nesting raise
`JSONDecodeError`. Non-bytes-like values raise the same documented decode
exception contract rather than being silently coerced.

### `orjson.Fragment`

Import path: `orjson.Fragment`

Signature: `Fragment(contents: bytes | str)`. A fragment is emitted verbatim
by `dumps` when used as a value. Bytes must be valid UTF-8 JSON fragment bytes;
strings are encoded as UTF-8. The object exposes `contents` and has stable
identity-style representation; it is not a normal JSON scalar.

## Implementation Notes

Keep the public functions positional-only where specified and preserve the
exception contract: `JSONDecodeError` is compatible with `ValueError`, while
`JSONEncodeError` is the exported TypeError-compatible alias used for encoding
failures. Do not silently ignore unsupported
values or callback errors. Preserve dictionary insertion order unless sorting
was requested, produce compact output by default, and ensure all option masks
compose deterministically. The verifier invokes the package through a separate
child process and does not require private implementation names, SIMD
performance, or the upstream Rust ABI.

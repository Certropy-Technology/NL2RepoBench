# Project Description

Build an installable Python package named `jiter` from an empty workspace. The
upstream project is a fast JSON parser, but this task uses a deterministic
pure-Python adaptation so it can run without a compiler, native library, or
network access during evaluation. Do not copy verifier files, depend on a
preinstalled `jiter`, or add a benchmark-specific server or CLI.

## Supports

- Import the top-level package `jiter` on CPython 3.12 with no runtime
  dependency outside the standard library.
- Implement `jiter.from_json` with the exact positional and keyword-only
  signature described below.
- Implement `jiter.cache_clear`, `jiter.cache_usage`, and the public
  `jiter.LosslessFloat` class.
- Accept JSON bytes and return ordinary Python `dict`, `list`, `str`, `int`,
  `float`, `bool`, or `None` values. Unicode must be decoded correctly.
- Support strict parsing, partial parsing modes, duplicate-key detection,
  non-finite values, decimal floats, and lossless float values.

## API Usage Guide

`jiter.from_json(json_data: bytes, /, *, allow_inf_nan: bool = True,
cache_mode: bool | Literal['all', 'keys', 'none'] = 'all',
partial_mode: bool | Literal['off', 'on', 'trailing-strings'] = False,
catch_duplicate_keys: bool = False,
float_mode: Literal['float', 'decimal', 'lossless-float'] = 'float') -> Any`

The input must be bytes-like JSON text. Leading and trailing JSON whitespace
is accepted. Return values preserve object insertion order. Integers remain
Python `int`; ordinary decimals and exponents become `float`. Invalid JSON,
invalid UTF-8, unsupported option values, incomplete strict input, recursion
overflow, and duplicate keys when requested raise `ValueError` (or
`TypeError` when the option has the wrong Python type). Error text must be
deterministic and include a useful line and column for syntax errors.

`allow_inf_nan=True` accepts `NaN`, `Infinity`, and `-Infinity` as floats;
false rejects them. `float_mode='decimal'` returns `decimal.Decimal` for
decimal/exponent tokens while integers remain `int`. `float_mode='lossless-float'`
returns `LosslessFloat` for decimal/exponent tokens while integers remain `int`.

`cache_mode` accepts `True`/`'all'` to cache keys and values, `False`/`'none'`
to disable caching, or `'keys'` to cache object keys only. `cache_clear()`
resets the process-global cache, and `cache_usage() -> int` reports the number
of cached strings. The exact cache count is observable and deterministic for
the exercised inputs.

`partial_mode=False` and `'off'` require one complete JSON value. `True` and
`'on'` accept an incomplete final container or string and return the complete
prefix, discarding an unfinished final value. `'trailing-strings'` also keeps
an unfinished final string or object string value. Valid UTF-8 prefixes are
handled at a code-point boundary; malformed UTF-8 still raises `ValueError`.

`LosslessFloat(raw: bytes)` validates one decimal/exponent token. It exposes
`as_decimal() -> decimal.Decimal`, `float(value) -> float`, `bytes(value) -> bytes`,
`str(value) -> str`, and `repr(value) -> str` in the form
`LosslessFloat(<token>)`. Invalid tokens raise `ValueError`.

## Implementation Notes

Use only the standard library. A small recursive-descent parser is sufficient;
it must not use `eval`, execute input as Python, contact the network, or rely
on JSON serialization as a substitute for option semantics. Preserve escape
handling, nested arrays/objects, duplicate-key order, and deterministic error
categories. Keep the package installable from a normal `pyproject.toml` or
`setup.py` using the build tools already present in the task image.

The hidden verifier calls the package only through an unprivileged JSON child
process. It checks the public behavior above and does not import candidate code
into the trusted verifier process. Private tests, the upstream archive, and
reference implementation details are not available in the workspace.

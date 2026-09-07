# Project Description

Build an installable pure-Python package named `jiter` from an empty workspace.
It parses UTF-8 JSON bytes and exposes partial parsing, duplicate-key checks,
float modes, lossless numeric values, and a small process-local cache API. The
upstream native/Rust implementation is outside this task; implement the
JSON-safe public contract without a compiler or runtime network.

# Natural Language Instruction

Create the top-level `jiter` package with `from_json`, `cache_clear`,
`cache_usage`, and `LosslessFloat`. Match the positional-only and keyword-only
signature, JSON primitive/container behavior, partial modes, float choices,
duplicate detection, deterministic errors, and lossless conversions. Make the
project installable from a normal `pyproject.toml` or `setup.py` and do not add
the verifier, tests, native code, or a benchmark server.

# Supports or Environment Configuration

- Python 3.12 on Linux; import and distribution name are `jiter`.
- Runtime dependencies are standard-library only. Build with the preinstalled
  `setuptools==80.9.0` closure.
- Install from the repository root without network access. Agent, candidate,
  verifier, Oracle, and controls use no network at run time.
- Input is bytes-like JSON text; output must be ordinary Python values or the
  documented `decimal.Decimal`/`LosslessFloat` numeric objects.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── jiter/
    ├── __init__.py
    └── py.typed
```

# API Usage Guide

```python
from_json(
    json_data: bytes, /, *, allow_inf_nan=True, cache_mode="all",
    partial_mode=False, catch_duplicate_keys=False, float_mode="float",
) -> Any
cache_clear() -> None
cache_usage() -> int
LosslessFloat(json_float: bytes)
```

`from_json` accepts bytes-like UTF-8 JSON with surrounding JSON whitespace.
Objects preserve insertion order and JSON values become `dict`, `list`,
`str`, `int`, `float`, `bool`, or `None`. `allow_inf_nan=True` accepts
`NaN`, `Infinity`, and `-Infinity`; false rejects them. `float_mode="float"`
returns normal floats, `"decimal"` returns `decimal.Decimal` for decimal or
exponent tokens, and `"lossless-float"` returns `LosslessFloat`; integers remain
integers. `catch_duplicate_keys=True` rejects duplicate object keys.

`partial_mode=False`/`"off"` requires one complete value. `True`/`"on"`
accepts an incomplete final container or string and returns the complete prefix;
`"trailing-strings"` additionally keeps an unfinished final string value.
`cache_mode=True`/`"all"`, false/`"none"`, and `"keys"` control process-local
key/value caching. `cache_clear` resets it and `cache_usage` reports its count.

`LosslessFloat(raw: bytes)` validates one decimal/exponent token. Its methods
are `as_decimal() -> decimal.Decimal`, `__float__() -> float`,
`__bytes__() -> bytes`, `__str__() -> str`, and `__repr__() -> str`; repr has
the form `LosslessFloat(<token>)`.

# Implementation Notes

Use a deterministic parser rather than `eval`. Decode UTF-8 strictly, retain
object insertion order, and report invalid option types separately from invalid
JSON. Cache state is process-local and must not depend on time, hash order, or
environment. The installed package must work without the upstream checkout.

# Examples

```python
from jiter import from_json, LosslessFloat

assert from_json(b'{"a":[1,true,null]}') == {"a": [1, True, None]}
assert isinstance(from_json(b"1.20", float_mode="lossless-float"), LosslessFloat)
```

```python
from jiter import from_json
assert from_json(b'{"a": 1', partial_mode=True) == {"a": 1}
```

# Error Handling and Boundary Conditions

- Invalid UTF-8, malformed JSON, incomplete strict input, and duplicate keys
  when requested raise `ValueError` with deterministic syntax context.
- Wrong option types raise `TypeError`; unsupported option values raise
  `ValueError`.
- `allow_inf_nan=False` rejects non-finite tokens.
- `LosslessFloat` rejects tokens that are not decimal/exponent numbers.
- Do not execute input as Python or contact package registries or external
services.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── jiter/
    ├── __init__.py
    └── py.typed
```

# Additional Examples

```python
from jiter import cache_clear, cache_usage
cache_clear()
assert cache_usage() >= 0
```

```python
from jiter import LosslessFloat
assert float(LosslessFloat(b"1.25")) == 1.25
```

The task id and import package are `jiter`; invalid UTF-8, malformed JSON,
unsupported options, duplicate keys when requested, and invalid number tokens
must fail deterministically.

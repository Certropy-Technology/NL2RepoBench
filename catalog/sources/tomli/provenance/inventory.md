# tomli inventory

## Frozen source

- Upstream: `https://github.com/hukkin/tomli`
- Revision: `5a77b12a7a9f052ce5a20c335d2825658f6aea52`
- Git tree: `e529ffa3388ab50d261dbba463f30b03d5d40014`
- Unprefixed `git archive --format=tar` SHA-256: `200b6c7f01286ef30a889ff4742c93e333049821badb15b53b8d2c3af584e322`
- Archive size: `1177600` bytes
- License: MIT, `LICENSE` SHA-256 `b80816b0d530b8accb4c2211783790984a6e3b61922c2b5ee92f3372ab2742fe`
- Git describe: `5a77b12`

## Source tree and API

The implementation is five regular files under `src/tomli`: `__init__.py`,
`_parser.py`, `_re.py`, `_types.py`, and `py.typed`. The public root exports
are `loads`, `load`, and `TOMLDecodeError`, with `__version__ == "2.4.1"`.
The parser also has the compatibility import `tomli._types` and internal
regular-expression/date conversion helpers.

The source is pure Python and has no runtime dependency. Its PEP 517 metadata
uses `flit_core.buildapi` and requires `flit_core>=3.12,<4` for building.

## Tests and frozen contract

The upstream suite has 18 unittest methods across `tests/test_data.py`,
`tests/test_error.py`, and `tests/test_misc.py`; one Python 3.15-only lazy
import test is skipped on the evaluator's Python 3.12 runtime. The data suite
contains 228 valid and 516 invalid TOML fixture files. With the package
installed at the frozen revision, CPython 3.14.6 collected and passed the
remaining 17 unittest methods in `0.076s`.

The Harbor verifier freezes 32 deterministic leaves. They cover root exports
and metadata, scalar and nested parsing, strings/numbers/dates, custom float
conversion, binary-file loading, deep-copy behavior, error coordinates and
constructor compatibility, malformed TOML rejection, recursion boundaries,
the `_types` compatibility module, and installed metadata.

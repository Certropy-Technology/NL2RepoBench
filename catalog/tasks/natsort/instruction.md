# Build `natsort`

Create a complete, installable Python package named `natsort` from an empty
workspace. The package provides deterministic natural sorting for text and
JSON-safe scalar data. This candidate is based on SethMMorton/natsort at the
exact commit `e90771d7c39157d079425b655763938c2709d486`.

This catalog entry is an audit candidate and is currently blocked. The source
archive, exact `LICENSE` bytes, source-only LOC report, test collection report,
offline dependency closure, and repeatability evidence must be completed by
the authoring pipeline before it is publishable. The commit, URL, and license
label in `task.toml` are not a substitute for those artifacts.

## Project Description

Implement a small, installable natural-sort library. Natural sorting splits
text into comparable text and numeric runs so that values such as `item2`,
`item10`, and `item100` sort in numeric order while preserving the original
values in the result. The implementation must be usable from an empty
workspace and must not depend on a preinstalled copy of `natsort`.

Runtime behavior in this candidate is the pure Python fallback. The optional
`fastnumbers` accelerator and optional PyICU locale backend are outside the
runtime dependency closure. Their absence must not make the package import or
the pure fallback fail. Do not claim optional-backend parity for behavior that
cannot be exercised without those packages.

## Supports

- Support CPython `>=3.8,<4.0` unless the frozen source evidence records a
  narrower supported range.
- Provide an installable package whose import root is `natsort`.
- Use only the Python standard library at runtime for the scored fallback.
- Run installation, import, and tests with no network access and with an empty
  pip/uv cache. Do not download packages at import time and do not invoke a
  subprocess or external service.
- Keep sorting stable: equal comparison keys retain input order, and sorting
  returns new lists without mutating the input sequence.
- Keep the candidate scope JSON-safe. Scored values are JSON null, booleans,
  finite numbers, strings, and arrays containing those values. Nested mappings,
  arbitrary user objects, open files, and values whose comparison calls user
  code are outside this candidate scope. Results from `index_*` are integer
  lists and results from `order_by_index` are lists of original JSON-safe
  values.
- Use `PYTHONHASHSEED=0`, `LC_ALL=C.UTF-8`, `LANG=C.UTF-8`, and UTF-8 source
  handling for deterministic probes. Locale mode must not silently depend on
  whichever locale happens to be installed on the host.

## Public API Usage Guide

The following names must be importable from `natsort` or their documented
submodules. Signatures use the public behavior of the pinned source; harmless
additional keyword-only compatibility parameters are allowed when they do not
change the documented fallback behavior.

### Flags

Expose `ns`, an integer-compatible flag namespace, with the sorting flags used
by the package: `INT`, `FLOAT`, `REAL`, `SIGNED`, `UNSIGNED`, `NOEXP`, `PATH`,
`LOCALE`, `IGNORECASE`, `GROUPLETTERS`, `NANLAST`, `NUMAFTER`, `PRESORT`,
`LOWERCASEFIRST`, `COMPATIBILITYNORMALIZE`, and `TYPEDVERSION`. Flag values may
be combined with bitwise operators. `ns` must also expose the package's
version-compatible enum members without requiring an optional dependency.

### Sorting functions

Implement these functions and preserve their return shapes:

```python
natsorted(seq, key=None, reverse=False, alg=ns.INT | ns.UNSIGNED, **kwargs)
humansorted(seq, key=None, reverse=False, alg=ns.INT | ns.UNSIGNED, **kwargs)
realsorted(seq, key=None, reverse=False, alg=ns.REAL | ns.UNSIGNED, **kwargs)
index_natsorted(seq, key=None, reverse=False, alg=ns.INT | ns.UNSIGNED, **kwargs)
index_humansorted(seq, key=None, reverse=False, alg=ns.INT | ns.UNSIGNED, **kwargs)
index_realsorted(seq, key=None, reverse=False, alg=ns.REAL | ns.UNSIGNED, **kwargs)
order_by_index(seq, index, iter=False)
```

`natsorted`, `humansorted`, and `realsorted` return a new list. The three
`index_*` functions return indices that would produce the corresponding sort;
the indices must be a permutation of the input positions. `order_by_index`
applies such an index and returns a list unless its documented iterator option
is requested.

`natsorted` treats integer-looking runs numerically. `humansorted` uses the
human-oriented numeric interpretation for decimal/exponent text, and
`realsorted` handles signed real-looking runs. `reverse=True` reverses the
final ordering while preserving the function's documented stable behavior.
Empty sequences return empty lists. A non-iterable input, invalid index, or
unsupported flag combination raises the normal Python exception for that
operation rather than being silently coerced.

### Key generation

Implement:

```python
natsort_keygen(key=None, alg=ns.INT | ns.UNSIGNED, **kwargs)
humansort_keygen(key=None, alg=ns.INT | ns.UNSIGNED, **kwargs)
realsort_keygen(key=None, alg=ns.REAL | ns.UNSIGNED, **kwargs)
natsort_key
humansort_key
realsort_key
```

Each `*_keygen` returns a callable suitable for `sorted` and the corresponding
convenience key is a reusable default key. A supplied `key` is applied once to
each item before tokenization. Key functions used in scored examples are
deterministic selectors over JSON-safe records; no custom object serialization
or side effects are required.

### Compatibility and helper surface

Expose the compatibility helpers and version metadata used by ordinary callers:

```text
natsort.compat
natsort.utils
natsort.__version__
natsort.__author__
natsort.__license__
```

The helpers must be importable without `fastnumbers` or PyICU. If an optional
module is absent, use the pure Python implementation and keep the public
function names available. Do not turn an optional import into a required
runtime dependency.

### Flags and deterministic text behavior

The fallback must cover the following combinations in the scored scope:

- `ns.INT | ns.UNSIGNED`: integer runs, including leading zeros, compare by
  numeric value with the source's deterministic tie behavior;
- `ns.FLOAT` and `ns.REAL`: decimal, exponent, and signed runs according to
  the selected flag set;
- `ns.NOEXP`: an exponent marker is treated as text rather than as part of a
  number;
- `ns.PATH`: separators are tokenized consistently for POSIX-style strings;
- `ns.IGNORECASE` and `ns.GROUPLETTERS`: case handling is deterministic;
- `ns.COMPATIBILITYNORMALIZE`: normalization is explicit, never implicit; and
- `ns.LOCALE`: use the frozen `C.UTF-8` locale only, with no PyICU requirement.

Unicode strings must round-trip unchanged in results. Include bounded examples
containing ASCII, combining text such as `cafe\\u0301`, precomposed text such
as `caf\\u00e9`, full-width digits, and non-Latin scripts. The implementation
must not use process hash order to break ties.

## Implementation Notes

- Keep package metadata deterministic and independent of a live Git checkout.
- Do not copy the upstream source or tests into the generated project. Recreate
  the behavior from this specification.
- Do not add `fastnumbers`, `PyICU`, locale data packages, NumPy, pandas, or
  other third-party packages as runtime dependencies.
- The authoring verification will run two bounded `pytest --collect-only`
  probes: one with plugin autoload disabled for deterministic baseline
  collection, and one with Hypothesis available to confirm property-based
  tests collect without changing the count. Collection errors, import errors,
  or differing node-id sets are blockers rather than test failures.
- The authoring verification will run the same pure-fallback probes twice in
  fresh processes with the environment in `task.toml`; it will compare sorted
  values, key outputs, Unicode results, locale results, and serialized reports
  byte-for-byte.
- A candidate report must serialize with the standard-library `json` module.
  It may contain only JSON null, booleans, finite numbers, strings, arrays,
  and objects with string keys. Do not put sets, bytes, callables, exceptions,
  or arbitrary Python objects in the candidate evidence payload.

## Audit Gates

This task remains blocked until all of the following are recorded outside the
public instruction as reproducible evidence:

1. An archive made from exactly commit
   `e90771d7c39157d079425b655763938c2709d486`, with its SHA-256 and a matching
   clean-tree commit check.
2. The exact upstream `LICENSE` bytes and a license classification that allows
   the task's source-derived tests and distribution model.
3. Source-only LOC measured from the frozen archive, excluding tests, docs,
   examples, generated files, packaging metadata, and vendored code.
4. Pytest and Hypothesis collection reports with stable node IDs and a fixed
   denominator in the final environment.
5. A no-network dependency closure showing that the pure fallback imports and
   tests without `fastnumbers` and PyICU.
6. Two fresh-process locale/Unicode repeatability runs under the pinned locale,
   including the explicit normalization cases above.
7. A JSON-safe candidate-scope report with no arbitrary-object or optional
   backend claims.

Until those gates pass, `expected_total` in `task.toml` is only a positive
integer required by the current catalog schema and must not be used for a
score. No hidden tests, Oracle, Harbor bundle, or large source/cache artifact

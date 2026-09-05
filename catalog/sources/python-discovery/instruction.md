# Build `python-discovery`

Create a complete, installable Python package named `python-discovery` from an
empty workspace. The import package is `python_discovery`. Implement the
observable behavior below as a local, deterministic interpreter discovery
library. Do not copy the upstream source or tests into the generated project.

## Project Description

The library parses compact Python interpreter requirements, compares PEP 440-like
versions and specifiers, collects structured metadata from Python executables,
and searches explicit paths, `PATH`, version-manager shims, and uv-managed
installations. It also provides a small JSON disk cache for collected metadata.
The scored contract is local and must work without a service, credentials, or
network access. Discovery may interrogate a candidate executable through a
bounded child process because that is the library's purpose; it must not invoke
shell commands or use network access.

## Supports

- CPython 3.12 on Linux amd64 is the evaluation runtime; keep ordinary code
  compatible with Python 3.8 and newer.
- Use only the standard library at runtime except for the required `filelock`
  dependency used by disk-cache locking.
- Provide a PEP 517 installable layout with `src/python_discovery/`, a
  `py.typed` marker, and a deterministic version that does not require `.git`
  metadata. The installed distribution name is `python-discovery`.
- Preserve insertion order in discovery proposals and deduplicate interpreters
  by their resolved system executable. Do not read arbitrary remote data or
  depend on the current working tree's Git state.
- Windows registry and Windows-only behavior are outside this Linux contract;
  do not require `winreg` or a Windows host to import the package.

## API Usage Guide

### Package exports

The root package must export `KNOWN_ARCHITECTURES`, `KNOWN_IMPLEMENTATIONS`,
`ContentStore`, `DiskCache`, `PyInfoCache`, `PythonInfo`, `PythonSpec`,
`SimpleSpecifier`, `SimpleSpecifierSet`, `SimpleVersion`, `get_interpreter`,
`iter_interpreters`, `normalize_isa`, and `__version__`. The modules
`python_discovery._cache`, `python_discovery._discovery`, `python_discovery._py_info`,
`python_discovery._py_spec`, and `python_discovery._specifier` are importable.

### Versions and specifiers

`SimpleVersion.from_string(version_str)` parses `major`, optional `minor` and
`micro`, and optional `a`, `b`, or `rc` prerelease suffixes. It returns a frozen
value object with `release`, `pre_type`, `pre_num`, string conversion retaining
the stripped input, and ordering where prereleases precede the final release.
Invalid input raises `ValueError`.

`SimpleSpecifier.from_string(spec_str)` accepts `===`, `==`, `~=`, `!=`, `<=`,
`>=`, `<`, and `>` with a version, including `==3.12.*` and `!=3.12.*`.
`contains(version_str)` returns whether the candidate satisfies the operator;
invalid candidate versions return `False`. Compatible release `~=3.12` covers
`3.12` up to but excluding `3.13`. `SimpleSpecifierSet.from_string` splits a
comma-separated expression, preserves valid items in order, ignores malformed
items, and requires every retained item to match. Its empty set matches all
versions.

`PythonSpec.from_string_spec(text)` recognizes a path, implementation prefix
(`cpython`, `pypy`, or `graalpy`), major/minor/micro version, `t` free-threaded
flag, debug markers (`d`, `-dbg`, `-debug`), `-32`/`-64`, and normalized machine
names. It also recognizes a PEP 440-like version expression such as
`python>=3.12`. `generate_re(windows=..., all_implementations=...)` returns a
compiled filename matcher. `satisfies(other)` compares path, implementation,
architecture, machine, threading, and version constraints without mutating
either object.

### Python metadata

`PythonInfo.current(cache=None)` and `PythonInfo.current_system(cache=None)`
return structured information about the running interpreter. `from_exe(exe,
cache=None, *, raise_on_error=True, ignore_cache=False, resolve_to_host=True,
env=None)` interrogates an executable and returns `PythonInfo` or, when
`raise_on_error=False`, `None` for a failed probe. `from_dict` and `from_json`
restore data produced by `to_dict` and `to_json`; the `version_info` field is a
five-field named tuple.

The object exposes `version_str`, `version_release_str`, `python_name`,
`is_old_virtualenv`, `is_venv`, `system_prefix`, `system_exec_prefix`,
`machine`, `spec`, `install_path(key)`, and `sysconfig_path(key, config_var=None,
sep=os.sep)`. `satisfies(spec, *, impl_must_match)` checks this metadata against
a `PythonSpec`. The patch component reflects the actual installed CPython 3.12
image; results for fixed interpreter metadata must otherwise be deterministic.

### Cache and discovery

`DiskCache(root)` maps an executable path to a `DiskContentStore` containing
JSON under `root/py_info/4/`. `read()` returns a decoded dictionary or `None`
and removes corrupt JSON; `write()` stores formatted JSON, `exists()` and
`remove()` have the obvious local-file semantics, and `locked()` is an exclusive
context manager. `NoOpCache` and `NoOpContentStore` are available from
`python_discovery._cache` and never persist data.

`get_interpreter(key, try_first_with=None, cache=None, env=None, predicate=None)`
returns the first matching `PythonInfo` or `None`. `key` can be a single spec or
an ordered sequence. `iter_interpreters` yields matching interpreters in proposal
order, applies the optional predicate, and deduplicates resolved executables.
`propose_interpreters` and `path_exe_finder` are available from
`python_discovery._discovery`; `get_paths(env)` yields existing, nonempty PATH
directories from left to right. Explicit absolute paths and `try_first_with`
entries are checked before normal search. A missing version such as `99.0`
must return no match rather than raising.

## Implementation Notes

Keep parsing, metadata collection, caching, and proposal logic modular. The
metadata collector is also shipped as `_py_info_collect.py` and must remain
usable as a standard-library child script. Use typed normal Python exceptions
for malformed versions, invalid paths, and failed probes. Cache files must be
keyed by the SHA-256 of the executable path and must not be trusted when their
JSON is corrupt.

## Natural Language Instruction

Build `python-discovery` from an empty workspace as a deterministic interpreter
discovery library. Implement immutable version/specifier models, structured
interpreter metadata, a JSON cache, PATH proposal logic, explicit executable
selection, and the documented root exports. The package may inspect a local
Python executable through its bounded child probe because that is core
functionality, but it must not invoke a shell, fetch a package, or consult a
remote service. Preserve proposal order, resolved-path deduplication, typed
errors, and the difference between a missing match and a failed probe.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── src/
    └── python_discovery/
        ├── __init__.py
        ├── py.typed
        ├── _cache.py
        ├── _cached_py_info.py
        ├── _compat.py
        ├── _discovery.py
        ├── _py_info.py
        ├── _py_info_collect.py
        ├── _py_spec.py
        └── _specifier.py
```

The distribution name is `python-discovery`, while imports use
`python_discovery`. The root module re-exports the documented models and
discovery functions. `_py_info_collect.py` is a standard-library child helper
and must remain usable independently. Do not create a live package-manager
plugin, Windows-only registry dependency, or network fallback.

## Examples

```python
from python_discovery import PythonSpec, SimpleVersion

spec = PythonSpec.from_string_spec("cpython3.12-64")
SimpleVersion.from_string("3.12rc1") < SimpleVersion.from_string("3.12")
```

```python
from python_discovery import DiskCache, PythonInfo

cache = DiskCache(".cache")
info = PythonInfo.current(cache=cache)
round_trip = PythonInfo.from_dict(info.to_dict())
```

```python
from python_discovery import iter_interpreters

matches = list(iter_interpreters("python>=3.12", env={"PATH": "/usr/bin"}))
```

## Error Handling and Boundary Conditions

- Invalid version text raises `ValueError`; invalid candidate versions in a
  specifier test return `False`. Malformed items in a comma-separated set are
  ignored while retained valid items remain ordered.
- An empty specifier set matches every version. Compatible release bounds and
  wildcard equality/inequality follow the documented version semantics.
- Corrupt cache JSON is removed and treated as a miss. Cache keys depend on
  the executable path, and cache locking is local and exclusive.
- PATH directories are considered left to right, empty entries are ignored,
  explicit executable paths are checked first, and duplicate resolved
  executables are yielded only once.
- A missing version or unavailable executable returns no match when the API
  promises an optional result; `from_exe(..., raise_on_error=True)` retains
  its documented failure behavior.

The hidden verifier observes behavior only through an isolated child-side JSON
adapter. It uses a fixed 32-leaf denominator covering public exports, version
and specifier semantics, metadata serialization, cache behavior, deterministic
PATH matching, and explicit interpreter discovery. The verifier does not
require Windows registry APIs, live package-manager downloads, or a mutable
external interpreter inventory.

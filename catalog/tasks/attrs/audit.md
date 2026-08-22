# `attrs` Static Authoring Audit

Status: **blocked**. This task-local directory contains public declarative
metadata, a behavior specification, and static provenance/collection evidence
only. It contains no upstream test bytes, hidden assertions, private command
plans, dependency wheels, Docker files, verifier code, Oracle solution, or
shared catalog/index update.

## Decision

Keep this candidate in the blocked authoring state. The frozen source is a
coherent pure-Python data-model library and is a reasonable hard candidate, but
the available evidence is not a publication gate:

- the build backend and test closure are not an authorized offline artifact;
- collection changes with Python version and optional test packages;
- the full API passes live Python classes, callables, descriptors, mutable
  objects, exception instances, and process state that a generic JSON client
  cannot represent;
- no private verifier bundle or child-side scenario adapter exists; and
- no final image, Oracle, or control results are authorized in this lane.

The public `instruction.md` therefore describes behavior without copying source
or test assertions, and `task.toml` records provisional observations as
`unknown` rather than as a frozen denominator.

## Candidate Identity

The candidate was read from `reports/python-package-candidates.v1.md` and its
JSON companion:

- distribution: `attrs`;
- repository: `python-attrs/attrs`;
- upstream URL: `https://github.com/python-attrs/attrs`;
- requested and resolved revision:
  `c1dc5dcba16ed827aa6dcad896b41a3afedb4e32`;
- commit date: `2026-08-07T07:35:45+02:00`;
- subject: `oops`;
- commit tree: `cba2bb49c6df962d90390f5c82a990a2b2a7b4a4`;
- submodules: none;
- report category: `data-model`;
- report difficulty: `hard`;
- report estimates: 5,646 source SLOC, 148 public API symbols, 32 test files,
  680 static test definitions, and zero runtime dependencies;
- report release metadata: `attrs 26.1.0`;
- report recommendation: `strong-pilot`.

A detached checkout at `/tmp/attrs-audit` resolved to the requested SHA and
was clean before and after inspection. The checkout is temporary audit
material and is not part of this repository.

## Source Archive and License

The source lock is the direct, unprefixed archive from the detached commit:

```text
git archive --format=tar HEAD
archive members: 152
archive bytes:   2,150,400
archive sha256:  c7ebd671099d268790f83a2bc3e51b0dc3844bafd41a71b9768567e656538fac
```

Two independent archive commands produced the same digest. The archive is not
prefixed or repacked. The source contains `.git_archival.txt` with
`export-subst` placeholders; dynamic package version resolution must therefore
be handled deliberately when a future build is run from a candidate workspace.

The license evidence is internally consistent:

- `LICENSE` is 1,109 bytes;
- Git blob: `2bd6453d255e19b973f19b128596a8b6dd65b2c3`;
- file SHA-256: `882115c95dfc2af1eeb6714f8ec6d5cbcabf667caff8729f42420da63f714e9f`;
- the text is the standard MIT permission, warranty, and liability license;
- `pyproject.toml` declares `license = "MIT"`;
- the candidate report records the GitHub license endpoint as MIT.

No license bytes were copied into the catalog. The report's PyPI release is a
public source-contamination path; a future run must decide whether the agent
environment is offline or whether PyPI access is explicitly controlled.

## Package Boundary and LOC

The runtime package boundary is the 19 tracked Python modules under
`src/attr/` and `src/attrs/`, plus 10 tracked stub files and two `py.typed`
markers. The primary implementation is in `attr`; the `attrs` package provides
modern re-exports and aliases.

The exact tree was counted using physical, nonblank, and noncomment lines:

| tree | Python files | physical | nonblank | noncomment |
| --- | ---: | ---: | ---: | ---: |
| `src/attr/` and `src/attrs/` runtime `.py` | 19 | 6,428 | 5,181 | 4,953 |
| runtime stubs `.pyi` | 10 | 950 | 884 | 814 |

The candidate report's 5,646 SLOC estimate is recorded as discovery evidence,
but its counting basis is not specified and it is not reproduced by the exact
tree with the direct counts above. The independent noncomment implementation
count is still in the original Hard band. The discrepancy must not be hidden
or silently used to change the recorded candidate difficulty.

The frozen package contains no C, Cython, Rust, or extension source. Runtime
imports use the standard library and the sibling `attr` modules only. The
package includes both legacy and modern API surfaces rather than a separate
native fast path.

## Public API Inventory

The explicit exports provide a lower-level cross-check of the report estimate:

- `attr.__all__`: 34 names;
- `attrs.__all__`: 38 names;
- `attr.converters.__all__`: 4 names;
- `attr.validators.__all__`: 20 names;
- `attr.setters`, `attr.filters`, and `attr.exceptions`: public functions,
  sentinels, and exception classes without explicit `__all__` declarations.

After accounting for aliases and re-exports, the report's 148-symbol estimate
is a characterization rather than a frozen API denominator. The public
instruction inventories the supported root names, submodule helpers, core
signatures, field metadata, generated class behavior, validators, converters,
setters, filters, exceptions, and `VersionInfo`/`ClassProps` introspection.

The main behavior groups verified against source and stubs are:

1. modern `attrs.define`, `attrs.frozen`, `attrs.mutable`, and `attrs.field`;
2. classic `attr.s`, `attr.attrs`, `attr.ib`, and `attr.attrib` compatibility;
3. generated initialization, repr, equality, ordering, hash, slots, weakref,
   pattern matching, pickling, and exception protocols;
4. `Attribute`, `Factory`, `Converter`, `ClassProps`, `fields`, `fields_dict`,
   `has`, `inspect`, `resolve_types`, and `cmp_using`;
5. recursive `asdict`/`astuple`, `evolve`, `assoc`, and `validate`;
6. validators, converters, assignment setters, and collection filters; and
7. package metadata, aliases, lazy submodules, exception identity, and typed
   stubs.

The source tests also import private helpers such as `attr._make` and
`attr._compat`. Those imports are test implementation seams, not additional
application API promises in the public instruction.

## Packaging and Dependencies

`pyproject.toml` was parsed from the exact checkout. Its relevant values are:

- distribution: `attrs`;
- Python requirement: `>=3.10`;
- build backend: `hatchling.build`;
- build requirements: `hatchling`, `hatch-vcs`, and
  `hatch-fancy-pypi-readme>=23.2.0`;
- runtime dependencies: none;
- dynamic fields: `version` and `readme`;
- wheel packages: `src/attr` and `src/attrs`;
- pytest testpaths: `tests`;
- pytest addopts: `-ra` and `--import-mode=importlib`;
- pytest warning policy: `once::Warning` plus a Pympler-specific ignore.

The source tracks `uv.lock` (446,387 bytes, SHA-256
`eef931b1489a490cd287fb0a3d14a0c066b3abddcb02e8370851e840c3f273f0`). The
lock contains an editable `attrs` package and development groups, but it does
not itself provide a task-authorized, image-bound offline wheelhouse. It also
does not replace the dynamic build requirements in the source package metadata.

The source-declared development groups include:

```text
tests:       cloudpickle (CPython), hypothesis, pympler, pytest>9,
             pytest-xdist[psutil]
mypy:        tests plus pytest-mypy-plugins (CPython), mypy
pyright:     tests plus pyright
pyrefly:     tests plus pyrefly>=1.2.0
ty:          tests plus ty
coverage:    tests plus coverage[toml]
docs/lint:   Sphinx, documentation plugins, Ruff, prek, and related tools
```

`tests/conftest.py` imports Hypothesis unconditionally, so it is required even
for collection. `tests/test_3rd_party.py` uses `pytest.importorskip` for
cloudpickle. `tests/test_slots.py` conditionally uses Pympler; its absence
does not prevent ordinary collection. `tests/test_pyright.py` invokes a
`pyright` executable through `subprocess` but skips when it is not installed.
These optional paths must be assigned an explicit final test policy rather than
silently included or omitted.

## Collection Evidence

The report's 680 value is a static source-definition estimate, not an
effective pytest denominator. The checkout has 25 `test_*.py` modules, 31
tracked test Python files including support files, 667 source `def test...`
definitions, and parametrization that expands the effective node count.

The following cache-disabled collect-only probes ran against the detached
source. No test body was executed.

### CPython 3.12 probe

```text
environment: CPython 3.12.11, pytest 8.4.1, hypothesis 5.35.4
command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/attrs-audit/src \
  /root/.cache/uv/archive-v0/mQtdXmoCFG4T8bfW/bin/pytest \
  --collect-only -q -p no:cacheprovider tests
result: exit 0, 1411 tests collected, no collection errors
normalized node-list sha256:
  7525e8d53d1327dfd66b822351037fc7a061c01a145c6ab9ba37ffd09f4eda6f
```

The optional cloudpickle module was skipped in this probe because it was not
installed. The Pympler branch was absent but the test module still collected.
Two identical runs produced the same node count and normalized node list.

### CPython 3.14 probe

```text
environment: CPython 3.14.6, pytest 9.1.1, hypothesis 5.35.4
command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/attrs-audit/src \
  python -m pytest --collect-only -q -p no:cacheprovider tests
result: exit 0, 1412 tests collected, no collection errors
normalized node-list sha256:
  1367a716ec19a8505c47e2b7bc2819ee03701e3a97e40bf8978f50917d1e5272
```

The only node-set difference between the two probes was
`tests/test_forward_references.py::test_forward_class_reference`, which
`conftest.py` ignores below Python 3.14. The cloudpickle module was again
skipped. Two CPython 3.14 collection runs had the same node set; raw pytest
output hashes differ when the timing summary changes.

These observations do not establish a frozen denominator, a passing baseline,
or an Oracle reward. A final verifier must select the Python version, optional
dependency set, plugin autoload policy, skip/xfail policy, and command plan,
then collect from the exact private bundle and record a structured denominator.

## Deterministic Behavior Review

Deterministic contracts observed in source and documentation include field
declaration order, explicit MRO collection mode, generated initializer aliases,
keyword-only ordering, converter/validator order, filter order, and stable
metadata lookups for a fixed class definition.

The following dimensions require explicit policy or controlled inputs:

- Python version gates change collection and generated protocol behavior;
- CPython versus PyPy changes slot, weak-reference, and Pympler behavior;
- `__version__` and `__version_info__` depend on installed distribution
  metadata, not only source text;
- Python hash randomization affects hash values and any incidental repr of
  unordered user values;
- generated function filenames include module and qualified class names;
- `validators.set_disabled` changes process-global behavior and is documented
  as not thread-safe, although `disabled()` restoration is nestable;
- generic-class field lookup caches metadata on specialized classes;
- warning filters and deprecation paths depend on the selected interpreter;
- `field_transformer`, converter, validator, setter, and comparison callbacks
  are user-controlled and can have arbitrary side effects; and
- user-supplied `repr`, equality, ordering, hash, factory, and metadata values
  can be non-deterministic by design.

The library itself has no runtime network or subprocess path in the inspected
implementation. The test suite does use subprocess for Pyright, temporary
files, pickle, weak references, garbage collection, and optional third-party
compatibility checks. Future tests must not use wall-clock timing as a semantic
oracle.

## Native and Optional Risks

There is no native runtime extension risk in this revision. The meaningful
risks are packaging and environment scope:

1. Hatch VCS metadata and the fancy README hook are required for a source
   build, but no final hash-locked build backend or offline wheelhouse exists.
2. Hypothesis is an unconditional collection dependency and its version can
   change parametrized behavior or deadlines.
3. Cloudpickle is a CPython-conditional compatibility test dependency and
   Pympler is an optional size-measurement dependency that is unsuitable for
   PyPy.
4. Pyright is an external executable used by a subprocess test and must be
   either pinned and provisioned or explicitly excluded from the denominator.
5. The upstream tox matrix spans CPython 3.10 through 3.15, PyPy 3.11, and
   platform-specific branches; a Linux-only final task must state that scope.
6. Type checker plugins, docs, lint, coverage, xdist, and benchmark groups are
   development tools, not runtime dependencies, but their package closure is
   not frozen for this task.

## Separate-Verifier and JSON Boundary

The generic `candidate_client` contract exchanges JSON-safe request arguments
and JSON-safe observations with an untrusted candidate child. It cannot carry
the full upstream API by simply naming a function and serializing its Python
arguments. The following behaviors cross that boundary:

- field defaults, factories, converters, validators, equality keys, ordering
  keys, repr callables, assignment hooks, and field transformers are live
  Python callables;
- `Attribute` metadata can contain arbitrary Python values and mapping keys;
- `Factory` and `Converter` retain callable state and may receive a live
  instance or field object;
- `define`, `frozen`, `attrs`, and `make_class` create classes, descriptors,
  inheritance relationships, generated methods, and `__attrs_attrs__` state;
- `cmp_using` creates a comparison wrapper from callables;
- `attrs.fields` and `attrs.inspect` return rich objects whose identity and
  properties are meaningful across several operations;
- frozen/slotted classes, weak references, generated pickling helpers, and
  `VersionInfo` require process-local Python object behavior;
- validator disable state, generic metadata caching, warning capture, and
  class registries are stateful across calls; and
- exception type/arguments, custom classes, type annotations, generators, and
  arbitrary user values are not JSON values.

Directly importing the candidate from trusted pytest would violate the required
separate candidate/verifier boundary. A production task therefore needs an
attrs-specific child-side scenario adapter. Trusted tests should send a
declarative JSON scenario describing class declarations, field options,
allowlisted callback recipes, operations, and expected JSON-safe projections;
the untrusted child must reconstruct classes and callbacks, keep state for a
scenario, and return only validated observations. The adapter must explicitly
cover generated classes, assignment hooks, validators/converters, fields and
metadata, recursion, pickling, warnings, and state transitions. A generic
stateless one-call JSON wrapper is insufficient.

No such adapter, private test bundle, or command artifact exists in this lane.

## Exact Blockers and Reopen Conditions

Reopen this task only after all of the following are independently recorded:

1. A final Python/OS/base-image lock and an offline, hash-locked build/test
   dependency bundle, including the dynamic Hatch build requirements.
2. An explicit policy for Python-version scope, optional cloudpickle/Pympler,
   Pyright subprocess tests, plugin autoload, warnings, skips, xfails, and
   platform branches.
3. Private tests and an allowlisted command plan in the authorized
   visibility-separated artifact store. Do not copy them into this catalog.
4. A reviewed child-side JSON scenario adapter that preserves the required
   Python object and state semantics without trusted candidate imports.
5. Final-environment collection with a structured report and frozen denominator.
6. Three valid Oracle runs followed by empty, stub, forgery, and offline
   controls, with all rewards and failure classifications retained.
7. A reviewed contamination policy for the public `attrs` package and source
   repository.

No full upstream test run, Docker build, private artifact materialization,
candidate cache, Oracle execution, secret use, or shared-file mutation was
performed by this static audit.

# `cachetools` static authoring audit

Status: **blocked**. This directory contains a public declarative task source,
public behavior specification, and static provenance evidence only. It does not
contain upstream test bytes copied as a verifier bundle, hidden assertions,
private command plans, dependency wheels, Docker files, an Oracle solution, a
shared dataset/index update, or secrets.

## Candidate identity and checkout

The candidate was read from `reports/python-package-candidates.v1.md` and its
JSON companion:

- package/distribution: `cachetools`;
- repository: `tkem/cachetools`;
- requested revision:
  `01af8e5b7ce44432b357e26c7d67eb7fa055ae72`;
- discovery label: `easy`, category `caching`, recommendation
  `strong-pilot`;
- discovery estimates: source SLOC `1,261`, public API estimate `18`,
  `14` test files, `132` static test definitions, and zero runtime
  dependencies;
- PyPI release named by the candidate report: `cachetools 7.1.7`.

A detached public checkout was created at `/tmp/cachetools-audit` and resolved
to the requested full SHA. The checkout was clean after checkout and after
inspection. The commit is tagged `v7.1.7`, has tree
`5a355d8586540978257589b42d6c6cb2c964bc12`, and is dated
`2026-08-01T23:18:21+02:00`. `git submodule status` produced no entries.

## Source archive and license

The source lock in `task.toml` is the unprefixed Git archive, not a mutable
branch or a GitHub-generated repack:

```text
git archive --format=tar HEAD
bytes: 276480
sha256: 67fe3a54397f9d1437464dfd149bdf54520a0c5a894eb4ab66eb1f37ea100449
```

The archive was generated twice with identical bytes; a plain archive command
and the worktree-attributes form also matched. The archive contains 50 members.

License evidence agrees across the frozen source and public metadata:

- `LICENSE` is 1,085 bytes, Git blob
  `f980a19c78c25959f922b8cc93854d91a89e686f`, SHA-256
  `28c000b52b0ee27138a68ef778227e4057046e86b65f62f1cacb99b0cc49e0d2`;
- the file contains the standard MIT permission, warranty, and liability
  terms and carries the 2014-2026 Thomas Kemmer copyright notice;
- the commit's `pyproject.toml` declares `license = "MIT"`;
- the GitHub license endpoint reports key `mit`, name `MIT License`, SPDX ID
  `MIT`, and path `LICENSE`;
- the commit-specific raw GitHub license bytes have the same 1,085-byte
  SHA-256 shown above.

The PyPI JSON endpoint for `cachetools 7.1.7` reports `requires_python >=3.10`
and no runtime `requires_dist`. Its release hashes are:

```text
cachetools-7.1.7.tar.gz          40680 bytes  sha256:a3e2a00b14d8f8a6b70c1dae7b4685e7ad3bc965c5b42124a2d6ce895da6cf50
cachetools-7.1.7-py3-none-any.whl 16830 bytes sha256:ef98ef375ad188819ef2f9b3645e3987f4b8c5b7550e436ad998c2de78296df0
```

The PyPI JSON `info.license` field is null, but the wheel metadata contains
`License-Expression: MIT`, `License-File: LICENSE`, and the same Python
version classifiers. This is not a license conflict because the authoritative
source license and package metadata both identify MIT; the null JSON field is
reported rather than filled in by guesswork.

The public sdist was inspected without copying it into this repository. Its 31
source/document files that also exist in the frozen checkout matched byte for
byte; the six unmatched members were generated packaging metadata (`PKG-INFO`,
`setup.cfg`, and egg-info records). The public wheel contains the five runtime
`.py` modules, three `.pyi` files, `py.typed`, and the MIT license metadata.

## Package boundary, LOC, and public API

The candidate implementation boundary is exactly `src/cachetools/`:

```text
src/cachetools/__init__.py
src/cachetools/__init__.pyi
src/cachetools/_cached.py
src/cachetools/_cachedmethod.py
src/cachetools/func.py
src/cachetools/func.pyi
src/cachetools/keys.py
src/cachetools/keys.pyi
src/cachetools/py.typed
```

The package has five implementation `.py` files. Counts from the frozen
checkout are:

| tree | files | physical | nonblank | noncomment |
| --- | ---: | ---: | ---: | ---: |
| `src/cachetools/*.py` | 5 | 1,637 | 1,325 | **1,261** |
| `src/cachetools/*.pyi` | 3 | 331 | 305 | 304 |
| `tests/*.py` | 14 | 3,046 | 2,455 | 2,403 |

The report's 1,261 SLOC is therefore reproduced as noncomment physical lines
of the five implementation modules. Stubs are tracked separately and are not
included in the source-size estimate.

The public API estimate of 18 is independently reproduced by the three
`__all__` declarations:

- top level: `Cache`, `FIFOCache`, `LFUCache`, `LRUCache`, `RRCache`,
  `TLRUCache`, `TTLCache`, `cached`, `cachedmethod` (9);
- `cachetools.func`: `fifo_cache`, `lfu_cache`, `lru_cache`, `rr_cache`,
  `ttl_cache` (5);
- `cachetools.keys`: `hashkey`, `methodkey`, `typedkey`, `typedmethodkey` (4).

The source also exposes `__version__ = "7.1.7"`, the `cachetools.func` and
`cachetools.keys` modules, public cache properties/mapping methods, and the
wrapper metadata documented in `instruction.md`. Private helper modules are
not promoted to required API.

No existing `test_files/<task-id>` or `catalog/tasks/<task-id>` entry named
`cachetools` or a normalized `cache-tools` duplicate was found. The candidate
therefore has a separate task-local boundary from the 104-task legacy baseline,
subject to the dataset integrator's final duplicate check.

## Packaging and dependency review

`pyproject.toml` was parsed with `tomllib` from the exact checkout:

- distribution name: `cachetools`;
- package layout: setuptools `src` discovery;
- build backend: `setuptools.build_meta`;
- build requirements: unpinned lower bounds `setuptools >= 80` and
  `setuptools-scm >= 8.2`;
- dynamic version source: `cachetools.__version__`;
- runtime requirements: none;
- declared Python requirement: `>= 3.10`;
- `MANIFEST.in` excludes `.github`, `.gitignore`, and `.readthedocs.yaml`.

The implementation imports only Python standard-library modules (`collections`,
`functools`, `heapq`, `math`, `random`, `time`, `threading`, `warnings`, and
`weakref`). The tests use standard-library `unittest`, `unittest.mock`,
`threading`, `time`, `datetime`, `pickle`, `weakref`, and `gc`, plus pytest's
collection/runtime support. `tox.ini` declares unpinned `pytest`, `pytest-cov`,
`sphinx`, `pyright`, and `ruff` environments. There is no committed lockfile or
hash-pinned wheelhouse at this revision.

Consequently the package is a good offline runtime candidate, but the build and
verifier dependency closure is **unknown**. A final verifier must pin the
interpreter, pytest and its transitive dependencies, setuptools build tools,
base image digest, and any test-only tools. A PyPI wheel must not be treated as
the frozen source because the public distribution creates a contamination path
for an agent; the task should run with no network or an explicitly reviewed
network policy.

## Collection evidence

The source suite consists of `tests/__init__.py` and 13 `test_*.py` modules.
A direct AST scan found 133 source-level `test*` function definitions. The
candidate report's 132 is the `test_`-prefix count; one upstream unittest
method is named exactly `test`, so it is collected but not included by that
static naming convention. Neither number is used as a denominator.

A collect-only probe was run against the public checkout with no test bodies
executed:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/cachetools-audit/src \
  /root/NL2RepoBench/.venv/bin/pytest \
  --collect-only -q -p no:cacheprovider tests
```

Probe environment: CPython `3.14.6`, pytest `9.1.1`. The probe is not a final
benchmark environment and did not use a candidate private cache or a Docker
image. It exited `0` with no collection errors and collected **312** unittest
items. The higher item count is expected: several concrete test classes inherit
shared test methods from mixins. The normalized item list (all node-id lines,
without the timing summary) has SHA-256
`b9e96992202a3e8469af125d332c3e45be5cd0e11126ff2bc384f1fbe48406a0`.
Two independent collect-only runs produced byte-identical stdout with SHA-256
`41100e6ada884ffd8d2520b43d7696ce841032ae0272758d345edf034bcb2260` and the
same 312-item summary. The observed module totals were:

```text
test_cache.py         20
test_cached.py        38
test_cachedmethod.py  46
test_classmethod.py    7
test_fifo.py          23
test_func.py          36
test_keys.py           6
test_lfu.py           24
test_lru.py           24
test_rr.py            25
test_threading.py      4
test_tlru.py          31
test_ttl.py           28
TOTAL                312
```

This demonstrates one-environment collection stability, not a frozen
denominator.

No full upstream test run was performed in this lane. The static/collect-only
result must not be reported as an Oracle reward or as proof that the source
baseline passes in the final verifier.

## Deterministic behavior review

The source archive and collection are reproducible under the commands above,
but library behavior has intentional and environment-sensitive dimensions:

- `LFUCache` can choose any key among equal-frequency entries; its internal set
  makes a particular tie victim dependent on runtime ordering.
- `RRCache` uses `random.choice` by default. A deterministic `choice` callback is
  required for repeatable replacement traces.
- `TTLCache` and `TLRUCache` use `time.monotonic` by default. Tests must inject
  a controllable timer/`ttu` or explicit expiration times; wall-clock sleeps are
  not a valid determinism strategy.
- Python hash randomization changes raw hash values and can affect unspecified
  LFU ties, although key equality and cache semantics remain the contract.
- Decorator calls with a lock but no condition may compute the same missing key
  concurrently; hit/miss counts and call counts in that race are intentionally
  weaker than condition-protected behavior.
- The threading tests contain ten-thread barriers implemented with one-second
  sleeps and ten-second joins. Resource-constrained verifier runs need explicit
  timeouts and repeated baseline checks.
- Tests exercise `datetime.now`, `gc.collect`, weak references, and Python
  version-dependent deprecated `cachedmethod`/`classmethod` behavior. These
  require a pinned interpreter and explicit warning policy.

There are no runtime network or subprocess calls in the candidate package or
public tests. The only network URLs are documentation links/examples.

## Separate-verifier boundary

The generic production `candidate_client` exchanges JSON-safe requests and
responses and must not import candidate code in trusted pytest. The upstream
API is not representable by a plain stateless JSON call contract because tests
and intended users pass live Python objects and retain state across calls,
including:

- `cached` key callbacks, lock context managers, condition variables, custom
  `getsizeof` functions, mutable mapping instances, and wrapped callables;
- `cachedmethod` descriptors, per-instance cache/lock/condition factories,
  custom method key functions, mutable `__dict__` behavior, and deprecated
  classmethod paths;
- `TTLCache` timers and `TLRUCache` `ttu` callbacks, including datetime-like
  values;
- `RRCache` choice callbacks and `Cache` subclasses overriding `__missing__`,
  `getsizeof`, or `popitem`;
- pickling of caches and `_HashedTuple` keys; and
- concurrent thread interactions and wrapper statistics.

A trusted pytest suite that directly imports the candidate would violate the
separate candidate/verifier boundary. Production packaging therefore needs a
cachetools-specific child-side scenario adapter: trusted tests send declarative
JSON scenarios, the untrusted child reconstructs callbacks/objects and runs
candidate operations, and only JSON-safe observations return to the trusted
grader. Hidden expected values and private assertions must remain in a private
bundle. No such adapter or private bundle exists here.

## Exact blockers and reopen conditions

Keep this task **blocked** and do not create a Harbor bundle from this static
evidence. Reopen only after:

1. freezing a Python/OS/base-image environment and a complete hash-locked
   offline build/test dependency bundle;
2. provisioning private hidden tests, an allowlisted command plan, and an
   Oracle solution through the authorized visibility-separated artifact store;
3. implementing and reviewing the child-side adapter for callbacks, stateful
   caches, timers, pickling, and threading;
4. recollecting in that final verifier and freezing the structured denominator
   and skipped/xfail policy;
5. running three valid Oracle baselines, then empty, stub, forgery, and offline
   controls; and
6. resolving the public-PyPI contamination policy and preserving all hashes and
   logs in the authoring record.

No Docker, hidden-test materialization, candidate/private-test cache or artifact
bytes, secret use, shared index mutation, full test execution, or Oracle run was
performed by this audit.

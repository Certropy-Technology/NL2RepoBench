# `toolz` Authoring Audit

Status: **blocked**. This task-local directory contains a public declarative
source, a behavior specification, and bounded static/source-probe evidence.
It contains no copied upstream tests, hidden assertions, private command plan,
dependency wheelhouse, Docker or Harbor asset, verifier, candidate adapter,
Oracle solution, secret, shared dataset edit, or persistent build cache.

## Decision And Scope

Keep the candidate at lifecycle status `blocked`. The exact revision and the
source-only facts are strong enough for a future pilot, but they do not satisfy
the production publication gate. In particular, the final image, hash-locked
build/test dependency closure, visibility-separated private tests and command
plan, and toolz-specific child-side adapter are absent.

Only `catalog/tasks/toolz/` is a durable repository write root for this audit.
All source checkouts, probe output, build output, and inventory JSON mentioned
below were temporary files under `/tmp` and are not task artifacts. No full
source baseline, hidden test run, Oracle, negative control, Harbor execution,
or shared index update was performed.

## Exact Source And Provenance

The disposable checkout was `/tmp/toolz-audit`, obtained from
`https://github.com/pytoolz/toolz` and detached at the requested revision.
The checkout was clean before the probes and after ignored build output was
removed. Its identity is:

```text
commit:       568c2b8393973cd172a466546c9d95779c452438
tree:         d0557ea4e684d2f6b625a7133878c62713ca3364
parent:       af7f85ad7b083c083aea6edabec417dec4e7fc12
tag:          1.1.0
commit date:  2025-10-16T22:29:39-05:00
subject:      Skip `no-commit-to-branch` in CI (#611)
submodules:   none (`git submodule status` produced no entries)
```

The source lock is the direct, unprefixed Git archive from this commit, not a
GitHub-generated repack:

```text
command:         git archive --format=tar HEAD
archive bytes:   358400
archive members: 93
sha256:          1f0ef83ae7991a23a6fb664180354551bd4ea24ce5de1472d91e69061f07b213
```

Three independent archive streams produced the same SHA-256. The digest is
recorded in `task.toml`; no archive bytes were copied into this repository.

License evidence agrees across source and packaging metadata:

```text
path:       LICENSE.txt
bytes:      1492
Git blob:   eeb91b202ca96aebc14d8d1ea5630e6e6212711f
sha256:     053664057b295b2f0c1332291a77102f01a099d87926e449e08a117eea9660bf
pyproject:  license = "BSD-3-Clause"
wheel:      License-Expression: BSD-3-Clause
```

The exact license text contains the BSD three-clause redistribution,
attribution, and warranty-disclaimer terms. The wheel build also included
`LICENSE.txt` under the distribution license metadata. The catalog records
the digest and blob identity only; it does not redistribute the license file.

The exact source `pyproject.toml` was independently hashed as:

```text
sha256: 8cd850541325356603cc146f19af4d31df2915b0ab85a9d09468296eebf1f8a9
```

## Source-Only LOC Boundary

The implementation boundary is the tracked runtime Python in `toolz/` and
`tlz/`, excluding every path component named `tests`. It includes the root
modules, `toolz/curried`, `toolz/sandbox`, and `tlz`, including compatibility
and internal support modules that are imported by the runtime. It excludes
`toolz/tests`, `toolz/sandbox/tests`, `bench`, `examples`, and `doc`.

The resulting source-only count from the exact checkout is:

| tree | files | physical lines | nonblank | nonblank/noncomment |
| --- | ---: | ---: | ---: | ---: |
| runtime `toolz` and `tlz` boundary | 16 | 3,807 | 3,121 | **3,070** |
| `toolz` and `toolz/sandbox` tests | 17 | 2,805 | 2,158 | 2,044 |

The 3,070 nonblank/noncomment implementation lines place the task in the
medium band under the repository's 1,500 to 4,000 LOC convention. The test
line count is evidence about the upstream suite only and is not a score
denominator.

The runtime file set is eight root `toolz/*.py` modules, three
`toolz/curried/*.py` modules, three `toolz/sandbox/*.py` modules, and two
`tlz/*.py` modules. No generated version file was counted as source.

## Packaging, SCM, And Version Risk

The exact metadata declares:

- distribution `toolz`, Python `>=3.9`, and BSD-3-Clause license metadata;
- PEP 517 backend `setuptools.build_meta`;
- unpinned build requirements `setuptools >=77` and
  `setuptools-git-versioning >=2.0`;
- dynamic project version (`dynamic = ["version"]`), enabled
  `setuptools-git-versioning`, and the templates
  `"{tag}+{ccount}.g{sha}"` and `"{tag}+{ccount}.g{sha}.dirty"`; and
- explicit packages `toolz`, `toolz.curried`, `toolz.sandbox`, both test
  packages, and `tlz`.

The exact commit is the `1.1.0` tag (`git describe --tags --long` reported
`1.1.0-0-g568c2b8`). A bounded no-cache build from the clean Git checkout
completed with `uv build --wheel --sdist`; the observed artifacts were:

```text
toolz-1.1.0-py3-none-any.whl  58093 bytes
sha256: 452ea91acbb8584807c7ab7bc2997cc864baca67e7f48ef132e581b8058a2c80

toolz-1.1.0.tar.gz            52728 bytes
sha256: da25d3b2648a16be7d1e6b1f4f66bc428072e5d4823a797fbe3eb2379a459462
```

The wheel metadata reported `Version: 1.1.0`, `Requires-Python: >=3.9`,
`License-Expression: BSD-3-Clause`, and no `Requires-Dist` entries. The
generated sdist was extracted to a separate temporary directory and rebuilt
without a `.git` directory; that build also reported version `1.1.0`.

This is build feasibility evidence, not a frozen build closure. The builder
emitted a setuptools deprecation warning about dash-separated `index-url`
configuration. More importantly, the builder requirements are lower bounds,
there is no committed lock or hash-pinned wheelhouse, and a candidate created
from an empty workspace cannot rely on the upstream tag being present. The
final task must pin the builder, interpreter, base image, and artifact hashes,
or require a reviewed static version strategy. The candidate must not fetch
SCM metadata or build dependencies from the network in the verifier.

## Runtime Dependency Closure

`[project.dependencies]` is absent in the exact `pyproject.toml`, the built
wheel has no `Requires-Dist`, and a static AST import scan over the 16 runtime
files found 65 import statements with no non-standard-library static import
root. Local roots are `toolz` and `tlz`; all other static roots are Python
standard-library modules such as `functools`, `inspect`, `itertools`, and
`importlib`.

There is one intentional optional path. `tlz/_build_tlz.py` uses
`importlib.import_module` to try `cytoolz.<submodule>` and then
`toolz.<submodule>`, selecting the faster implementation when `cytoolz` is
installed and falling back to pure Python otherwise. `cytoolz` is not a
declared runtime dependency and the pure fallback must work without it.

The source test imports additionally mention `pytest`, optional `cytoolz`, and
standard-library multiprocessing/pickle/doctest modules. The absence of a
runtime closure does not prove a build/test closure: `pytest` is unpinned,
the build backend is unpinned, and the optional test branch is not locked.
`dependencies.status` therefore remains `unknown` in `task.toml`.

## Pytest Collection Evidence

The source configuration sets `testpaths = ["toolz"]`, strict config and
marker checks, strict xfail behavior, and warning-as-error behavior except for
the deprecated compatibility-module warning. The configured tree has 17
Python test files under `toolz/tests` and `toolz/sandbox/tests`.

The repeated source-only probe was:

```bash
cd /tmp/toolz-audit
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. \
  /root/NL2RepoBench/.venv/bin/pytest \
  --collect-only --continue-on-collection-errors -q -p no:cacheprovider
```

Under CPython 3.14.6 and pytest 9.1.1, two independent runs exited `0`,
produced no stderr, and each reported `186 tests collected`. The full output
hashes differ only because pytest includes elapsed time. After retaining only
normalized node-id lines, both runs had 186 nodes and SHA-256:

```text
dbf16d0c2af84ed258aef368db355de79da94bc5f241be3f1de930b1a7ca8294
```

A third collect-only probe under CPython 3.12.11 and pytest 9.1.1 used the
same plugin-isolated command and also exited `0` with 186 nodes and the same
normalized node hash. The two 3.14 full-output hashes were
`fd7febef2c306dbfdaa52e2e7fde00af9190a906d5964911aa24d677e3cb3ad4` and
`3490c42bb22c56b6b0618149de2a2a517a7feeb5e4fbb9dfc1e1e794d2a22978`.

The collection result is repeated source evidence, not a frozen verifier
denominator. No full upstream test run was performed, so this audit makes no
source pass-rate or Oracle claim. The provisional `expected_total = 186`
therefore has `expected_total_source = "unknown"`.

## AST API Inventory

The repository scanner was run without importing candidate modules:

```bash
.venv/bin/nl2repo author scan-source /tmp/toolz-audit \
  --output /tmp/toolz-api-inventory.json
```

The scanner identity was `python-ast-stdlib`. Its source digest was
`sha256:dc1205b5aa5ef45e254d277c631a86429db7c2ab5cc686e6273c8ed09d5eaa84`
and the inventory JSON SHA-256 was
`d46557681af3a793c67eb29c9e149943c020d58c668d3edbe22665b63167e5b6`.
Because this broad scanner includes benchmark/example/doc Python and uses a
generic test-path rule, its metrics are intentionally separate from the
explicit runtime LOC boundary above:

```text
implementation_loc: 3146
test_loc:           2157
python_files:       20
test_files:         31
public_symbol_count: 401
test_count:          175
import_count:       293
risk_flags:         dynamic-execution
syntax diagnostics: none
```

The explicit export inventory from the exact AST is:

| module | names in `__all__` |
| --- | ---: |
| `toolz.itertoolz` | 36 |
| `toolz.functoolz` | 14 |
| `toolz.dicttoolz` | 13 |
| `toolz.recipes` | 2 |
| `toolz.compatibility` | 13 |
| `toolz.curried.exceptions` | 2 |

The main callable groups are iterator transforms and accessors, dictionary
copy/update/filter operations, composition/memoization/curry classes, recipe
helpers, curried wrappers, and the sandbox's `EqualityHashKey`, `unzip`, and
`fold`. Public classes include `InstanceProperty`, `curry`, `Compose`, `juxt`,
`excepts`, and `EqualityHashKey`. The root package re-exports the functional
module exports and aliases. `_signatures` and `utils` are implementation
support but remain relevant to upstream introspection and serialization tests.

The scanner's `dynamic-execution` flag is a structural warning for dynamic
attribute/import operations, not evidence of `eval` or a network service in
the runtime. The relevant code uses `getattr` for signature registries and
callable metadata, and `import_module` for dynamic callable restoration and
the `tlz` loader. AST inventory proves names and syntax only; it does not
prove semantics.

## JSON-Safe Candidate Subprocess Scope

The repository's generic candidate boundary sends a JSON object containing a
module, attribute, JSON arguments, and JSON keyword arguments to an untrusted
child. The child alone imports candidate code and emits a JSON response. The
current runner bounds requests and responses to 1 MiB, applies an 8-second CPU
limit per child, and does not permit trusted pytest to import the candidate.

The full toolz suite cannot be preserved by that stateless generic call. It
passes live Python callables and callable classes to `groupby`, `mapcat`,
`reduceby`, `join`, `memoize`, `compose`, `curry`, `juxt`, `excepts`, recipes,
and `fold`; it retains iterator and curry state across calls; it checks
pickling and callable metadata; it uses custom mapping factories and random
state objects; it exercises the dynamic `tlz` namespace; and it includes a
subprocess/multiprocessing path in sandbox tests. A raw iterator, function,
class instance, exception object, or `cytoolz` module is not JSON-safe.

A defensible future first slice could use a toolz-specific child-side scenario
adapter with the following bounded operations:

- call data-only `itertoolz` access/count/partition/uniqueness/frequency
  operations with recursively JSON-safe lists, tuples, strings, numbers,
  booleans, nulls, and plain objects;
- call `dicttoolz.merge`, `assoc`, `dissoc`, and `get_in` with plain JSON
  mappings and paths, restricting factories to an allowlisted plain mapping;
- call `functoolz.identity` and other explicitly allowlisted no-callback
  operations; and
- reconstruct a small, named callback recipe vocabulary inside the untrusted
  child when a reviewed scenario intentionally covers callback behavior, then
  materialize bounded iterator results before returning them.

The adapter would need explicit limits for nesting, item count, string size,
numeric finiteness, output projection, exception type/message normalization,
and child cleanup. It must reject arbitrary module names, imports, callbacks,
filesystem paths, commands, and object serialization. This is a feasibility
review only: no toolz adapter, private test bundle, or command plan exists in
this task directory. Direct trusted pytest imports cannot be used as a silent
substitute.

## Publication Blockers And Reopen Conditions

Keep this candidate blocked until all of the following are independently
resolved and recorded:

1. Freeze an immutable OS/interpreter/base-image policy and a complete
   hash-locked offline closure for the PEP 517 builder and pytest verifier.
2. Provide authorized private tests, an allowlisted command plan, and their
   visibility-separated artifact references; do not put their bytes here.
3. Review and implement the child-side adapter for callable recipes, lazy
   iterator materialization, stateful curry/pickle behavior, `tlz`, and the
   sandbox boundary, or deliberately rescope and version the task.
4. Recollect in the final verifier image with structured reporting and freeze
   the denominator and skipped/xfail policy.
5. In a later execution lane, run three valid Oracle baselines and the empty,
   stub, forgery, and offline controls.
6. Complete blind and traceability review before changing lifecycle status.

No hidden tests, Harbor assets, Oracle, shared catalog/dataset update, secret,
large persistent cache, or full source baseline was created by this audit.

## 2026-08-25 Bounded Harbor Remediation

- The bounded local adapter passed all 49 cases.
- Source and Harbor compilation passed in temporary output.
- Oracle candidate installation failed because the frozen `pyproject.toml`
  license metadata was incompatible with the resolved setuptools closure.
- No controls were run.
- Partial runtime and private assets were removed.
- Exact next step: regenerate the hash-locked dependency artifact with a
  setuptools closure compatible with the frozen metadata and its
  `setuptools >=77` requirement, update the source
  `[dependencies].lock_artifact` digest and private bundle, repopulate the
  task-local artifact store, compile without `--allow-incomplete`, and rerun
  one Oracle before any controls.

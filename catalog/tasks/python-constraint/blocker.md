# `python-constraint` Freeze Revalidation and Blocker

Audit date: **2026-08-22**

## Decision

**Blocked. Do not compile or publish a Harbor task from this directory.** The
requested source revision, license bytes, archive digest, package metadata, and
local source baselines are coherent. The candidate is not safe to advance,
however, because three independent gates are still open:

1. the existing public instruction is not traceable to the complete frozen
   suite (notably the `examples/` tree and the compiled-extension/test-mode
   contract);
2. the production JSON `candidate_client` has no state/session, callback, or
   object-handle protocol for the upstream assertions; and
3. no final immutable verifier image or hash-locked offline dependency bundle
   is available.

`task.toml` and `instruction.md` were intentionally **not** rewritten in this
repair. The traceability findings below are reopen work, not an implicit change
to the measured task or its version. No hidden/private bytes, Oracle solution,
Dockerfile, Harbor bundle, or shared catalog/index artifact is stored here.

## Frozen source and license revalidation

The public checkout was made in `/tmp/python-constraint-audit-src` and detached
at the requested full revision:

- Upstream: `https://github.com/python-constraint/python-constraint`
- Requested and resolved commit:
  `d91ba03d1fd6acc30d64fd9d513dc0523f697b5b`
- Commit tree: `a2f6010080fc1518988e86bcbb8de1b4bfb233cf`
- Commit date: `2026-08-18T16:06:43+02:00`
- Subject: `Updated changelog before release`
- Submodules: none
- `git describe --tags --always --long HEAD`:
  `2.7.3-0-gd91ba03`

Three independent unprefixed archives from `git archive --format=tar HEAD`
were byte-identical:

- Size: `7,618,560` bytes
- SHA-256:
  `c15171bf0b6e8271e099566d5acef4c322e2d2efa13dd1f92cb3370b5f4675ff`

`LICENSE` was also checked against the pinned raw GitHub URL. Both copies are
identical:

- Git blob: `1551a23ae2154250683c4e52001ade66e147d5cd`
- Size: `1,335` bytes / `23` lines
- SHA-256:
  `e5894c331ba462210b707470b25f61ccd46bdadec5ee8290e71482a74742b62c`
- `pyproject.toml` declares `BSD-2-Clause`
- The text is the two-condition BSD license

The package inventory is consistent with the candidate record:

- `constraint/*.py`: `3,235` newline-counted lines
- `constraint/*.py` plus `examples/**/*.py`: `4,148` lines
- All tracked Python files: `5,819` lines
- Non-underscore top-level definitions in `constraint/`: `43` (30 classes,
  13 functions), before star re-exports from `constraint.__init__`

## Package metadata and dependency revalidation

The pinned `pyproject.toml` identifies distribution `python-constraint2`,
version `2.7.3`, Python `>=3.11`, no runtime `Requires-Dist` entries, and a
Poetry build backend with these lower bounds:

```text
poetry-core>=2.4.1
setuptools>=84.0.0
Cython>=3.2.9
```

The test group declares lower bounds for `pytest`, `pytest-benchmark`,
`pytest-cov`, `nox`, `ruff`, and `pep440`. There is no upstream
`poetry.lock`, `uv.lock`, hash-bearing requirements file, or committed offline
wheelhouse in the frozen source.

A temporary CPython `3.12.11` environment on the audit host resolved and
installed the exact roots used by the prior evidence probe:

```text
poetry-core==2.4.1
setuptools==84.0.0
Cython==3.2.9
pytest==9.1.1
pytest-benchmark==5.2.3
pytest-cov==7.1.0
pep440==0.1.2
```

The resolver additionally installed `coverage==7.15.4`, `iniconfig==2.3.0`,
`packaging==26.3`, `pluggy==1.6.0`, `py-cpuinfo==9.0.0`, and
`Pygments==2.21.0`. With those packages preinstalled, the recorded candidate
build command succeeded:

```text
python -m pip install --no-index --no-build-isolation --no-deps -e .
```

The resulting metadata reported `python-constraint2==2.7.3`, no runtime
requirements, and five Cython extension modules. This is a temporary local
build probe, not a dependency artifact or an Oracle image.

An empty-cache offline probe was deliberately run as a negative check. The
same build/test roots failed before installation with `poetry-core` unavailable
when the network was disabled. Therefore the dependency state in `task.toml`
correctly remains `unknown`; network resolution success must not be promoted to
an offline closure.

The host used for this revalidation is Fedora 44 / `linux-amd64`, CPython
3.12.11, and GCC 16.1.1, not the recorded Debian 13 image. Docker and image
rebuilds were out of scope. The previously recorded Debian/system-package
values are not re-claimed here as a fresh final-image verification. In
addition, `task.toml` currently declares `network_mode = "public"`; that is a
contamination/publication risk until an approved no-network experiment and
source-download policy are frozen.

A temporary wheel metadata probe further showed that the upstream wheel does
not contain `examples/`, `tests/`, or `README.rst` (it does contain the
license). No wheel was retained in the repository.

## Collection and source-baseline revalidation

The upstream pytest configuration enables coverage by default, so all counts
below use the task's explicit `--no-cov` and cache-disabled collection. The
source-only collection is stable at 49 nodes because the benchmark module is
skipped at module scope when compiled extensions are absent:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --no-project \
  --with pytest==9.1.1 --with pytest-benchmark==5.2.3 \
  --with pytest-cov==7.1.0 --with pep440==0.1.2 \
  python -m pytest --no-cov --collect-only -q -p no:cacheprovider tests
```

- Source-only collection: `49` nodes
- Sorted node-list SHA-256:
  `7b03bcce47e67115e757dbf8916060e2696c1a592c4e1288f15f18d315216266`

After the temporary editable build produced C extensions, the same collection
was `52` nodes. The compiled node-list SHA-256 was
`284b59ee7eb251b9d876a9b2686d2ca49535867f8027c8310b460b3d2df2a110`.
Three independent direct-source runs with the task command shape produced:

| Run | Collected/JUnit cases | Passed | Failed | Errors | Skipped | Wall time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 52 | 52 | 0 | 0 | 0 | 43.51 s |
| 2 | 52 | 52 | 0 | 0 | 0 | 44.60 s |
| 3 | 52 | 52 | 0 | 0 | 0 | 43.79 s |

All three JUnit reports had the same sorted testcase/status digest:
`205b619be74070c61efbdc6bacfacebf7d0dc18173928fb3f2a97640a576b233`.
These are valid local source baselines only; they are not Harbor Oracle jobs
and do not establish a production `valid=true` result.

The intended no-extension branch was also probed by copying the built
extensions and renaming them with the source `tests/setup_teardown.py` helper.
That mode collected 50 JUnit testcase elements, with `49` passed and one
intentional benchmark-module skip, across three runs. A completely source-only
checkout with no extension files instead fails `test_if_compiled` (`48` passed,
`1` failed, `1` skipped). This distinction matters because the public
instruction currently says Cython is optional, while the default compiled
suite includes `test_if_compiled` and three benchmark nodes. A final task must
choose and document one test mode; the current `expected_total = 52` is not a
portable denominator until that choice and final image are frozen.

## Public-spec traceability findings

The existing `instruction.md` was preserved byte-for-byte (SHA-256
`c17404a568ba5400fc543f0d49b1c0dfc6297401b10ae329f5df87deb5f8a168`). The
source and test audit found concrete promises that are not currently public:

1. `tests/test_constraint.py` imports six modules from `examples/` (`abc`,
   `coins`, `einstein`, `queens`, `rooks`, and `studentdesks`), and
   `tests/test_examples.py` imports six more (`crosswords`, `sudoku`, three
   wordmath modules, and `xsum`). These are 12 collected tests requiring a
   repository fixture tree that the instruction never names. The wheel also
   omits that tree.
2. `tests/test_toml_file.py` reads the repository's `pyproject.toml` and
   `README.rst` and checks authors, keywords, classifiers, license, version,
   and required metadata keys. “A standards-compliant `pyproject.toml`” is
   not a sufficiently precise public contract for those assertions.
3. `tests/test_compilation.py` and `tests/test_util_benchmark.py` make the
   optional-Cython wording operationally significant. A pure-Python checkout
   does not pass the default compilation test, while the compiled branch adds
   three benchmark nodes whose timing assertions depend on the frozen machine.
4. `tests/test_doctests.py` executes module doctests at import time and extracts
   every Python code block from `README.rst`. The instruction gives one API
   example but does not require the README/doctest fixture or its exact
   behavior.
5. Parser tests inspect concrete specialized constraint classes and the
   private `_maxprod` field for strict bounds. The instruction describes the
   broad parser result shape but does not expose those exact specialization
   decisions.

These are `spec`/traceability blockers, not reasons to silently edit the
instruction in a blocked task. A future repair must either add the missing
public repository/packaging contract and bump the task version, or explicitly
scope and version a different adapted test bundle.

## Separate-verifier boundary blocker

The current production `candidate_client`/`candidate_runner` protocol:

- starts a fresh unprivileged Python child for each operation;
- accepts JSON arguments and one module attribute or module/console entry
  point;
- JSON-serializes the returned value;
- has no object handles, persistent session, callback transport, or child-side
  task adapter.

A direct local protocol probe against the pinned package demonstrated the
boundary rather than relying only on static reasoning:

| Probe | Result |
| --- | --- |
| `constraint.domain.check_if_compiled()` | JSON boolean returned successfully |
| `constraint.problem.Problem()` | child exited while serializing `Problem`; no result prefix |
| `constraint.parser.parse_restrictions(...)` | only the string-only result serialized |
| `constraint.parser.compile_to_constraints(...)` | child exited while serializing `FunctionConstraint` |

The frozen tests require behaviors that cannot be flattened into independent
JSON calls without changing their meaning:

- construct and mutate one `Problem` through several calls, then solve it;
- pass lambdas and a custom `Constraint` subclass;
- preserve a custom `Domain` subclass and observe forward-check mutations;
- return/inspect `Constraint` objects and consume lazy solution iterators;
- execute module and README doctests in process;
- exercise thread/process `ParallelSolver` behavior and pickling rejection;
- import and execute the `examples/` modules in the same candidate tree.

Putting upstream pytest directly in the trusted verifier would violate the
repository's separate-verifier policy. Moving the assertions into a
candidate-owned test/driver would make them forgeable. A reviewed, task-
specific stateful child RPC/driver could be a safe future implementation, but
none exists in this task and no architecture change is approved by this audit.

## Reopen gates

Keep lifecycle `blocked`. Reopen only after all of the following are approved
and recorded:

1. a versioned instruction repair or explicit adapted-scope decision covering
   examples, packaging metadata, README/doctests, parser specialization, and
   compiled-vs-pure-Python test mode;
2. a task-specific child-side adapter/RPC that preserves state, callbacks,
   subclasses, iterators, and process-mode semantics without trusted direct
   candidate imports;
3. an immutable final OS/Python/base-image lock and a content-addressed,
   hash-locked offline build/test dependency bundle;
4. a fresh final-image collection/JUnit record and metric contract that fixes
   the denominator, benchmark skip policy, and collection-mismatch behavior;
5. authorized private test/command/Oracle artifacts with visibility, size, and
   digest metadata; and
6. three valid stable Oracle runs followed by empty, stub, forgery, and offline
   controls, then blind/spec traceability review.

Until those gates exist, `expected_total = 52` remains a local compiled-suite
observation rather than a publishable denominator. No Harbor, Docker, Oracle,
private-artifact materialization, or negative-control run was performed.

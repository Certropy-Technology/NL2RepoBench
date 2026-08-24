# `pydantic` Static Authoring Audit

**Status: blocked.** This task-local directory is public audit evidence only.
It contains no `task.toml`, instruction projection, source archive, license
bytes, copied upstream tests, hidden assertions, private artifact reference,
dependency wheel or crate cache, Docker/Harbor asset, verifier, Oracle solution,
secret, reward, or shared catalog/dataset change.

## Decision

Do not create a production task from the current candidate record. The
candidate report identifies the repository and flags the native dependency,
but it does not identify an immutable upstream revision. Selecting a branch
tip, a release tag, or the commit nearest the report timestamp would invent the
source lock. This blocks source, license, LOC, collection, dependency, and
Oracle attestation as one coherent task version.

A report-era upstream checkout was inspected only to characterize the likely
risk surface. It shows additional independent blockers:

- the Python package imports and version-checks a compiled
  `pydantic_core._pydantic_core` extension;
- the monorepo's `pydantic-core` tree had six source/test paths changed after
  the public `core-v2.48.0` release tag while still declaring version `2.48.0`;
- the Cargo lock has checksums but no vendored crate source, and an offline
  locked fetch fails in the audit environment;
- the Python locks name registry artifacts but are not a materialized,
  authorized, image-bound wheelhouse;
- the test set is highly parametrized and interpreter/platform sensitive, and
  no final-environment collection record exists; and
- upstream behavior relies on live Python types, generated classes,
  validators/serializers, callbacks, object identity, mutable state, rich
  exceptions, and native objects. The generic stateless JSON candidate client
  cannot preserve that suite, and no Pydantic-specific child adapter exists.

These are source/environment/verifier blockers, not model results. No test body,
Oracle, or negative control was run.

## Authoritative Candidate Record

The only approved candidate input is the `pydantic` shortlist row in:

```text
reports/python-package-candidates.v1.md
sha256: 8b69e9658705324979bd6b540c114a2f488488dfad34298c10530b23b6f9a2c5

reports/python-package-candidates.v1.json
sha256: fd613b5114ac315e3d3276ef10c7dbf8dab1b3e0d899d8be4f1c2009302c2bc4
```

The JSON report was added by repository commit
`2e485a451f1bf2d03977d5a039f5d9d291889615` at
`2026-08-18T11:59:20+08:00`. Its row records:

- distribution: `pydantic`;
- repository: `pydantic/pydantic`;
- category: validation;
- discovery stars: 28,561;
- reported license: MIT;
- reported language share: 83% Python;
- reported last push: `2026-08-17`;
- status: `conditional`; and
- reason: `pydantic-core introduces a native Rust dependency; offline wheel
  and platform matrix required`.

There is **no** `pydantic` entry in the report's `deep_validation` array. The
report therefore supplies no revision, tree, source digest, release version,
source LOC, public API estimate, test-file/static-definition count, runtime
closure, or recommendation. Its own limits say that no candidate was frozen
and that the next stage must freeze a complete commit, environment, dependency
closure, adapted tests, and separate verifier.

## Blocker: Exact Upstream Revision Is Unspecified

Read-only upstream inspection confirms why the date is not an immutable lock:

```text
repository: https://github.com/pydantic/pydantic
current remote HEAD/main observed during audit:
  2151025aa51263f3016502b00010b78e4481eaa1
```

The current branch tip is mutable and postdates the candidate report. More
importantly, upstream `main` had **eight** commits on 2026-08-17 that were no
later than the report commit time:

```text
aeeefbeabadc3179ecd3738216a95f61e7f4e0d9
f002759018732fc7208d9c9547ab6dd3f8a35e35
7c85e07e10d48845e19feef6da29e0da3be766ab
77760be772adda4dc249ba610110cb7c0d81c015
99a31fb8d6ab41ce02e99921a6f96d56a5e68bd4
31edf22f1738165cf220cd185fdf6b05d63f43fc
ce84b307de84b1a14638223f68f8866f55c286ad
6d03f94f7b470729822ce8c88f88cba0c411833a
```

`aeeefbeabadc3179ecd3738216a95f61e7f4e0d9` is the latest of those commits,
but that ordering does not prove that the discovery process inspected it. A
push date is not a revision, and the report does not authorize a nearest-time
heuristic. Tags `v2.12.4`, `v2.12.5`, and the current branch tip are likewise
not substitutes for the missing candidate SHA.

No `task.toml` or instruction is created because either would falsely imply a
selected implementation contract.

## Non-authoritative Report-era Reference

The rest of this audit uses
`aeeefbeabadc3179ecd3738216a95f61e7f4e0d9` **only as a risk-characterization
reference**. None of these values is a candidate source lock or publication
claim.

A detached public checkout resolved cleanly to:

```text
commit:         aeeefbeabadc3179ecd3738216a95f61e7f4e0d9
tree:           d28aaa07222c410d453fc63a7f02733da58fd6d8
author/commit:  2026-08-17T22:24:24+02:00
subject:        Use config of `TypeAdapter` in JSON Schema generation (#13676)
describe:       core-v2.48.0-25-gaeeefbe
submodules:     none
```

A direct, unprefixed `git archive --format=tar HEAD` was generated twice and
was byte-identical:

```text
members: 890 (including directory entries)
bytes:   11,868,160
sha256:  4a8501801b7902ebffce85da76ae2bc66d78353e24a82d5c7479027bcf11e4ae
```

The archive remains temporary evidence outside this repository. Its digest
must not be copied into a future `source_digest` unless a task owner explicitly
selects this exact commit.

At this reference, `pydantic/version.py` declares pre-release version
`2.14.0b1`, and the root project pins `pydantic-core==2.48.0`. This is not the
same thing as selecting a released Pydantic source distribution.

## License Evidence

The discovery row reports MIT. The non-authoritative reference is internally
consistent with that report:

| reference path | bytes | Git blob | SHA-256 | observation |
| --- | ---: | --- | --- | --- |
| `LICENSE` | 1,129 | `488c6260c10f2e88fa1fae58a63fccec8d600cd1` | `a9e186f3ca16b5eef84318e7a701721351a00cb7b8ae3a4394b67b49e3529ef3` | MIT text; Pydantic Services/contributors notice |
| `pydantic-core/LICENSE` | 1,080 | `0716871caabdbbb3e77a0371d49936cef1923ea1` | `2afdd30d54b4d62b6f488a6bcc1546e84ec5061f13f4209c03d012348783795a` | MIT text; Samuel Colvin notice |

The files are not byte-identical because their copyright notices differ. The
reference `pyproject.toml`, `pydantic-core/pyproject.toml`, and
`pydantic-core/Cargo.toml` each declare MIT, and the inspected public
`pydantic_core 2.48.0` wheel metadata declares `License-Expression: MIT` and
contains the 1,080-byte core license.

This establishes coherent **reference** license evidence, not the frozen
candidate's license. Exact license bytes, vendored notices, and source scope
must be rechecked after an authorized commit is selected. No license bytes are
copied into this catalog.

## Reference Package Boundary and LOC

The report's 83% language share is a GitHub discovery signal, not a reproducible
SLOC method. The table below uses tracked files in the detached reference.
`physical` counts `splitlines()`; `nonblank/noncomment` excludes blank lines
and lines whose first non-whitespace token is `#` for Python or `//` for Rust.
Docstrings and Rust block-comment lines remain counted, so the method is
explicit and intentionally simple.

| reference tree | files | physical | nonblank | nonblank/noncomment |
| --- | ---: | ---: | ---: | ---: |
| `pydantic/**/*.py` including compatibility `v1/` | 105 | 46,153 | 37,966 | 35,654 |
| same tree excluding `pydantic/v1/` | 79 | 32,987 | 27,098 | 25,264 |
| `pydantic-core/python/pydantic_core/**/*.py` | 2 | 4,834 | 4,154 | 4,101 |
| `pydantic-core/python/pydantic_core/**/*.pyi` | 1 | 1,115 | 939 | 922 |
| `pydantic-core/src/**/*.rs` plus `build.rs` | 129 | 33,770 | 30,134 | 28,700 |

The complete runtime is therefore not Python-only. The root package eagerly
checks the exact core version in `pydantic/version.py`; many modules import
`SchemaValidator`, `SchemaSerializer`, `ValidationError`, core-schema types,
URLs, and the compiled extension through `pydantic_core`. The reference is
well inside the original Hard LOC band under any reasonable inclusion policy,
but no production difficulty is assigned without the exact candidate and an
approved decision on whether compatibility V1 and core source are in scope.

## Reference Test Inventory

No test count exists in the candidate report. Static inventory of the
non-authoritative reference found:

| public source tree | tracked paths | Python files | `test*.py` files | static `test*` defs | explicit `pytest.mark.parametrize` calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| root `tests/` | 221 | 201 | 121 | 2,764 | 501 |
| `pydantic-core/tests/` | 117 | 116 | 108 | 1,576 | 422 |

The root tree includes a tracked symlink
`tests/pydantic_core -> ../pydantic-core/tests`, so test path policy must avoid
silently double-counting or omitting the native suite. It also contains mypy,
plugin, type-checking, benchmark, documentation, and shell integration paths;
static function definitions are not pytest items.

Environment-sensitive marker/control signals in the same public source include:

```text
root tests: 75 skipif, 11 skip, 30 xfail decorators,
            13 runtime skips, 1 runtime xfail, 1 importorskip
core tests: 34 skipif, 18 xfail decorators,
            8 runtime skips, 1 runtime xfail
```

Root test configuration validates generated schemas with `jsonschema`, creates
and imports temporary modules, executes subprocesses, monkeypatches Pydantic
internals, and marks thread-unsafe fixtures. Core tests require Hypothesis,
exercise Python and JSON paths, change process working directories, dynamically
import generated modules, and contain free-threaded/interpreter-specific
branches. The upstream CI spans CPython 3.10-3.15 (including free-threaded
builds), PyPy, Linux, macOS, Windows, multiple architectures, manylinux,
musllinux, GraalPy, and Emscripten paths.

No `pytest --collect-only` was run. Without an approved revision, matching
native core, final OS/interpreter/plugin policy, and offline dependency bundle,
a host collection number would be false precision rather than a frozen
denominator. No test body, JUnit report, baseline, or Oracle result was
produced.

## Native `pydantic-core` and Build Closure

### Root Python project

At the report-era reference, root `pyproject.toml` declares:

```text
Python:          >=3.10
build backend:   hatchling.build
build requires:  hatchling, hatch-fancy-pypi-readme>=22.5.0
runtime:         typing-extensions>=4.15.0
                 annotated-types>=0.6.0
                 pydantic-core==2.48.0
                 typing-inspection>=0.4.4
```

The test/development groups additionally include pytest, coverage, pytz,
dirty-equals, pytest-mock, pytest-pretty, pytest-examples, Faker,
pytest-benchmark, pytest-codspeed, pytest-run-parallel, packaging, jsonschema,
time-machine on non-PyPy, and further optional/type-checking/documentation
tools. Optional runtime paths include `email-validator` and Windows `tzdata`.

The root `uv.lock` parses and passes `uv lock --check` at this checkout. It has
176 package records: 173 registry packages, two editable workspace packages
(`pydantic` and `pydantic-core`), and a commit-pinned Git source for
`pydantic-docs`. Registry URLs and hashes are resolver evidence, not artifact
bytes. There is no task-authorized wheelhouse or clean-cache no-network replay.

### Native core source build

The reference `pydantic-core` project declares:

```text
build backend:   maturin
build requires:  maturin>=1.13.3,<2
Rust edition:    2024
minimum Rust:    1.88
extension:       pydantic_core._pydantic_core (PyO3 cdylib)
Python:          >=3.10
runtime:         typing-extensions>=4.14.1
```

`pydantic-core/Cargo.lock` is lock format 4 with 101 packages: one workspace
package and 100 crates.io packages, all 100 registry entries carrying
checksums, with no Git dependencies. This is useful reproducibility metadata,
but the repository has no vendored Cargo source. The audit host had an empty
Cargo registry, and this command failed closed:

```text
cargo fetch --locked --offline --manifest-path pydantic-core/Cargo.toml
exit: 101
error: no matching package named `ahash` found
```

`Cargo.toml` includes `/rust-toolchain` in package source metadata, but no
`pydantic-core/rust-toolchain` file is tracked at the reference. `rust-version
= "1.88"` is a minimum, not a full compiler/target/sysroot lock. The audit host
happened to have Fedora `rustc/cargo 1.97.1`; it had no `rustup` or `maturin`.
Those host facts are not a production toolchain.

The standalone core `uv.lock` has 56 package records and also only names
registry artifacts. Neither Python lock materializes Rust crates, a linker,
system libraries, cross-target tools, wheels, or a final base image.

### Released core wheel is not a proven source substitute

Public PyPI JSON for `pydantic_core==2.48.0` was inspected only as registry
metadata:

```text
metadata response sha256:
  2e2e504390780c9011f1f2d18f6ee3f6d5dbe4520aa26457220de0c57d24920f
files:       137 (136 wheels, 1 sdist)
total bytes: 290,605,890
sdist:       pydantic_core-2.48.0.tar.gz
             479,692 bytes
             sha256:8714f70dafdffea0a5596cc88eddbdc71f5856563947970dcbd0f1ced61ed05f
```

The matrix is ABI/platform-specific across CPython versions, free-threaded
builds, PyPy, GraalPy, macOS, Windows, manylinux, musllinux, multiple CPU
architectures, and Emscripten. For one concrete target, the CPython 3.12
manylinux2014 x86-64 wheel is:

```text
filename: pydantic_core-2.48.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
bytes:    2,074,576
sha256:   3463fb9e857362b896f345f6c4349d20b817865a05eb570bf838d7c406536412
native extension bytes: 4,725,504
native extension sha256:
  22e6314ee50eac652f694d9d83da814d524028edc13905181fb0cd6d8f083399
ELF dependencies: libgcc_s.so.1, librt.so.1, libpthread.so.0,
                  libdl.so.2, libc.so.6, ld-linux-x86-64.so.2
observed maximum GLIBC symbol version: GLIBC_2.14
```

That wheel is not stored here and is not an approved dependency artifact.
More importantly, the report-era monorepo reference is
`core-v2.48.0-25-gaeeefbe`: compared with tag commit
`5922459fcf33d9a8767fd0fd25a982bbf0d7668d`, six `pydantic-core` paths had
changed (135 insertions and 33 deletions) while project metadata still declared
`2.48.0`. The paths include core schema, serializer/validator Rust modules, and
a core garbage-collection test. Therefore the released wheel cannot silently
stand in for the reference workspace implementation.

A future task owner must approve one coherent scope:

1. require the generated repository to build the exact monorepo Rust core from
   a pinned compiler/target and vendored crates; or
2. define an exact released core wheel as an external runtime dependency,
   freeze one platform/ABI artifact, and explicitly accept that substantial
   validation/serialization behavior is supplied by upstream native code.

The second option changes what the repository-generation task measures and can
be a contamination/scaffolding risk; the first requires a much larger native
build closure. This audit does not make that product decision.

## Duplicate Audit

The candidate report says it screened normalized package-name duplicates
against the 104-task legacy baseline. That baseline was independently
reproduced by sorting the current `test_files/` directory names, writing one
name per line with a final newline, and hashing the bytes:

```text
legacy task directories: 104
sha256: 31fd544eb261f084ffca370ea02515950a8538cdf144b0fdb9052f67b5e76cc7
```

That matches the report's `existing_legacy_task_ids_sha256`. Current local
checks found:

- no exact or PEP-503-style normalized `pydantic` directory under
  `test_files/`;
- no exact or normalized `pydantic` task ID among existing catalog TOML files;
- no existing catalog source URL equal to
  `https://github.com/pydantic/pydantic`; and
- no other occurrence of that upstream URL in task records.

The catalog does contain independent validation/data-model projects such as
`attrs`, `cattrs`, `marshmallow`, `schema`, and `validators`, plus projects that
use Pydantic as a dependency. They are not repository/ID duplicates based on
available metadata. Final publication still needs a human semantic-duplicate
review; this static audit does not certify that a broad Pydantic task is not
behaviorally overrepresented by those adjacent tasks.

## Separate-Verifier Feasibility

The production generic Python client in
`src/nl2repobench/verification/candidate_client.py` JSON-encodes one request,
starts a fresh untrusted child, imports candidate code only there, and requires
a JSON-serializable response. It provides no persistent object handles or
callback/class definition protocol.

Static import inventory found 490 direct `pydantic`/`pydantic_core` import
statements in root test Python files and 164 in core test Python files. The
suite constructs and retains behavior that cannot cross the generic boundary:

- dynamically declared `BaseModel`, dataclass, `TypedDict`, named-tuple, enum,
  generic, recursive, deferred-annotation, and custom-schema classes;
- live validators, serializers, decorator callbacks, descriptors, computed
  fields, factories, plugins, and validation context;
- arbitrary Python inputs/outputs including classes, callables, generators,
  dates, decimals, UUIDs, paths, IP/network objects, secrets, exceptions,
  native URL objects, and native validator/serializer instances;
- rich `ValidationError` trees and user-defined exception behavior;
- process-local caches, module creation, monkeypatching, warnings, pickling,
  garbage collection, plugin registration, and repeated object operations; and
- native `SchemaValidator`/`SchemaSerializer` behavior whose identity and
  Python-object interaction are observable.

Running those public tests as trusted/root pytest with direct candidate imports
would violate the required verifier boundary. A production task needs a
Pydantic-specific child-side scenario/RPC adapter that declaratively builds
allowlisted types and callbacks in the untrusted child, preserves state for a
scenario, and returns normalized JSON-safe observations while hidden expected
values remain private. No such adapter, narrowed reviewed contract, private
test bundle, or command-plan artifact exists.

## Review Findings and Reopen Conditions

1. **BLOCKER — `reports/python-package-candidates.v1.json:42`:** the candidate
   row has no immutable revision; eight same-day upstream commits satisfy the
   recorded date, so source identity cannot be inferred safely.
2. **BLOCKER — reference `pyproject.toml:46-51` and
   `pydantic/version.py:7-97`:** Pydantic requires an exact native core and
   rejects an incompatible version, but no final core source/wheel policy is
   approved.
3. **BLOCKER — reference `pydantic-core/Cargo.toml`, `Cargo.lock`, and
   `pyproject.toml`:** the native build requires Rust/Maturin and 100 locked
   registry crates; no vendored crate closure, compiler/target lock, or
   offline build artifact exists.
4. **BLOCKER — reference `tests/` and `pydantic-core/tests/`:** no final-image
   collection, fixed denominator, skip/xfail policy, private adapted test
   bundle, or allowlisted command plan exists.
5. **BLOCKER — `src/nl2repobench/verification/candidate_client.py`:** the
   generic fresh-process JSON contract cannot represent the class/callback/
   native-object/stateful upstream behavior, and no task-specific adapter is
   available.
6. **BLOCKER — authoring lifecycle:** no immutable base image, dependency
   artifact, Oracle bundle, three valid Oracle runs, empty/stub/forgery/offline
   controls, traceability review, or blind review exists.
7. **MEDIUM — duplicate policy:** mechanical ID and upstream-URL checks are
   clean, but adjacent validation/data-model tasks still require human semantic
   review before dataset integration.

Reopen only after an owner supplies or approves a full upstream SHA. Then:

1. repeat the archive, tree, license, LOC, API, and test inventories at that
   exact revision;
2. approve whether exact monorepo core source or one immutable released native
   wheel is part of the candidate/runtime contract;
3. freeze a digest-pinned OS/Python/ABI/base image and complete hash-locked
   Python, Rust, build-tool, and system-library closure, then prove a clean-cache
   no-network build/install;
4. create authorized private test and command-plan artifacts outside this
   public directory and implement/review the Pydantic-specific child adapter;
5. collect structured node IDs in the final verifier, define skip/xfail/xpass
   semantics, and freeze the denominator;
6. write a behavior-only public instruction with bidirectional test
   traceability; and
7. run three independent valid Oracle trials plus empty, stub, forgery, and
   offline controls before review or publication.

## Commands and Scope

Principal commands used against public or local evidence were:

```text
sha256sum reports/python-package-candidates.v1.{md,json}
git log --follow -- reports/python-package-candidates.v1.json
git ls-remote --symref https://github.com/pydantic/pydantic.git ...
git clone --filter=blob:none --no-checkout --depth=300 <upstream> <tmp>
git checkout --detach aeeefbeabadc3179ecd3738216a95f61e7f4e0d9
git log/rev-list/show/describe/submodule/status at the temporary checkout
git archive --format=tar HEAD | sha256sum  # repeated twice
Python AST and line inventories over tracked reference source/test paths
uv lock --check --project <reference>
uv lock --check --project <reference>/pydantic-core
cargo fetch --locked --offline --manifest-path <reference>/pydantic-core/Cargo.toml
curl public PyPI JSON and one CPython 3.12 manylinux x86-64 core wheel
unzip, sha256sum, file, and readelf on that temporary wheel
normalized task-ID/source-URL duplicate checks over catalog/tasks and test_files
```

The expected negative Cargo probe exited 101 because no crate cache was
available; it is recorded as missing offline closure, not as a source or model
test failure. A commit-specific GitHub license API request was rate-limited
with HTTP 403, so no API response is used as evidence; license observations
come from Git blobs and project metadata in the detached public reference.

No dependency sync for the upstream source, native build, pytest collection or
execution, Docker/Harbor command, private artifact access, Oracle, control,
secret use, generated manifest, or shared-file mutation was performed. The
only tracked repository artifact created by this audit is this `blocked.md`.

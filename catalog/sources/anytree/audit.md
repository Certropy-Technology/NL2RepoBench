# `anytree` Static Authoring Audit

Status: **controls-passed** for the bounded, Graphviz-free production contract.
This file began as a static authoring audit; the remediation now materializes
the private lock, verifier, Oracle bundle, Docker image definitions, controls,
and generated Harbor task under their task-local/content-addressed locations.
The historical source-only observations below remain useful provenance, but
they do not override the current lifecycle or production evidence.

## Decision and Scope

The exact source revision is coherent and the local tree, traversal, search,
resolver, rendering, JSON/dictionary, and Mermaid behavior forms the bounded
candidate boundary. The initial source-only audit was blocked by missing
packaging and verifier evidence; remediation subsequently supplied those
artifacts, froze a 19-leaf child-side contract, and passed the production
Oracle and controls. The task does not claim full upstream pytest parity.

The public task deliberately excludes Graphviz. The upstream package includes
DOT generators, but `DotExporter.to_picture()` writes a temporary file and
invokes the external `dot` command. The host used for this audit has no `dot`
executable. The safe candidate surface is therefore tree behavior and local
text/dictionary/JSON/Mermaid rendering only.

The only durable write root for this audit is `catalog/tasks/anytree/`.
`/tmp/anytree-audit`, disposable build outputs, and probe output files are
not task artifacts and were not copied into the catalog.

## Candidate Identity

- Distribution/import package: `anytree`.
- Upstream: `https://github.com/c0fec0de/anytree`.
- Requested and resolved revision:
  `2e0a1b956172654d75aff93277ce3d883355e0bf`.
- Commit tree:
  `f54c043868ab776b40accc3249fdd9de3cb4b932`.
- Parent:
  `b8c1d254f058f02cfd5e4e9dcd1f736930b79e13`.
- Subject: `Merge pull request #274 from c0fec0de/remove-six`.
- Author and committer time: `2025-04-08T23:01:34+02:00`.
- The resolved commit is the `main` head and points at tag `2.13.0`.
- Detached checkout was clean after inspection and has no submodules.
- The source file `src/anytree/__init__.py` reports
  `__version__ = "2.12.1"`, which differs from the SCM-derived distribution
  version. This is retained as a build/provenance risk, not normalized away.

## Archive and Apache License Evidence

The source lock is an unprefixed Git archive from the exact detached commit:

```text
command: git -C /tmp/anytree-audit archive --format=tar HEAD
archive members including directories: 168
archive bytes: 696320
sha256 (three independent runs):
  bc253cb8287fdbeae24cf78801f81024fcc4317541a6334419582378940b28ce
```

The tree has 129 tracked files. The source-only partition has 40 archive
members including directories and SHA-256
`6dae569f8f3f8a069ffe3b0e568f07de28af3c528df72bb747bab0e7fc8a67dc`.
The test partition has 69 members and SHA-256
`456f6647516a927670b852d788b27ed80898519dff1a3f53227a55edca01901c`.
Partition hashes are audit observations, not additional source locks.

License evidence is internally consistent:

- path: `LICENSE`;
- size: 11,357 bytes and 201 lines;
- Git blob: `8dada3edaf50dbc082c9a125058f25def75e625a`;
- file SHA-256:
  `b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1`;
- the file is the Apache License, Version 2.0; and
- `pyproject.toml` declares `license = "Apache-2.0"`.

No license bytes or upstream source bytes are duplicated in this task
directory. The digest and blob identity are provenance evidence only.

## Package Boundary and Source-Only LOC

The installable package boundary is `src/anytree/`, selected by
`[tool.pdm.build] includes = ["src/anytree"]`. It contains 33 tracked Python
files. Counts use physical lines, nonblank lines, and noncomment lines where a
comment line is a nonblank line whose left-stripped text starts with `#`;
docstrings remain counted. This is the source-only count, not a test or docs
count:

| tree | Python files | physical | nonblank | noncomment |
| --- | ---: | ---: | ---: | ---: |
| `src/anytree/**/*.py` | 33 | 4,056 | 3,417 | **3,365** |
| safe candidate after excluding DOT modules | 31 | 3,584 | 3,022 | **2,977** |
| `tests/**/*.py` | 26 | 3,472 | 2,869 | 2,825 |

The full implementation is in the Medium band under the repository's
1,500-4,000 source-line convention. The safe boundary remains Medium as well.
The excluded modules are `src/anytree/dotexport.py` (11 noncomment lines) and
`src/anytree/exporter/dotexporter.py` (377 noncomment lines).

The package has no tracked C, Cython, Rust, shared-library, `binding.gyp`,
`pyx`, or native binary files. Runtime imports are standard-library modules
plus sibling `anytree` modules. `cachedsearch.py` attempts an optional
`fastcache` import and supplies a `functools` fallback; `fastcache` is not a
declared runtime dependency.

## Metadata and Dependency Review

Values below were parsed from the exact checkout rather than inferred from
PyPI:

- project name: `anytree`;
- Python requirement: `>=3.9.2,<4.0`;
- project runtime dependencies: `[]`;
- build backend: `pdm.backend`;
- build requirement: unpinned `pdm-backend`;
- package include: `src/anytree`;
- dynamic project field: `version`; and
- SCM configuration: `source = "scm"`, `fallback_version = "0.0.0"`.

The tracked `uv.lock` has SHA-256
`1c12025382c91e8dbe36b4c48c2b59c8802a8e1307386d672d1e75a0f0382a94`.
It is a development lock containing pytest, test2ref, coverage, lint,
documentation, and other tooling records; it is not an approved offline
DependencyBundle. The lock has no `pdm-backend` package record, so the PEP 517
build requirement is not closed by the source lock.

A clean source-only import under `python3 -S` (site packages disabled) passed:

```text
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -S ...
import=anytree
version=2.12.1
runtime_dependencies=none_observed
```

Both disposable wheels produced by `uv build --offline` had no
`Requires-Dist` metadata. This proves only that the package declares no runtime
dependencies; it does not prove an approved build/test dependency closure.

## SCM Build Risk

The dynamic version configuration is not archive-safe by itself. Two bounded
offline builds used the exact tree without changing source files:

| input | result | metadata version | observation |
| --- | --- | --- | --- |
| detached Git checkout | wheel and sdist built | `2.13.0` | SCM metadata is available from `.git` |
| unpacked `git archive` without `.git` | wheel and sdist built | `0.0.0` | PDM emitted `Can't get a valid version from scm, use fallback_version instead` |

Both wheels still contain `__version__ = "2.12.1"` in the runtime module.
This creates three visible version values (`2.13.0`, `0.0.0`, and `2.12.1`)
depending on build context. A production task must choose and lock a
deterministic source-only build/version policy before freezing packaging
assertions. The public instruction requires an archive build not to depend on
`.git`, but this candidate is not approved until that policy and an offline
`pdm-backend` artifact are recorded.

## Pytest Collection Evidence

The source `pyproject.toml` has default addopts for coverage, doctests,
HTML coverage, logging, and JUnit output. The bounded audit intentionally
overrode those options and disabled ambient plugin autoload so collection
would measure the tracked test modules rather than an unpinned local plugin
environment.

Final collection command:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
uv run --no-project --with pytest==8.3.5 --with test2ref==0.8.1 \
python -m pytest --collect-only -q -p no:cacheprovider -o addopts='' tests
```

Probe runtime: CPython `3.12.11`, pytest `8.3.5`, test2ref `0.8.1`. Two
independent runs each exited zero and reported:

```text
163 tests collected
normalized node-id SHA-256:
  233f238396cde57636829f33c276ded9bf285b0c90f3e407cab46a8f39558348
```

The raw outputs differ only in timing summaries. The normalized node lists
matched byte-for-byte. `test2ref` is imported by four reference-data modules;
without it, the first bounded probe failed closed during collection with four
`ModuleNotFoundError` errors and only 143 items collected before interruption.
That failure is evidence that the development test closure is incomplete until
the dependency is explicitly provisioned.

The 163 source items include 15 items from the three DOT-related test modules:

```text
tests/test_dotexport.py             3
tests/test_dotexporter.py          6
tests/test_uniquedotexporter.py    6
```

The Graphviz-free collection excludes those three modules and collects 148
items with normalized node-id SHA-256
`d5d35e00d61141b5f7fec9e73042d2dff1fccd93989857a3919d98a9d01e0d47`.

A source-only behavior baseline for that safe collection also passed:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
uv run --no-project --with pytest==8.3.5 --with test2ref==0.8.1 \
python -m pytest -q -p no:cacheprovider -o addopts='' \
  --ignore tests/test_dotexport.py \
  --ignore tests/test_dotexporter.py \
  --ignore tests/test_uniquedotexporter.py tests

148 passed in 0.74s
```

This remains a source baseline only; it is not the production Oracle result.
The remediation separately freezes a 19-leaf child-side contract in
`tests.expected_total = 19` and records collection against that denominator
in the Harbor evidence. The 148-item upstream baseline must not be substituted
for the bounded production denominator.

## Deterministic Tree and Rendering Boundary

The public inventory and source review cover:

- `Node`, `AnyNode`, `NodeMixin`, `LightNodeMixin`, `SymlinkNode`, and
  `SymlinkNodeMixin` relationship invariants, hooks, paths, depth, height,
  descendants, leaves, siblings, and atomic attach/detach behavior;
- preorder, postorder, level-order, grouped, and zigzag iterators;
- `RenderTree` rows, multiline `by_attr`, four fixed styles, repr, and exact
  Unicode branch characters;
- search functions, cached-search fallback, resolver wildcard/relative/
  absolute paths, walker paths, and sibling/common-ancestor utilities; and
- dictionary, JSON, and Mermaid exporter/importer behavior.

A bounded fresh-process probe built the same ordered tree and compared
JSON-safe projections of traversal, render rows/text, search, resolver,
dictionary/JSON round trips, and Mermaid lines under three hash seeds:

```text
PYTHONHASHSEED=1       75d197d610b023babb1186633e39898f1cdd140892b1c23bd580ba01e74bc540
PYTHONHASHSEED=2       75d197d610b023babb1186633e39898f1cdd140892b1c23bd580ba01e74bc540
PYTHONHASHSEED=random  75d197d610b023babb1186633e39898f1cdd140892b1c23bd580ba01e74bc540
```

The outputs were byte-identical. This supports the fixed-input determinism
boundary; it does not make user callbacks, object identity, hash values,
filesystem ordering, or arbitrary user attribute reprs deterministic.

## Graphviz Exclusion Evidence

The source importer scan found no Python Graphviz dependency. The DOT module
does, however, contain:

```text
from subprocess import check_call
from tempfile import NamedTemporaryFile
DotExporter.to_picture(...) -> check_call(["dot", ...])
```

`DotExporter.to_dotfile` is local text generation, but it belongs to the same
excluded DOT surface. `tests/test_dotexport.py` marks the picture test with a
`dot` executable check; `dot` was absent on the audit host. No Graphviz test
was executed. DOT names, DOT refdata, `UniqueDotExporter`, and the legacy
`RenderTreeGraph` are not part of the public score surface.

Mermaid generation is retained because it only returns/writes deterministic
text and does not invoke a renderer.

## Bounded Contract and Reopen Conditions

The production task freezes 19 deterministic JSON scenarios covering the safe
tree, traversal, path, rendering, and import/export surface. The separate
verifier imports candidate code only in an unprivileged child process, and the
Graphviz/DOT surface remains explicitly excluded because it requires the
external `dot` executable. Reopen the task if the public instruction, source
revision, dependency closure, verifier bundle, or frozen denominator changes;
those changes require a new production compile and fresh Oracle/control
evidence. Review, traceability review, and model pilot are publication-stage
follow-ups outside this remediation goal.

## Validation Commands

The bounded validation record includes:

- exact-SHA remote resolution, detached checkout, tree/parent/tag/submodule
  checks, clean status, repeated archive hashing, and license hash/blob checks;
- tracked package inventory and source-only LOC counts;
- `tomllib` parsing of project/build/runtime/dev metadata and static import/
  native-marker scans;
- `python3 -S` import and local tree smoke probe with site packages disabled;
- two full source collect-only probes and a Graphviz-free collect-only probe;
- a Graphviz-free source baseline (`148 passed`);
- three hash-seed deterministic behavior probes; and
- Git checkout versus source-archive `uv build --offline` comparisons.

These commands provide audit evidence, not publication approval.

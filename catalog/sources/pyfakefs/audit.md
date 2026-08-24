# `pyfakefs` Authoring Audit

Status: **blocked**. This file records bounded provenance, license, source-size,
and test-framework evidence for `pytest-dev/pyfakefs`. It contains no task
metadata, public instruction, copied tests, hidden assertions, Harbor assets,
verifier, Oracle, dependency bundle, or shared catalog edit.

## Scope And Decision

The candidate is suitable for further investigation as a filesystem and test
integration library, but it is not ready for task packaging. The canonical
upstream suite is an in-process `unittest` aggregator, not a simple pytest
collection. Its complete CI coverage also changes with optional data-library
dependencies, operating system, interpreter, privilege, and real-filesystem
mode. Those dependencies and environment branches do not currently have a
hash-locked offline closure or a frozen verifier contract, so the candidate
remains blocked.

Only `catalog/tasks/pyfakefs/audit.md` is a durable repository output from this
audit. The detached checkout and all probes were temporary material under
`/tmp`. No long test or property baseline was run.

## Exact Source And Archive

The source was obtained from
<https://github.com/pytest-dev/pyfakefs> and detached at the full commit
resolved from `refs/heads/main` on 2026-08-23:

```text
commit:          a07cb07ee9ae0f78233fa382bf48dcaf6ccc2d99
tree:            ffedf18248d95c8170106a6add2bb89628fb33c4
parent:          ecf5f43785b35c4bb5c1399f3d49a729f2a112ef
author date:     2026-07-27T00:22:47Z
committer date:  2026-08-22T20:21:46+02:00
subject:         Bump actions/setup-python from 6 to 7
nearest tag:     v3.4.3-837-ga07cb07
source version:  6.3.dev0 (pyfakefs/__version__)
submodules:      none observed
```

The source lock is the direct, unprefixed Git archive from that commit. Two
independent `git archive --format=tar HEAD` streams produced the same result:

```text
archive members: 121
archive bytes:   1464320
archive sha256:  667cc2737b759f02491d24c04bbf73daf5e409bcd1d5ee3dd86e5fed1764c788
```

No archive bytes were copied into this repository. The commit is not a release
tag; a future task must continue to use the full SHA rather than the branch or
nearest-tag description.

## License Evidence

The root `COPYING` file is the Apache License, Version 2.0. The declaration in
the exact `pyproject.toml` independently reports `license = "Apache-2.0"` and
lists `COPYING` in `license-files`.

```text
path:       COPYING
bytes:      10142
Git blob:   67db8588217f266eb561f75fae738656325deac9
sha256:     09e8a9bcec8067104652c168685ab0931e7868f9c8284b66f5ae6edae5f1130b
```

The license text contains the standard Apache 2.0 grant, notice, and warranty
disclaimer. This is license evidence only; no distribution approval is implied
by this audit.

## Source-Only LOC

The runtime boundary is the 16 tracked Python files immediately under
`pyfakefs/`. It includes the public pytest plugin and patched-package support,
and excludes `pyfakefs/tests/`, `pyfakefs/pytest_tests/`, fixtures, and other
non-runtime files. The tracked `_version.py` is included because it is part of
the exact source tree.

| boundary | Python files | physical lines | nonblank | nonblank/noncomment |
| --- | ---: | ---: | ---: | ---: |
| runtime `pyfakefs/*.py` | 16 | 11,692 | 9,996 | **9,468** |
| `pyfakefs/tests/**/*.py` | 27 | 17,378 | 14,884 | 14,121 |
| `pyfakefs/pytest_tests/**/*.py` | 24 | 662 | 489 | 377 |

The runtime nonblank/noncomment count is in the repository's hard size band
(`>= 4,000` implementation LOC). Test counts and line counts above are source
inventory only; they are not a frozen score denominator.

## Test Framework And Official Commands

The primary official test path is standard-library `unittest`:

```text
python -m pyfakefs.tests.all_tests
```

`pyfakefs/tests/all_tests.py` directly imports 14 test modules, feeds them to
`unittest.defaultTestLoader`, and runs the resulting `unittest.TestSuite` with
`unittest.TextTestRunner`. The tree has 15 `*_test.py` modules under
`pyfakefs/tests/`; `performance_test.py` is not included by the aggregator.
A bounded static scan found 1,396 `test_*` method definitions in that tree,
but no collection or full-suite run was performed, so this is not a frozen
total.

The secondary integration path is pytest. `pyproject.toml` declares the
pytest entry point `fakefs = "pyfakefs.pytest_plugin"`; the development group
requires `pytest>=6.2.5`, and the pytest tree contains 10 `*_test.py` modules.
The source and CI invoke, among other commands:

```text
python -m pytest pyfakefs/pytest_tests/pytest_plugin_test.py
pytest pyfakefs/pytest_tests
cd pyfakefs/pytest_tests/ns_package && pytest --log-cli-level=INFO test
```

These pytest checks exercise the plugin fixtures and reload behavior; they do
not replace the unittest aggregator.

## Integration Dependency Blockers

The source declares no runtime `Requires-Dist`, but the official test and
integration closure is broader and is not hash locked:

- The `dev` group supplies an unpinned lower bound, `pytest>=6.2.5`.
- The `extra` group pins `pandas==2.3.3`, `xlrd==2.0.2`, and
  `openpyxl==3.1.5`. `pyfakefs/tests/patched_packages_test.py` conditionally
  defines pandas CSV/table tests, plus Excel tests requiring pandas with xlrd
  or openpyxl. Omitting these packages changes which unittest methods exist,
  so a single bare-stdlib run would silently reduce coverage.
- `pyfakefs/pytest_tests/pytest_reload_pandas_test.py` conditionally imports
  `pandas` and `parquet`; the CI job installs `pandas`, `parquet`, and
  `pyarrow`. `pyfakefs/patched_packages.py` also has optional pandas,
  `pyarrow`, and Django patch/reload paths.
- The CI workflow separately installs `zstandard` and `cffi` for regression
  coverage, and its static-analysis job installs Django and pyarrow. These are
  source-observed integration requirements, not a verified offline bundle.

The upstream workflow runs the unittest suite both with and without extra
packages, under non-root and root modes where supported, and with
`TEST_REAL_FS=1` for real-filesystem coverage. Its matrix spans Linux, macOS,
Windows, CPython 3.10 through 3.15, and PyPy. Symlink permissions, root
behavior, platform path semantics, temporary files, and real-versus-fake I/O
therefore affect behavior. A generic candidate subprocess boundary cannot
claim parity with this suite without an explicit task-specific adapter and a
reviewed OS/interpreter policy.

## Blocking Gates And Work Not Performed

Keep this candidate blocked until a future authoring stage provides all of the
following:

1. A final OS/interpreter image and hash-locked offline build, pytest, and
   optional-integration dependency closure.
2. A deterministic policy for the unittest aggregator, pytest plugin tests,
   extra-package branches, root/non-root behavior, and real-filesystem tests.
3. A child-side adapter and separate verifier that preserve the observable
   filesystem, patching, platform, and integration semantics without importing
   the candidate in the trusted grader.
4. Frozen collection, Oracle, empty/stub/forgery/offline controls, and review
   artifacts.

This lane did not run `python -m pyfakefs.tests.all_tests`, the full pytest
tree, property tests, an Oracle, hidden tests, Harbor, or any scoring/control
experiment. It performed only Git metadata/archive/license checks, source LOC
counting, and bounded source inspection.

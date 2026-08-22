# `tomlkit` Static Authoring Audit

Status: **blocked**. This directory contains task-local evidence only. It has
no task descriptor, public instruction, Harbor bundle, private test bundle,
hidden-test cache, Oracle solution, Docker asset, or shared catalog update.
No full test body run was performed.

## Decision

Do not advance `tomlkit` beyond static authoring. The exact public source is
coherent and has no runtime third-party dependencies, but production use is
blocked by four independent gaps:

1. The PEP 517 backend requirement `poetry-core>=1.0.0a9` is unpinned and is
   absent from the committed Poetry lock. An empty-cache offline editable-build
   probe failed before building because `poetry-core` was unavailable.
2. The default test suite requires the pinned `tests/toml-test` git submodule.
   The root source archive contains only a gitlink, so collection fails without
   the submodule.
3. The observed 1,051-node collection is source-only evidence, not a frozen
   final-image denominator. No immutable verifier image, authorized command
   plan, private test artifact, or metric record exists for this task.
4. Upstream tests import internals and exercise rich mutable Python objects,
   exact formatting, filesystem paths, pickle, and process-local custom
   encoder state. The generic JSON subprocess contract cannot preserve the
   complete suite without a task-specific child adapter.

Keep the candidate blocked. Do not run Oracle, controls, Docker, or a trusted
direct-import verifier until the missing environment, artifacts, collection
contract, and adapter are separately reviewed.

## Candidate And Source Lock

- Upstream: `https://github.com/python-poetry/tomlkit`.
- Requested and resolved revision:
  `d8ed1e3cdb024dfc2c6f12b45a0dfd4d4d91f727`.
- Disposable detached checkout: `/tmp/nl2repo-candidates/tomlkit`.
- Commit tree: `1af692f3944e67c7de962dc8094faf184ec3427f`.
- Parent: `94e62fbef9d16093dec86728888474197f4a5cc7`.
- Subject: `chore: release 0.15..1 (#564)`.
- Commit time: `2026-07-17T09:49:51+08:00`.
- Checkout was detached at the requested SHA and clean after inspection.
- Distribution/import package: `tomlkit`; version: `0.15.1`.
- Root tracked files: `81`.

The root checkout has one submodule, initialized only in `/tmp` for the
collection probe:

- Path and URL: `tests/toml-test`,
  `https://github.com/BurntSushi/toml-test.git`.
- Pinned commit: `08ed8697864548b3cdb4b8decbf496bef47e1c82` (`Release 2.1`,
  `2025-12-27T01:08:02Z`).
- Submodule files: `1,042` total, `1,017` under `tests/`.
- Submodule archive: `1,310,720` bytes,
  SHA-256 `8f1c7ae0ff8b245c41712ac4175e51605e5960f0f9e1ab287203191b31a3dcaa`.
- Submodule `LICENSE`: `1,079` bytes,
  SHA-256 `01ef58ee6449fa01a284c10808e27800d66bfea271bc29281125ff8e5642b86f`.

No submodule content was copied into this repository.

## Archive And License

Repeated `git archive --format=tar HEAD` runs on the root commit matched:

- archive size: `542,720` bytes;
- archive SHA-256:
  `16c73ff25629e5975f1b64579d8b78d0f3c1831c1a94fa59509238afe6a3f07c`.

The root archive is not self-contained because it does not contain the
submodule bytes. License evidence agrees between source metadata and bytes:

- `LICENSE` is MIT, `1,062` bytes;
- `LICENSE` SHA-256:
  `f2f9b460ba719da6626add264d3782f275a4ff7aab677beda08b330911e23adb`;
- `pyproject.toml` declares `license = "MIT"`.

Supporting exact-checkout hashes:

- `pyproject.toml`: `780e61fc1fc1c1ddb7641eeeb66fc36c932877b7f0a12372c90c47bd18412b41`;
- `poetry.lock`: `59b8b98f0a3c1d33b6b6bc489470a0f06049aa35fc993316c04e4f13cf6b47db`;
- `.gitmodules`: `24946fbac24df47b147d94dd00e4afd3a7b8c1d32d7cd72a8f6806688796a7e3`.

## LOC And API Inventory

The discovery record reports `Hard`, source SLOC `4,631`, public API estimate
`81`, `12` test files, `241` static definitions, and zero runtime dependencies.
The exact checkout independently measures:

| tree | Python files | physical lines | nonblank | noncomment* |
| --- | ---: | ---: | ---: | ---: |
| `tomlkit/*.py` | 12 | 6,187 | 5,010 | **4,631** |
| `tests/*.py` | 12 | 4,572 | n/a | n/a |

\* Noncomment excludes blank lines and lines whose first non-whitespace
character is `#`; inline comments remain part of their code line.

The root `tomlkit.__all__` has 27 names:

```text
TOMLDocument, aot, array, boolean, comment, date, datetime, document, dump,
dumps, float_, inline_table, integer, item, key, key_value, load, loads, nl,
parse, register_encoder, string, table, time, unregister_encoder, value, ws
```

The module-level API inventory is:

- `tomlkit.api`: `parse`/`loads`/`load`, `dumps`/`dump`, document and item
  constructors, key/value helpers, and custom encoder registration. Core
  signatures include `parse(string: str | bytes) -> TOMLDocument`,
  `dumps(data: Mapping[str, Any], sort_keys: bool = False) -> str`, and
  `dump(data: Mapping[str, Any], fp: IO[str], *, sort_keys: bool = False)`.
- `tomlkit.container`: mutable `Container` and `OutOfOrderTableProxy` for
  mapping operations, dotted-table merge, copying, unwrapping, and rendering.
- `tomlkit.items`: 23 public item/value classes and enums, including
  `StringType`, `Key`, `Item`, `Integer`, `Float`, `Bool`, `DateTime`, `Date`,
  `Time`, `Array`, `Table`, `InlineTable`, `String`, and `AoT`, plus overloaded
  `item()` conversion.
- `tomlkit.exceptions`: 20 public exception classes rooted at `TOMLKitError`;
  `ParseError` exposes `line` and `col`.
- `tomlkit.parser.Parser`, `tomlkit.source.Source`,
  `tomlkit.toml_document.TOMLDocument`, and `tomlkit.toml_file.TOMLFile`.

The `81` figure remains the discovery estimate, not a frozen symbol count:
submodules do not consistently define `__all__`, and tests import documented
classes as well as underscore-prefixed helpers.

## Parser And Document Semantics

This is a style-preserving TOML object model, not merely a JSON parser:

- `parse()`/`loads()` accept `str` or bytes and return a dict-like mutable
  `TOMLDocument`.
- Parsed documents retain comments, whitespace, quote style, key order, dotted
  keys, table/array-of-table layout, and source line endings. `dumps(parsed)`
  round-trips valid source text.
- Mapping access returns typed wrappers such as `Table`, `String`, and `Array`;
  `unwrap()` returns ordinary Python dictionaries/lists/scalars.
- Mutating a document/table updates rendered TOML while preserving existing
  trivia. `item()` converts Python scalars, dates/times, mappings, lists, and
  tuples into typed items.
- `string()` controls literal/basic and single/multiline escaping;
  `array()`, `table()`, `inline_table()`, `aot()`, `key()`, `value()`, `ws()`,
  `nl()`, and `comment()` create or parse document fragments.
- Custom encoder registration is process-global and may pass `_parent` and
  `_sort_keys`; registration/removal is observable state.
- Invalid syntax raises specific `ParseError` subclasses for number/date/time,
  Unicode/control characters, unexpected characters, duplicate keys, and table
  structure, retaining source line and column.
- `TOMLFile.read()`/`write()` use filesystem paths and preserve detected LF,
  CRLF, or mixed-EOL behavior. Tests also require copy/deepcopy and pickle
  round-trips for items and documents.

A direct semantic probe, without running upstream tests, verified comment
round-trip, typed wrappers, `unwrap()`, table mutation, a custom `Path`
encoder, parse error position `1/7`, and CRLF file write. Probe output SHA-256:
`9e979e6e423ca8e68866f55363516663ef27312686d42579b73a8b3278c98e8a`.

## Test Collection

An AST scan found `241` functions beginning with `test` across 9 test modules.
The disposable environment was CPython `3.14.6` with `pytest==7.4.4` and
`-p no:cacheprovider`. Collection only was performed; no test body ran.

Without initializing the submodule, the command exited `2` after reaching 371
nodes and failed while importing `tests/test_toml_tests.py`:

```text
FileNotFoundError: .../tests/toml-test/tests/files-toml-1.1.0
```

The stdout SHA-256 was
`25fd4ae8f9bad1e69fcb22eac90e998f4beab4c4c8fc354a5a9a02e1bc08617f`.

With only the pinned public submodule initialized, two runs exited `0` with no
collection errors and collected 1,051 nodes:

| module | nodes |
| --- | ---: |
| `test_api.py` | 157 |
| `test_build.py` | 4 |
| `test_items.py` | 86 |
| `test_parser.py` | 34 |
| `test_toml_document.py` | 71 |
| `test_toml_file.py` | 8 |
| `test_toml_tests.py` | 680 |
| `test_utils.py` | 7 |
| `test_write.py` | 4 |
| **total** | **1,051** |

Normalized node-ID SHA-256 matched across both runs:
`17c9c9a3813b7c20d3c45f191883c3c1a4b9f5e9f0644ff0ed7adc9181e99406`.
Full output hashes differed only in timing: run 1
`d3d9fd587eee57a877ad17041efbec44791f4555f36477ff6ea8ee968cddfe12`; run 2
`33be375828dccb70537e4c1d56e56647449010fbca3c58e30a2a4c067b75f4cd`.
The 1,051 count is not a frozen verifier denominator.

## Dependency And Build Closure

`pyproject.toml` declares Python `>=3.9`, no runtime dependencies, build
requirement `poetry-core>=1.0.0a9`, and backend
`poetry.core.masonry.api`. Dev dependencies are pytest `^7.2.0`, pytest-cov
`^4.0.0`, PyYAML `^6.0`, pre-commit `^2.20.0`, mypy `1.19.1`, Sphinx
`^4.3.2`, and furo `^2022.9.29`.

`poetry.lock` parses as 51 packages, all `dev`, with Python range `>=3.9` and
content hash `0eec9d00c51b390c077534841b531d85c22a7aa138e622b20525166f6a628967`.
It includes pytest `7.4.4` and pytest-cov `4.1.0`, but no `poetry-core` entry;
it is therefore not a complete build closure or offline wheelhouse.

The runtime import scan found only standard-library imports. Package filesystem
access is confined to `TOMLFile`; no runtime network, socket, HTTP, subprocess,
or service call was found. The submodule generator imports Go/subprocess tools,
but is not a collected test and was not run.

An empty-cache probe:

```text
UV_CACHE_DIR=/tmp/tomlkit-empty-cache uv pip install --offline --no-cache \
  --no-deps --python /tmp/tomlkit-offline-venv/bin/python \
  -e /tmp/nl2repo-candidates/tomlkit
```

exited `1` before building because `poetry-core>=1.0.0a9` was unavailable.
Captured stderr SHA-256:
`e006d985d9995fe15e8d2eb815309f85810fbf53aa00890181b20800a9697b3b`.
This is closure evidence, not an Oracle or model result.

## Candidate Subprocess Adapter Feasibility

The production contract sends JSON-safe arguments to an unprivileged child and
requires a JSON-safe result. A narrowed adapter could support parse a string,
return an unwrapped value, render text, and normalize exception class/position.
The complete upstream suite is not representable by independent generic calls:

- tests directly import `api`, `items`, `parser`, `container`,
  `toml_document`, and `toml_file`, including private helpers;
- tests retain and mutate typed documents/items, inspect exact formatting, and
  use dotted tables, arrays of tables, comments, and trivia;
- tests register Python encoder callables and depend on process-global state;
- tests use datetime/date/time, `Path`, mapping wrappers, file paths, temporary
  files, copy/deepcopy, and pickle; and
- tests call parser internals and assert exception classes plus line/column.

A task-specific adapter would need declarative scenario sequences executed in one
child, tagged date/time/path values, explicit encoder operations, and normalized
JSON observations. It does not exist here. Fresh children per generic call lose
document and encoder state; trusted pytest direct-imports would violate the
separate-verifier boundary.

## Reopen Requirements

1. Freeze a Python/OS/base-image lock and complete hash-locked offline build/test
   bundle, including `poetry-core`, pytest plugins, and transitive artifacts.
2. Resolve the exact public `toml-test` fixture corpus as an immutable source/test
   artifact without publishing private verifier bytes.
3. Recollect in the final image with structured IDs, fixed total, skip/xfail and
   collection-error policy, plus repeated baseline evidence.
4. Review a `tomlkit` child adapter for stateful documents, typed items, encoders,
   parser errors, files/EOL, copy, and pickle, or version a deliberately narrower
   public contract.
5. Only in a later lane provide authorized private tests, command plan, Oracle,
   and empty/stub/forgery/offline controls.

No Docker build, hidden-test materialization, private-cache access, Oracle run,
shared index edit, or full test execution was performed.

## Acceptance Report

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Only catalog/tasks/tomlkit/blocked.md was added with exact-revision static evidence; no implementation, private tests, cache, Docker, Oracle, or shared catalog file was changed."
    }
  ],
  "changedFiles": [
    "catalog/tasks/tomlkit/blocked.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git clone/fetch/checkout https://github.com/python-poetry/tomlkit at d8ed1e3cdb024dfc2c6f12b45a0dfd4d4d91f727",
      "result": "passed",
      "summary": "Detached checkout resolved to the requested SHA and remained clean."
    },
    {
      "command": "git archive --format=tar HEAD | sha256sum (repeated)",
      "result": "passed",
      "summary": "Root archive matched at 542720 bytes with SHA-256 16c73ff25629e5975f1b64579d8b78d0f3c1831c1a94fa59509238afe6a3f07c."
    },
    {
      "command": "git submodule update --init --depth 1 tests/toml-test",
      "result": "passed",
      "summary": "Pinned public submodule commit was resolved in disposable /tmp only."
    },
    {
      "command": "pytest --collect-only -q -p no:cacheprovider tests without the submodule",
      "result": "failed",
      "summary": "Expected FileNotFoundError for tests/toml-test/tests/files-toml-1.1.0 after 371 nodes; exit 2."
    },
    {
      "command": "pytest --collect-only -q -p no:cacheprovider tests with the pinned submodule",
      "result": "passed",
      "summary": "Two runs exited 0 with no collection errors and 1051 nodes; normalized node IDs matched."
    },
    {
      "command": "python3 AST/import/LOC inventory and parser/document semantic probe",
      "result": "passed",
      "summary": "Measured 4631 noncomment package lines and verified round-trip, mutation, encoder, parse-error, and CRLF file semantics."
    },
    {
      "command": "python3 tomllib parse of pyproject.toml and poetry.lock",
      "result": "passed",
      "summary": "Metadata parsed; runtime dependencies are empty and the lock lacks poetry-core."
    },
    {
      "command": "UV_CACHE_DIR=/tmp/tomlkit-empty-cache uv pip install --offline --no-cache --no-deps -e /tmp/nl2repo-candidates/tomlkit",
      "result": "failed",
      "summary": "Expected build-closure failure because poetry-core was absent from the empty cache; exit 1."
    },
    {
      "command": "git status --short and diff check in the task worktree",
      "result": "passed",
      "summary": "Only the task-local blocked audit is present and no files are staged."
    }
  ],
  "validationOutput": [
    "Exact source, submodule, archive, license, pyproject, and lock hashes are recorded.",
    "Package size is 4631 noncomment lines; root __all__ has 27 names and discovery API estimate is 81.",
    "Collection requires the pinned public submodule and observes 1051 nodes; this is not a frozen denominator.",
    "Parser/document semantics, dependency/build closure, and subprocess-adapter feasibility are documented.",
    "Lifecycle remains blocked because final image, offline artifacts, authorized verifier assets, and adapter are absent."
  ],
  "residualRisks": [
    "No immutable final verifier image or hash-locked offline build/test bundle exists.",
    "The root archive is not self-contained because the test corpus is a git submodule.",
    "No full baseline, Oracle, fixed metric denominator, or private artifact exists.",
    "Generic JSON calls cannot preserve complete stateful document, encoder, file, copy, pickle, and parser-internal semantics.",
    "Public source availability creates contamination risk without an explicit later network policy."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added one blocked task-local static audit for tomlkit revision d8ed1e3cdb024dfc2c6f12b45a0dfd4d4d91f727; no generated task, tests, verifier, Docker, Oracle, or shared files were added.",
  "reviewFindings": [
    "No static-authoring evidence category requested by the task is omitted.",
    "Publication is intentionally blocked pending final environment, offline artifacts, authorized verifier assets, and a task-specific child adapter."
  ],
  "manualNotes": "The 1051-node result is collect-only in CPython 3.14.6 with pytest 7.4.4 and the pinned public submodule. Preserve blocked status and do not interpret collection or the expected offline-build failure as Oracle evidence."
}
```

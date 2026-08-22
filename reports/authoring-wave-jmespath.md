# JMESPath Authoring Wave Handoff

This report mirrors the task-local audit at `catalog/tasks/jmespath/blocked.md` and adds the required acceptance record. The audit is intentionally blocked: the pinned source and source baselines are verified, but no private artifacts or production adapter were invented.

# `jmespath` Authoring Audit

Status: **blocked**. This directory contains an audit record only. It does
not contain a task descriptor, public instruction projection, Harbor bundle,
Oracle solution, verifier code, hidden test bytes, or dependency archive.
No legacy task exists at `test_files/jmespath/`, so no legacy denominator or
command plan is being inferred here.

## Decision

Do not publish a task from the current evidence. The pinned upstream source is
coherent and its default test suite is deterministic and local, but the full
suite cannot be moved across the production separate-verifier boundary by the
generic JSON adapter. The suite requires Python objects and process-local
state that JSON requests cannot represent. In addition, no authorized private
test/command artifact, complete offline dependency bundle, or Oracle artifact
has been supplied in this worktree.

The core JSON query path is a plausible future task boundary. It must be
versioned as a deliberately adapted contract, however; reusing the upstream
pytest suite through direct candidate imports would violate the separate
verifier policy, and silently dropping the Python-specific tests would change
the measured task.

## Source Provenance

- Upstream: `https://github.com/jmespath/jmespath.py`
- Requested revision: `2812594e69d43098ef60f81f4efc404c071b0418`
- Resolved commit: `2812594e69d43098ef60f81f4efc404c071b0418`
- Commit tree: `9c54fa72fc42fbef72011798bc3eba3610934541`
- Commit date: `2026-01-22T11:29:18-05:00`
- Subject: `Merge branch 'release-1.1.0' into develop`
- Parents: `5ce13aab582ba08b07e1c615feeb3654a7cd8d62` and
  `17e964f81911b49babb33e8697b34a31f869420f`
- Checkout: detached at the requested full SHA; clean before and after the
  audit
- Archive command: `git archive --format=tar HEAD`
- Unprefixed archive size: `337920` bytes
- Unprefixed archive SHA-256:
  `878aae1a0c13f72226998d07402200365ba0335ce106566bd95077e8abae28b4`
- Submodules: none (the tracked `.gitmodules` file is empty)

The archive was generated directly from the detached commit and was not
repacked or prefixed. The archive and source checkout were temporary audit
material outside this repository.

## License And Package Metadata

The revision contains `LICENSE`, whose first line is `MIT License`:

- Git blob: `9c520c6bbff8c6a0b73416c45775ad31b8156e84`
- Size: `1113` bytes
- SHA-256: `6eefacfa4d71b82d08408c751470ac8d9854538da2142cb27be0287fb13d0ab9`
- SPDX mapping: `MIT`

The source uses `setup.py`, not `pyproject.toml`:

- Distribution and import package: `jmespath`
- Version: `1.1.0` (both `setup.py` and `jmespath.__version__`)
- Python requirement: `>=3.9`
- Build mechanism: setuptools `setup()` with `find_packages()`
- Declared runtime dependencies: none
- Installed script: `bin/jp.py`
- `bin/jp-compliance` is in the source archive but is not listed in
  `setup.py`'s `scripts` argument

A temporary wheel build succeeded as a packaging sanity check:

- File: `jmespath-1.1.0-py3-none-any.whl`
- Size: `20500` bytes
- SHA-256: `0ed697af5092bc84e3dfe583558041d66a75ddfa07794f200ab407ade62a0622`
- Wheel metadata: `Requires-Python: >=3.9` and no `Requires-Dist` entries

The wheel was built with the host `uv` build cache. It is not an approved
offline dependency artifact and is not stored in this task directory.

## LOC And Repository Shape

The installed package has eight Python modules under `jmespath/`:
`__init__.py`, `ast.py`, `compat.py`, `exceptions.py`, `functions.py`,
`lexer.py`, `parser.py`, and `visitor.py`.

For those eight files:

| Measure | Count |
| --- | ---: |
| Physical lines | 1,675 |
| Nonblank, non-comment code lines | 1,274 |
| Comment-only lines | 148 |
| Blank lines | 253 |

The 1,274 code-line count agrees with the discovery record and places the
implementation in the original Easy (`<=1500`) LOC band. The repository also
contains seven Python files under `tests/`, one optional property-test file at
`extra/test_hypothesis.py`, and 17 JSON fixture files (16 compliance files and
one legacy file).

## Query Semantics And API Inventory

The public root API is small and has these exact signatures:

```text
jmespath.compile(expression)
jmespath.search(expression, data, options=None)
```

`compile()` returns a cached `jmespath.parser.ParsedResult`; its
`search(value, options=None)` method evaluates the same compiled expression.
`jmespath.Options` is re-exported from `jmespath.visitor` and has
`Options(dict_cls=None, custom_functions=None)`.

The language and implementation cover:

- unquoted and quoted field identifiers, subexpressions, current-node `@`,
  JSON/raw literals, and Unicode/escape handling;
- list and object access, positive/negative indexes, slices, list/object
  wildcards, projections, flattening, filters, multi-select lists and hashes;
- pipe, `&&`, `||`, `!`, and comparison operators with JMESPath truthiness and
  numeric/string comparison behavior;
- expression references (`&`) used by functions such as `map`, `sort_by`,
  `min_by`, and `max_by`;
- 26 built-in functions: `abs`, `avg`, `not_null`, `to_array`, `to_string`,
  `to_number`, `contains`, `length`, `ends_with`, `starts_with`, `reverse`,
  `ceil`, `floor`, `join`, `map`, `max`, `merge`, `min`, `sort`, `sum`,
  `keys`, `values`, `type`, `sort_by`, `min_by`, and `max_by`;
- custom functions registered through a `Functions` subclass and the
  `functions.signature(*arguments)` decorator;
- parser/lexer error classes including `ParseError`, `LexerError`,
  `IncompleteExpressionError`, `ArityError`, `VariadictArityError`,
  `JMESPathTypeError`, `EmptyExpressionError`, and `UnknownFunctionError`.

The package modules also expose `parser.Parser(lookahead=2)`,
`parser.ParsedResult`, `lexer.Lexer`, `functions.Functions`, AST constructor
helpers, and visitor classes. The AST dictionary shape and
`ParsedResult._render_dot_file()` are implementation-facing details; the
upstream tests nevertheless assert them. A public behavior specification can
describe the JSON query language and supported root API without copying source
or test assertions, but it must explicitly decide whether these Python-level
surfaces remain in scope.

## Test Collection And Baseline

The upstream default test command is `python -m pytest tests` from `tox.ini`.
The GitHub workflow instead installs the requirements and package, changes to
`tests/`, and runs `python -m pytest --cov jmespath --cov-report term-missing`.
There is no repository pytest configuration file. The optional
`extra/test_hypothesis.py` is not included by the default tox command.

Static inventory at the pinned revision:

- 81 `test_*` definitions across the seven `tests/` Python files plus the
  seven definitions in `extra/test_hypothesis.py`;
- the two compliance test definitions expand from JSON fixtures;
- 920 compliance/error parametrized nodes are yielded by the source
  collector, and 72 ordinary test nodes are collected from the other test
  methods;
- the collector walks `tests/legacy` both through `tests/` and explicitly,
  so its nine legacy cases are included twice in the source baseline;
- benchmark-only JSON cases are loaded but intentionally excluded from the
  pytest result/error parametrization.

With CPython `3.14.6` and `pytest==8.4.1`, cache-disabled collection of the
detached source completed as:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with pytest==8.4.1 \
  python3 -m pytest --collect-only -q tests -p no:cacheprovider
992 tests collected in 0.12s
```

The collected node list (992 lines, excluding the summary) has SHA-256
`ddcdb859b7cd9510138d161e4981c3b67f435f08a97a014cbff22971093582e7`.
Three independent direct-source runs used the same cache-disabled command and
JUnit output:

| Run | Collected | Passed | Failed | Errors | Skipped | Wall time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 992 | 991 | 0 | 0 | 1 | 1.667 s |
| 2 | 992 | 991 | 0 | 0 | 1 | 1.677 s |
| 3 | 992 | 991 | 0 | 0 | 1 | 1.740 s |

The one skip is intentional: `test_search.py` skips the Python-2-only long
integer test when `sys.maxint` is absent. These are source baselines only, not
Harbor Oracle results, and `expected_total` must remain unknown until a final
verifier test bundle and collection contract are approved.

The optional extra suite collected 999 nodes when run with
`pytest==8.4.1`, `hypothesis==5.35.4`, `setuptools==71.1.0`, and
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. A first attempt without the pinned
setuptools build/test support failed during Hypothesis plugin import because
`pkg_resources` was unavailable. This makes the optional suite especially
unsuitable for an unpinned offline denominator.

## JSON-Safe Adapter Feasibility

The generic verifier client sends JSON `args`/`kwargs` to an unprivileged
candidate subprocess and JSON-serializes the returned `value`. A local probe
against the pinned source showed:

| Operation/value | JSON result |
| --- | --- |
| `jmespath.search()` over JSON data | serializable |
| `Lexer().tokenize()` token list | serializable |
| `compile(...).parsed` AST dictionary | serializable |
| `compile(...)` / `ParsedResult` object | not serializable |
| `datetime` or `decimal.Decimal` input | not serializable without tagged reconstruction |
| `Options(dict_cls=OrderedDict)` object | not serializable as a request value |
| custom `Functions` instance/function table | not serializable |

The upstream tests directly import candidate modules and exercise the following
non-JSON or stateful behaviors:

1. `Options(dict_cls=OrderedDict)` and ordered output; a class object cannot
   cross the generic JSON request boundary.
2. Dynamically defined custom functions and expression references; a callable
   and subclass cannot cross that boundary.
3. `decimal.Decimal` and `datetime` values, including a `datetime.now()`-based
   test; JSON has no equivalent Python object type.
4. `Parser` cache size/purge and a multi-threaded cache exercise; independent
   one-call child processes cannot observe the same cache or thread behavior.
5. Parsed AST shape, exact parser/lexer exception messages, and
   `_render_dot_file()`; a compile-then-inspect chain must execute inside one
   candidate child and normalize observations explicitly.

Therefore the generic adapter is **partially feasible** for pure JSON
`search()` and selected lexer/AST observations, but it is not a faithful
adapter for the complete 992-node suite. Directly putting upstream pytest in a
trusted verifier would violate the repository policy. A task-specific child
adapter with declarative tagged values, in-child custom-function definitions,
stateful operations, and JSON-safe normalized observations is required before
the full suite can be considered.

## Dependencies And Offline Closure

The package has no runtime dependency according to `setup.py` and the built
wheel. The source test/build requirements are recorded in `requirements.txt`
(SHA-256
`9e07a6cda3633b866cb3668a1e2052593e753076f6899918bf9bdaf6a604cc15`):

```text
wheel==0.45.1
pytest==8.4.1
pytest-cov==3.0.0
hypothesis==5.35.4
setuptools==71.1.0 ; python_version >= '3.12'
packaging==24.1 ; python_version >= '3.12'
```

`tox.ini` declares `pytest` without a version. The requirements file has no
hashes, transitive lock, `--no-index`/wheelhouse declaration, or build-system
pin in a `pyproject.toml`. A transient resolver probe produced a 13-package
environment (including `attrs`, `coverage`, `iniconfig`, `pluggy`, `pygments`,
and `sortedcontainers`), but that result depends on the current package index
and is not an immutable artifact. No task-authorized wheelhouse, content-
addressed dependency bundle, final base-image digest, or private command plan
was supplied.

The default tests themselves use local JSON fixtures and Python standard
library facilities; a static scan found no runtime network endpoint. Thus an
offline verifier is plausible after the complete build/test closure is
materialized, but offline closure is currently **unproven**. The successful
temporary `uv build` only proves that this host's build cache had a usable
setuptools backend; it does not prove a clean no-network source build.

## Blockers And Reopen Conditions

Keep this candidate blocked for authoring/publication. The blockers are:

1. No authorized private test bundle, allowlisted command-plan artifact,
   Oracle bundle, or dependency wheelhouse exists in the task-local scope.
   Creating opaque refs without bytes would be non-resolvable; copying the
   upstream fixture files here would publish test assets.
2. The generic JSON candidate boundary cannot preserve the complete upstream
   API/test behavior described above. Direct candidate imports are disallowed
   in the trusted grader.
3. The source has no complete hash-locked offline build/test closure or pinned
   final verifier image.
4. The source collection count of 992 is a reproducible baseline, not a
   frozen benchmark denominator; the optional Hypothesis suite has a separate
   999-node collection and dependency sensitivity.

To reopen, obtain all of the following:

- an owner-approved task-specific subprocess adapter and scenario contract
  that either preserves the full Python API semantics or explicitly defines a
  new pure-JSON task version;
- private content-addressed tests, command plan, and Oracle artifacts with
  digest/size/visibility metadata;
- a hash-locked offline wheelhouse covering the selected Python version,
  setuptools build backend, pytest/plugins, and all transitive dependencies;

- a pinned final verifier image and a fresh collection/JUnit record;
- three valid stable Oracle runs followed by empty, stub, forgery, and offline
  controls.

No `task.toml`, `instruction.md`, Harbor files, private test bytes, Oracle,
Dockerfile, or shared index was created by this audit.

The task-local change is deliberately limited to this `blocked.md` evidence
record. No tests were added or modified.


## Handoff Summary

Changed only the task-local blocker record plus this required external report. Verified revision `2812594e69d43098ef60f81f4efc404c071b0418`, archive SHA-256 `878aae1a0c13f72226998d07402200365ba0335ce106566bd95077e8abae28b4`, MIT license SHA-256 `6eefacfa4d71b82d08408c751470ac8d9854538da2142cb27be0287fb13d0ab9`, 1,274 implementation code lines, 992 default collected nodes, and three stable source runs of 991 passed plus one intentional skip. No Docker, Harbor, Oracle, secrets, network service, or shared catalog operation was run. No tests were added or updated. The isolated worktree has no staged files.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Only catalog/tasks/jmespath/blocked.md was added under the task directory; no Harbor, private, shared, legacy, Docker, Oracle, or secret artifacts were created."
    }
  ],
  "changedFiles": [
    "catalog/tasks/jmespath/blocked.md",
    "/root/NL2RepoBench/reports/authoring-wave-jmespath.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git -C /tmp/jmespath-source-audit checkout --detach 2812594e69d43098ef60f81f4efc404c071b0418",
      "result": "passed",
      "summary": "Resolved the requested full commit."
    },
    {
      "command": "git -C /tmp/jmespath-source-audit archive --format=tar HEAD | sha256sum",
      "result": "passed",
      "summary": "337920-byte archive matched the recorded SHA-256."
    },
    {
      "command": "sha256sum /tmp/jmespath-source-audit/LICENSE",
      "result": "passed",
      "summary": "MIT license bytes and hash were verified."
    },
    {
      "command": "uv build --wheel --out-dir /tmp/jmespath-dist",
      "result": "passed",
      "summary": "Temporary jmespath 1.1.0 wheel built successfully."
    },
    {
      "command": "PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with pytest==8.4.1 python3 -m pytest --collect-only -q tests -p no:cacheprovider",
      "result": "passed",
      "summary": "Collected 992 nodes."
    },
    {
      "command": "for run in 1 2 3; do uv run --no-project --with pytest==8.4.1 python3 -m pytest -q tests -p no:cacheprovider --junitxml=/tmp/jmespath-baseline-${run}.xml; done",
      "result": "passed",
      "summary": "All three runs reported 991 passed, 1 skipped, 0 failed, 0 errors."
    },
    {
      "command": "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest==8.4.1 --with hypothesis==5.35.4 --with setuptools==71.1.0 python3 -m pytest --collect-only -q tests extra/test_hypothesis.py -p no:cacheprovider",
      "result": "passed",
      "summary": "Optional suite collection reported 999 nodes."
    },
    {
      "command": "git diff --check && git diff --cached --name-only",
      "result": "passed",
      "summary": "No whitespace errors and no staged files in the isolated worktree."
    }
  ],
  "validationOutput": [
    "Pinned source, archive, MIT license, package metadata, and LOC were verified.",
    "Default collection and three direct-source baselines were stable.",
    "Pure JSON operations are feasible, but the full API/test surface needs a task-specific adapter.",
    "Private artifacts, final image, and offline closure are absent, so the task remains blocked."
  ],
  "residualRisks": [
    "No final pinned verifier image, private test bundle, command plan, Oracle, or dependency wheelhouse exists.",
    "The 992-node source baseline is not a frozen benchmark denominator.",
    "A future adapter must preserve rich Python values, custom functions, state, and exact error observations without trusted candidate imports."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added one task-local blocked.md audit record and this required handoff report; no tests or shared files changed.",
  "reviewFindings": [
    "blocker: complete upstream suite is not faithfully representable by the generic JSON candidate boundary",
    "blocker: private artifacts and offline closure are unavailable",
    "no additional scope findings"
  ],
  "manualNotes": "Stop after handoff. Reopen only after the adapter, private artifacts, final offline image, collection record, Oracle, and controls are provisioned."
}
```

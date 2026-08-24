# `click` Static Authoring Audit - Blocked

**Status: blocked.** This directory is an evidence record only. It is not a
task descriptor, public instruction, Harbor bundle, verifier, Oracle bundle,
private test artifact, dependency cache, or publication approval. No hidden
bytes, secrets, Docker/Harbor state, Oracle result, legacy projection, or
shared catalog file is included.

## Audit scope

The requested source is the exact revision
`cbd7a4109da16ce58f54c2a618b4c986e3041fcf` of
`https://github.com/pallets/click`. The audit covered source and license
provenance, package/build metadata, dependency closure, test collection,
CLI/subprocess behavior, and compatibility with the repository's separate
candidate boundary. The upstream checkout was temporary material under
`/tmp`; it was not copied into this task directory.

The only task-local change is this blocked record. Do not create
`task.toml`, `instruction.md`, `harbor/`, private artifact references, or
generated projections from this evidence.

## Source and license lock

- Requested and resolved revision:
  `cbd7a4109da16ce58f54c2a618b4c986e3041fcf`.
- Commit subject: `Run Flask's test suite in the nightly workflow (#3768)`.
- Commit date: `2026-08-16T16:43:41-07:00` for both author and committer.
- Parents: `fc5c7f45da0a4443f60ba2d322fe4bf829977739` and
  `3ee9309b9c1804528842392c461526760bff0035`.
- Commit tree: `4b9f0ce67bab42c2780e67397774e1288acef8d7`.
- The detached checkout was clean and had no submodules. It contains 165
  tracked files.
- Three independent unprefixed archives from `git archive --format=tar HEAD`
  were identical: 1,740,800 bytes and SHA-256
  `1e48394d9815df68dd94d614c90e16f509532a28f906e745da396d929f1eadc1`.
- `LICENSE.txt` is the BSD 3-Clause License. Its Git blob is
  `d12a849186982399c537c5b9a8fd77bf2edd5eab`; it is 1,475 bytes with SHA-256
  `9a8ad106a394e853bfe21f42f4e72d592819a22805d991b5f3275029292b658d`.
- The package tree has 17 Python modules/files under `src/click`. An
  implementation-only count gives 9,483 nonblank, non-comment lines and
  12,649 physical lines. This agrees with the discovery report's Hard-band
  characterization; it is not a publication or difficulty approval.

`pyproject.toml` declares package version `8.5.0.dev`, BSD-3-Clause, and
Python `>=3.10` (`pyproject.toml:1-16`). The source archive is the provenance
anchor; no registry package or mutable tag is substituted for this revision.

## Build and dependency closure

The pinned project has no declared runtime dependency. A static import scan of
`src/click` found only standard-library imports and relative `click` imports;
the Windows-only `msvcrt` import is a standard-library platform module.

The build and test declarations are not yet a complete offline task closure:

- The build backend is `flit_core>=3.11,<4` with
  `flit_core.buildapi` (`pyproject.toml:62-64`). `flit_core` does not have a
  package record in the committed lock, so the build backend remains a
  range-based external input.
- `uv.lock` is committed, has 81 package records, is 258,440 bytes, and has
  SHA-256 `14c74547b7e155a6aca455130da3e6bf08f593fcb29d1d9d9ece49bc4dcf3a87`.
  It is a project development lock, not a task-specific offline wheelhouse.
- The tests dependency group declares only `pytest`
  (`pyproject.toml:48-50`). `uv tree --locked --no-default-groups --group
  tests` resolves the selected test environment to Click plus `pytest==9.0.2`
  and its four transitive packages: `iniconfig`, `packaging`, `pluggy`, and
  `pygments`.
- The repository's default groups also include development, pre-commit, and
  typing tools (`pyproject.toml:80-81`). Those 81 locked packages must not be
  mistaken for the minimal test closure.
- `tool.flit.sdist.include` includes `docs/`, `tests/`, `CHANGES.md`, and
  `uv.lock` (`pyproject.toml:69-75`). A future candidate build must preserve
  the hidden-test boundary even though the public upstream tests are present
  in an upstream source distribution.

An evidence-only `uv build --out-dir /tmp/...` probe succeeded using the host
tool/cache. It normalized the version to `8.5.0.dev0` and produced:

```text
click-8.5.0.dev0.tar.gz       383005 bytes
  sha256 17a27d6e739d2dbe18dc30691606b1fc5ac0e4c5e696a36b6002ff36baa09c27
click-8.5.0.dev0-py3-none-any.whl 124708 bytes
  sha256 7e80c25380488100ea0931dea56e314476565b9dfbf58fd4474d4a8ddf711383
```

The wheel metadata has `Requires-Python: >=3.10`, `License-Expression:
BSD-3-Clause`, and no `Requires-Dist` entries. This proves only that this host
could build the source; it does not prove a clean no-network build. No final
verifier image digest, base-image lock, hash-locked wheelhouse, or offline
build transcript exists for this candidate. Do not use the temporary build
artifacts as a dependency bundle.

## Test collection

The tree contains 46 Python test-support files: 34 ordinary test modules, 10
typing examples, `conftest.py`, and the test-utils package marker. An AST
inventory finds 541 functions whose names begin with `test_` (including nested
test functions and the typing example). Static function definitions are not a
test denominator.

The source collection commands were run with the locked tests group and no
test bodies were executed:

```text
uv run --locked --no-default-groups --group tests \
  python -m pytest --collect-only -q -p no:cacheprovider
```

On the temporary Linux/CPython environment, collection completed without
errors and reported:

```text
1995/32995 tests collected (31000 deselected)
```

The deselection is intentional: `pyproject.toml:83-91` sets
`addopts = "-m 'not stress'"`. With that default removed, all 32,995 nodes
were collected. Selecting `-m stress` collected 31,000 nodes, consisting of
30,000 parametrized thread/stream nodes in
`tests/test_stream_lifecycle.py` and 1,000 pager-cleanup nodes in
`tests/test_utils/test_echo_via_pager.py`. The stress environment explicitly
uses `-m stress` and `--override-ini=addopts=` (`pyproject.toml:178-185`).

Three independent default collection runs each reported 1,995 selected nodes
and produced the same node-list SHA-256
`557b4fac535830a565da75001f7d5c2005e732e72b18f0a3d59387135a4dc2d0`.
This is reproducible source collection evidence, not a frozen benchmark
denominator. A final verifier must recollect its approved private adapter
tests, record structured collection/JUnit output, and version the stress and
platform policy.

The collection shape is environment-sensitive. The suite contains skip/xfail
conditions for Windows, symlink support, file descriptor capture, `cat` and
`sed` availability, and filesystem behavior. The upstream CI matrix covers
CPython 3.10 through 3.14, free-threaded 3.14, PyPy 3.11, Windows, and macOS;
the static Linux collection above cannot establish parity across that matrix.

## CLI and subprocess surface

Click is a library for building user command-line applications, not a
standalone command. The package has no `src/click/__main__.py` and
`pyproject.toml` has no `[project.scripts]` entry. Its examples create user
callbacks and invoke those callbacks through a generated application. Thus a
generic module or console-entry invocation does not exercise the package's
core behavior.

The upstream test surface is strongly in-process and object-oriented:

- 21 Python files use `CliRunner` or `runner.invoke`, with 529 matching lines.
  These tests construct live `Command`, `Group`, `Option`, `Argument`, and
  `Context` objects and define callbacks, generators, custom parameter types,
  and custom command/context/group subclasses.
- 45 of the 46 Python test-support files import `click` or a `click.*`
  submodule. The imports include private modules such as `click._compat`,
  `click._utils`, and `click._termui_impl`, so root-level public exports alone
  do not describe the tested surface.
- Four files contain subprocess/Popen behavior: `tests/test_imports.py`,
  `tests/test_types.py`, `tests/test_termui.py`, and
  `tests/test_utils/test_echo_via_pager.py`, with 28 matching lines.
- `tests/test_imports.py:7-80` starts a child interpreter, patches
  `builtins.__import__`, emits JSON, and checks the import allowlist.
- `tests/test_types.py:131-151` starts `python -bb -c ...` and treats a clean
  child exit as the assertion for bytes/string path handling.
- `tests/test_termui.py:543-602` patches `subprocess.Popen` to inspect editor
  argv, environment, shell behavior, exit status, and error handling. Other
  termui cases run real pager binaries such as `cat`.
- `tests/test_utils/test_echo_via_pager.py:228-259` tracks real pager
  subprocesses and asserts they are reaped; the stress variant repeats this
  1,000 times.

The suite also uses monkeypatch/patch in 13 files, temporary filesystem paths
or files in 12 files, environment manipulation in six files, and fd/stream
capture in multiple files. Examples include `pathlib.Path` and bytes return
values, open file objects, `BytesIO`, `sys.stdout`/`sys.stderr` replacement,
`os.write`/`dup2`, thread pools, logging handlers, environment variables, and
platform-specific console APIs. These are behavior under test, not incidental
test harness details.

## JSON adapter and candidate boundary

The reusable Python candidate client in
`src/nl2repobench/verification/candidate_client.py` sends a deterministic,
sorted JSON request with `module`, dotted `attribute`, `args`, `kwargs`, and an
`operation`. `candidate_runner.py` imports candidate code only in the
unprivileged child, applies process limits, and serializes a bounded response.
Each ordinary call starts a fresh child process. The response path uses
`json.dumps`; a `Path`, file object, Click `Result`, callback, class, context,
generator, exception instance, or other non-JSON return value cannot cross
unchanged. A child-side exception is representable only as its type and
string message.

The generic `run_module` operation cannot target Click because there is no
`click.__main__` module. The generic `run_console` operation cannot target
Click because the distribution declares no console entry point. The generic
`call` operation cannot receive the Python callbacks, custom classes,
`Context` objects, streams, file handles, or stateful resource managers used
by the upstream tests. A fresh process per call also cannot observe the
process-global context stack, stream restoration, repeated invocation state,
or thread interactions tested by Click.

A future Click task would therefore require an owner-approved, versioned
task-specific adapter. At minimum it would have to define:

1. A JSON-safe command description or other reviewed fixture mechanism for
   constructing the command graph, parameter types, callbacks, and custom
   classes inside the candidate child. JSON cannot transport arbitrary Python
   callback code or class identity; choosing a callback DSL would be a new
   task contract.
2. A bounded invocation request containing only allowlisted argv, stdin,
   environment values, color/terminal settings, working-directory fixtures,
   and any explicit multi-invocation/session operation needed for stateful
   tests.
3. A deterministic response schema for exit code, stdout, stderr, return
   values, and exception type/message. Path, bytes, UUID, datetime, file, and
   custom-object results must be explicitly normalized or excluded.
4. Explicit handling for pager/editor/import subprocess checks. Arbitrary
   shell commands, ambient executables, network access, host paths, current
   time, locale, and random state cannot be implicit inputs.
5. Root-owned collection and reporting. The trusted verifier must not import
   candidate code, patch candidate modules in-process, accept candidate-owned
   tests, or trust candidate-written JUnit/reward files.

The generic adapter is therefore not a faithful boundary for the complete
upstream suite. Narrowing the measured behavior to a pure-JSON CLI subset may
be feasible, but that is a new task version and must not be silently presented
as full Click API or upstream test parity.

## Blockers and reopen conditions

Keep `click` blocked. The blockers are:

1. No final verifier environment/image digest or content-addressed offline
   dependency closure exists. The project lock does not lock the Flit build
   backend, and the collection probe relied on the host uv cache.
2. The 1,995-node default collection is only a source baseline. Stress
   inclusion, platform skip policy, external pager availability, and the
   effective passed/skipped denominator are not frozen in a task verifier.
3. The upstream tests directly import the candidate and exercise callbacks,
   classes, streams, files, subprocesses, monkeypatches, and persistent state.
   No Click-specific child-side JSON/CLI adapter or approved behavior mapping
   exists.
4. No private test bundle, allowlisted command plan, structured final
   collection artifact, Oracle bundle, or control record exists. These assets
   were intentionally not created or run under the static-only request.

To reopen, provide a reviewed task version and adapter contract, then freeze a
final Python/image/toolchain environment and a complete no-network build/test
dependency artifact. Adapt only the approved behavior scope to the separate
candidate child, collect that private suite in the final image, and record
structured collection/JUnit evidence before any Oracle, empty, stub, forgery,
or offline control. Do not claim Click upstream parity if the task is narrowed
to a JSON/CLI subset.

## Static validation record

Completed without Docker, Harbor execution, full test execution, Oracle,
negative controls, or shared edits:

- Read the repository authoring, metadata, roadmap, and verifier guidance.
- Cloned the public upstream repository, detached at the requested full SHA,
  checked commit/tree/submodule state, generated and compared three source
  archives, and hashed `LICENSE.txt`, `pyproject.toml`, and `uv.lock`.
- Counted source/test files and lines with standard shell tools and Python
  AST inspection; searched the test tree for collection markers, CliRunner,
  monkeypatch, filesystem, environment, and subprocess usage.
- Ran locked test-group collection only (`pytest --collect-only`), all-node
  collection, stress-only collection, and three repeated default collection
  runs. No test body was executed.
- Ran an evidence-only `uv build` in `/tmp`; the temporary wheel and sdist were
  not copied into this repository.
- Inspected the generic candidate client/runner to determine JSON
  serialization and process-boundary constraints.

No tests were added or modified. No task descriptor, instruction, Harbor
asset, hidden/private test, dependency cache, Oracle, Docker artifact, secret,
legacy task, dataset manifest, or shared index was created or changed.

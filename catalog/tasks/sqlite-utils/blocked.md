# `sqlite-utils` static authoring audit and blocker

Status: **blocked**. This task-local file records public static authoring
evidence for the exact requested revision. It does not contain copied upstream
tests, hidden assertions, a private command plan, dependency wheels, a Docker
file, a Harbor task, verifier code, an Oracle solution, a generated reward, or
a shared catalog/index edit. Temporary source, collection, and packaging probes
were kept under `/tmp` and were not added to the repository.

## Decision

Do not compile or publish this candidate from the current evidence. The source
and Apache-2.0 license boundary are coherent, and the default collection was
stable across the local probes, but the publication prerequisites are not:

- there is no immutable OS/Python/SQLite/SpatiaLite environment or hash-locked
  offline build and test dependency closure;
- upstream CI deliberately varies Python, OS, NumPy presence, SQLite versions,
  a compiled SQLite extension, SpatiaLite, and an alternate autocommit mode;
- the effective pass denominator depends on native facilities and skip policy;
- the generic production `candidate_client` starts a fresh process for each
  JSON call and cannot preserve the live database objects, callbacks,
  generators, transactions, plugins, or filesystem sessions used by the
  upstream tests; and
- no reviewed `sqlite-utils` child-side scenario adapter, private adapted test
  bundle, instruction, or test-to-spec traceability record exists.

This is an environment/verifier blocker, not a license rejection. A CLI-only
or stateless utility subset could be adapted more cheaply, but publishing that
subset as full upstream `sqlite-utils` parity would silently change the task.

## Exact source identity

- Upstream repository: `https://github.com/simonw/sqlite-utils`.
- Requested and resolved revision:
  `56dd09702fdb9e899f577ffd51693c1f2176cb08`.
- Commit tree: `2a795dc89303b1f58921d2fe732aeddf2cd9e3f5`.
- Parent: `28dc6278cc03a9245325d056e6986818544abc68`, which is
  tag `4.2.1`.
- Description after fetching that tag: `4.2.1-1-g56dd097`.
- Author and commit time: `2026-08-13T17:01:47-07:00`.
- Subject: `Run no-default-groups smoke test from Justfile`.
- Submodules: none.
- The detached checkout was clean after source, collection, and build probes.

The requested commit changes only `Justfile` relative to tag `4.2.1`. It adds a
prerequisite smoke command that runs `uv run --isolated --no-default-groups
sqlite-utils --help`. Runtime code and public tests are unchanged from the
tagged parent, while `pyproject.toml` still declares package version `4.2.1`.
A PyPI `4.2.1` artifact is therefore not the exact source revision even though
its runtime behavior may be identical. The full commit SHA, not the release
name, must remain the source lock.

Two direct, unprefixed archives generated with:

```text
git archive --format=tar HEAD
```

both produced the following result:

```text
bytes:       1,546,240
members:     118 (107 tracked files plus archive directory entries)
sha256:      0e2c4a006448eb062d10aaf589ee1e1046faa17ad908cd089cd3612c73a16e29
```

This Git archive is the static source-lock observation. No archive bytes were
copied into the catalog.

## Apache-2.0 license evidence

The exact commit has one tracked license file, root `LICENSE`. It is the full
Apache License, Version 2.0 text:

```text
bytes:       11,357
Git blob:    261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64
sha256:      c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4
```

Commit-specific raw GitHub bytes matched the checkout byte-for-byte. The exact
`pyproject.toml` has Git blob
`92650e23b6b8013ec72beea6539b0d16c19f3cf1`, is 2,234 bytes, has SHA-256
`ec133707085153fae34f663ec8934ec95a731575a2b3b7577347ec2de0ac432c`,
and declares `license = "Apache-2.0"`. `MANIFEST.in` includes `LICENSE`, and
the README badge also identifies Apache 2.0. No conflicting source license or
separate notice file was found in the tracked tree.

The test-only `tests/ext.c` has no separate license header. It is tracked in
the same Apache-2.0 repository boundary; a future artifact review should still
retain the root license when distributing that fixture or a binary compiled
from it.

## Package and build boundary

The installable `sqlite_utils` directory has ten Python modules plus a
`py.typed` marker. The exact Python tree has:

```text
Git tree:             f87bbc2e91b4ca7dc31efb36286d4c8c6cc1fe31
Python bytes:         393,982
physical lines:       11,248
nonblank lines:       10,183
noncomment lines:     9,813
```

An AST inventory found 91 non-underscore module functions, 35 non-underscore
classes, and 129 non-underscore class methods across all runtime modules.
Those are inventory aids, not a public API denominator: they include Click
command functions and implementation-visible submodule names. The exact root
`sqlite_utils.__all__` has six entries:

```text
ANY, Database, Migrations, hookimpl, hookspec, suggest_column_types
```

The installed console entry point is
`sqlite-utils = sqlite_utils.cli:cli`. Runtime inspection found 48 Click
commands, covering database creation and queries, JSON/CSV/TSV import,
insert/upsert/bulk operations, schema and foreign-key management, FTS,
WAL/count triggers, transforms/extracts, migrations, plugins, package
install/uninstall, and SpatiaLite geometry operations.

One evidence-only `uv build` outside the catalog used setuptools 84.0.0 and
produced:

| artifact | bytes | SHA-256 |
| --- | ---: | --- |
| `sqlite_utils-4.2.1-py3-none-any.whl` | 99,482 | `2b330557aa6beb32436bf5cbcf8bf2f4e4aef30e1b580113a5f66817a04e0388` |
| `sqlite_utils-4.2.1.tar.gz` | 311,731 | `0aa70b6cd4b85b1567c18c87f98fdc0fd70bcf7b81c29ed21ab5180c872027da` |

The wheel is marked `Root-Is-Purelib: true`, has tag `py3-none-any`, contains
all ten runtime modules, `py.typed`, and the exact root license under
`dist-info/licenses`. These hashes describe one temporary online build probe;
they are not approved or reproducible dependency artifacts.

The generated sdist is not a complete source for the upstream test contract.
It includes the 54 Python files under `tests/`, but omits all five non-Python
test inputs: `tests/ext.c` and four `tests/sniff/*.csv` files. A future test
bundle must originate from the exact Git tree or an explicitly manifested
public-test artifact, not from this sdist.

## Dependency closure

`pyproject.toml` requires Python `>=3.10` and uses
`setuptools.build_meta` with the open-ended build requirement
`setuptools>=77`. Runtime requirements are:

```text
click>=8.3.1
click-default-group>=1.2.3
pluggy
python-dateutil
sqlite-fts4
tabulate
pip
```

The repository tracks no `uv.lock`, requirements lock, artifact hashes, or
offline wheelhouse. A temporary Python 3.14 `uv run --isolated
--no-default-groups` resolution observed these unique versions:

```text
click 8.4.2
click-default-group 1.2.4
pip 26.2.1
pluggy 1.6.0
python-dateutil 2.9.0.post0
six 1.17.0
sqlite-fts4 1.0.3
sqlite-utils 4.2.1 (local source build)
tabulate 0.10.0
```

The runtime-only `sqlite-utils --help` smoke command exited successfully, but
the live resolution is not a lock. The default development group additionally
pulls unpinned `pytest`, `hypothesis`, `cogapp`, type checkers, linters, and
type stubs. The collection probes resolved 38 packages and observed pytest
9.1.1 and Hypothesis 6.165.10. Those cache-backed, online observations cannot
be used as a verifier closure.

The Python requirements are not the complete environment:

- the selected CPython build supplies the native SQLite library and its
  compile options;
- `tests/ext.c` needs a C compiler and SQLite extension headers to produce a
  platform-specific shared library;
- GIS tests need a loadable SpatiaLite library and its native dependency
  closure, not just a Python package;
- NumPy and pandas activate optional conversion behavior;
- if installed, `pysqlite3` silently replaces the standard-library driver;
  `sqlite-dump` then changes the dump implementation; and
- `pip` is a runtime dependency because the public `install` and `uninstall`
  commands execute pip in-process. Networked package installation must not be
  allowed during an offline verifier run.

A final closure must pin and hash the interpreter, SQLite library and compile
flags, every Python wheel, setuptools build wheel, compiler/native inputs,
SpatiaLite and its shared libraries, and the optional-package inclusion or
exclusion policy. It must install and run with network disabled.

## Public test tree and collection

No upstream test bytes were copied into the task. Static evidence refers to
the public tree at the exact commit:

```text
tests Git tree:       e0f60285b998590763eb5a82197f6a50a1fb34a7
tracked test files:   59
tracked test bytes:   542,998
Python test files:    54 (52 test modules plus __init__.py and conftest.py)
static test defs:     804
parametrize uses:     199
Hypothesis tests:     4
```

The five non-Python inputs are public source fixtures. Their exact evidence is:

| path | bytes | Git blob | SHA-256 |
| --- | ---: | --- | --- |
| `tests/ext.c` | 1,547 | `f5b3276e94467a05b10522e9ba9f9bf3be1030af` | `86d27831b0741c66058903505cb6a6b51d7d649920d69fc285f1ddc51ef50724` |
| `tests/sniff/example1.csv` | 98 | `3daaaddb264fe6957654ba7fb6128305ce9cbb20` | `a18a05773c74ed99875d61bdfea1db653466cd8a23a6aec2ce6118d80ac7925a` |
| `tests/sniff/example2.csv` | 98 | `0452e7f14da4e9deb20e70cbe050eb338c2874b4` | `2d92578b91185eec3755303b46aef6558dd69b117f18d71d1384760e2c9ff61a` |
| `tests/sniff/example3.csv` | 98 | `172c3d31ce4aeb447384f6105dae2c7d98c02490` | `531e0a52b3f9da5a4905db690e3378d91f24c0ebcd330343e0ebd3f21d2c7e5a` |
| `tests/sniff/example4.csv` | 98 | `71b671e09f4381b7cf813f49d8c810f2babc9dee` | `8e67d4dba42a671c9517aa078166995801d34897f72bf8d98e6da9396783d097` |

The suite also reads documentation as test input. The `docs` tree has 18 files,
476,476 bytes, and Git tree
`3152d998a88e074a466ea467872f8c73505f7f3b`. In particular,
`tests/test_docs.py` parses `docs/cli.rst` and `docs/plugins.rst`; those files
are part of the test artifact boundary even though they are not Python tests.

Only cache-disabled collection was run. No test body was executed:

| probe | Python / SQLite | mode | collected | normalized node-list SHA-256 |
| --- | --- | --- | ---: | --- |
| run 1 | CPython 3.14.6 / SQLite 3.51.2 | default | 1,504 | `f76b25b9d38fce3de2809dfb24d5638572098d23514d495df2da5d1859a0e07a` |
| run 2 | CPython 3.14.6 / SQLite 3.51.2 | default | 1,504 | `f76b25b9d38fce3de2809dfb24d5638572098d23514d495df2da5d1859a0e07a` |
| run 3 | CPython 3.12.11 / SQLite 3.50.4 | default | 1,504 | `f76b25b9d38fce3de2809dfb24d5638572098d23514d495df2da5d1859a0e07a` |
| run 4 | CPython 3.14.6 / SQLite 3.51.2 | `--sqlite-autocommit` | 1,504 | `f76b25b9d38fce3de2809dfb24d5638572098d23514d495df2da5d1859a0e07a` |

The probed interpreters expose extension loading and SQLite compile options
for FTS3, FTS4, FTS5, and RTREE. No configured SpatiaLite path, compiled
`tests/ext` shared library, pandas, NumPy, `pysqlite3`, or `sqlite-dump` was
present in the collection environments.

Collection-marker inventory on the Python 3.14 default probe found no xfails.
Sixteen unique items had a true `skipif` condition: all 12 GIS items because
SpatiaLite was absent, three parameterized extension-loading items because
`ext.c` had not been compiled, and one pandas/NumPy item. Another 28 unique
items had false `skipif` conditions in that environment; GIS items carry a
second, false extension-loading marker and therefore overlap the marker sets.
Tests also call `pytest.skip()` inside bodies based on SQLite features, so
collection alone does not determine the final passed/skipped counts.

The stable node list is useful source evidence, but `1,504` is not declared as
a frozen benchmark denominator. A final metric must decide whether default and
autocommit are separate modes, whether native/optional branches are
provisioned, how skipped items are scored, and how a collection mismatch
invalidates the result.

## CLI, SQLite, and API coverage

The suite is not a simple command smoke test. A source and node-ID inventory
shows these broad surfaces:

- 373 collected items live in the six `test_cli*.py` modules. Additional CLI
  assertions cover analyze-tables, insert-files, CSV sniffing, count triggers,
  FTS, GIS, plugins, and command documentation/help.
- `test_docs.py` alone expands to 100 items: all 48 commands must be documented
  and have help, convert help is checked, and three recipe functions must be
  documented.
- The dedicated FTS module has 53 items. The dedicated GIS module has 12,
  plugin module four, migration API module 15, migration CLI module 16, and
  Hypothesis module four.
- The remaining API-heavy tests create and retain `Database`, `Table`, and
  `View` instances; inspect schemas, columns, indexes, triggers, checks, and
  foreign keys; consume row/query generators; and compare exact exception,
  transaction, SQL, JSON, CSV, TSV, table, and filesystem behavior.
- Mutating tests cover create/insert/upsert/update/delete, schema transforms,
  FTS triggers, WAL, counts, attached databases, views, migrations, callbacks,
  nested atomic blocks/savepoints, rollback behavior, and multiple live SQLite
  connections to one file.
- Three modules start real subprocesses. Two use `Popen` plus timing loops to
  exercise streaming bulk/insert behavior, and one checks `python -m
  sqlite_utils`. Many other CLI tests use Click's in-process `CliRunner`.

A manual function-level classification identifies approximately 514 collected
items as directly CLI, CLI metadata/help, or command-documentation behavior;
the other 990 are predominantly Python API and SQLite state behavior. The
numbers are an audit partition, not separate score weights, and mixed modules
mean feature groups overlap.

The tests contain no genuine remote-network call. URL strings are table names,
documentation references, or issue links. The public `install` command can
reach package indexes, but upstream tests only include it in documentation and
help coverage.

## Native SQLite, FTS, GIS, and optional-driver risks

### SQLite version and compile flags

Behavior depends on the native SQLite linked into Python. Tests gate or branch
on STRICT tables, `RETURNING`, `pragma_function_list`, legacy-alter behavior,
UTF-8 BOM acceptance, view `rowid`, extension loading, and FTS/RTREE support.
The upstream `test-sqlite-support` workflow compiles SQLite 3.46 and 3.23.1
with explicit `SQLITE_ENABLE_DESERIALIZE`, FTS3/4/5, RTREE, and JSON1 flags;
that workflow is marked `continue-on-error`. A production task must select one
supported native boundary rather than treating every CI variant as one metric.

### FTS

FTS4 and FTS5 are core tested behavior, not optional decoration. Tests create
virtual tables, triggers, tokenizer configurations, ranking queries, rebuild
and optimize indexes, inspect internal FTS tables, and validate quoting and SQL
generation. FTS4 ranking also depends on the `sqlite-fts4` Python package.
Collection success does not prove that the final SQLite library contains both
modules.

### Loadable extension fixture

`tests/ext.c` defines three SQLite extension entry points. Upstream Ubuntu CI
uses `gcc ext.c -fPIC -shared -o ext.so`; three collected cases are skipped
without that output. The build requires the platform SQLite headers, and the
result is architecture- and libc-specific. The generated Python sdist omits
the C source, so it cannot be the fixture source.

### SpatiaLite/GIS

Ubuntu CI installs `libsqlite3-mod-spatialite`. All 12 GIS items are module-
marked to skip when SpatiaLite cannot be found or the Python driver lacks
extension loading. Runtime discovery checks five hard-coded x86_64, aarch64,
macOS, and Homebrew paths. Tests initialize spatial metadata, add geometry
columns, create spatial indexes, and invoke matching CLI operations. A final
environment must pin the SpatiaLite binary, dependent native libraries, path,
SQLite ABI, and extension-load policy; silently accepting 12 skips is a metric
choice, not an environment proof.

### Optional Python drivers and data types

`sqlite_utils.utils` imports `pysqlite3` in preference to standard `sqlite3`
when present. `db.py` also conditionally imports `sqlite-dump`, pandas, and
NumPy. These alter dump behavior and supported values. Final dependency
installation must explicitly include or exclude them. Ambient packages cannot
be allowed to select a different candidate behavior.

## Plugin and process-global risks

The package uses a process-global Pluggy manager for the `sqlite_utils` entry
point group. Plugins can register Click commands and modify every new SQLite
connection through `prepare_connection`. `Database(...,
execute_plugins=False)` is the opt-out.

The upstream `conftest.py` sets `sys._called_from_test = True`, which suppresses
ambient setuptools entry-point loading. Plugin tests then reload the CLI,
mutate the shared manager, register in-memory plugin classes, inspect hook
metadata, and verify a dynamically registered command and SQL function. A
fresh process per ordinary candidate call loses this state. Allowing arbitrary
installed plugins would make results depend on the verifier environment and
would execute third-party code inside the candidate child.

The final adapter must provide fixed child-side plugin fixtures, reset manager
and module state between scenarios, disable unrelated entry-point discovery,
and ensure no plugin can see hidden tests or write trusted reports. Testing the
real `install` command against the network is outside an offline metric; any
local package-install scenario would need a separate allowlisted artifact.

## Determinism and runtime policy

Four Hypothesis tests exercise integer, Unicode text, binary, and floating
round trips. Hypothesis and its profile/database/seed behavior are not pinned.
Two streaming CLI tests use one-second sleeps, another has retry sleeps, and
several assertions vary by OS, default encoding, Python version, or SQLite
version. UUIDs and current timestamps are generated in some scenarios, though
the tests generally compare round trips or shapes rather than fixed values.

Upstream CI spans Python 3.10 through 3.15-dev, Ubuntu, macOS variants, and
Windows; optionally installs NumPy; installs SpatiaLite and compiles `ext.c`
only on Ubuntu; and runs the full suite again with `--sqlite-autocommit` only
on Python 3.14/Ubuntu. A final task needs one explicit interpreter/OS/SQLite
policy, a deterministic Hypothesis profile, locale/encoding settings, process
timeouts, and an approved test-mode matrix.

## Candidate subprocess adapter blocker

The generic production boundary in
`src/nl2repobench/verification/candidate_client.py` and
`candidate_runner.py` is intentionally stateless. Each `call` or `get` starts
a fresh UID-10001 child, accepts JSON arguments for one module attribute, and
JSON-serializes one return value. Module and console operations return bounded
stdout/stderr and an exit code. There is no persistent object handle, working-
directory fixture protocol, callback registry, transaction session, plugin
fixture, or typed binary value transport.

That contract cannot directly preserve this suite:

- `Database`, `Table`, `View`, `Migrations`, SQLite connections/cursors,
  generators, context managers, exception objects, type objects, bytes, paths,
  and namedtuple/dataclass metadata do not all serialize as JSON;
- tests mutate one database through many calls and inspect lazy iteration,
  partial iteration, transaction state, commit visibility from a second
  connection, and cleanup behavior;
- APIs accept Python callables for tracing, conversion, registered SQL
  functions, migration functions, and plugin hooks;
- plugin tests depend on module reload and process-global manager state;
- CLI tests need controlled stdin, files, database persistence, current
  directory, exact stdout/stderr/exit status, and sometimes concurrent child
  processes; and
- native extension and SpatiaLite tests need approved binary paths inside the
  same unprivileged process that imports the candidate.

The generic `run_module("sqlite_utils", ...)` operation can cover a single
stateless CLI invocation and text stdin, but it cannot by itself set up and
inspect the multi-step filesystem/database scenarios. `run_console` does not
accept stdin. Running the original tests in trusted pytest would directly
import untrusted candidate code and violate the separate-verifier contract;
moving assertions into a candidate-owned script would make results forgeable.

A compliant future task needs a reviewed `sqlite-utils` child-side scenario
adapter with at least these properties:

1. One bounded child executes a declarative operation sequence and maintains
   handles for databases, tables, views, iterators, connections, and migration
   sets for the duration of that scenario only.
2. A tagged value codec represents bytes, paths, UUID/date/time/decimal values,
   tuples/namedtuples/dataclasses, SQLite rows, and exception type/message/args
   without accepting arbitrary candidate-controlled serialization code.
3. An allowlisted callback and plugin-fixture registry reconstructs the exact
   public callable behaviors needed by adapted assertions. Hidden expected
   values and pass/fail decisions remain in trusted pytest.
4. A CLI operation supplies argv, text or tagged-binary stdin, a child-local
   temporary filesystem, deterministic environment values, and bounded
   stdout/stderr/exit status. Follow-up operations inspect SQLite state and
   approved artifact hashes inside the child rather than importing the
   candidate in the trusted process.
5. The child receives pinned, read-only public native fixtures at fixed paths
   for extension/SpatiaLite scenarios. Arbitrary extension paths, package
   installation, network access, unrelated plugins, and writes to trusted
   result paths are rejected.
6. Every scenario starts from clean process-global/plugin state and ends with
   process-group cleanup and bounded artifact accounting. Trusted pytest owns
   collection, JUnit, and reward files.

Adapting 1,504 upstream items to that contract while preserving assertion
meaning is substantial verifier work. No adapter code or hidden test rewrite
was authorized in this static lane, so candidate isolation remains a blocker.

## Reopen conditions

Reopen this task only after all of the following are approved and evidenced:

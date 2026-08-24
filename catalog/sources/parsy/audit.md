# Parsy Authoring Audit

Status: `blocked` development source. This task-local record contains public
provenance, source/package inventory, and source-only validation evidence. It
does not contain upstream test bytes, a verifier, an allowlisted command-plan
artifact, dependency wheels, an Oracle bundle, or a private artifact handoff.

## Decision And Scope

Keep the task at lifecycle status `blocked`. The exact requested revision,
source archive, license evidence, and source-only collection/baseline probes
were revalidated below. Those probes do **not** freeze a production denominator
or establish a runnable Harbor task. Do not add placeholder private references,
copy upstream tests into this public catalog, advance the lifecycle, or run
Docker/Harbor/Oracle from this lane.

The only durable write root authorized for this audit is
`catalog/tasks/parsy/`. Temporary checkouts and virtual environments mentioned
below are disposable validation inputs, not task artifacts.

## Source Provenance

- Upstream: `https://github.com/python-parsy/parsy`
- Checkout: `/tmp/nl2repo-candidates/parsy`
- Requested and resolved revision:
  `03deafa98a17adc27b1f650241701b2d21902b3e`
- Commit tree: `27d0aea710ca276102890907c10180a6efbc2fb8`
- Parent: `a1db5ae4270157056e098f565a07d90b735bfafb`
- Commit subject: `Update awesome-python link`
- Commit timestamp: `2026-06-22T08:23:35+01:00`
- Git submodules: none (`git submodule status` produced no entries)
- Checkout status: clean before and after validation; `.pytest_cache` was
  removed after each probe

The source lock is the direct, unprefixed archive from the resolved commit:

- Command: `git -C /tmp/nl2repo-candidates/parsy archive --format=tar HEAD`
- Archive members: `55`
- Archive bytes: `194560`
- Repeated archive SHA-256 (three runs):
  `5b3f5d7aa6d5ee31659ce341bc15dee031ca631cc69e1d3ac392b4b03df6f10f`

The archive is not prefixed or repacked. This digest is the `source_digest`
recorded in `task.toml`.

License evidence agrees with the frozen source:

- Path: `LICENSE`
- Git blob: `48d1298a3f4119db9d312e4d62a1cb20ddcf2010`
- Size: `1132` bytes
- File SHA-256: `3cd274c6ec7873e4f03693145819ec1fb82768d1386b7c59b4ff194c79853e06`
- `pyproject.toml` declares the project license as MIT

No license bytes were copied into the catalog; the digest and blob identity
are provenance evidence only.

## Package And Dependency Inventory

Values below were read from the exact checkout, not inferred from the task
instruction:

- Distribution and import package: `parsy`
- Package version: `2.2` (`src/parsy/__init__.py::__version__`)
- Python requirement: `>=3.9`
- Runtime dependencies: none (`project.dependencies = []`)
- Build backend: `setuptools.build_meta`
- Build requirement: `setuptools>=61.2`
- Package layout: `src/parsy`
- Source implementation: `src/parsy/__init__.py`, `719` physical lines and
  `551` nonblank, noncomment lines
- Public surface is re-exported from `parsy.__init__`; the reviewed source
  defines `ParseError`, `Result`, `Parser`, parser constructors/combinators,
  primitive parser objects, enum support, and forward declarations
- `pyproject.toml` SHA-256:
  `da0f30b759746c74d685c080021e91536dad32c22a20bdb26d4234b16289977b`
- `pytest.ini` SHA-256:
  `203b4368d3742b10f175cddb7f6b262374274f3399b6acf76713fdb052f9bfcb`

The dedicated upstream test requirements at this revision are:

```text
pytest==9.0.3
pytest-cov==4.0.0
coverage==6.3.2
```

The broader `pyproject.toml` development group uses lower bounds and is not a
hash-locked verifier closure. The dependency status therefore remains
`unknown` in `task.toml`, even though the runtime package itself has no third-
party dependency.

## Collection And Source Baseline Evidence

The frozen checkout's `pytest.ini` sets:

```ini
python_files = examples/*.py tests/*.py
pythonpath = src/
```

The source-only probe shape was:

```bash
cd /tmp/nl2repo-candidates/parsy
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=src \
<probe-python> -m pytest \
  -p no:cacheprovider --collect-only -q
```

The actual disposable probe interpreters were
`/tmp/cattrs-venv312/bin/python` and `/tmp/cattrs-venv313/bin/python`; they
are recorded as execution evidence only and are not task artifacts.

Two independent collection runs were made under each of these disposable
probe environments:

| Interpreter | Pytest | Collection result |
| --- | --- | --- |
| CPython `3.12.11` | `9.0.3` | `88` items, no collection errors |
| CPython `3.13.14` | `9.0.3` | `88` items, no collection errors |

The two runs for each interpreter were byte-identical after retaining only
node-id lines. All four normalized node lists have SHA-256
`b156aa7804fedf335969487eac050d89ca38f4847886f3575581ebff3d50de23`.
The 88 items comprise 83 `tests/` items and five example items:

```text
examples/json.py::test
examples/simple_eval.py::test_item
examples/simple_logo_parser.py::test_item
examples/sql_select.py::test_select
examples/sql_select.py::test_optional_where
```

A source-only full run was also completed once under each interpreter with:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=src \
<probe-python> -m pytest \
  -p no:cacheprovider -q -rs
```

Both runs produced `86 passed, 2 skipped`, with no failures or collection
errors. The two skips are the example `test_item` helper exclusions, marked by
the source so pytest does not execute those helper functions as tests. This is
a source baseline only; it is not an Oracle reward and does not prove a final
verifier image or private test bundle.

`task.toml` consequently keeps `tests.expected_total_source = "unknown"`.
The observed 88-item list must be recollected after private test materialization
in the final locked verifier environment before it can become a frozen
benchmark denominator.

## Exact Publication Blocker And Private Boundary

The source and public instruction are present, but no visibility-separated
private artifact store or artifact handoff is authorized in this lane. In
particular, the following production inputs are missing/non-resolvable here:

1. `tests.test_bundle`: hidden tests and their expected assertions;
2. `tests.commands_artifact`: the production allowlisted command plan;
3. `dependency_bundle`: a hash-locked offline build/verifier wheelhouse;
4. `oracle_bundle`: a reference solution bundle.

The embedded `tests.commands` entry in `task.toml` is retained only as a
provisional source-probe command. It is not a substitute for the private
allowlisted command-plan artifact. No opaque `artifact://private/...` refs are
invented, because an ephemeral ref without corresponding bytes in the
visibility-separated resolver would be non-resolvable and misleading.

No upstream tests, generated Dockerfiles, `harbor/tests/`, `harbor/solution/`,
private grader, or dependency bytes were copied under this task. The local
`harbor/task.toml` is explicitly a development descriptor, not a runnable
Harbor bundle.

## Separate-Verifier Adapter Blocker

The upstream suite exercises behavior that the generic JSON-only
`candidate_client` boundary cannot transparently preserve. Examples include:

- callbacks and lambdas passed to `string`, `combine`, `test_item`,
  `generate`, and enum transforms;
- generator functions whose yielded parsers carry state across calls;
- live `enum.Enum` classes and named-tuple results;
- arbitrary token-list and byte-stream values, including one-byte `bytes`
  predicates; and
- recursive `forward_declaration` parser objects.

Trusted pytest must not import candidate code directly merely to preserve those
objects. A task-specific child-side scenario adapter is therefore required to
reconstruct JSON-safe scenarios in the untrusted candidate process and return
JSON-safe observations while keeping expected values and assertions private.
No reviewed adapter or private bundle exists in this lane.

## Lifecycle And Reopen Conditions

`task.toml` remains `lifecycle.status = "blocked"`. The blocker is not the
source revision or the source-only baseline; it is the absent final
provenance/environment and private execution boundary. Reopen only after the
final interpreter/OS/base-image lock and offline dependency closure are
provisioned, the private test and command artifacts plus Oracle are resolved,
the task-specific adapter is reviewed, and final-image collection and control
records are frozen. Only then can Oracle, empty/stub/forgery, and offline
controls be considered.

### Validation commands run

- `git -C /tmp/nl2repo-candidates/parsy rev-parse HEAD` and exact commit/tree
  checks;
- repeated `git archive --format=tar HEAD` hashing and archive/member counts;
- license file/blob size and SHA-256 checks;
- `tomllib` metadata parsing and source line/API inventory;
- cache-free, plugin-isolated collect-only probes under CPython 3.12 and 3.13;
- source-only full pytest probes under both interpreters; and
- clean-checkout checks before and after each probe.

No Docker, Harbor execution, Oracle, negative control, shared catalog/index,
legacy projection, or private artifact materialization was performed.

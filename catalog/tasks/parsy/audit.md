# Parsy Authoring Audit

Status: `blocked` development source. This file records public provenance and
local validation evidence only. It does not contain upstream test bytes,
verifier code, command-plan bytes, dependency wheels, or an Oracle bundle.

## Source Provenance

- Upstream: `https://github.com/python-parsy/parsy`
- Checkout: `/tmp/nl2repo-candidates/parsy`
- Revision: `03deafa98a17adc27b1f650241701b2d21902b3e`
- Archive command: `git -C /tmp/nl2repo-candidates/parsy archive --format=tar HEAD`
- Unprefixed archive SHA-256: `5b3f5d7aa6d5ee31659ce341bc15dee031ca631cc69e1d3ac392b4b03df6f10f`
- License: MIT
- LICENSE size: `1132` bytes
- LICENSE SHA-256: `3cd274c6ec7873e4f03693145819ec1fb82768d1386b7c59b4ff194c79853e06`
- Checkout status: clean before and after validation; local test caches removed

The archive hash is the source lock used by `task.toml`. It was revalidated
from the exact frozen checkout; the archive was not prefixed or repacked.

## Package Metadata

Read directly from `pyproject.toml` with Python `tomllib`:

- Distribution: `parsy`
- Import package: `parsy`
- Python requirement: `>=3.9`
- Runtime dependencies: none
- Build backend: `setuptools.build_meta`
- Version source: dynamic attribute `parsy.__version__`
- Package layout: `src/parsy`
- Package version from the checkout: `2.2`
- Homepage: `https://github.com/python-parsy/parsy`

## Size And Collection Evidence

- Source file: `src/parsy/__init__.py`
- Source LOC: `719` total lines; `551` nonblank, noncomment lines
- Dedicated test modules: `tests/test_parsy.py`, `tests/test_sexpr.py`
- Additional collected modules: `examples/json.py`, `examples/simple_eval.py`,
  `examples/simple_logo_parser.py`, and `examples/sql_select.py`
- Upstream test pin: `pytest==9.0.3`; the local offline cache contained pytest
  `9.1.1` only, so final locked-environment collection remains required
- Pytest file pattern: `examples/*.py tests/*.py`
- Collection command (cache-free):
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /tmp/parsy-collect-venv/bin/python -m pytest -p no:cacheprovider --collect-only -q`
- Collection environment: temporary local uv environment, CPython `3.13.14`,
  pytest `9.1.1`, installed from the local uv cache with no network request
- Collected total: `88`
- Full local run: `86 passed, 2 skipped`
- Skips: intentional `test_item` helper exclusions in example modules
- Full-run command (cache-free):
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /tmp/parsy-collect-venv/bin/python -m pytest -p no:cacheprovider -q -rs`

The `88` count is evidence from the frozen checkout, not a final frozen
benchmark denominator. The final denominator must be regenerated in the
locked verifier environment after private test materialization.

## Exact Publication Blocker

The frozen checkout contains the upstream source and tests. However, the only
authorized durable write root in this lane is the public
`catalog/tasks/parsy/` tree. No private `FileArtifactStore` path, object-store
URI, or artifact handoff was authorized. Copying or archiving tests under the
catalog would commit them publicly. Consequently:

1. `tests.test_bundle` is absent, so hidden tests cannot be materialized.
2. `tests.commands_artifact` is absent, so the production allowlisted command
   plan cannot be resolved.
3. `dependency_bundle` is unknown, so an offline wheelhouse and hash-locked
   verifier dependency closure are not available.
4. `oracle_bundle` is absent, so no reference solution can be compiled.

The current artifact model can represent each item as a private
`artifact://private/sha256:...` reference, but the local resolver requires the
corresponding bytes in its visibility-separated filesystem store. An ephemeral
reference without an authorized durable store would be non-resolvable and
non-integrable. Therefore this lane adds only declarative source, audit
evidence, and the non-runnable Harbor 1.4 separate-verifier descriptor. It does
not create `harbor/tests/`, `harbor/solution/`, Dockerfiles, or placeholder
artifact refs.

## Separate-Verifier Adapter Blocker

The upstream tests construct live `Parser` objects and pass lambdas, generator
functions, enum classes, named tuples, and opaque token objects. The generic
`candidate_client.call` protocol accepts JSON request values and requires a
JSON-serializable response, so it cannot preserve these in-process interactions.
Directly importing the candidate from trusted pytest would violate the required
separate-verifier boundary.

Production packaging therefore also requires a task-specific scenario adapter
that runs entirely in the untrusted candidate child. Trusted hidden tests must
send declarative JSON-safe scenarios and compare JSON-safe observations without
importing candidate code. The adapter must preserve upstream assertion semantics and be packaged as a
candidate-readable verifier runtime component or purpose-built
`candidate_runner` operation. Hidden expected outcomes and trusted comparisons
must remain in the authorized private test bundle.

Do not publish or run Oracle until all four private artifacts and this adapter
are provisioned, the final collection is frozen, and the task is compiled with
the production private resolver.

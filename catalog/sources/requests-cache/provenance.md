# requests-cache Authoring Provenance

## Frozen source

- Upstream: `https://github.com/requests-cache/requests-cache`
- Revision: `8da22ce1963788a066b65c15e6efe17ea8b4ac82`
- Package metadata version: `1.3.4`
- License: BSD-2-Clause; `LICENSE` SHA-256 `sha256:1aedf075663a232d425816b8b6c6c852e7e7976b5f98b968643162ec593d0b69`
- Unprefixed `git archive --format=tar HEAD`: 3809280 bytes,
  `sha256:aba1dbfa17ed1083567035edf760ad4264e738e7fe2f7364c7bffcb41bce89ef`

The source was cloned and checked out detached in `.nl2repo/authoring-work/requests-cache/source/repo`.
The revision, archive, license, package metadata, file counts, and mode entries were recorded before
the catalog source was authored. The source has no submodules; executable example modes are upstream
metadata and are not copied into the Agent image by the task.

## Environment and dependency remediation

The frozen revision uses Hatchling and declares six core runtime dependencies. A task-local CPython
3.12.11 environment was created and `uv pip compile --python-version 3.12 --generate-hashes`
produced a 33840-byte lock containing the core closure, Hatchling build backend, and deterministic
local test tools. The lock is stored as private artifact
`sha256:57c041091534bbfa2ce4909c20da5cfc6f5d462042582132de1b0878dcfd4534` and is installed only
during Docker image build with `--require-hashes`; Agent and verifier runs have no network.

## Test inventory and adaptation

The upstream-compatible collection probe reached 1288 tests and reported two collection errors for
optional `pymongo` and `redis` modules. A unit plus in-memory integration probe ran 558 tests with
466 passed, 88 failures caused by the test fixture's unavailable live/mock transport assumptions,
3 skips, 1 xfail, and 20 warnings. Those aggregate probes are preserved as evidence, not used as a
misleading production denominator. The production denominator is a separate 30-leaf deterministic
contract for JSON-safe local behavior. It covers normalization, cache keys, expiration, settings,
in-memory response storage, serialization, cached sessions with a local adapter, patching, and
public exports. Network services and remote database integrations are explicitly excluded.

## Boundary

The private verifier uses `custom-json-v1`. Its trusted root never imports candidate code. Each
scenario is passed to `nl2repobench.verification.candidate_client.execute_script`, which starts a
UID-10001 child with bounded output, CPU, memory, process, storage, per-call timeout, and cumulative
wall-clock limits. The root owns collection, JUnit, grading, and reward. The Oracle solution fetches
the exact revision only in the trusted Oracle run, verifies the archive digest, and never enters the
model Agent context.

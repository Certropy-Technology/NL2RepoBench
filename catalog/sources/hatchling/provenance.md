# `hatchling` production authoring provenance

## Frozen source and license

- Upstream repository: `https://github.com/pypa/hatch`
- Exact commit: `ed8e30bebf98f2fe4d70c18a32a50a8160c391cb`
- Commit date: `2026-08-13T13:47:42-07:00`
- Commit subject: `Refactor extras so that the logic is in one place (#2382)`
- Distribution subtree: `backend/`
- Unprefixed full repository `git archive --format=tar`:
  8,704,000 bytes, SHA-256
  `b24cd536f687101398922778ba986061455d1a5a7bc75b77c1737ca8c8ec83bb`.
- `git archive --format=tar <commit> backend`:
  378,880 bytes, SHA-256
  `b3acd9e2fcdc976fd53eaa6f496ea2e32ad380d5046ec1bd7514c82cca5692d7`.
- `backend/LICENSE.txt`: 1,088 bytes, SHA-256
  `7f143a8127ad4873862d70854b5bd2abd0085aa73e64fd2b08704a3b9f5c07fc`.
- Declared and inspected license: MIT.
- Submodules: none.

The source descriptor binds the task to the backend subtree archive because
the repository root is the separate `hatch` CLI distribution. The Oracle
fetches only the declared commit, asserts `FETCH_HEAD^{commit}`, recreates the
same backend archive, verifies the digest, and strips the `backend/` prefix into
`/workspace`. No source host is declared in task metadata; the Oracle run must
receive an exact `github.com` host authorization from the runner.

## Upstream inventory

At this revision, `backend/pyproject.toml` declares `hatchling` version 1.32.0,
Python 3.10+, the `hatchling` console script, and the `hatchling.ouroboros`
self-build backend. Runtime dependencies are Packaging, PathSpec, Pluggy,
Tomlkit, Trove Classifiers, and Tomli only below Python 3.11.

The backend subtree contains 67 Python files and one `py.typed` marker under
`backend/src/hatchling`. It has only downstream integration data under
`backend/tests`; there are zero collectable upstream Hatchling unit tests in
the frozen subtree. The repository root tests exercise the separate `hatch`
distribution and were deliberately not reused as a false denominator.

## Runtime and dependency closure

- Runtime: CPython 3.12.14 on Debian 12 amd64.
- Base image: `python:3.12-slim` at
  `sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
- Docker inspection confirmed Linux/amd64 and the same image ID.
- Candidate runtime dependencies: Packaging 26.3, PathSpec 1.1.1, Pluggy 1.6.0,
  Tomlkit 0.13.3, and Trove Classifiers 2026.6.1.19.
- Setuptools 80.10.2 and Wheel 0.45.1 are build-stage tools available to an
  implementation starting from an empty workspace. Hatchling itself is not
  preinstalled as a candidate dependency.
- The 1,317-byte lock has SHA-256
  `1c65ec786efe51baa5f9ff90c60c963719c41216451db6f18842eb89ba231a42`
  and includes package-index hashes for every pinned requirement.
- No wheel, wheelhouse, vendor tree, `--no-index`, or `--find-links` input is
  present. Docker build may reach the package index; Agent and verifier runtime
  are no-network.

## Frozen verifier contract

The private `custom-json-v1` bundle contains `run.py`, `adapter.py`, and
`expected.json`. It has 21 unique leaves covering backend API exports, metadata
normalization and validation, requirement normalization, version files and
schemes, built-in plugin registration, PEP 517 requirement hooks, metadata
preparation, wheel members/metadata/entry points/RECORD/selection,
wheel and sdist reproducibility, sdist metadata, builder utilities, Core
Metadata round-tripping, and wheel tag selection.

The trusted parent never imports candidate code. Each scenario runs as UID
10001 in a fresh subprocess with CPU, address-space, file-size, descriptor,
process, wall-clock, and report-size limits. The child imports from the isolated
candidate site plus the read-only dependency site and emits one bounded JSON
observation. Exceptions, timeouts, crashes, malformed output, or mismatches are
failed leaves. The generic verifier runtime owns collection, JUnit, grading,
reward, network checks, install supervision, and process cleanup.

Binary/app builders, Cargo/network execution, live package indexes,
third-party plugin implementations, arbitrary custom scripts, and macOS-only
rewriting are outside this deterministic slice. The task does not claim full
behavior of the separate Hatch CLI or an unavailable upstream test suite.

## Controls and lifecycle

Task-local controls include an importable metadata-only stub, a reward/test
forgery attempt, an import-time CPU hang, and an installation hang. Production
status remains `packaged` until the generated bundle has passed source/network
gates, official Harbor Oracle, empty/stub/forgery, timeout, and offline checks.
Review, model pilot, dataset integration, and publication remain outside this
lane.

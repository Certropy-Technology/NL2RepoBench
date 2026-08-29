# rfc3986 authoring audit

## Frozen source

- Upstream: `https://github.com/python-hyper/rfc3986`
- Revision: `7a64092490c1b3c4f354b9b14d060fa758d66848` (release 2.0.0)
- Direct `git archive --format=tar HEAD` SHA-256:
  `sha256:2a7c7ef66d324b1ba3196e6fdb5be491f7842e6ae96d0f5c3273f5bfc1824346`
- `LICENSE` SHA-256:
  `sha256:c0ddce33bfac480a66bde40c590ede2647a4c8a729dcb0d2ce46c014473d5dd8`
- Source is pure Python under `src/rfc3986`; no submodules and no required
  runtime dependency. The optional `idna` extra is not needed by the ordinary
  URI contract.

## Inventory and probes

- Public root exports: 14 ordered names including `URIReference`,
  `IRIReference`, `ParseResult`, functional API helpers, and release metadata.
- Runtime modules: `api`, `builder`, `compat`, `exceptions`, `iri`, `misc`,
  `normalizers`, `parseresult`, `uri`, and `validators`; 2,699 physical source
  lines in `src/rfc3986`.
- Source-only collection under CPython 3.12.11 with the locked pytest environment:
  2,836 tests; one full run passed 2,836 tests with exit code 0. A first probe
  without `PYTHONPATH` failed during collection because the shared authoring
  venv has no pip-installed candidate; this is recorded as an environment
  probe issue, not an upstream failure.
- The production verifier uses 38 deterministic child-process scenarios over
  the public contract. It does not import candidate code in the trusted
  verifier process.
- The verifier child timeout was reduced from 20 seconds to 2 seconds after a
  bounded call-hang control exposed a potential 38-scenario verifier timeout.
  The repaired control completed in 2m08s with 38 collected failed leaves and
  no verifier-internal error.

## Runtime and dependency closure

- CPython 3.12.11, Debian 12 amd64, base image
  `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
- Candidate build dependency is setuptools 84.0.0 only, with a private
  hash-locked requirements artifact. No wheelhouse or vendored dependency is
  used. Agent and verifier execution are no-network.
- The legacy setup.py/setup.cfg build was probed and the task package uses
  `--no-build-isolation` with the build backend preinstalled in the candidate
  dependency site.

## Harbor boundary

The custom verifier invokes an adapter as UID `candidate` with `python -I` and
an explicit candidate site. It returns one JSON object per scenario; trusted
code generates the collection, JUnit, grading, reward, and network evidence.
The Oracle script fetches only the exact upstream repository revision, asserts
the resolved commit and source archive digest, restores the package, and
removes upstream tests/docs from the Oracle workspace before verification.

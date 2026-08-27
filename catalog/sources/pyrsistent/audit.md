# Pyrsistent Authoring Audit

## Source Freeze

- Upstream: `https://github.com/tobgu/pyrsistent`
- Requested and resolved revision:
  `0c0b7aec8cd25b1d2d8ba07b10acdefd0f38f2c7`
- Source archive command: `git archive --format=tar <revision>`
- Source archive bytes: `501760`
- Source archive SHA-256:
  `349f0b11f5eea9c8fa69564a13757352d4136b3c635f4340c695f9da29834aa8`
- Submodules: none
- License: MIT, `LICENSE.mit`, 1060 bytes, SHA-256
  `3fd3d3d1ab9c733ee453fbf3bbbaa845440d0d8c20d7b5a039d2e46a2ed7fc01`

Fetch and digest evidence is stored under
`.nl2repo/evidence/pyrsistent/source-freeze/`.

## Package Inventory

The frozen source publishes `pyrsistent 0.21.0`, requires Python 3.10 or
newer, uses `setuptools.build_meta`, and declares no runtime dependencies. It
contains 16 Python implementation modules with 4348 physical lines and 42
names in `pyrsistent.__all__`. CPython may build the optional `pvectorc`
extension; the pure-Python implementation is a supported fallback and is the
minimum benchmark contract.

The upstream test tree has 19 conventional test modules and 535 syntactic
`test_*` functions. In the frozen CPython 3.12.11 environment, pytest collected
638 leaves. Three independent runs each produced 637 passed and one skipped,
with no failures or collection errors. Baseline JUnit and logs are under
`.nl2repo/evidence/pyrsistent/baseline/`.

## Frozen Verifier

The benchmark verifier is a bounded 72-leaf public-behavior subset. It covers
packaging, PEP 561 files, all collection families, immutable update semantics,
hashing and pickling, evolvers, conversions, transformations, records,
classes, fields, checked types, serialization, invariants, and errors.

The root-owned custom verifier does not import candidate code. It copies the
private fixture to a read-only temporary tree and invokes pytest as UID 10001
against `/tmp/candidate-site`. It then converts the unprivileged JUnit report
to the fixed `custom-json-v1` node list. The frozen node list has SHA-256
`bcc2439e6dfd49e15d9b81826caae8963b9ab031fe4cfaeeafab1d6ba57676cb`.
Per-leaf assertion-to-spec mappings are stored in
`.nl2repo/evidence/pyrsistent/traceability.json`.

The first production Oracle probe exposed three source-archive symlinks that
the candidate boundary intentionally rejects as non-regular files. The Oracle
solution now verifies that each link stays inside `/workspace` and materializes
its regular-file target after extracting the same frozen archive. This is a
workspace-boundary adaptation only; it does not alter source bytes, public
instruction, or hidden assertions. The repaired production Oracle passed
72/72.

## Immutable Inputs

- Base image: `python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
  (`Python 3.12.14`, Debian 13, linux/amd64)
- Dependency lock: `sha256:5d35f14e65efab521aaea8470ab259e5463e97c8eedeba785ecbbbcc591fed36`
- Private verifier bundle: `sha256:053072a4f128e1733641fffccc806c89d54bd592184c5d3d5c8fe917dc84f407`
- Private Oracle bundle: `sha256:fc5d99af82e4296b57098a2606995853db6000a441e16a3e00ac1ead142377e7`

The dependency artifact is a requirements lock with exact versions and hashes.
Dependencies install only during Docker build; no wheelhouse or `--no-index`
path is present. Agent and verifier phases are `no-network`. The trusted Oracle
solution alone fetches the exact commit using a run-scoped `github.com` grant,
asserts `rev-parse`, reproduces `git archive`, and checks the source digest
before extracting the workspace.

## Production Gates

Harbor compile, Oracle, controls, and final evidence are recorded in
`.nl2repo/evidence/pyrsistent/harbor/` and the task-local handoff. The final
production compile uses Harbor `0.21.0` and toolchain lock
`sha256:f4effe9ffc4b8a0dc0762b3dfce2d575f03bcf4df7c2755c2157cd36b35eb4ff`.
Trusted Oracle is `valid=true`, reward `1.0`, and test pass rate `1.0`.
Controls remain task-local and are not model runs: stub `0/72`, forgery `0/72`,
install-hang bounded timeout `0`, call-hang bounded timeout `0/72`, and invalid
workspace `0`; all verifier network probes report
`public_network_available=false`. Blind review, specification traceability
review, and model pilot remain integrator-owned follow-up stages. The
declarative task remains the authority; `catalog/tasks/pyrsistent` is generated
output and is not edited by this authoring lane.

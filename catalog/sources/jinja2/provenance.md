# Jinja2 Authoring Provenance

- Upstream: `https://github.com/pallets/jinja`
- Frozen commit: `5ef70112a1ff19c05324ff889dd30405b1002044`
- Source archive: unprefixed `git archive --format=tar HEAD`
- Source archive size: `1249280` bytes
- Source archive SHA-256: `61082a25b5f6e7c49a0e4c12d9aa6be8e684489e0d613dc14512e8ea0c001421`
- License: BSD-3-Clause, `LICENSE.txt` SHA-256 `3b49dcee4105eb37bac10faf1be260408fe85d252b8e9df2e0979fc1e094437b`
- Authoring runtime: CPython 3.12.11, uv 0.11.32, Debian 12 amd64
- Source tree: 107 files; 25 Python files under `src/jinja2`; 31 test files
- Static upstream test inventory: 911 test functions across 22 test modules
- Production verifier denominator: 44 deterministic custom-json-v1 leaves
- Runtime dependency: MarkupSafe 3.0.2; build dependency: flit_core 3.12.0
- Candidate dependency lock is private, hash-locked, and installed only during
  image build. The candidate and verifier run with no network access.
- The frozen Oracle workspace initially lacked the cached `trio` test dependency;
  `uv sync --locked --offline --no-default-groups --group tests` repaired the
  test environment from the upstream lock, and the full suite then completed
  with 911 passed tests in 3.17 seconds.
- A full default-group offline sync was also attempted and stopped at the
  uncached `uv==0.7.8` dependency pulled by `pre-commit-uv`; this is a tooling
  group limitation and is outside the runtime/test closure.
- The first call-hang control imported a module-level sleep and caused a
  verifier-internal timeout. It was replaced with one bounded call-path sleep;
  the final call-hang control produced a valid fixed-denominator report.
- The final local Docker tag for the OpenHands agent was observed as
  `sha256:dbfa15a345a0ab167aa205e895b02c5a581c569fea71941ab64c3df4569ec123`,
  while the shared toolchain records `sha256:70525a5fbee81f4d202b7f7de14857fe78f961ce2ec3995efd1a4850e45c7ea5`;
  the integrator must resolve this image identity before a model run.

The Oracle solution bundle contains only a script that fetches the exact commit,
asserts the resolved SHA, verifies the same archive digest, and extracts it into
`/workspace`. The source host is authorized only for the trusted Oracle run.

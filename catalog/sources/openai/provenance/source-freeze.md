# openai source freeze

- Upstream: `https://github.com/openai/openai-python`
- Revision: `555ac487f450f24928d859478ea2f41b58906206`
- Commit tree: `901abab6c406d71500675b9cc68f5ff9f23f109b`
- Commit: `fix(api): encode Realtime call offers and session configuration (#3736)`
- Commit timestamp: `2026-08-25T20:32:14Z`
- Distribution version: `3.3.1`
- License: Apache-2.0, `LICENSE`
- License SHA-256: `sha256:636eb7d79da9bb6d515a4b3fd417aa26679eb3cf16396ddab4bc55fa74e616e4`
- `pyproject.toml` SHA-256: `sha256:afe733c3f305857839fa7d473c17934722b873b7a149693bda3fba58549f4f3c`
- Git submodules: none
- Git archive command: `git archive --format=tar HEAD`
- Git archive bytes: `14653440`
- Git archive SHA-256: `sha256:3fee3c1832ceafd565161d3a0c42555823c7bdb7ca20dc2f217e8f7437365720`

The archive and hashes were computed from a detached checkout of the exact
revision. The task does not copy the archive, upstream tests, or upstream
implementation into the public source. Oracle-only source acquisition remains
inside the private solution bundle and is checked against this revision and
archive digest.

## Baseline and scope decision

The checkout contains 1,900 tracked files, 1,531 tracked `src` Python files,
173 tracked Python test files, and approximately 236,104 Python physical lines.
The full suite mixes generated endpoint smoke tests with live transports,
provider integrations, cryptographic/TLS fixtures, optional dependencies, and
repository tooling. Under the remediation guide it is not a safe transparent
verifier boundary. The selected deterministic contract preserves core model,
serialization, query, SSE, webhook, client configuration, and injected
transport behavior in 36 private leaf tests.

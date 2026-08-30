# wrapt Authoring Provenance

## Source freeze

- Upstream: `https://github.com/GrahamDumpleton/wrapt`
- Frozen full revision: `537612871898f46b394477d701d26dbb78240064`.
- `git archive --format=tar <revision>`: 1,843,200 bytes,
  SHA-256 `aa3892a27dfae6781dc98bf9a70d2cba3eb2954f6fcf8ca2d5582ae5df4c670f`.
- License: BSD-2-Clause; frozen `LICENSE` is 1,304 bytes.
- The revision has no submodules. The package reports version `2.4.0rc5`.

## Baseline and risks

The CPython 3.12.11 authoring probe installed the pinned source with the
optional C extension using setuptools 84.0.0 and wheel 0.48.0. The upstream
pytest suite collected 1,215 nodes and completed with 1,172 passed and 43
skipped; the skips are expected mypy/platform cases. Static inventory found 21
implementation files, 100 test files, 1,180 test definitions, and risk flags
for dynamic signature construction and import-hook/external module behavior.

The production score is an independent 40-leaf JSON adapter. It covers the
stable core proxy, callable wrapper, decorator, signature, patch-chain,
caching, synchronization, and import-hook contracts. It intentionally does
not claim full upstream parity for mypy output, free-threading stress, native
exception propagation, or platform-specific behavior.

## Runtime and network

The target is CPython 3.12.14 on Debian 12 amd64 with the digest-pinned Python
base image in `task.toml`. Candidate build dependencies are installed during
Docker image construction from a private hash-locked requirements artifact;
candidate and verifier execution use `no-network`. The Oracle alone fetches
the exact Git revision, verifies the archive digest, and exposes the resulting
source workspace to the trusted verifier.

Private verifier and Oracle bytes are content-addressed under the task-local
`.nl2repo/artifacts` store and are never placed in this public source tree.

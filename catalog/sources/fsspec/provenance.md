# fsspec Authoring Provenance

## Frozen source

- Upstream: `https://github.com/fsspec/filesystem_spec`
- Revision: `9b7cd481e5d1c4395752e69653443e6b05ac9a3e`
- Commit subject: `Keep block caches usable after pickling (#2102)`
- Commit parent: `c45f6011c37a74e4cf64d4378bad3e0af38382d0`
- Tracked files: 156; production Python files: 48; production physical lines: 19,640.
- `git archive --format=tar <revision>` was repeated and is locked as
  `sha256:9a0fc72facc3b4b8adc7ae9d6719e7d06e7a9a677ddab826931d71079e688e0a`.
- `LICENSE` declares BSD 3-Clause and its bytes were inspected at the frozen
  commit. No source or license bytes are copied into this catalog source.

## Environment and dependencies

The production projection uses CPython 3.12.14 on Debian 12 amd64 with the
immutable `python:3.12.14-slim-bookworm` image digest recorded in `task.toml`.
The package declares no runtime dependencies. The build backend is Hatchling
with Hatch VCS; its exact transitive build closure is hash-locked in the private
requirements artifact referenced by `task.toml` and installed only during image
construction. Candidate and verifier execution are no-network.

The upstream repository has 64 test modules. The full suite includes remote
services, optional native dependencies, credentials, FUSE, and external command
surfaces, so it is not copied into the trusted verifier. The task freezes an
independent 18-leaf deterministic child-side contract covering local behavior.

## Boundary and exclusions

The verifier never adds candidate code to the trusted interpreter path. Each
scenario is executed through `candidate_client.execute_script` as UID 10001;
private tests and reports remain root-owned. Timestamps, object identities,
filesystem ordering outside the documented sorted APIs, network services, and
optional integrations are excluded from the score. This is an adaptation of the
upstream public surface, not a claim of full upstream pytest parity.

Private verifier and Oracle bundles are digest-bound CAS artifacts. The Oracle
fetches only the exact revision, checks the commit and archive digest, removes
remote/optional test trees, and installs the resulting source tree. It receives
the source-host authorization only in the trusted Oracle run.

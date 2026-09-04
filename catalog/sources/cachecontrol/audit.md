# `cachecontrol` authoring audit

## Frozen source

- Upstream: `https://github.com/psf/cachecontrol`
- Revision: `9ff6af2c397bdfbddb57567b2350c202fed45356`
- Commit date: `2026-08-31T09:11:44+08:00`
- Exact `git archive --format=tar` SHA-256:
  `sha256:a4759421bdf464fc3b0bebfaa3ff6d93d11dac0f460621a4b20ae012908fc965`
- License: Apache-2.0, `LICENSE.txt` SHA-256
  `sha256:86eeee87be2a43f3ff1f56496f451f69243926f025fedbb033666c304c4c161b`
- The archive contains 64 regular files/directories, no submodules, no native
  extension, and no special file.

## Test and behavior boundary

The upstream suite collected 113 tests and passed 113/113 in the authoring
environment. Many integration tests start a loopback CherryPy server, and the
optional Redis cache requires a service. The scored contract instead uses 27
deterministic child scenarios for the same local decisions: URI normalization,
cache directives, cache admission/freshness, conditional headers, 304 updates,
MessagePack serialization, heuristics, memory storage, bounded filesystem
storage, and session adapter setup. It never invokes adapter transport.

## Dependency closure

This revision uses `uv_build` and declares `requests` plus `msgpack` at runtime;
the supported filesystem cache also needs `filelock`. The private requirement
lock pins `uv-build==0.11.32`, `requests==2.33.0`, `msgpack==1.2.1`,
`filelock==3.20.3`, and all transitive packages with SHA-256 hashes. The
compiler installs this closure during the verifier image build. Candidate
installation uses `--no-deps --no-build-isolation` after network isolation.

## Security boundary

The custom verifier is root-owned, but every candidate observation runs in a
fresh UID-10001 process. The candidate package and dependency site are separate
from the trusted verifier runtime. Agent and verifier policies are
`no-network`, static agent hosts are empty, and generated agent Compose does
not declare a network. The Oracle alone fetches the exact commit, checks
`FETCH_HEAD`, creates `git archive`, verifies its SHA-256, and copies it into
the workspace.

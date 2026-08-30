# Uvicorn Authoring Provenance

## Source freeze

- Upstream: `https://github.com/Kludex/uvicorn`
- Revision: `9ee5694516b01f1d3d6ff9ed38f117fc869ee6ae`
- Package version: `0.52.4`
- Raw `git archive --format=tar` size: 1,955,840 bytes
- Raw archive SHA-256: `sha256:ea14dd890be1bf0e78f1a5f4984794b9c1b762251a2701435f8d7c29145b0184`
- License: BSD-3-Clause; `LICENSE.md` SHA-256
  `sha256:efe1acf3e62fb99c288b0ec73e5a773b7268ef4320fe757ea994214e4b63c371`
- Submodules: none

The detached revision was resolved and archived in the task-local authoring
workspace. The Oracle repeats the fetch, asserts the exact commit, recreates
the raw archive, and rejects any digest mismatch before restoring `/workspace`.

## Environment and dependencies

The selected immutable image is
`python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
with CPython 3.12.14 on Debian 13.6 amd64. The private dependency lock was
generated with `uv 0.11.32` for Python 3.12 and contains exact hashes for
Uvicorn's `click` and `h11` runtime plus Hatchling, setuptools, wheel, and the
Hatchling transitive closure. A clean image installed it with
`pip --require-hashes`; no wheelhouse, vendor directory, `--no-index`, or
runtime registry access is used.

## Upstream baseline and adaptation

The frozen upstream environment collected 1,329 tests. With network disabled,
1,319 passed and 10 platform/protocol parametrizations skipped in 33.89 seconds.
The production verifier freezes 45 deterministic leaves covering package and
CLI identity, import resolution, Config behavior, logging, trusted proxy
headers, protocol utilities, WSGI/ASGI adapters, flow control, and server state.
The frozen implementation passed all 45 leaves in the authoring probe.

Live listeners, WebSocket transports, TLS fixtures, signals, process
supervisors, filesystem watchers, and optional native protocol engines are
excluded. The verifier uses only bounded in-memory scenarios and invokes the
candidate through the UID-separated child client.

## Handoff policy

The private verifier and Oracle solution are content-addressed under
`.nl2repo/artifacts`. Generated Harbor output remains task-local under
`.nl2repo/`; no `catalog/tasks/uvicorn` projection and no model Agent Run are
created in this lane.

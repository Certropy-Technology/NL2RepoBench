# Frozen Source and Environment

- Upstream: `https://github.com/florimondmanca/httpx-sse`
- Revision: `ccba32e3f9b03d1c1c42b788fdae7ea59ebcb9b8`
- Package version: `0.4.3`
- License: MIT; frozen `LICENSE` bytes are recorded in the handoff.
- Source archive: `git archive --format=tar --prefix=httpx-sse/ ccba32e3f9b03d1c1c42b788fdae7ea59ebcb9b8`
- Runtime: CPython 3.12.11 on `debian-12-amd64`, base image
  `python:3.12.14-slim-bookworm` with the locked digest in `task.toml`.
- Runtime dependency: `httpx==0.28.1`; build dependencies are the pinned
  `setuptools` and `wheel` entries in the private requirements lock.

The upstream repository contains five implementation modules and six test
modules. Its tests cover the SSE decoder, event model, sync/async response
iteration, request headers, and an ASGI integration path. The latter requires a
service adapter and is not needed for the deterministic scored contract.

The selected commit was refetched directly and resolved to
`ccba32e3f9b03d1c1c42b788fdae7ea59ebcb9b8`. A fresh `git archive` was
byte-identical to the Oracle `source.tar` at
`sha256:b8c8d892b6c6557f7ffebf2dd28a14b2d4b12b30ff2c6f110736e7f5ff852220`.
The MIT `LICENSE` bytes hash to
`sha256:beec67e4ee83a7af26f242bed9987aa863d6d2dfb776106aa2360c4187f31901`.

The full upstream baseline ran on CPython 3.12.11 with the revision's pinned
HTTPX, pytest, pytest-asyncio, Starlette, and sse-starlette dependencies. It
passed 59/59 tests. The JUnit receipt is
`.nl2repo/authoring-work/httpx-sse/source-inspect/upstream-baseline.xml`
(`sha256:745fe116153ee050dcfa5672faafedf2f9a84992d937350e07c293b18cd8035b`).

The final production compile contains 60 files. Its bundle manifest is
`.nl2repo/authoring-final/httpx-sse/bundle.manifest.json`, with SHA-256
`66938bbe2a0b7ff2fe06adf7aadbce9e9db046ce4fec3503061c590e5d882d4d`
and canonical manifest digest
`sha256:72ca340fd3055d9f6d838d986978e4d89831a54c17e5847e4971231e60d4dfb1`.
The final Harbor Oracle passed 26/26 leaves at reward 1.0. Empty and
install-hang produced the permitted candidate-installation-failed 0/0 outcome;
stub, forgery, and call-hang each collected 26 leaves and passed 0. A second
offline Oracle passed 26/26. Every verifier network receipt reports
`public_network_available=false`.

The candidate and verifier execute with no network. Only the trusted Oracle
bundle contains the frozen reference source archive; the candidate receives no
source-host authorization and no reference bytes.

The shared `toolchain.lock.toml` declares agent runtime image ID
`sha256:70525a5fbee81f4d202b7f7de14857fe78f961ce2ec3995efd1a4850e45c7ea5`,
but that image ID is absent locally and the current tag resolves to repo digest
`sha256:dbfa15a345a0ab167aa205e895b02c5a581c569fea71941ab64c3df4569ec123`.
The integrator must restore and verify the declared immutable agent image before
any model Agent Run. This lane did not start such a run.

# Frozen Source And Authoring Provenance

- Upstream: `https://github.com/python-websockets/websockets`
- Revision: `e87ea9be0373edd5065b5e94dfa714cfde23023b` (release `17.1`)
- License: BSD-3-Clause; the frozen `LICENSE` bytes hash to
  `sha256:3d6a0c050d8bec52fabad502e45fb25bd02bcadbd70dea34d447b6a0ff4e6da8`.
- Repeated `git archive --format=tar HEAD` streams are 2,775,040 bytes and
  hash to `sha256:f2e255aa0f376ef720727ff3568fd8b0614f91bb0b65a43ccd2e44119bb5d672`.
- The upstream tree has 52 Python implementation files, including the asyncio,
  sync, Trio, legacy, protocol, frame, URI, and header modules; it also has an
  optional `speedups.c` extension.
- The frozen upstream baseline on CPython 3.12.14 ran 2,565 tests, passed
  2,557, and skipped 8 in 100.802 seconds with Docker networking disabled. It
  exited 0. A background sync-server thread printed a non-fatal bad-file-
  descriptor traceback during teardown; the unittest result remained `OK`.
  The authoring Loop archived that run; its verified object inventory is
  retained as `logs/prior-attempt-archive-receipt.json` under the task-local
  authoring-work directory.
- The scored contract is an independently authored 28-leaf deterministic subset
  over pure local APIs. It excludes live networking, TLS, proxies, server/client
  lifecycle, legacy and Trio compatibility, and the optional C extension.
- Candidate and verifier phases are no-network. Only the trusted Oracle bundle
  contains a digest-checked source fetch script. The resumed Oracle run again
  resolved the exact revision, verified the archive digest, and passed all 28
  contract leaves.

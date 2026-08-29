# rsa Authoring Provenance

- Frozen upstream: `https://github.com/sybrenstuvel/python-rsa`, revision
  `42b0e14ffbeeb9d99d1037e6440a2cc61780e4ea`.
- Git archive digest: `sha256:d5f3ae5ac30dc2c284dd449bb8f3aada2612ed41a0eab1decdd1d70b11806ed8`.
- License: Apache-2.0; the frozen `LICENSE` bytes are hash-bound in
  `production-evidence.json`.
- The frozen upstream suite collected 100 tests and ran 99 passed / 1 failed.
  The failure is its mypy self-check under the pinned mypy 1.5.1 and Python 3.12
  combination, not a runtime library failure. The Harbor contract therefore
  uses 100 deterministic custom-json-v1 leaves covering the documented API.
- The private verifier and Oracle bundle are stored in the local private CAS and
  referenced by digest in `task.toml` and `production-evidence.json`. Candidate
  imports and calls run in UID-isolated subprocesses; the verifier owns grading,
  JUnit, collection, and reward files.
- Final production compile used Harbor 0.21.0 and `toolchain.lock.toml` with
  `--allow-private` and no `--allow-incomplete`. Final Oracle, empty, stub,
  forgery, install-timeout, call-timeout, and offline receipts are under
  `.nl2repo/` and are hash-bound by the evidence record.
- No Harbor model Agent Run was started. The local OpenHands image digest does
  not currently match the immutable digest in the shared toolchain lock; this
  is an integrator precondition before model execution.

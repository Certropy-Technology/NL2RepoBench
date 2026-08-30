# Authoring Audit

## Identity and scope

This lane freezes `sysid/sse-starlette` at detached commit
`a815cd3682ce4b01f28e93f4bc59f3d6d5db3d00`, version 3.4.8, under the
BSD-3-Clause license. The unprefixed git archive digest is
`sha256:9945c5a862cd5d6cd5182347c2dad4a633caea80a4bcd21d7b82fcc0941a9703`.
The license file digest is
`sha256:80af6bfccbebd2c14d4aab96695cab9950e177190cc80f5ef819e99996883e8e`.

The package is pure Python but depends on Starlette and AnyIO. Its scored
surface is local event formatting and bounded ASGI behavior; live servers,
database examples, uvicorn signal integration, and thread/multi-loop stress
are outside the deterministic contract.

## Remediation

- The upstream `setuptools` backend and runtime/test closure are pinned in a
  private hash-locked `requirements.lock.txt`; no wheelhouse is vendored.
- The future candidate and verifier use no network. Only the trusted Oracle
  solution receives the exact GitHub host override and verifies the immutable
  revision and archive bytes before extraction.
- The custom verifier calls candidate scenarios through the UID-isolated
  `custom-json-v1` runner and owns collection, JUnit, grading, network, and
  reward output.

## Contract boundary

The private contract has 28 unique leaves covering exports, all event encoding
boundaries, response headers and validation, async/sync streaming, ping and
locking, timeouts, callbacks, shutdown, websocket adaptation, background work,
and package metadata. Every hidden scenario is traceable to the public
instruction and no upstream test or reference implementation is copied into
the public task.

The task remains `discovered` until dependency artifact materialization,
production compile, local verifier replay, and controls are complete. Harbor
Agent Run, review, pilot, and publication are owned by the integrator.

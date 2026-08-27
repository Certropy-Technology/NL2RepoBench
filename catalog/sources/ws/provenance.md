# `ws` Authoring Provenance

## Source and license

- Upstream revision: `d9b89544e627f2a260fb85a6f42c8ecba98d7615`.
- Commit tree: `6c2c918db932afbec8bf0461d96153b354eaf4b4`.
- Source archive SHA-256:
  `ef59e63af8772e6cc00100a743fa267f53fff2022ca32f4b1e303c5fc57140f3`.
- Source archive size: 573,440 bytes; 64 tracked files; 17,685 tracked
  lines, including 15,955 JavaScript lines.
- License: MIT. `LICENSE` SHA-256:
  `2b29dcfe0d6471f7e8c92c5fb38c9f93edee10330937055440192f1832b1ecef`.
- No submodules and no source modifications were present at freeze time.

## Frozen upstream baseline

The source contains 12 Mocha unit files and one external integration file,
with 434 textual `it(...)` declarations. The unit command was run three times
in Node 24.19.0/npm 11.17.0 with both optional native accelerators disabled and
container networking set to `none`. Every run exited 0 with 437 passing and
one pending test; durations were 5, 4, and 4 seconds. Coverage was identical:
99.08% statements, 98.67% branches, 97.82% functions, and 99.15% lines.

The two-test integration file contacts an external echo service over `ws` and
`wss`; it is excluded because it cannot be frozen or executed offline. The
Harbor task instead uses deterministic loopback client/server scenarios.

## Runtime and dependency closure

- Agent source image:
  `docker.io/library/node@sha256:4196d66a565c6f195728d9952f161f4adfe2ad753052a08b7ec7f1c5a6bda42b`.
  It contains Node 24.19.0, npm 11.17.0, Git 2.39.5, Debian Bookworm, and glibc
  2.36. The digest freezes the Oracle's Git and certificate material.
- Required candidate runtime dependencies: none. The optional native peers in
  the reference metadata are not part of the scored contract.
- Private npm closure:
  `sha256:359d8250c8e5f5ee21ca088d7041da898990e9145a957ba0adde94f5160db515`
  (10,240 bytes). It contains a v3 zero-dependency lock, an empty npm cache,
  and a file-digest manifest. Candidate installation still validates the
  candidate's own matching lock with `npm ci --offline --ignore-scripts`.

## Verifier and Oracle

The fixed denominator is 44 `node:test` leaves. A private adapter runs each
allowlisted operation in a UID 10001 Node subprocess with no native addons, a
20-second call timeout, bounded process/file-descriptor limits, and local
loopback sockets only. It covers packaging and exports, extension/subprotocol
parsing, server modes, messaging, binary delivery, protocol/compression
negotiation, ping/pong, broadcast, streams, manual upgrades, EventTarget
behavior, payload limits, state transitions, and close validation. The frozen
package passed 44/44 in 3.31 seconds in the locked image.

Private artifacts:

- command plan:
  `sha256:a832562812d78324c3ac1b16a15a9ab97c6e9e92ad7de119f2da7bb997be8661`
  (10,240 bytes);
- hidden test bundle:
  `sha256:59c5daae8a1e5ec4a4539ec5d4d42d7b7ec31683fa7786b8d5c82c50841b3eb3`
  (30,720 bytes); and
- Oracle bundle:
  `sha256:7ecfc80b5cb9027e8b8c0e38afc4558a38349cb9b28e33a838524c265295a6f3`
  (10,240 bytes).

The Oracle solution alone fetches the full pinned revision, asserts the
resolved commit, recreates `git archive`, verifies it against `source_digest`,
and writes a runtime-only zero-dependency package lock. The model agent never
receives the solution or the run-scoped source-host authorization.

## Scope and residual risk

- This is a bounded, behaviorally representative 44-leaf slice, not all 437
  passing upstream unit tests or the external integration service.
- TLS provisioning, proxies, redirects, Autobahn campaigns, native
  acceleration, and exhaustive low-level frame-class internals are outside the
  denominator.
- One Oracle run plus deterministic controls does not establish cross-run
  model stability; downstream pilot and human review remain separate gates.

## Final production gate evidence

- Production compile command used `toolchain.node.lock.toml`,
  `.nl2repo/artifacts`, `--allow-private`, and the task-local output
  `.nl2repo/authoring-work/node-author-wide-20260826-remediation/ws/compiled-handoff`;
  exit code was 0. The bundle contains 69 files and its manifest records the
  canonical manifest digest `sha256:97ef714126e256a4ea1cd6afca95e13c99da383b7171db956e91152133902152`.
- Harbor `0.21.0` Oracle job
  `harbor-oracle-final/2026-08-27__19-19-27` completed with exit code 0, reward
  `1.0`, `valid=true`, and 44/44 leaves passed with no collection errors.
  This also supplies the offline verifier control: its network receipt
  recorded `public_network_available=false`.
- Empty, stub, forgery, and call-hang controls completed with Harbor exit code
  0 and `valid=true`. Their rewards were respectively `0.0`, `0.0`, `0.0`,
  and `0.0`; the failure reasons were installation failure for empty,
  candidate test failures for stub/forgery, and candidate-call failure for the
  bounded hang. The forgery's workspace reward file did not affect grading.
  All control verifier network receipts recorded `public_network_available=false`.
- Final shell and Node syntax checks and JSON/TOML parser checks exited 0.
  Direct Oracle workspace `npm ci --offline --ignore-scripts` exited 0; a
  corrected `npm pack --ignore-scripts` exited 0 and produced
  `ws-8.21.3.tgz` with SHA-256
  `cd832c14585261ca8d33f22695b4ea6f43bd473eb1e37ec5cacb491ca6383e49`.

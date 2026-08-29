# `is-fullwidth-code-point` authoring provenance

Status: `controls-passed`; source and verifier artifacts are task-local. The handoff remains
`awaiting-agent-run` because model evaluation and catalog integration belong to the parent loop.

## Source and license freeze

- Upstream: `https://github.com/sindresorhus/is-fullwidth-code-point`.
- Frozen revision: `2696d873463fde9f6b09b49c98380bd49c67b00a` (`5.1.0`).
- The revision has no submodules and declares MIT in its root `license` file.
- The source archive and license bytes are hashed in `evidence/source-freeze.json`.

The private Oracle bundle contains the digest-verified upstream archive. It is
materialized only for the trusted Oracle and is not copied into the model image
or public instruction.

## API and test inventory

- Runtime surface: one default ESM function,
  `isFullwidthCodePoint(codePoint: number): boolean`.
- Upstream behavioral baseline: one AVA test file with seven assertions, plus
  TypeScript declaration coverage.
- Production verifier freezes 24 unique `node:test` leaves covering package
  shape, representative Unicode width categories, invalid input behavior,
  range boundaries, and repeat-call determinism. The detailed mapping is in
  `traceability.md`.

## Environment and dependency closure

- Runtime image: Debian bookworm Node image pinned in `task.toml`.
- Runtime: Node `24.19.0`, npm `11.17.0`, linux/amd64, glibc.
- Runtime dependency: exact `get-east-asian-width@1.6.0`, in a private npm v3
  closure with integrity-checked cache entries.
- Candidate and verifier runtime network mode is `no-network`; source,
  registry, and provider hosts are absent from task metadata.

## Verifier boundary

- Separate verifier image with candidate UID 10001 and no network.
- Candidate package is copied to a bounded staging tree, installed with scripts
  disabled, packed, validated, and installed into a candidate-owned prefix.
- Trusted `node:test` invokes the default export only through the bounded JSON
  child-process boundary. It never imports candidate code directly.

## Gate record

The current production compile is `.nl2repo/final-compile/is-fullwidth-code-point`
with manifest SHA-256
`658e066def3d2990b665686d89abe869c6c9b09a0e57c4b941f436b5e8682d7d`.
Harbor 0.21.0 Oracle collected and passed 24/24 with reward 1.0; empty, stub,
forgery, install-script, loader-hook, bounded-hang, and offline controls all
completed with the expected zero/low score and `public_network_available=false`.
Exact commands, receipt hashes, and control classification are recorded under
`.nl2repo/evidence/is-fullwidth-code-point/production-evidence.json` and the
current3 receipt directories. Independent review, publication, and a model Agent
Run remain outside this authoring lane.

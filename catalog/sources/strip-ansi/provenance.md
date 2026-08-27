# `strip-ansi` authoring provenance

Status: `controls-passed`; ready for independent review and later model pilot.

## Source and license freeze

- Upstream: `https://github.com/chalk/strip-ansi`.
- Frozen revision: `38ff9f2282540422031ed523f0060c7bb575e20f` (`v7.2.0`).
- Commit timestamp: `2026-02-26T20:50:15+07:00`.
- `git archive --format=tar` SHA-256:
  `fd02f8851dfbe8b499d8847da63563d587d070a7324e61b3a2243d577eab07f3`.
- Archive size: 30,720 bytes; no submodules.
- Root license is MIT text, SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- `package.json` declares `MIT`.

The private Oracle bundle contains this digest-verified source archive. It is
materialized only for the trusted Oracle agent and is not copied into the
model image or public instruction.

## API and test inventory

- Runtime surface: one default ESM function, `stripAnsi(string)`.
- Declaration surface: `stripAnsi(string: string): string`.
- Implementation plus declaration: 34 lines.
- Upstream framework: AVA with XO and tsd development gates.
- Upstream behavioral denominator: eight AVA tests.
- Three isolated baseline executions on the locked Node image passed all eight
  tests; the first run installed the development closure and the next two ran
  with `--network none`.

The production verifier freezes 24 unique `node:test` leaves. The expansion
covers only publicly specified CSI/OSC terminators, Unicode/text preservation,
input errors, package shape, and repeat-call determinism. The detailed
test-to-spec mapping is in `traceability.md`.

## Environment and dependency closure

- Runtime image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64,
  glibc.
- Runtime dependency resolution is frozen to `ansi-regex@6.3.0`, the exact
  version resolved by the clean revision baseline.
- Private npm v3 closure:
  `sha256:fca0905de2da87051d3d77c8c6ea2a643115894d0f1431b21b6673678ecb8c4c`
  (71,680 bytes).
- The closure contains a lockfile, four content-addressed npm cache files, and
  per-file SHA-256 records. It passes `validate_npm_dependency_bundle` and a
  clean `npm ci --offline --ignore-scripts --no-audit --no-fund` probe.
- Candidate and verifier runtime network mode is `no-network`; package source,
  registry, and provider hosts are absent from task metadata.

The source revision declares development dependencies and disables lockfile
generation in `.npmrc`. The Oracle performs a bounded packaging adaptation:
it removes development-only scripts/dependencies and `.npmrc`, pins the
runtime dependency to `6.3.0`, and writes the reviewed npm v3 lock. Runtime
implementation bytes remain the exact frozen source archive.

## Verifier boundary and private artifacts

- Verifier: separate, no-network Node/Python image with candidate UID 10001.
- Candidate source is copied to a bounded staging tree, installed with
  lifecycle scripts disabled, packed, validated, and installed into a
  candidate-owned prefix.
- Trusted `node:test` never imports candidate code. Each operation launches a
  bounded candidate child and exchanges one JSON request/response.
- Dependency bundle:
  `sha256:fca0905de2da87051d3d77c8c6ea2a643115894d0f1431b21b6673678ecb8c4c`.
- Command-plan bundle:
  `sha256:ff24615a926405b2fa2d1bde2ccbb0816fc0a5d3364f4585da23888979c665cf`.
- Private test bundle:
  `sha256:2b156c1c4019d222dc87ad63e095e44ad1c5874ecb5ef1f17b7e4df9b7089f5e`.
- Oracle bundle:
  `sha256:f9498afac8df8ccf36debd67aa6a884f8c3e6a11739607eab627471013a9e455`.

## Production gates

- `uv run nl2repo task validate-source catalog/sources/strip-ansi`: pass.
- `uv run nl2repo task lint-network --tasks-root catalog/sources`: zero errors
  and no `strip-ansi` finding; unrelated legacy warnings remain outside this
  lane.
- Production compile with `toolchain.node.lock.toml`,
  `.nl2repo/artifacts`, and `--allow-private`: pass.
- Final Harbor Oracle: `valid=true`, 24 collected, 24 passed, reward `1.0`.
- Negative controls: empty `0.0`; stub `2/24` (`0.08333333333333333`);
  forgery `0.0`; install-script rejected as candidate installation failure;
  loader-hook `5/24` (`0.20833333333333334`) without loader activation;
  bounded hang `0.0` with `candidate-call-failed`; offline fetch `0.0`.
- All Oracle/control network receipts report
  `public_network_available=false`.
- `scripts/validate_node_production.py`: pass.

The task has not received independent blind/spec review, publication approval,
or a model Agent run. Those remain integrator/campaign stages.

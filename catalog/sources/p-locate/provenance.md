# `p-locate` Authoring Provenance

## Source and license freeze

- Upstream: `https://github.com/sindresorhus/p-locate`
- Frozen revision/tag: `b9ccdaaa83f8d2f53f8acf8ff3c97b7aa21f655b` / `v7.0.0`
- Commit date/subject: `2026-02-03T14:57:33+07:00` / `7.0.0`
- Source archive: unprefixed `git archive --format=tar HEAD`
- Source archive SHA-256: `7c1a4f05591c63b2ef538dfb24df894a3ff3d2de56622a85b7787d54e3e0299b`
- Source archive size: 30,720 bytes; 13 tracked files; no submodules
- License: MIT; frozen `license` SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`

## Upstream baseline and inventory

The complete upstream `npm test` command (`xo && ava && tsd`) passed in the
locked Node 24.19.0/npm 11.17.0 image. AVA collected and passed 13/13 leaves;
XO and tsd also exited zero. The same command passed on the authoring host's
Node 22.23.1/npm 10.9.8. The runtime consists of one 59-line ESM source file,
one 79-line declaration, one 166-line AVA file, and one tsd file.

The upstream `.npmrc` sets `package-lock=false`. Production remediation keeps
the frozen source unchanged but creates an exact runtime-only package manifest
and npm v3 lock with `p-limit@7.3.1` and `yocto-queue@1.2.2`.

## Runtime and dependency closure

- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm glibc `2.36`,
  `linux/amd64`.
- Base image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- The npm closure has two package entries, both with SHA-512 integrity and no
  native, platform, lifecycle, workspace, Git, or file dependency.
- The private closure archive is
  `sha256:6a0913d75bb8ab3708466dceb83046fa8244cfd279591a09183f991a068ccc9f`
  (133,120 bytes). It contains only `package-lock.json`, `npm-cache/`, and a
  per-file-hash manifest.
- The repository validator accepted the bundle with npm 11.17.0. A fresh
  `npm ci --offline --ignore-scripts --no-audit --no-fund` under Docker
  `--network none` installed exactly `p-limit@7.3.1` and
  `yocto-queue@1.2.2`.

## Private verifier and Oracle boundary

- Command plan:
  `sha256:10e70a89b271a2cd71d8dbaa6848530c6550ac4d87e65ae87d7332265e5eedd9`
  (10,240 bytes).
- 38-leaf test/adapter bundle:
  `sha256:6a2b2aedd4529bd2e6dd0f4d1a4cb641b617ee118306fe88e67ce80e851fb424`
  (30,720 bytes).
- Oracle bundle:
  `sha256:4af6763bc0c4901a9f0a4b3d7b5f9f6d0cfe555d4f5e24a9de1e74d67acd9cf9`
  (10,240 bytes).

The Oracle script is private. It fetches only the full frozen revision from
`github.com`, asserts the resolved commit, recreates the unprefixed archive,
checks its SHA-256, and applies the runtime-only manifest/lock. That source
host is authorized only for the trusted Oracle run. The model Agent and
separate verifier remain `no-network` with no static allowed hosts and do not
receive the source, tests, adapter, or Oracle bytes.

## Harbor and control results

The production compiler resolved all four private artifacts without
`--allow-incomplete`. The first Oracle attempt collected 38 leaves but failed
them before candidate import because a task-local 512 MiB `prlimit --as` was
too small for Node 24's V8 virtual-address reservation. Direct reproduction
captured `Fatal process out of memory: SegmentedTable::InitializeTable`. The
incompatible per-child address-space cap was removed while retaining the
container memory limit plus child CPU, process, FD, wall-time, and output
bounds. The resealed verifier then passed a no-network Docker Oracle `38/38`.

Harbor 0.21.0 subsequently produced these v2 task-local receipts before the
final lifecycle-only recompile:

| Run | Valid/collection | Reward | Network |
| --- | --- | ---: | --- |
| Oracle | `true`, 38/38 | 1.000 | `false` |
| Empty | `true`, allowed install exception 0/0 | 0.000 | `false` |
| Packaging stub | `true`, 7/38 | 0.184 | `false` |
| Forged tests/reward | `true`, 7/38, verifier-owned | 0.184 | `false` |
| Network-attempting candidate | `true`, 3/38 | 0.079 | `false` |
| Forbidden lifecycle script | `true`, allowed install exception 0/0 | 0.000 | `false` |
| Non-settling calls | `true`, 1/38 | 0.026 | `false` |

Every row's `network.json` records `public_network_available=false`. Final
canonical receipts are bound in `production-evidence.json` after the lifecycle
transition is recompiled.

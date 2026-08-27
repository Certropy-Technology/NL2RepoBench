# `execa` authoring provenance

## Immutable source and license

- Upstream: `https://github.com/sindresorhus/execa`
- Revision: `8017b279e19347efaf2587711c2d57dbd4330740`
- Tree: `f8ab67228ee0a417058f9bc2282945f915f64f39`
- Unprefixed archive command: `git archive --format=tar <revision>`
- Archive SHA-256: `186d006054087f9a5b24cfc73b583e6a7be36920d210a8b87ac12ba15bfad2e3`
- Archive size: 2,519,040 bytes; no submodules.
- Root `license` and `package.json` declare MIT. License SHA-256:
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.

The prior blocked source record used archive digest `8ee157...f49115` without
retained bytes. A fresh shallow fetch of the full immutable SHA produced the
same `186d006...ad2e3` digest for `HEAD`, the full SHA, and `FETCH_HEAD`; the
repository has no `export-subst`. Version 1.1.0 corrects that stale metadata.

## Frozen environment and upstream baseline

The production image is
`node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`:
Node `24.19.0`, npm `11.17.0`, linux/amd64, Debian glibc 2.36. The source does
not commit a lockfile. In that image, authoring generated npm lockfile v3 with
691 integrity-bearing dependency entries, then a clean
`npm ci --ignore-scripts --no-audit --no-fund` succeeded. The generated lock's
SHA-256 is `5909554583fb61c2ebd0938b56d24dc17ee3aa7fa6e5477e5fe62e94039a33e7`.

The full AVA unit command under `--network none` completed in 353 seconds with
5,134 passed leaves and 16 failures. All 16 failures came from
`test/methods/node.js` and were `getaddrinfo EAI_AGAIN nodejs.org` from the
`get-node` downloader. With only that externally downloading module removed
from discovery, three independent offline runs each passed 5,069/5,069 in
259, 263, and 260 seconds.

## Deterministic adaptation

The frozen package exposes 11 runtime values and has 5,150 observed AVA leaves.
This task does not claim full-suite parity. It documents and scores the six
non-IPC exports used for deterministic local process execution. The private
Node test bundle freezes 30 leaves covering package exports, command parsing,
argument boundaries, UTF-8 output, input, newline handling, cwd/environment,
structured async and sync failures, command-resolution failure, Node script
execution by path and file URL, and timeout termination.

Every candidate call runs in a fresh UID 10001 process with sanitized
environment, resource limits, bounded JSON I/O, and an outer timeout. The
30-leaf bundle passed 30/30 against the frozen upstream implementation and in
three independent runs against the standalone no-dependency Oracle adaptation.

## Private artifact closure

- npm v3 dependency bundle:
  `sha256:1aedbed27defe188f08008f6164c41f5b430a19bd6074de3657828ac9c662712`
- command-plan bundle:
  `sha256:4b49a84dde430c8a5988cc9de93258aeadffea62d82d120f24fd0a4cb1e82bb8`
- private 30-leaf test bundle:
  `sha256:7de308551563e361e7f633ca8295aff9a53c02a559fb71ffa1e4216fb53911e0`
- standalone Oracle bundle:
  `sha256:e10899d815598165aeefa7acaaf5de57176bad491a75d677ee2708e9cd78b2cf`

The candidate and Oracle packages have no runtime npm dependencies. The private
npm bundle contains a scripts-free v3 lock and an empty cache. Production
compile and Harbor control evidence are recorded in `production-evidence.json`
after those gates complete.

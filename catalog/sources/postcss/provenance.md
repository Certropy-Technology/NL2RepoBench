# `postcss` Authoring Provenance

## Source and license freeze

- Upstream: `https://github.com/postcss/postcss`.
- Revision: `6d23bc362203118478bc8051b81f2910907ebe6e`.
- Package: `postcss@8.5.26`.
- Root `git archive` SHA-256:
  `58ec002726ff181bc854a0d8c91e4bd6b261ff2cfb1b60be8385f568aa938e55`
  (the private Oracle bundle verifies this exact archive before it materializes
  `/workspace`).
- License: MIT; `LICENSE` SHA-256:
  `5be1f3465bba68a626777f984878814aaf35e7ef8e9fd314d469bcf887050fb8`.

## API and test inventory

- The package root exports the callable PostCSS factory, parsing/stringifying
  helpers, constructors, and ESM wrapper documented in `api-inventory.json`.
- The frozen revision has 115 tracked files, 28 runtime JavaScript files and
  one ESM wrapper in `lib/`, and
  699 passing upstream unit assertions across its TypeScript/JavaScript suite.
- Baseline command in the locked Node image was
  `corepack pnpm install --frozen-lockfile --ignore-scripts && corepack pnpm unit`.
  It passed 699/699 tests. Development dependencies are baseline-only and are
  not present in the candidate runtime closure.
- The production adaptation has 32 fixed `node:test` leaves. See
  `traceability.md` and `candidate-boundary.json`.

## Environment and dependency closure

- Runtime image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc.
- Exact runtime dependencies: `nanoid@3.3.18`, `picocolors@1.1.1`, and
  `source-map-js@1.2.1`.
- Private npm v3 closure:
  `sha256:19bcd8e05e38de3a80b5ec32e970b34f693efe98f9ba49045182d76f3d2b3d35`
  (542,720 bytes). It contains the package lock, the three exact dependency
  tarballs, the three registry packuments required by npm v11 offline ideal-tree
  resolution, and per-file SHA-256 records. A clean Node 24
  `npm ci --offline --ignore-scripts --no-audit --no-fund` plus packed-candidate
  install probe passed.

## Verifier and Oracle boundary

- Separate no-network verifier; candidate child UID is 10001.
- Candidate workspace is bounded-copied, installed and packed with npm scripts
  disabled, then loaded only inside one-shot JSON subprocesses.
- The trusted test process does not import candidate JavaScript. Requests are
  capped at 64 KiB, responses at 256 KiB, tree projections at 512 nodes.
- Command bundle: `sha256:98d5fb2a995517606e3537badf8e157afb053151f99b2516cea47b11ecc4e800`.
- Test bundle: `sha256:edb020f278c59bf35768d9490f8c9e4e13081152dfcb4d55e6f7158966dab8a5`.
  Its trusted client makes the copied adapter executable for UID 10001 while
  leaving the private source tree root-only.
- Oracle bundle: `sha256:3b7a0559065f1d69eab0823ad16440659581b7d7371eb997a28d2e9a72c8eb1c`.

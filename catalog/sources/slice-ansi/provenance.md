# `slice-ansi` authoring provenance

## Source and license freeze

- Upstream: `https://github.com/chalk/slice-ansi`.
- Frozen revision: `50fc7781f5dd4d1421dbe061822d815708831af4` (`9.0.0`).
- Git tree: `d8d15a66e822efdbb4aaa632559d4854d2c5193d`.
- Deterministic archive command: `git archive --format=tar HEAD`.
- Source archive SHA-256: `sha256:178ba29b83709711b44e533074d5b8c5c16ecb79b60956ae965b6b15d724b402`.
- The tracked `license` file is MIT; its SHA-256 is
  `sha256:c91d87c3bca16ab6d96d82da08edc54377d14b679547a331eecc4adef3c353c8`.
- The frozen checkout is clean after the source probe. It has no submodules.

## Inventory and probes

- Public runtime surface: one default ESM function
  `sliceAnsi(string: string, startSlice: number, endSlice?: number): string`.
- Supporting runtime modules: `index.js` and `tokenize-ansi.js`; declaration:
  `index.d.ts`.
- Upstream test runner: AVA 7 with 94 passing assertions on the authoring
  checkout. XO emitted two max-line warnings only; TypeScript declaration
  checking passed.
- The production denominator is a deterministic 24-leaf node:test slice,
  recorded in `traceability.md`, because random AVA tests and the upstream
  development dependency graph are not suitable for a fixed offline verifier.

## Environment and dependency closure

- Production image: Debian bookworm Node image pinned by digest in `task.toml`.
- Runtime contract: Node `24.19.0`, npm `11.17.0`, linux/amd64, glibc.
- Exact candidate dependency closure:
  `ansi-styles@6.2.3`, `is-fullwidth-code-point@5.1.0`, and
  `get-east-asian-width@1.6.0`.
- A task-local npm cache was created and an isolated `npm ci --offline
  --ignore-scripts --no-audit --no-fund` install was completed successfully.
- Candidate and verifier phases use no network. The Oracle alone fetches the
  exact source revision with a digest assertion.

## Boundary and controls

The verifier is a separate environment. It copies the candidate workspace
through the bounded Node tree copier, installs and packs it with scripts
disabled, then calls the default export through a UID-isolated JSON child.
Trusted `node:test` never imports candidate code directly. Empty, stub,
forgery, install-script, loader-hook, call-hang, oversized-output, and offline
controls are task-local controls generated from the source bundle.

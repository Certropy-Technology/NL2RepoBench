# `flatted` authoring provenance

Status: `controls-passed`; ready for independent review and a later model
Agent Run.

## Source and license freeze

- Upstream: `https://github.com/WebReflection/flatted`.
- Frozen revision: `e6f5ca700c4ca8104a6a83472c8219e267bd5e84`.
- Commit tree: `42ddd776bb147fb487277b27bc190d5526c1c1bc`.
- Commit subject: `3.4.4`.
- Commit timestamp: `2026-07-30T11:52:52+02:00`.
- Raw `git archive --format=tar HEAD` size: 2,242,560 bytes.
- Raw archive SHA-256:
  `e784adfcfef6c281d5700256dc1762b704eb11943cad7a46c18029c1a9e04c2a`.
- Submodules: none; detached source worktree was clean.
- `package.json` declares `flatted@3.4.4` and `ISC`.
- Root `LICENSE` is ISC text, SHA-256
  `148718606d34f467fd08a2176bb4c1ab275f999576f779368503d8d3e3642861`.

No upstream source bytes are stored in the public source directory. The trusted
Oracle fetches only the full frozen commit using a run-scoped `github.com`
authorization, asserts the commit, and verifies the raw archive digest before
materializing the package.

## Package and API inventory

The package is dual ESM/CommonJS and exports `parse`, `stringify`, `toJSON`, and
`fromJSON`. `types/index.d.ts` declares all four functions. The package has zero
runtime dependencies. Its npm v3 lock contains 235 non-root development entries
used only for build, coverage, TypeScript, and compatibility comparisons.

Production intentionally excludes those development packages. The published
runtime files at the frozen revision are already built, so the Oracle strips
development scripts/dependencies and writes an exact root-only npm v3 lock.
The candidate dependency closure is therefore an empty integrity-recorded npm
cache plus that root lock, not an unfrozen development install.

Pinned file digests:

- `package.json`: `b2ff4da4785cbefcbdb4bd5951cf9232f3fe8d9c55c210cab5e28c0a120f0ba0`;
- `package-lock.json`: `52bd287d74c4a21a05898429cd5c7627bbcd159928c38afb7bfb7202ee5a2c9a`;
- `esm/index.js`: `d697ad948769363b99110e1bffe84269a7e74955b42e4e74abac61b02f6c9de6`;
- `cjs/index.js`: `a6fda60d434e62631778a7d18acfc2aeaac59740205cffbae894fd654cd82171`;
- `types/index.d.ts`: `9d8bf1b59550675cba7b63b35eacdbeb25db851efdb4b8bca235bc8e4be9b245`.

## Upstream baseline

The first source-only `npm test` attempt exited 127 because `c8` was absent.
After an exact `npm ci --ignore-scripts --no-audit --no-fund`, `npm test`
exited 0 and reported 100% statements, branches, functions, and lines. The
upstream file uses `console.assert` rather than `node:test`, so it does not
publish a stable leaf count; the production denominator is the separately
named 35-leaf behavior contract described in `traceability.md`.

## Verifier adaptation

Circular identity cannot cross ordinary JSON directly. A fixed-operation child
adapter constructs allowlisted graphs inside UID 10001, invokes the installed
package, and returns bounded canonical graph observations. The trusted test
process receives no candidate object and never imports the candidate. Replacer
and reviver callbacks are fixed adapter behaviors rather than executable input.

The candidate and separate verifier run with no network. The model environment
receives neither source bytes nor source-host authorization. Complete artifact
digests, compiled bundle identity, Oracle grading, controls, and runtime network
receipts are recorded in `production-evidence.json` after final validation.

# `date-fns` Authoring Provenance

This is a bounded Node/npm task for the frozen upstream revision
`a0a39220522ed1228445792c768ed887709aea5f`. The upstream repository is a pnpm
monorepo; the publishable package is `pkgs/core`, version `4.4.0`.

## Source Freeze

- Upstream: `https://github.com/date-fns/date-fns`
- Commit: `a0a39220522ed1228445792c768ed887709aea5f`
- Commit tree: `f53cf87f3d0908b3a99d0fdc42362a334ae78b4d`
- Commit subject: `Fix \`set\` docs example`
- Commit timestamp: `2026-06-03T02:49:24+05:30`
- Reproducible source archive: `.nl2repo/authoring-work/evidence/source/date-fns-a0a39220522ed1228445792c768ed887709aea5f.tar.gz`
- Source archive SHA-256: `bfae8a8d4c91f0d01026245898ff9b3a49ad4a1ce10df4c711a97cae302b4bf9`
- Archive command: `git -C .nl2repo/authoring-work/source/repo archive --format=tar --prefix=date-fns/ a0a39220522ed1228445792c768ed887709aea5f | gzip -n`
- License: MIT, declared by `pkgs/core/package.json` and present in `pkgs/core/LICENSE.md`.

The source checkout was verified with `git rev-parse`, `git show`, and a clean
status at the frozen commit. The source archive contains the commit tree and
does not include the checkout's `node_modules` directory.

## Inventory and Scope

The checkout contains 1,903 tracked files, the root package exposes 250 value
exports and 741 export paths, and the core package has 256 upstream test files
with 3,666 static Vitest declaration sites. The core package has no runtime
dependencies, but the full development closure includes workspace packages,
Vitest, browser tooling, and a native TypeScript preview package.

The scored contract therefore uses 21 deterministic JSON-boundary leaves in
arithmetic, calendar boundaries, parsing/formatting, predicates, intervals,
and min/max selection. The exact private bundle and test-to-contract mapping
are recorded in `test-inventory.json` and `traceability.json`.

## Dependency and Build Probes

The source checkout was probed with Node `22.23.1`, npm `10.9.8`, pnpm
`10.33.0`, and the preloaded pnpm store:

- `pnpm install --offline --frozen-lockfile`: exit 1 because the store lacked
  `@typescript/native-preview@7.0.0-dev.20260421.2`.
- direct core `npm ci --offline`: exit 1 because workspace metadata contains
  `workspace:*` development dependencies.
- `npm pack --dry-run --ignore-scripts` for `pkgs/core`: exit 0.
- a direct import probe of the existing built core output: exit 0.

These failures are environment/remediation evidence for the full monorepo,
not a task blocker: the production task uses a zero-runtime-dependency npm
candidate contract and a lockfile-3 offline closure. The verifier installs
with `npm ci --offline --ignore-scripts`, then packs and installs the candidate
tarball in a separate child-process boundary.

## Evidence Layout

- `api-inventory.json`: observed public API and selected JSON surface.
- `test-inventory.json`: upstream and frozen test inventory.
- `traceability.json`: private leaf to public contract mapping.
- `.nl2repo/authoring-work/private/date-fns/`: source material for the private
  dependency, test, command-plan, and Oracle bundles.
- `.nl2repo/authoring-work/evidence/`: source archive and later gate reports.

The task is not published or added to a dataset by this lane. An integrator
must perform the final independent reviews and publication transaction.

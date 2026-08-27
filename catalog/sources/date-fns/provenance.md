# `date-fns` Authoring Provenance

This is a bounded Node/npm task for the frozen upstream revision
`a0a39220522ed1228445792c768ed887709aea5f`. The upstream repository is a pnpm
monorepo; the publishable package is `pkgs/core`, version `4.4.0`.

## Source Freeze

- Upstream: `https://github.com/date-fns/date-fns`
- Commit: `a0a39220522ed1228445792c768ed887709aea5f`
- Commit tree: `f53cf87f3d0908b3a99d0fdc42362a334ae78b4d`
- Commit subject: `Fix \`set\` docs example`
- Commit timestamp: `2026-08-10T16:47:37+08:00`
- Reproducible raw source archive: `.nl2repo/authoring-work/date-fns/evidence/date-fns-a0a39220522ed1228445792c768ed887709aea5f.tar`
- Raw `git archive` SHA-256: `636db05bafd090414a7d3f6d72aa8f50a4e9afdd0624f86c92f46a3084be170d`
- Raw archive size: `13,312,000` bytes
- Deterministic gzip SHA-256: `da07b0f4ee6e4eb5d9f868ded08cc8c00b54defdfa74185820d09e19af642ad5`
- Archive command: `git -C .nl2repo/authoring-work/date-fns/source/repo archive --format=tar --output=<path> a0a39220522ed1228445792c768ed887709aea5f`
- License: MIT, declared by `pkgs/core/package.json` and present in `pkgs/core/LICENSE.md`.

The source checkout was verified with `git rev-parse`, `git show`, and a clean
status at the frozen commit. The source archive contains the commit tree and
does not include the checkout's `node_modules` directory.

## Inventory and Scope

The checkout contains 1,903 tracked files, the root package contains 246 export
statements and 741 export paths, and the core package has 258 upstream test
files with 2,889 static `test`/`it` declaration sites. The core package has no runtime
dependencies, but the full development closure includes workspace packages,
Vitest, browser tooling, and a native TypeScript preview package.

The scored contract therefore uses 39 deterministic JSON-boundary leaves in
arithmetic, calendar boundaries, parsing/formatting, predicates, intervals,
and min/max selection. The exact private bundle and test-to-contract mapping
are recorded in `test-inventory.json` and `traceability.json`.

## Dependency and Build Probes

The earlier source checkout was probed with Node `22.23.1`, npm `10.9.8`, pnpm
`10.33.0`, and the preloaded pnpm store:

- `pnpm install --offline --frozen-lockfile`: exit 1 because the store lacked
  `@typescript/native-preview@7.0.0-dev.20260421.2`.
- direct core `npm ci --offline`: exit 1 because workspace metadata contains
  `workspace:*` development dependencies.
- `npm pack --dry-run --ignore-scripts` for `pkgs/core`: exit 0.
- a direct import probe of the existing built core output: exit 0.

These failures concern the full development monorepo and are not a task
blocker. The production task uses the core package's observed zero-runtime-
dependency contract and a validated lockfile-3 empty-cache closure. The verifier installs
with `npm ci --offline --ignore-scripts`, then packs and installs the candidate
tarball in a separate child-process boundary.

The frozen package exports TypeScript source. Node 24 intentionally refuses to
strip TypeScript after installation under `node_modules`, so the Oracle uses
the locked Node 24.19.0 `node:module.stripTypeScriptTypes` transform before
packing. It rewrites relative `.ts` module specifiers to `.js`, removes test and
declaration files, and emits 1,238 JavaScript files with no remaining
TypeScript. No registry package or external build backend is required. Three
independent final-image verifier baselines each collected and passed `39/39`
leaves with reward `1.0` and `public_network_available=false`.

## Evidence Layout

- `api-inventory.json`: observed public API and selected JSON surface.
- `test-inventory.json`: upstream and frozen test inventory.
- `traceability.json`: private leaf to public contract mapping.
- `.nl2repo/authoring-work/date-fns/private/`: source material for the private
  dependency, test, command-plan, and Oracle bundles.
- `.nl2repo/authoring-work/evidence/`: source archive and later gate reports.

The task is not published or added to a dataset by this lane. An integrator
must perform the final independent reviews and publication transaction.

# ajv-formats authoring provenance

## Freeze

- Upstream: `https://github.com/ajv-validator/ajv-formats`
- Revision: `4ca86d21bd07571a30178cbb3714133db6eada9a`
- Commit timestamp: `2024-04-05T22:53:40+01:00`
- Package version: `3.0.1`
- License: MIT, verified from the frozen root `LICENSE` and package metadata.
- Raw `git archive --format=tar` SHA-256: `e801e2f5c06e5cf85258abfb0d260c2d7eb2a681b525a7a447b85ff00a19d3e4`.
- Frozen tree: `f2c2b8f206cf1b2ebfe290ed05e623bb966e5698`.
- Submodules: none required by the package source or selected tests.

## Baseline probes

- Node `v22.23.1`, npm `10.9.8` authoring probe: `npm install --ignore-scripts --no-audit --no-fund` succeeded and installed 625 packages.
- `npm run build` succeeded and emitted `dist/formats.js`, `dist/index.js`, `dist/limit.js` and declarations.
- `npm run test-spec -- --runInBand` succeeded: 4 suites, 350 tests passed.
- The upstream full `npm test -- --runInBand` reached prettier, TypeScript build, then failed at ESLint because the nested authoring checkout and its parent both supplied `@typescript-eslint/eslint-plugin`; this is a tooling-path collision, not a source or test failure.

## Remediation decision

The production task is a bounded CommonJS/JSON adapter slice. The upstream Jest and JSON Schema suite is inventoried as ground truth but is not copied into the public task. Private `node:test` leaves cover the documented format table, full/fast validation, `.get`, registration selection, and format comparison keywords. Candidate code is installed and exercised in an unprivileged subprocess inside a separate no-network verifier.

# `jsonc-parser` Node v2 Pilot Audit

**Status: blocked.** This is an evidence record for the failed authoring lane,
not a Harbor task or a production dataset entry. No upstream hidden tests,
private bytes, dependency cache, or secrets are included.

## Candidate lock

- Package: `jsonc-parser`
- Upstream revision: `900046d46a96dd5d014030e37c0055157921ef92`
- Upstream source was rechecked from
  `https://github.com/microsoft/node-jsonc-parser/commit/900046d46a96dd5d014030e37c0055157921ef92`;
  the fetched object resolves to the exact locked commit.
- The locked `package.json` declares ESM (`"type": "module"`), MIT
  licensing, and no runtime `dependencies`; `LICENSE.md` contains the MIT
  license text. This confirms source/license eligibility only and does not
  clear the dependency or authoring gates.
- The requested Node v2 contract is Node `22.23.1`, npm `10.9.8`, ESM, and
  the JSON-only subprocess boundary used by `node-synthetic`.

## Static evidence

- The locked source has **87 direct `node:test` leaf declarations** across
  four suites: `src/test/edit.test.ts` (20), `src/test/format.test.ts` (38),
  `src/test/json.test.ts` (27), and `src/test/string-intern.test.ts` (2).
- The locked `package-lock.json` is npm lockfile v3. Its `packages` object has
  162 keys including the root entry, or **161 non-root package entries**.
  The root has zero runtime dependencies and six development dependencies.
- Of those 161 non-root entries, 160 use `sha512-` integrity and exactly one
  uses legacy `sha1-` integrity:
  `node_modules/is-extglob`, version `2.1.1`, resolved from
  `https://registry.npmjs.org/is-extglob/-/is-extglob-2.1.1.tgz`, with
  `sha1-qIwCU1eR8C7TfHahueqXc8gz+MI=`.
- A temporary metadata-only fixture containing the locked package-lock was
  checked with `validate_npm_dependency_bundle(..., expected_npm_version="10.9.8")`.
  It was rejected as `package integrity is missing: node_modules/is-extglob`,
  because the validator requires every package integrity value to start with
  `sha512-`. No fixture, npm cache, or dependency artifact was added here.
- The prior authoring lane produced no
  task descriptor, public test bundle, Oracle solution, or verifier artifact.

## Blockers and next action

Source and MIT license checks now pass, but the npm dependency closure remains
unproven and is demonstrably incompatible with the repository validator.
Do not compile or publish this candidate, and do not modify upstream source to
work around a development-lock integrity issue. Reopen only after a separately
reviewed normalized npm v3 lock/cache closure has been produced with approved
integrity metadata, plus a private test/command artifact and task-specific JSON
subprocess API inventory. Then run the Node Oracle and control gates separately

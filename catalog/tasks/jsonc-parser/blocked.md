# `jsonc-parser` Node v2 Pilot Audit

**Status: blocked.** This is an evidence record for the failed authoring lane,
not a Harbor task or a production dataset entry. No upstream hidden tests,
private bytes, dependency cache, or secrets are included.

## Candidate lock

- Package: `jsonc-parser`
- Upstream revision: `900046d46a96dd5d014030e37c0055157921ef92`
- Candidate source and license details are recorded in
  `reports/npm-package-candidates.v1.md`.
- The requested Node v2 contract is Node `22.23.1`, npm `10.9.8`, ESM, and
  the JSON-only subprocess boundary used by `node-synthetic`.

## Static evidence

- The upstream audit identified **87 direct `node:test` leaf declarations**
  across four suites.
- The upstream development lock describes **161 packages** and no runtime
  dependencies, but it is not an approved production dependency artifact.
- One transitive entry, `is-extglob@2.1.1`, carries legacy `sha1` integrity.
  The repository's stricter npm bundle validator rejects that lock until a
  separately reviewed normalized lock/cache artifact is produced.
- The authoring worker could not complete upstream access and produced no
  task descriptor, public test bundle, Oracle solution, or verifier artifact.

## Blockers and next action

Do not compile or publish this candidate. Reopen only after a fresh source and
license verification, a reviewed npm v3 lock/cache closure compatible with
`validate_npm_dependency_bundle`, a private test/command artifact, and a
task-specific JSON subprocess API inventory are available. Then run the Node
Oracle and control gates separately from the Python dataset.

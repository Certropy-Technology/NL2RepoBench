# `jsonc-parser` Node v2 Authoring Provenance

Status: `controls-passed` production task. This record contains source, license,
build, dependency, adapter, and denominator evidence. Hidden tests and private
artifact bytes remain in the private content-addressed store, not in this
public source directory.

## Immutable source and license

- Upstream: `https://github.com/microsoft/node-jsonc-parser`.
- Revision: `900046d46a96dd5d014030e37c0055157921ef92`.
- Resolved tree: `9ed24f2588f831e3f830d5b42539490b13e85654`.
- Commit subject: `npm audit fix + bump to 4.0.0-next.2 (#124)`.
- Commit timestamp: `2026-06-16T11:40:00-07:00`.
- Submodules: none; detached source status was clean before the baseline.
- `git archive --format=tar` size: 266,240 bytes.
- Source archive SHA-256:
  `4d9fef513a7d3543b79aa9965ffe967cede24c3b675037e44374123589a2ad9b`.
- The pinned `package.json` declares name `jsonc-parser`, version
  `4.0.0-next.2`, ESM, MIT, zero runtime dependencies, and six development
  dependencies.
- Pinned `LICENSE.md` is the MIT text, 1,092 bytes, SHA-256
  `c3a24c02d678e5f0711623dcf3ab3f243b273c2633f638a1fa8e35fb7c7f8e4d`.
- Pinned `package.json` SHA-256:
  `7422c4ba6fd0e9857baf73513a9877fe30fde6aca6397efe2ea386949d271754`.

The source contains 27 tracked files and 6,780 physical lines.

## Locked baseline

The exact revision was installed with lifecycle scripts disabled and tested in
`docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`:

```text
node --version  -> v24.19.0
npm --version   -> 11.17.0
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

The upstream compile, ESLint pass, and all four `node:test` suites completed:
87 collected, 87 passed, 0 failed/skipped/todo. Full output is retained at
`.nl2repo/authoring-work/repairs/jsonc-parser/evidence/upstream-baseline.log`.

## Development lock issue and production rescope

The upstream npm v3 lock has 161 non-root development package entries. One old
development-only entry, `is-extglob@2.1.1`, uses SHA-1 integrity, so the full
upstream development closure does not meet this repository's SHA-512 npm bundle
validator. That lock is not normalized, rewritten, or promoted to runtime.

The package has zero runtime dependencies. Production therefore uses a
scripts-stripped distribution containing only package metadata, MIT license,
compiled ESM JavaScript/declarations, and a newly generated npm 11.17.0 v3 root
lock with no package entries beyond the root. The distribution has no
`scripts`, `dependencies`, `devDependencies`, tests, TypeScript source, source
maps, or source-map references.

- Distribution archive SHA-256:
  `99ecb53a34efa2cc74f71a0907eb732215c16a5741f733183fab715625f44260`.
- Distribution lock SHA-256:
  `dad392f127e2e8fccead155f9120e9bdbab57b786d48fabe0d7db6b9ac4d3623`.
- Distribution root manifest SHA-256:
  `25c7e0e20a87441fe394783cc7b1751aeb675fc3c5f30ef42dd89968aa0c274f`.
- Offline `npm ci --ignore-scripts --no-audit --no-fund` and `npm pack
  --ignore-scripts --dry-run` both passed with Node 24.19.0/npm 11.17.0.

The private npm artifact is intentionally a zero-entry cache plus that exact
v3 lock and a manifest digest for the lock. This is a complete cache closure
for a zero-runtime-dependency package, not a claim that the excluded
source-development toolchain is a production dependency.

## Bounded JSON-safe API slice

The scored package slice covers root ESM exports `parse`,
`printParseErrorCode`, `modify`, `format`, and `applyEdits`.

A task-specific child adapter accepts at most 64 KiB of JSON and emits at most
256 KiB. It imports only the fixed package name. Requests use a fixed operation
tag and validated JSON fields:

- parse: document text plus three boolean options; the adapter returns the
  parsed JSON value and normalized error records;
- modify: document text, a bounded string/integer path, a JSON value or fixed
  deletion flag, and JSON-only formatting/insertion options;
- format: document text, a bounded range, and scalar formatting options;
- applyEdits: document text and bounded JSON edit records; and
- metadata: fixed package identity and dependency/script fields.

No source code, callbacks, JavaScript functions, custom loaders, regular
expressions, executable strings, or candidate object references cross the
boundary. Scanner objects, parse trees with parent identity, visitor callbacks,
location match functions, and callback-valued insertion ordering are excluded.
This is an explicit bounded rescope, not full upstream API parity.

## Frozen verifier denominator

The private `node:test` contract has 37 named leaves:

- 1 package/distribution leaf;
- 12 parse/error leaves;
- 13 modify/apply behavior leaves;
- 9 format leaves; and
- 2 direct `applyEdits` leaves.

The exact Node 24.19.0 local adapter run collected 37 and passed 37. The test
runner excludes the helper client and the adapter exits without registering a
test when invoked outside adapter mode, so helper files do not change the
fixed denominator. Collection policy is `node-test-leaf-pass-rate-v1` with a
frozen denominator of 37 and mismatch=`fail`.

## Private artifact references

- npm v3 lock/cache:
  `sha256:95f5d2f3b01cdde10bd0755a35f81fcafe3481f035a87ba55604092f3a5eab48`
  (10,240 bytes);
- command declaration:
  `sha256:e3eae4a8e5200c195e49c2a40e53b184d57bb3c291d1abbd94f2710daec42233`
  (10,240 bytes);
- test/adapter bundle:
  `sha256:44f78a303e09ed29d26b217fa368606f063079d931dd5876aa9d052132069f55`
  (30,720 bytes);
- Oracle source/distribution bundle:
  `sha256:3d2ff9790b3049f39f3f93621a45bd79cef6ec3f89485611a1812cc1c09280b8`
  (389,120 bytes).

The Oracle verifies both source and distribution archive digests, checks the
pinned source package identity/license, extracts only the scripts-stripped
distribution to `/workspace`, and rejects source/tests/maps or dependency and
script fields.

## Network and isolation

The source declares `mode=no-network`,
`offline_dependencies=private-artifact`, and
`reference_source_fetch=forbidden`. The agent receives no upstream source and
no source host authorization. Candidate code is imported only in the
unprivileged child adapter; the trusted report writer consumes structured TAP
results and writes reward artifacts itself.

## Official Harbor gate and controls

The final production compile uses no `--allow-incomplete` flag and resolves all
four private artifacts through `.nl2repo/artifacts` with explicit private-read
authorization.

An initial Oracle attempt exposed a verifier fixture packaging issue: a helper
named `candidate_adapter.mjs` was collected by Node as a synthetic extra leaf,
and its private mode was unreadable to the unprivileged child. The repair keeps
the adapter source under a non-JavaScript extension, then the trusted test
client copies it once into a root-owned, mode-0555 runtime directory before
spawning the candidate child. No helper is now collected and the child cannot
replace the adapter. The corrected official runs produced:

- Oracle: `valid=true`, collected 37, passed 37, reward 1.0;
- empty/nop: valid model failure, reward 0 (`candidate-installation-failed`);
- installable metadata-only stub: `valid=true`, collected 37, passed 1,
  reward `1/37` (`0.02702702702702703`);
- forged workspace `reward.json` claiming 1.0: trusted verifier reward 0; and
- offline: the Oracle and verifier completed under Harbor no-network modes with
  no run-specific host authorization.

Complete command logs, structured grading/report/reward JSON, and the deliberate
control task copies are under
`.nl2repo/authoring-work/repairs/jsonc-parser/evidence/`. This task is not added
to a shared dataset or report by this repair.

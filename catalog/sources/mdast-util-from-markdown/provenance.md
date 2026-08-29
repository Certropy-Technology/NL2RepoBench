# Authoring Provenance

## Source Freeze

- Upstream: `https://github.com/syntax-tree/mdast-util-from-markdown`
- Revision: `f94143765912425fb94ed6518d3a3d1c54f994d4`
- Commit timestamp: `2026-06-03T09:39:51-07:00`
- Package version: `2.0.3`
- License: MIT; license file is `source/license`
- Git archive digest: `sha256:515825acb5478f8bf59c32403e5febc499a100ed0b1183f4596e8be2f38b5a19`
- Frozen checkout: `.nl2repo/authoring-work/mdast-util-from-markdown/source`

## Inventory

The frozen package is ESM-only and exports `fromMarkdown` from its root. Its
runtime dependency closure contains 33 npm package entries after exact
resolution. The source contains 54 fixture files, 27 JSON expected trees, and
the upstream `node:test` suite in `test/index.js`.

The upstream baseline built successfully with Node `22.23.1`/npm `10.9.8` in
the authoring environment: `npm ci --ignore-scripts` installed 835 packages,
`npm run build` passed, and `npm run test-api` passed 727/727 leaves. The
production task uses a smaller private JSON-safe contract so the instruction
describes behavior without exposing the upstream assertions or fixture corpus.

## Dependency Remediation

The first private npm cache artifact was produced by a Node 22/npm 10 authoring
probe. It passed a local npm 10 offline install but failed inside the locked
Node 24/npm 11 verifier with `ENOTCACHED` for the registry metadata of
`@types/mdast`; the verifier therefore collected 0 of 21 leaves. The closure
was regenerated during the build phase with Node `24.19.0` and npm `11.17.0`,
including npm content and index metadata. The replacement artifact is
`sha256:ff246aef973478493951ab7b6db855b735b58ede0e23e6bd493eb82dcb359a1c`
(2222080 bytes), and its 138 manifest entries pass an independent archive/hash
check. The final cache contains npm tarballs plus package metadata needed by
the verifier's packed-tarball install. The task lock now points to this
replacement; earlier artifacts remain in the task-local CAS only as
remediation history.

## Verifier Remediation

The first compiled verifier collected the 21 contract leaves but timed out
because `run_tests.mjs` correctly discovers `.mjs` test files and the private
`candidate_adapter.mjs` was also discovered as a test. The adapter waits for a
JSON request on stdin, so this was a task-bundle naming defect rather than a
candidate behavior result. The replacement private test bundle is
`sha256:132c271ac97ca12cc0f761796c4db70a9d4f665dd81973975d92481196286842`
(20480 bytes); it keeps only `contract.test.mjs` and `test_client.mjs`. The
trusted adapter is now inline in the root-only client and is passed with
`node --eval` to the candidate child. This preserves UID separation without
granting the candidate read access to `/tests/private` or a writable trusted
adapter file. The bundle is bound by the task lock.

## Adaptation Boundary

The public task accepts only string input and evaluates only JSON-serializable
trees through a separate child process. Typed arrays, extension callbacks,
custom micromark extensions, and the full development condition are inventoried
but excluded because they cannot be represented by the JSON bridge. No network,
native addon, browser, database, or external service is required.

# qs authoring-wave report

Implemented a task-local Node v2 development source for the pinned `qs`
revision. The task is **specified / development-only**, not publishable: source
and license provenance are locked, the CommonJS JSON boundary is documented,
and deterministic local test evidence is recorded, while the private adapter,
offline dependency artifact, verifier, Oracle, and controls remain intentionally
absent.

## Changed files

- `catalog/tasks/qs/task.toml` — schema v2 metadata, exact source/runtime lock,
  provisional 1,045-leaf source observation, Node metric, and development
  lifecycle record.
- `catalog/tasks/qs/instruction.md` — public JSON-compatible CommonJS
  `parse`/`stringify` contract, options, defaults, errors, packaging, and
  explicit callback/JavaScript-value exclusions.
- `catalog/tasks/qs/provenance.md` — source/license/test/build/dependency audit,
  posttest exclusion, and production blockers. It contains hashes and
  observations only; no upstream/private bytes.

No tests were added or modified. No Harbor tree, Dockerfile, hidden test,
private cache/tarball, Oracle, verifier, reward, secret, dataset, or shared file
was written.

## Audit findings

### Source and license

- Exact detached revision: `3a890d4ecd3deb72a45d90be36f4f8c5970467c7`.
- Revision tree: `0087de81352794a9d68dbcdd1a339336a7f35c63`.
- Unprefixed `git archive --format=tar` size/hash: `12,011,520` bytes,
  `sha256:f5bb4b5c13cb29aba6441d5781bb17de37b473f74aec203898b28f980ff95402`.
- `LICENSE.md` is BSD-3-Clause, 1,600 bytes, SHA-256
  `e7dc37bf662d7f786efcb46c545615e70c1daf458a38385521c63cf6607cdfe1`.
- Package metadata is `qs@6.15.3`, CommonJS `main: lib/index.js`, with root
  exports `formats`, `parse`, and `stringify`.

### JSON-compatible CommonJS scope

The instruction narrows the scored surface to fixed JSON requests/responses:
query-string text plus JSON options for `parse`, and recursively JSON-compatible
values plus JSON options for `stringify`. It explicitly excludes callbacks,
RegExp delimiters, Buffer/Date/Symbol/BigInt/function values, sparse holes,
custom prototypes/`toJSON`, cycles, browser/dist/publish paths, and network
behavior. It documents deterministic repeated-call output while preserving the
upstream JavaScript own-key enumeration order (it does not falsely promise
lexicographic key sorting).

### Tests and deterministic behavior

Runtime used for the source audit: Node `22.23.1`, npm `10.9.8`.

- Direct local Tape collection/execution of the exact source suite: `1..1045`,
  `1045` pass, `0` fail.
- Per-file leaves: `parse.js` 461, `stringify.js` 426, `utils.js` 158;
  `empty-keys-cases.js` is fixture data.
- Three direct Tape runs produced byte-identical TAP with SHA-256
  `cabe2c0a4dae5f62accfc804a68cd0545babdfb9d813ce4253bc336f96de02dd`.
- `npm run tests-only` also reported 1,045 passes and NYC coverage of 100%
  statements/functions/lines and 99.85% branches.
- Two `# SKIP TODO` assertions and feature-gated skip branches are recorded;
  the future `node:test` adapter must define todo/skipped normalization rather
  than silently treating them as ordinary passes.
- `node --check` passed for all nine tracked JavaScript files; a CommonJS root
  smoke check confirmed callable `parse` and `stringify` exports.

The 1,045 count in `task.toml` is a development source observation, not a
production frozen private denominator. A future JSON-adapted `node:test` suite
may narrow the subset and must version/freeze its own denominator.

### Build and posttest boundary

- The source `posttest` script is network-capable:
  `npx npm@'>=10.2' audit --production`.
- Per scope, `npm test`, `npm audit`, `npx npm ... audit`, and all posttest hooks
  were **not run**. Only direct local `tests-only`/Tape commands were run.
- Repeated `npm run dist` invocations in the same checkout produced different
  53,431-byte Browserify bundle hashes, so `dist/qs.js` and the prepack/publish
  workflow are explicitly outside the scored contract. The CommonJS library
  entry works without that bundle.
- `npm pack --ignore-scripts` is the safe packaging shape. Script-enabled
  prepack also depends on Git-aware `npmignore --auto`, which is unsuitable as a
  required empty-workspace build step.

### Dependency closure

The upstream source has no `package-lock.json`/shrinkwrap and intentionally sets
`package-lock=false`. A temporary network-backed npm 10.9.8 resolution was used
only as diagnostic evidence; its cache and lock are outside the repository and
were not promoted as an artifact.

- Runtime-only diagnostic graph: 18 packages (19 lock entries including root),
  all observed with registry integrity fields and MIT metadata. A populated
  temporary cache passed `npm ci --offline --ignore-scripts --no-audit --no-fund`;
  an empty cache failed closed with expected `ENOTCACHED`.
- Full development diagnostic graph: 934 lock entries for 32 declared dev
  roots; 182 legacy nested entries lacked integrity fields. It is not an
  acceptable candidate runtime closure.
- `[dependencies].status = "unknown"` is intentional. Production still needs a
  reviewed content-addressed v3 runtime lock/cache artifact and license/integrity
  audit.

## Validation

Commands run and results:

- `uv run --frozen nl2repo task validate-source catalog/tasks/qs` — **passed**;
  parsed as schema v2, status `specified`.
- `uv run --frozen nl2repo task compile catalog/tasks/qs --output /tmp/qs-catalog-compile` — **passed**;
  generated a temporary canonical manifest (`qs`, no repository artifact).
- `uv run --frozen pytest -q --no-cov tests/test_node_foundation.py` — **passed**;
  37 tests.
- `uv run --frozen pytest -q --no-cov tests/test_catalog.py` — **passed**;
  13 tests.
- `git diff --check -- catalog/tasks/qs` — **passed**.
- `git diff --cached --name-only` — empty; no staged files.
- A first run of `uv run --frozen pytest -q tests/test_node_foundation.py`
  executed 37 passing tests but returned nonzero on the repository-wide 80%
  coverage gate (isolated-file coverage 50.34%); the required `--no-cov` rerun
  passed and no source regression was observed.

## Residual risks / blockers

1. No private `node:test` adapter or frozen JSON-boundary denominator exists.
2. No reviewed offline npm lock/cache artifact exists; diagnostic network
   resolution is not production evidence.
3. Browserify `dist` output is byte-nondeterministic and is intentionally
   excluded from the scored API.
4. Tape todo/skip semantics must be normalized by the future v2 report adapter.
5. Separate verifier, forged-report/install-script/loader/hang/offline controls,
   and three valid Oracle runs have not been run by policy.
6. The task must remain in the separate Node pilot and must not be merged into
   the Python dataset or used for cross-language score parity.

Recommended next step: build and review the private JSON child adapter and
runtime-only npm v3 cache closure, then recollect/freeze the adapted leaf suite
before any Harbor or Oracle work.

## Acceptance report

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Added only catalog/tasks/qs/task.toml, instruction.md, and provenance.md; the files are task-local v2 development evidence for the exact pinned revision, with no Harbor/Docker/Oracle/private/shared artifacts."
    }
  ],
  "changedFiles": [
    "catalog/tasks/qs/task.toml",
    "catalog/tasks/qs/instruction.md",
    "catalog/tasks/qs/provenance.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "uv run --frozen nl2repo task validate-source catalog/tasks/qs",
      "result": "passed",
      "summary": "Schema v2 source parsed successfully; task status is specified."
    },
    {
      "command": "uv run --frozen nl2repo task compile catalog/tasks/qs --output /tmp/qs-catalog-compile",
      "result": "passed",
      "summary": "Temporary canonical manifest generated successfully."
    },
    {
      "command": "uv run --frozen pytest -q --no-cov tests/test_node_foundation.py",
      "result": "passed",
      "summary": "37 tests passed."
    },
    {
      "command": "uv run --frozen pytest -q --no-cov tests/test_catalog.py",
      "result": "passed",
      "summary": "13 tests passed."
    },
    {
      "command": "./node_modules/.bin/tape 'test/**/*.js' (three runs, temporary detached source checkout)",
      "result": "passed",
      "summary": "1,045/1,045 direct Tape leaves passed on each run; TAP hash was stable."
    },
    {
      "command": "npm run tests-only (temporary diagnostic install; no npm test/posttest)",
      "result": "passed",
      "summary": "1,045 tests passed; NYC reported 100% statements/functions/lines and 99.85% branches."
    },
    {
      "command": "node --check lib/*.js test/*.js and CommonJS root smoke check",
      "result": "passed",
      "summary": "All nine tracked JavaScript files parsed and root parse/stringify exports were callable."
    },
    {
      "command": "git diff --check -- catalog/tasks/qs",
      "result": "passed",
      "summary": "No whitespace errors."
    },
    {
      "command": "uv run --frozen pytest -q tests/test_node_foundation.py",
      "result": "failed",
      "summary": "37 tests passed, but the repository-wide coverage gate returned nonzero for isolated-file coverage; rerun with --no-cov passed."
    },
    {
      "command": "npm test / npm audit / posttest audit",
      "result": "not-run",
      "summary": "Explicitly excluded because upstream posttest invokes network-capable npx npm audit."
    }
  ],
  "validationOutput": [
    "Exact source archive: 12,011,520 bytes, sha256:f5bb4b5c13cb29aba6441d5781bb17de37b473f74aec203898b28f980ff95402.",
    "BSD-3-Clause LICENSE.md SHA-256: e7dc37bf662d7f786efcb46c545615e70c1daf458a38385521c63cf6607cdfe1.",
    "Direct Tape leaf plan was 1..1045 with 0 failures; three TAP outputs matched sha256:cabe2c0a4dae5f62accfc804a68cd0545babdfb9d813ce4253bc336f96de02dd.",
    "Runtime-only diagnostic dependency graph had 18 packages; populated-cache offline ci passed and empty-cache ci failed closed with ENOTCACHED.",
    "No Docker, Harbor, Oracle, hidden test, private cache, secret, or posttest audit was run or committed."
  ],
  "residualRisks": [
    "Private JSON child adapter and adapted node:test denominator are not yet frozen.",
    "Reviewed content-addressed npm v3 lock/cache closure is absent; dependencies.status remains unknown.",
    "Browserify dist builds are byte-nondeterministic and intentionally outside the scored contract.",
    "Oracle, empty/stub/forgery/install-script/loader/hang/offline controls remain parent-owned future gates."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added a task-local v2 development specification and provenance audit for qs@6.15.3 at commit 3a890d4; no runtime implementation or shared artifact was changed.",
  "reviewFindings": [
    "no blockers to the requested development-only authoring record",
    "publication blocker: offline npm lock/cache closure and private JSON adapter are absent",
    "publication blocker: dist/prepack path is nondeterministic and excluded from scope"
  ],
  "manualNotes": "The task lifecycle is intentionally specified/development-only. Do not compile for production, run Harbor, or claim Oracle parity until the listed private artifacts and gates exist."
}
```

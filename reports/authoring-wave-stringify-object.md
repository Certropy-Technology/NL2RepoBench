# stringify-object Authoring-Wave Findings

## Decision

Keep `catalog/tasks/stringify-object/` blocked. The exact upstream revision is
reachable and source/license eligibility is confirmed, but this lane has no
reviewed offline npm closure, private JSON adapter, separate verifier, or
Oracle/control evidence. Only the task-local `blocked.md` record was added; no
Harbor task, hidden bytes, secrets, Docker asset, Oracle bundle, or shared
catalog file was created.

## Evidence

- Exact revision: `c359727290822d9cabf7c07fb86cdb08701c1010`, from
  `sindresorhus/stringify-object`; commit tree
  `ec2212a53155afeea2c5f86b92c5cc8883ddb895`, package version `7.0.0`, and
  archive SHA-256
  `4076617d57ba117f7bc776c0a1124d544441bdbaa7572d2afcc17e2e28811dc3`.
- `package.json` declares BSD-2-Clause, `type: module`, Node `>=22`, and the
  root ESM `exports` entry with `types` and `default` conditions. The source
  has no submodules and its `.npmrc` disables package-lock generation.
- The scored default export is `stringifyObject(input, options?) -> string`.
  The proposed v2 boundary accepts only recursively JSON-compatible input and
  the JSON options `indent`, `singleQuotes`, and `inlineCharacterLimit`.
  Callback-valued `filter`/`transform`, cycles, Maps, Sets, Date, RegExp,
  BigInt, Symbol, undefined, functions, custom prototypes/toJSON, and the
  undocumented third parameter are explicitly excluded.
- `test/index.js` has 22 top-level `node:test` declarations. With Node
  `22.23.1` and npm `10.9.8`, a temporary runtime install followed by
  `node --test test/index.js` passed 22/22. The source suite also tests
  JavaScript-only callbacks, cycles, and other values; that broad upstream
  suite is not a valid frozen denominator for the narrowed JSON task.
- The upstream package has five range-based runtime dependencies and one
  range-based development dependency (`xo`). A temporary npm `10.9.8` v3
  metadata probe produced 405 lockfile package keys, 404 non-root entries,
  and a 194,661-byte lock with SHA-256
  `1838e8baa94f58e46ff4a5c0c1ecca8eef6ef4ff620a6e029da261efefe0a833`.
  The lock was not retained.
- Empty-cache offline installation failed with `ENOTCACHED` for
  `zwitch-2.0.4.tgz`; the `--omit=dev` probe against the same generated lock
  also failed, first reporting `web-worker-1.5.0.tgz`. The temporary network
  install/cache was discarded, so no dependency bytes or credentials are
  included.
- The eventual candidate protocol must pack and inspect the candidate, install
  from an npm 10.9.8 lock/cache closure with `npm ci --offline --ignore-scripts
  --no-audit --no-fund`, and call only the default export through an isolated
  line-delimited JSON child process. The trusted verifier must own test files,
  collection, report paths, and the fixed denominator.

## Changed Files

- `catalog/tasks/stringify-object/blocked.md`: task-local v2 development
  evidence and blocked/unblock conditions.
- `/root/NL2RepoBench/reports/authoring-wave-stringify-object.md`: this report.

No tests were added or updated. No shared source, dataset, index, Docker,
Harbor, hidden artifact, Oracle, or verifier file was changed.

## Validation

- Detached source checkout, exact revision, tree, archive hash, package
  metadata, license, and lockfile absence checks: passed.
- Node/npm version, ESM export, dependency, and 22-test declaration scans:
  passed.
- Temporary npm v3 lock generation: passed; generated lock not retained.
- Empty-cache `npm ci --offline --ignore-scripts --no-audit --no-fund`: failed as
  expected and recorded as the missing-cache blocker.
- Temporary runtime install plus upstream `node --test test/index.js`: passed;
  all 22 upstream tests passed.
- `git diff --check -- catalog/tasks/stringify-object/blocked.md`: passed.
- Isolated worktree status and staged-file check: only the intended task-local
  record is untracked and no files are staged.
- No Docker, Harbor compilation, Oracle, negative control, or shared catalog
  mutation was run.

## Residual Risks

The task cannot advance until a reviewed content-addressed npm lock/cache
closure, final Node image/runtime lock, private JSON-boundary tests and
commands, separate structured verifier, and control plan exist. The scoped
leaf denominator must be frozen from those private adapter tests; the 22-test
upstream observation must not be used as a publication denominator.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Only catalog/tasks/stringify-object/blocked.md was added with exact-revision, ESM/node:test, JSON-boundary, lock/cache, and candidate-protocol evidence; no shared or production artifacts were created."
    }
  ],
  "changedFiles": [
    "catalog/tasks/stringify-object/blocked.md",
    "/root/NL2RepoBench/reports/authoring-wave-stringify-object.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git clone --filter=blob:none --no-checkout https://github.com/sindresorhus/stringify-object.git /tmp/stringify-object-audit; git fetch --depth=1 origin c359727290822d9cabf7c07fb86cdb08701c1010; git checkout --detach c359727290822d9cabf7c07fb86cdb08701c1010",
      "result": "passed",
      "summary": "Fetched and checked out the exact requested revision in a clean detached checkout."
    },
    {
      "command": "git show/archive/tree/license/package metadata inspection for c359727290822d9cabf7c07fb86cdb08701c1010",
      "result": "passed",
      "summary": "Recorded commit tree, archive SHA-256, BSD-2-Clause license, ESM exports, dependency lists, and absence of a committed npm lock."
    },
    {
      "command": "node --version && npm --version && static node:test/dependency/export scan",
      "result": "passed",
      "summary": "Confirmed Node 22.23.1, npm 10.9.8, five runtime dependencies, one dev dependency, ESM root export, and 22 test declarations."
    },
    {
      "command": "npm install --package-lock-only --ignore-scripts --lockfile-version=3 --no-audit --no-fund",
      "result": "passed",
      "summary": "Temporary npm 10.9.8 lock probe generated 405 package keys and the recorded SHA-256; the lock was not retained."
    },
    {
      "command": "npm ci --offline --ignore-scripts --no-audit --no-fund --cache=/tmp/stringify-object-offline-empty-cache",
      "result": "failed",
      "summary": "Expected blocker: an empty cache produced ENOTCACHED for zwitch-2.0.4.tgz."
    },
    {
      "command": "npm ci --offline --ignore-scripts --omit=dev --no-audit --no-fund --cache=/tmp/stringify-object-offline-runtime-cache",
      "result": "failed",
      "summary": "Expected blocker: the generated full lock still had no offline cache closure and first reported web-worker-1.5.0.tgz."
    },
    {
      "command": "npm install --ignore-scripts --omit=dev --no-audit --no-fund && node --test test/index.js",
      "result": "passed",
      "summary": "Temporary network-backed runtime install completed and all 22 upstream node:test cases passed."
    },
    {
      "command": "git diff --check -- catalog/tasks/stringify-object/blocked.md",
      "result": "passed",
      "summary": "No whitespace errors in the task-local record."
    },
    {
      "command": "git status --short --untracked-files=all && git diff --cached --name-only",
      "result": "passed",
      "summary": "Only catalog/tasks/stringify-object/blocked.md is untracked in the isolated worktree; no files are staged."
    }
  ],
  "validationOutput": [
    "Exact source revision, tree, archive hash, license, ESM metadata, and package-lock absence are recorded.",
    "The proposed JSON-only values/options boundary explicitly excludes callbacks and cycles.",
    "The upstream node:test observation is 22/22, but is not used as the private publication denominator.",
    "Generated lock/cache evidence demonstrates that lock generation alone does not establish offline installation.",
    "Task directory contains only blocked.md; no Docker, Harbor, Oracle, hidden bytes, secrets, or shared catalog edits were made."
  ],
  "residualRisks": [
    "No reviewed content-addressed npm v3 lock/cache closure exists.",
    "No private JSON adapter, command artifact, separate verifier, or frozen scoped denominator exists.",
    "No Oracle, empty/stub, forgery, install-failure, hang, or offline controls were run by design."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added one task-local blocked v2 evidence record for stringify-object; no production, hidden, Docker, Oracle, verifier, or shared catalog artifacts were changed.",
  "reviewFindings": [
    "blocker: catalog/tasks/stringify-object/blocked.md - offline dependency closure, private adapter/verifier artifacts, and Oracle/control gates remain intentionally unresolved"
  ],
  "manualNotes": "The source and public upstream baseline are usable for authoring evidence only. Preserve the blocked status until the reviewed npm closure and separate JSON verifier are available."
}
```

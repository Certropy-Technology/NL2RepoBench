# Validator Authoring Wave Report

## Result

Implemented the requested task-local v2 development evidence record for the npm
candidate `validator`. The task remains **blocked** and no Harbor task, hidden
bytes, secrets, Docker image, Oracle bundle, verifier, or shared catalog update
was created.

## Findings

- The requested source revision is verified as
  `a79ff980ab14257e795332989e497bdff3218e87`, tree
  `2135a5dc37902736cfb283785021644605318f9c`, archive SHA-256
  `dd8284c8fa6d4345e538e15fb235326762ea106699177d041e5ed6ba2e0e064b`.
- `package.json` declares `validator` 13.15.35, CommonJS `main: index.js`, no
  runtime `dependencies`, and 17 range-based development dependencies. The
  source is ESM, but Babel's development build emits CommonJS and adds an
  enumerable `default` self-reference. The exact build has 112 source object
  names, 104 callable exports, seven locale arrays, and one version string;
  the required CommonJS package has 113 own keys after Babel output.
- The source Git tree intentionally omits generated `index.js`, `lib/`, `es/`,
  `validator.js`, and `validator.min.js`. An isolated Node 22.23.1/npm 10.9.8
  build probe generated the distributions reproducibly under one temporary
  lock; representative output hashes and the build/test details are recorded
  in [blocked.md](../catalog/tasks/validator/blocked.md).
- The exact source tree has no npm, Yarn, or pnpm lockfile. A temporary npm
  10.9.8 lock resolution contained 541 v3 package entries and could not be
  installed with an empty cache (`ENOTCACHED` for `yargs-unparser-1.6.0.tgz`).
  The temporary network install is evidence only and is not an approved
  dependency closure.
- The public upstream suite has 14 test files and 323 Mocha leaf tests. The
  isolated `npm test` baseline passed all 323 after building and linting. The
  suite directly imports source/generated artifacts and uses Date, undefined,
  NaN, Buffer, RegExp, VM/browser, and time-dependent cases that are outside a
  plain JSON request.
- The generic Node subprocess runner successfully called the built CommonJS
  package for boolean, string, and Date-to-JSON results, but it is not a
  validator-specific contract: it permits any callable export and cannot
  represent scalar/array metadata. A private fixed export allowlist and JSON
  normalization adapter are still required.
- Registry metadata for version 13.15.35 points to Git head
  `7a8079709cd4cb27b2a1846e6f6508d68c9d928f`, not the requested revision. The
  registry generated artifacts differ from the exact-revision build; notably,
  the registry CommonJS `toString("123")` smoke result is `[object Object]`,
  while the exact-revision build returns `"123"`.

## Changed Files

Only this task-local file was added:

- `catalog/tasks/validator/blocked.md`

No tests were added or updated. The record deliberately contains hashes,
counts, commands, and contract observations rather than source/test bytes.

## Validation

Commands run included:

- Detached source clone/checkout and `git archive` hash verification: passed.
- Temporary `npm install --package-lock-only --ignore-scripts --legacy-peer-deps`: passed; generated lock was not retained.
- Temporary `npm ci --offline --ignore-scripts` with an empty cache: failed as expected and recorded as the dependency-closure blocker.
- Temporary network `npm ci --ignore-scripts --legacy-peer-deps`: passed; 539 packages installed outside the worktree.
- Temporary `npm test`: passed; 323 Mocha leaves, with build and lint included.
- Repeated temporary `npm run build`: passed; representative hashes were stable under the same temporary lock.
- CommonJS `require()` and JSON subprocess smoke calls: passed for the recorded cases.
- Native import of generated `es/index.js`: failed with the expected extensionless-import `ERR_MODULE_NOT_FOUND`; native ESM is not claimed for this CommonJS pilot.
- Worktree/status and cached-path checks: passed; the only worktree change is the untracked task-local record and no paths are staged.

No Docker, Harbor, Oracle, negative control, dataset compilation, or shared
catalog mutation was run.

## Residual Risks

The task cannot advance until the generated package is rebuilt from the exact
revision with a reviewed content-addressed build lock/cache, and the private
JSON adapter/test/command artifacts are authored and reviewed. The scope must
also explicitly exclude unsupported RegExp/callable/undefined/non-finite and
browser/VM cases, or define a task-specific normalization contract for them.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Added only catalog/tasks/validator/blocked.md with exact-revision provenance, CommonJS/generated-output evidence, lock and no-runtime-dependency audit, test denominator, and JSON-boundary blockers; no shared or runtime code was changed."
    }
  ],
  "changedFiles": [
    "catalog/tasks/validator/blocked.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git clone --filter=blob:none --no-checkout https://github.com/validatorjs/validator.js.git /tmp/validatorjs-source && git -C /tmp/validatorjs-source checkout --detach a79ff980ab14257e795332989e497bdff3218e87",
      "result": "passed",
      "summary": "Exact requested revision checked out cleanly."
    },
    {
      "command": "git -C /tmp/validatorjs-source archive --format=tar HEAD | sha256sum",
      "result": "passed",
      "summary": "Archive SHA-256 dd8284c8fa6d4345e538e15fb235326762ea106699177d041e5ed6ba2e0e064b."
    },
    {
      "command": "npm install --package-lock-only --ignore-scripts --legacy-peer-deps --no-audit --no-fund",
      "result": "passed",
      "summary": "Temporary npm 10.9.8 v3 lock generated with 541 package entries; not retained."
    },
    {
      "command": "npm ci --offline --ignore-scripts --legacy-peer-deps --no-audit --no-fund --cache=/tmp/validatorjs-empty-npm-cache",
      "result": "failed",
      "summary": "Expected blocker: empty cache produced ENOTCACHED for yargs-unparser-1.6.0.tgz."
    },
    {
      "command": "npm ci --ignore-scripts --legacy-peer-deps --no-audit --no-fund",
      "result": "passed",
      "summary": "Temporary network install completed with 539 packages."
    },
    {
      "command": "npm test",
      "result": "passed",
      "summary": "Build, lint, and 323 Mocha leaf tests passed."
    },
    {
      "command": "npm run build",
      "result": "passed",
      "summary": "Generated CommonJS, ES, browser, and minified outputs; repeated hashes were stable under the same temporary lock."
    },
    {
      "command": "node CommonJS require and JSON subprocess smoke calls",
      "result": "passed",
      "summary": "Boolean, string, and Date-to-JSON calls crossed the bounded child protocol."
    },
    {
      "command": "node native import of generated es/index.js",
      "result": "failed",
      "summary": "Expected native ESM limitation: extensionless generated imports yield ERR_MODULE_NOT_FOUND."
    },
    {
      "command": "git status --short --untracked-files=all && git diff --cached --name-only",
      "result": "passed",
      "summary": "Only catalog/tasks/validator/blocked.md is untracked; no staged files."
    }
  ],
  "validationOutput": [
    "Exact revision and source archive hash recorded.",
    "CommonJS output shape and generated artifact hashes recorded.",
    "323-leaf upstream baseline recorded without copying test bytes.",
    "Missing lock/cache closure and JSON adapter gaps recorded as blockers.",
    "No Docker, Harbor, Oracle, or shared edits performed."
  ],
  "residualRisks": [
    "No durable build lock or offline npm cache closure exists.",
    "Registry version 13.15.35 is not provenance-equivalent to the requested Git revision.",
    "No reviewed validator-specific JSON adapter or private verifier test bundle exists."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added one task-local blocked v2 evidence record; no source, tests, shared metadata, or generated artifacts changed.",
  "reviewFindings": [
    "blocker: catalog/tasks/validator/blocked.md - exact generated package provenance, offline build closure, and separate JSON verifier adapter remain unresolved"
  ],
  "manualNotes": "The record intentionally stops at development evidence. Oracle, Docker, Harbor, hidden bytes, and shared catalog integration remain out of scope."
}
```

# Authoring-wave audit: `query-string`

## Result

**Blocked (development-only evidence only).** The exact candidate source and
Node/npm feasibility were audited in an isolated temporary checkout. The task
cannot be compiled or scored with the current Node v2 JSON subprocess runtime,
because the package's public API is a default namespace object while the locked
runner only invokes a direct callable export. No hidden tests, private cache,
Oracle, Docker image, secret, or shared catalog/index file was created.

Task-local evidence: `catalog/tasks/query-string/blocked.md`.

## Review findings

| Severity | Location | Finding | Evidence |
| --- | --- | --- | --- |
| **blocker** | `catalog/tasks/query-string/blocked.md`; `src/nl2repobench/verification/node/candidate_runner.mjs:52-66`; upstream `index.js:1-3`, `package.json:14-17` | `query-string` exposes only a callable-looking default **object** containing `parse`/`stringify`; the runner accepts only a literal export whose value is a function. | Exact installed probes for `parse`, `stringify`, and `default` returned `{"ok":false,"error":"export-is-not-callable"}`. No nested `default.parse` resolution exists. |
| **high** | upstream `package.json:22-24`; `src/nl2repobench/verification/node/validate-package.mjs:39-44` | The verbatim upstream tarball declares `benchmark` and `test` scripts and is rejected by the runtime package validator's no-scripts policy. | `npm pack --ignore-scripts` followed by `validate-package.mjs` exited `71`. This requires an explicit generated-package adaptation, not silent parity. |
| **high** | `src/nl2repobench/harbor/node_dependencies.py:90-175`; temporary generated lock/cache | Upstream has no lockfile; a v3 lock can be generated, but lockfile-only generation does not establish offline closure. | Generated lock: 698 package entries, SHA-256 `5b15f3b377c4c81dc99e144e218476289d6a27af0ec78f04ef322dca9a0c8cf2`. Initial offline `npm ci` failed `ENOTCACHED` for `yocto-queue@0.1.0`; after temporary cache hydration, offline install passed. No cache was committed. |
| **medium** | upstream `package.json:22-24`; `test/*.js`; Node v2 `run_tests.mjs` | Upstream uses AVA + XO + tsd, not the locked `node:test` report contract. | 183 declarations (182 ordinary plus one expected-failure property test); full source run produced 182 passes and one known failure. A reviewed node:test adapter and fresh frozen collection are required. |
| **medium** | `src/nl2repobench/verification/node/candidate_runner.mjs:5-7`; upstream `test/parse.js:97-174`, `test/stringify.js:40-85` | JSON request/response bounds exclude unchanged upstream stress cases. | Runner request limit is 64 KiB and response limit 256 KiB; upstream constructs approximately 80 KiB, 120 KiB, 400 KiB, 5 MiB, and 400 KiB cases. These cannot be silently counted as covered. |
| **medium** | upstream `base.js:484-490` | `stringify` copies into a plain object, so an own JSON key `__proto__` is dropped (`a=1` for `{"__proto__":"x","a":"1"}`). | Scope must explicitly preserve this pinned behavior or constrain keys before hidden assertions are written. |

## Source and license lock

- Upstream URL: `https://github.com/sindresorhus/query-string`
- Revision: `aae373a54526c7b297f60e4d7b77eb0709d2ae9c`
- Subject: `9.5.0`; timestamp `2026-08-06T19:04:10+02:00`
- Tree: `12b0d49165b2e1a09f58510ac121147bbf7f9dde`
- Repeated `git archive --format=tar HEAD | sha256sum`:
  `12cb02c8cb732a9baf76a8799c452529b1e0a7506dc250161bc5021102d1f8fb`
- MIT `license`: 1,117 bytes,
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- `package.json` SHA-256:
  `3b42454731e8600a46f849b4a04ac930a128c555c71d4f447d772d8b3deb94fa`
- Detached source checkout was clean; 23 tracked files / 4,269 physical lines.

## JSON-only API boundary assessment

A future task-local scope could cover only JSON-serializable calls to
`parse(query, options)` and `stringify(object, options)`:

- parse: string query plus JSON options `decode`, documented array formats,
  one-character separator, `parseNumbers`, `parseBooleans`, `sort: false`, and
  string-valued `types` declarations;
- stringify: JSON object of strings, finite numbers, booleans, null, and arrays
  of those values, with JSON options `encode`, `strict`, array format/separator,
  `sort: false`, `skipNull`, and `skipEmptyString`;
- exclude callbacks/functions (`sort`, callback `types`, `replacer`), BigInt,
  undefined, Symbol, Date, cycles, arbitrary class values, and URL helper APIs.

That scope is semantically plausible but is **not executable** through the
current runner because the package root has no direct callable `parse` or
`stringify` export. A task-specific wrapper or shared protocol change would be
an architectural decision and was not made in this worker.

## Dependency/lifecycle evidence

Using Node `22.23.1` and npm `10.9.8` in a temporary copy:

- `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`
  (with `package-lock=true`) generated lockfile v3 with 698 non-root entries and
  314,718 bytes;
- all entries had `sha512-` integrity and HTTPS resolutions; no git/file/
  workspace/link source, native marker, install script, or platform `os`/`cpu`
  field was observed;
- runtime closure was the three pure-JS dependencies declared by the package;
  each has test scripts but no install script, so `--ignore-scripts` remains
  mandatory;
- after a temporary network hydration only, `npm ci --offline
  --ignore-scripts --no-audit --no-fund` succeeded; the verified cache had
  1,149 index entries / 241,423,867 content bytes (2,303 files including
  metadata/logs). The fully installed development tree contained 495 package manifests with
  ordinary `test`, `build`, or other npm scripts; no install/preinstall/postinstall
  markers were present in the lock scan, and every install used `--ignore-scripts`.
  Ordinary package scripts are still untrusted even when npm does not execute them.

The lockfile and cache are not task artifacts. A production attempt must create
an access-controlled, content-addressed npm bundle and exact `bundle.manifest.json`;
network success is not accepted as offline evidence.

## Test inspection and validation

The pinned source declares:

| Suite | Declarations |
| --- | ---: |
| `test/parse.js` | 83 |
| `test/stringify.js` | 57 |
| `test/parse-url.js` | 6 |
| `test/exclude.js` | 18 |
| `test/stringify-url.js` | 11 |
| `test/pick.js` | 4 |
| `test/extract.js` | 3 |
| `test/properties.js` | 1 expected failure |
| **Total** | **183** |

The source-only test command `npm test` passed XO, AVA, and tsd after the
temporary offline install: **182 passed, 1 known expected failure**. This is
not an Oracle run and does not establish a Harbor denominator.

## Residual risks

- No `task.toml`, public `instruction.md`, private test bundle, command plan,
  Oracle bundle, controls record, or publication manifest was produced because
  the API boundary blocker precedes safe task authoring.
- Any adapter that unwraps the default namespace, adds a generated re-export,
  or changes `candidate_runner.mjs` could alter the measured API and must be
  approved and versioned before implementation.
- A future spec must decide how to represent `__proto__` and other prototype-key
  inputs, as well as whether to exclude oversized performance cases rather than
  alter their assertions.
- The generated npm lock/cache observation is development evidence only; it is
  not a reviewed private dependency artifact.

## Recommended next step

Keep this candidate blocked. The parent should first approve either a fixed
JSON boundary that can safely call methods on a default namespace or a different
candidate with direct callable exports. Only then should a writer create the
JSON-only instruction, generate the private node:test adapter and npm closure,
and run the separate Oracle/control gates.

## Acceptance report

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "catalog/tasks/query-string/blocked.md and this report contain concrete severity-tagged findings with upstream and runtime file paths, exact revision evidence, dependency observations, test counts, and boundary probes."
    }
  ],
  "changedFiles": [
    "catalog/tasks/query-string/blocked.md",
    "/root/NL2RepoBench/reports/authoring-wave-query-string.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git clone --filter=blob:none --no-checkout https://github.com/sindresorhus/query-string.git /tmp/query-string-audit-src && git checkout --detach aae373a54526c7b297f60e4d7b77eb0709d2ae9c",
      "result": "passed",
      "summary": "Exact requested revision resolved; detached checkout clean."
    },
    {
      "command": "npm install --package-lock-only --ignore-scripts --no-audit --no-fund --package-lock=true",
      "result": "passed",
      "summary": "Generated npm lockfile v3 with 698 non-root package entries."
    },
    {
      "command": "npm ci --offline --ignore-scripts --no-audit --no-fund",
      "result": "failed",
      "summary": "Expected closure probe failed before cache hydration with ENOTCACHED for yocto-queue@0.1.0."
    },
    {
      "command": "npm install --ignore-scripts --no-audit --no-fund --package-lock=true && npm ci --offline --ignore-scripts --no-audit --no-fund",
      "result": "passed",
      "summary": "Temporary cache hydration followed by exact offline install succeeded."
    },
    {
      "command": "npm test",
      "result": "passed",
      "summary": "XO, AVA, and tsd completed: 182 passing and one declared expected failure."
    },
    {
      "command": "node --no-addons src/nl2repobench/verification/node/candidate_runner.mjs (parse/stringify/default probes)",
      "result": "failed",
      "summary": "All requested query-string API probes returned export-is-not-callable, confirming the blocker."
    },
    {
      "command": "npm pack --ignore-scripts followed by validate-package.mjs",
      "result": "failed",
      "summary": "Verbatim upstream tarball was rejected with exit 71 because package.json contains scripts."
    },
    {
      "command": "git diff --check",
      "result": "passed",
      "summary": "No whitespace errors in the shared worktree diff."
    },
    {
      "command": "Harbor/Docker/Oracle/control runs",
      "result": "not-run",
      "summary": "Explicitly prohibited by the assigned audit scope and unsafe while the boundary blocker remains."
    }
  ],
  "validationOutput": [
    "Node 22.23.1 and npm 10.9.8 were used.",
    "Source archive, license, package metadata, lockfile, lifecycle, and JSON-boundary evidence are recorded.",
    "No hidden/private/cache/secret/shared artifacts were added to the task directory."
  ],
  "residualRisks": [
    "Current runner cannot invoke the package's default namespace methods.",
    "A reviewed private npm cache closure and node:test adapter do not exist yet.",
    "Prototype-key behavior and oversized upstream performance cases need explicit future scope decisions."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added one task-local blocked audit record; no compiler, runtime, Docker, hidden-test, cache, secret, or shared-index edits.",
  "reviewFindings": [
    "blocker: src/nl2repobench/verification/node/candidate_runner.mjs:62-64 — only direct callable exports are invocable, but query-string exposes parse/stringify under a default namespace object.",
    "high: src/nl2repobench/verification/node/validate-package.mjs:39-44 — exact upstream tarball contains scripts and is rejected by lifecycle policy.",
    "high: src/nl2repobench/harbor/node_dependencies.py:90-175 — generated lockfile alone did not satisfy offline cache closure.",
    "medium: upstream test/*.js — AVA/tsd suite requires reviewed node:test adaptation and excludes non-JSON callbacks/stress cases."
  ],
  "manualNotes": "Recommended disposition is blocked.md until the parent approves a boundary/adapter decision; no routine completion handoff or production-readiness claim is made."
}
```

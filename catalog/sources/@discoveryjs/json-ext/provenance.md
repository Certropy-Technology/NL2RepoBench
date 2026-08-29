# `@discoveryjs/json-ext` Authoring Provenance

Status: `controls-passed`. Private Oracle,
test, adapter, command, and dependency bytes are content-addressed under
`.nl2repo/artifacts`; this public source directory contains only declarations,
digests, controls, and reviewable behavioral provenance.

## Immutable Source And License

- Upstream: `https://github.com/discoveryjs/json-ext`.
- Revision: `457d4d9d4e55bb1e14fde192715114b80e20c4c9`.
- Tree: `0869a915876c7ce1fe2e9e8aa33dd82c82191a36`.
- Commit subject: `Add summary to benchmark readme`.
- Commit timestamp: `2026-07-02T02:22:25+02:00`.
- Submodules: none; the detached source was clean before the baseline.
- `git archive --format=tar` size: 116,111,360 bytes.
- Source archive SHA-256:
  `dbc66fd6d20e59d441667a70b99d11d1f96a50d24ee2b43479db882070531894`.
- Root `LICENSE`: MIT text, 1,096 bytes, SHA-256
  `f1f8656800605835965b43a777c1b459d2756d0429913f17c8c7a817729926c1`.
- Pinned `package.json` SHA-256:
  `693f8862b3db75d469bb3065768869853e2b0b49d0cd15045dc5b48c13f1e475`.
- Pinned `package-lock.json` SHA-256:
  `bb99e45375adc885d408413e5582b46a7a62bbec5fd42ca46098dac4ce395776`.

The source contains 50 tracked files and 116,060,761 tracked bytes. Most of
that size is benchmark data: `benchmarks/fixture/big.json` alone is 99,947,225
bytes. The scored distribution does not contain benchmarks or fixtures. The
runtime implementation is six JavaScript modules, 1,171 physical lines and
36,244 bytes.

## Locked Upstream Baseline

The exact revision was installed and tested in
`docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`:

```text
node --version  -> v24.19.0
npm --version   -> 11.17.0
npm ci --ignore-scripts --no-audit --no-fund
npm run lint
npm test
npm run bundle
npm run transpile
npm run test:all
```

The source suite passed 1,526/1,526. The generated CJS copy passed
1,526/1,526, the generated dist bundle passed 6/6, and the E2E package checks
passed 9/9. Full output is retained at
`.nl2repo/authoring-work/node-author-wave2-20260828/discoveryjs-json-ext/evidence/upstream-baseline.log`.
The source Mocha JSON report is 1,017,664 bytes with SHA-256
`4be97b7208d488eb054a4df563120649b29889154dc6dd55875a271a8e2dcc52`.

## Scripts-Stripped Production Adaptation

The upstream package has no runtime dependencies, but its development lock
contains the test, lint, coverage, and bundle toolchain. Those packages are
not candidate runtime requirements and are not promoted into the evaluation
closure.

The Oracle fetches only the full pinned Git revision, verifies the exact
116,111,360-byte `git archive` digest, verifies package identity and MIT
license, and then writes a scripts-stripped ESM distribution to `/workspace`.
The distribution contains six upstream runtime modules, `index.d.ts`, LICENSE,
a root package manifest, and a zero-dependency npm v3 lock. It omits source
tests, benchmarks, generated CJS/dist files, build scripts, dev dependencies,
registry configuration, and lifecycle hooks.

The generated reference distribution has 10 files and 41,044 bytes. Its
package manifest SHA-256 is
`cfa79ef6a99ce221d2fb983746930a49e7b428ccf02ba942b93e9d6f2067ba7c`.
`npm ci --offline --ignore-scripts --no-audit --no-fund`, package creation,
and isolated installation all passed with an empty npm cache.

The actual generated Agent base is the locked image
`nl2repobench/openhands-sdk-fork:930e9b1da-bookworm`, image ID
`sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f`.
It preinstalls exact system packages `git=1:2.39.5-0+deb12u3` and
`ca-certificates=20250419~deb12u1`; the compiler verifies those versions and
copies Node/npm from the locked Node image without running a package installer.

## Bounded Candidate Boundary

The scored root exports are `parseChunked`, `stringifyChunked`,
`stringifyInfo`, `parseFromWebStream`, and `createStringifyWebStream`.
Each call runs as UID 10001 in a new bounded child process. Requests are at
most 64 KiB and responses at most 256 KiB, with fixed operation names, bounded
depth/items/text, finite JSON values, and validated byte-chunk and option
records.

The adapter constructs iterables, generators, callbacks, Web Streams,
`undefined`, non-finite numbers, and two fixed circular graphs inside the child
only. No JavaScript source, function body, loader, callback implementation,
regular expression, path, environment override, or object identity crosses the
JSON transport. The trusted Node test runner owns collection and report output;
the candidate cannot write the verifier report directory.

## Frozen Denominator

The private `node:test` contract contains 50 unique leaves:

- 1 package/distribution leaf;
- 17 `parseChunked` leaves;
- 17 `stringifyChunked` leaves;
- 9 `stringifyInfo` leaves;
- 3 `parseFromWebStream` leaves; and
- 3 `createStringifyWebStream` leaves.

The locked reference distribution collected 50 and passed 50 through the
unprivileged child adapter. The final local log SHA-256 is
`b6dfdbb2512b6e1493488c4374c54245ae052476540a419e581e81b5967f84b9`.
Collection uses `node-test-leaf-pass-rate-v1`, fixed denominator 50, and
collection mismatch `fail`.

## Private Artifact Closure

- npm v3 dependency bundle:
  `sha256:6acea79a33b13906b4804a2f4f701b3b3e969cafea1bcb247e0fe1b31e74fa75`
  (10,240 bytes);
- fixed command plan:
  `sha256:10e70a89b271a2cd71d8dbaa6848530c6550ac4d87e65ae87d7332265e5eedd9`
  (10,240 bytes);
- hidden test and child-adapter bundle:
  `sha256:8403e76eb9a4efd4aedd2fce07b329935067b615738ec6c93f0a1a494a9b2e6e`
  (30,720 bytes); and
- Oracle-only exact-fetch script:
  `sha256:a81c1f5209e45cc9272fb26701c6aeb660acbaa055a9aba8299cdbee0049615c`
  (10,240 bytes).

The npm bundle validator passed with npm `11.17.0`; its cache closure is
intentionally empty because the scripts-stripped candidate has no runtime
dependencies.

## Production Gate And Controls

The model Agent and separate verifier are `no-network`, with no static allowed
hosts and no registry closure. The Oracle script is never included in the
Agent image or model upload. Only an Oracle run may receive the exact
`github.com` run-scoped source-host authorization required to fetch and verify
the pinned revision.

The Node runner originally imposed a hardcoded 120-second test-process timeout
despite the task declaring a 300-second cumulative candidate budget. Under
concurrent host load this produced a valid but incomplete-behavior Oracle
result (25/50). The generic runtime now accepts a bounded `--timeout`, the
compiler passes `candidate_total_timeout_sec`, the locked runtime digest was
updated, and all 48 Node foundation tests pass. The corrected official Oracle
is `valid=true`, collected/passed 50/50, reward 1.0.

Negative controls on the corrected runtime produced:

| Control | Result |
| --- | --- |
| Empty | Valid installation-failure exception, collected 0, reward 0 |
| Installable stub | Valid, collected 50, passed 2, reward 0.04 |
| Forged workspace grading/reward/report | Trusted verifier valid, collected 50, passed 2, reward 0.04 |
| One hanging candidate call | Valid, collected 50, passed 2, reward 0.04 after bounded termination |
| Direct offline verifier | Docker `--network none`, valid, 50/50, reward 1.0, public network false |

One initial direct offline replay under concurrent campaign load scored 41/50;
the official Harbor Oracle, an immediate diagnostic first pass, a visible
second pass, and a clean final offline replay all scored 50/50. The superseded
result remains in task-local evidence and is not used as the canonical offline
receipt.

Canonical production evidence and generated runtime are refreshed after this
lifecycle transition. Review, model pilot, dataset publication, and parity are
outside this lane.

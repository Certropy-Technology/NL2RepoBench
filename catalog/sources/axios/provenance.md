# Axios Authoring Provenance

## Freeze

- Upstream: `https://github.com/axios/axios`
- Revision: `84a9f3b9a4f3244b8c8e818f557d64c7b964fb25`
- Frozen checkout: `source/`
- Commit timestamp: `2026-08-19T17:53:46+02:00`
- License: MIT
- Package version at the frozen revision: `1.20.0`
- Candidate evidence supplied for comparison: latest `1.19.0`, 478298666 monthly downloads, last activity `2026-07-29`

## Static Inventory

`api-inventory.json` was produced by `tools/node-inventory` without importing or executing
the candidate. The scanner passed its own build and self-test first.

- Source digest: `sha256:c5d3d80a6b3f09d0e35e5a4b1bc78cb47216190b4b46f745f96c63fe16f1a0eb` (`git archive --format=tar 84a9f3b9a4f3244b8c8e818f557d64c7b964fb25`)
- Scanner digest: `sha256:8fd59259135f05911302fe7f2c3e1fd83b7c1cb148e2cb373786a604161b99e1`
- 94 source files, 8792 implementation LOC, 448 public symbols, 614 imports
- 127 test files, 24740 test LOC, 1548 static test registrations
- Observed test framework: Vitest/browser/module/smoke; `node:test` registrations: 0
- Static risks: `dynamic-import`, `external-service`, `filesystem-access`, `process-access`
- Syntax diagnostics: none

`deterministic-test-inventory.json` retains the full upstream inventory and records the separately
frozen private `node:test` slice at 16 leaves. The private bundle is stored only in the content-
addressed artifact root and is not present in the public catalog source.

## Dependency Probe

- Root runtime dependencies: `follow-redirects`, `form-data`, `https-proxy-agent`, `proxy-from-env`
- Lockfile: npm v3, 683 package entries, 683 integrity entries, all resolved from the npm registry
- Install-script packages present in the lock closure: `fsevents` and nested Playwright `fsevents`
- The source package declares 39 development dependencies and Vitest-based test scripts.

## Remediation decision

The approved slice is deterministic and no-network: public exports, headers, configuration merge,
URI construction, adapter-driven request preparation, form serialization, errors, cancellation,
HTTP status helpers, and promise helpers. The full upstream Vitest/browser/module/smoke suite is
not used as the fixed denominator. The private test bundle, npm cache closure, Oracle source
archive, compiled Harbor bundle, and negative-control receipts are task-local evidence; no Agent
Run was started in this lane.

## Instruction migration revalidation (2026-09-05)

- Current catalog source content digest: `sha256:fd2d7ce17988470b91085ef5df896c250af3b2647d3869144539782f398bcffd`.
- Two independent NoNetwork Node projections were byte-identical. The fresh canonical manifest
  digest is `sha256:f46af14d968a0cd972a96a1dabbc7a139fb02f0a3ec150f0a9f0061ec319a021`; the
  `bundle.manifest.json` bytes are SHA-256
  `sha256:41919f056d9a258c2eb75194281e1eefe30e3d47d10932c8a3e15667bfb1b4e9`.
- Harbor `0.21.0` Oracle run `axios-revalidation-oracle-20260905` collected and passed `16/16`
  leaves with reward `1.0`; network probes reported `public_network_available=false`.
- Fresh independently prepared `stub` and `forgery` controls each collected `16/16` leaves,
  passed `0`, and scored `0.0`. Forgery wrote candidate `reward.json` and `report.json`, while
  verifier-owned grading remained `0.0`.
- Task-local receipt summaries are in `evidence/revalidation-*.json`; complete ignored Harbor
  run trees remain under the worker `.nl2repo/axios-revalidation-runs/` directory for parent
  artifact inspection. The parent must regenerate `catalog/tasks/axios` from the fresh manifest.

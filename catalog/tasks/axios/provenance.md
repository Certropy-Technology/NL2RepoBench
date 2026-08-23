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

- Source digest: `sha256:e81bdadfeb7d7a3bcd31aaf85f6cf269d03e55176f73daf604330697b0fb83d1`
- Scanner digest: `sha256:8fd59259135f05911302fe7f2c3e1fd83b7c1cb148e2cb373786a604161b99e1`
- 94 source files, 8792 implementation LOC, 448 public symbols, 614 imports
- 127 test files, 24740 test LOC, 1548 static test registrations
- Observed test framework: Vitest/browser/module/smoke; `node:test` registrations: 0
- Static risks: `dynamic-import`, `external-service`, `filesystem-access`, `process-access`
- Syntax diagnostics: none

`deterministic-test-inventory.json` records the stable summary and explicitly does not claim
runtime collection or a frozen denominator.

## Dependency Probe

- Root runtime dependencies: `follow-redirects`, `form-data`, `https-proxy-agent`, `proxy-from-env`
- Lockfile: npm v3, 683 package entries, 683 integrity entries, all resolved from the npm registry
- Install-script packages present in the lock closure: `fsevents` and nested Playwright `fsevents`
- The source package declares 39 development dependencies and Vitest-based test scripts.

## Gate Decision

Status is `blocked`. Axios's product behavior is HTTP/network I/O, while the active first
slice requires a JSON-only candidate boundary and a separate no-network verifier. The upstream
test suite also cannot be used as the required private `node:test` leaf bundle. Packaging would
therefore require an unapproved behavioral narrowing and new private tests; no private test,
dependency bundle, verifier, Oracle, control, model, or publication artifact was invented.

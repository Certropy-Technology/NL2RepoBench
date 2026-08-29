# `fs-extra` Authoring Provenance

## Source freeze

- Upstream: `https://github.com/jprichardson/node-fs-extra`
- Revision: `53a8d1a63c8eb30573110ed0f6528975f98801f0`
- Commit subject: `11.4.0`
- Git tree: `470acb0afecade7dfd0ddcd40a349d94b75739cb`
- Raw `git archive --format=tar` SHA-256:
  `3b7a476361ff49cdba8037c03fcc6bab044c85ff3c33e29ed8a1f489309a41f0`
- Raw archive size: 634,880 bytes
- License: MIT; `LICENSE` SHA-256:
  `c6a7de1428955aa5a692f4d3a3d3ede658d959616944713337cda296736442e1`
- Submodules: none

The trusted Oracle fetches only the exact commit from `github.com`, asserts
`FETCH_HEAD`, recreates the raw git archive, and verifies the digest before
copying source into `/workspace`. The model Agent remains offline and receives
neither the Oracle bundle nor source-host authorization.

## Upstream baseline

The frozen source was tested in the locked Node `24.19.0` image with npm
`11.17.0`. `npm install --ignore-scripts --no-audit --no-fund` followed by
`npm test` exited zero: StandardJS lint passed, Mocha reported 731 passing and
8 pending, and the ESM smoke suite passed. The pending cases are the documented
cross-device move fixtures that require `CROSS_DEVICE_PATH` on a second mount.

## Dependency closure

The upstream repository intentionally sets `package-lock=false`. Authoring
therefore generated a production-only npm lock using the locked npm version and
pinned the resulting pure-JavaScript closure:

- `graceful-fs@4.2.11`
- `jsonfile@6.2.1`
- `universalify@2.0.1`

The private npm bundle contains the lockfile, only the matching npm cache
entries, a file-by-file SHA-256 manifest, no `node_modules`, no lifecycle
scripts, and no native packages.

## Verifier adaptation

The supported API is filesystem-stateful, so a generic function-call adapter
would not be sufficient. The task-specific child adapter creates one bounded
temporary tree per request, imports the installed candidate only as UID 10001,
executes one allowlisted scenario, and returns a JSON-safe projection. Trusted
tests never put candidate paths on their module search path and own all grading,
collection, and reward files.

The fixed denominator is 50 leaves. Network checks, workspace ingestion,
offline candidate installation, process/file-descriptor limits, per-request
timeouts, report bounds, and UID process cleanup are supplied by the shared
Node verifier runtime.

# `universalify` Authoring Provenance

## Source freeze

- Upstream: `https://github.com/RyanZim/universalify`
- Revision: `dc17e0e00fb39c8d52e97ce77e494cdadfa8d19c`
- Commit date / subject: `2023-11-01T13:11:55-04:00` / `2.0.1`
- Unprefixed `git archive --format=tar HEAD`: 20,480 bytes
- Archive SHA-256: `f127a1e7e44b6583ee6ae2451824fb1e4d0b886f5a3ba5282738c7700d36b380`
- License: MIT, `LICENSE` SHA-256
  `3fda5977c0904e226190b4e21d64340c1731e2142d6fe5f3dee0090a216b8b63`
- Seven tracked files, no submodules, and a clean detached source tree before
  baseline dependency installation.

## Baseline and adaptation

The complete upstream command `standard && nyc --reporter text --reporter
lcovonly tape test/*.js | colortape` passed 37/37 assertions under the locked
Node 24.19.0/npm 11.17.0 image with 100% statement, branch, function, and line
coverage for `index.js`.

The scored runtime has no dependencies. Upstream development dependencies are
not part of the candidate contract or private offline closure. The trusted
Oracle verifies the exact source archive first, removes only development
scripts/dependencies from `package.json`, and generates an npm v3 root-only
lock offline before verification.

## Runtime and private artifacts

- Runtime image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Runtime: Node `24.19.0`, npm `11.17.0`, linux/amd64, glibc.
- npm closure: `sha256:e4d96e45c33b5fea369b323dd7c3ae956d6bc534909e11a513a8dae7a96ed436` (10,240 bytes).
- Command plan: `sha256:1f3a4333c063d3a0b87b0367e8bca94d7c999b30d62cfa1ebdf8ae6004207f6f` (10,240 bytes).
- Private tests and adapter: `sha256:bf52a2fedbbe0467d4ec866d7da51a8c2360c228b7dba6614494c17e11ba87ee` (20,480 bytes).
- Oracle: `sha256:6ff998fc6304d53f8a9fc4de50f230c5a6e107e653edadbd800bb56307924422` (10,240 bytes).

The candidate and separate verifier are no-network with no static allowed
hosts. Only a trusted Oracle execution receives the exact `github.com`
run-scoped source authorization. No reference source or private verifier bytes
are included in the public source directory or candidate image.

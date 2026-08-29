# `crypto-random-string` Authoring Provenance

## Immutable source

- Upstream: `https://github.com/sindresorhus/crypto-random-string`
- Revision: `09e2f1d01be98dff129f52555a733cf25a319067`
- Commit subject: `Add todo comment (#53)`
- Tree: `e9a5c198c584ea20967a1a3990402c0fae6eec5a`
- Git archive SHA-256: `f2c17dd0596c7e2b89f506f78b22ea49265ecda48d6822051413a401b29d177c`
- Tracked files: 13; submodules: none
- License: MIT; upstream `license` SHA-256:
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`

The source was fetched into the task-local authoring work directory, checked
out detached at the exact revision, and verified clean. The reference source is
not copied into the public source or candidate image. The private Oracle bundle
fetches only this revision during the trusted Oracle phase, asserts the resolved
commit and archive SHA-256, removes the temporary clone, and then writes the
documented dependency-free adaptation. The model Agent receives neither the
bundle nor the run-scoped `github.com` authorization.

## Upstream inventory

The pinned package is `crypto-random-string@6.0.0`, ESM, with a default root
export. Its upstream runtime imports `uint8array-extras`; its type declaration
imports `type-fest`. The task adaptation removes those nonessential runtime and
build dependencies while preserving the documented output and error behavior
using Node's built-in `node:crypto` and `Buffer` APIs. Upstream `test.js` and
`index.test-d.ts` were inspected for behavior inventory but are not bundled.
The source checkout intentionally sets `package-lock=false` and therefore has
no upstream lockfile. In a separate task-local `git archive` extraction,
`npm install --ignore-scripts --no-audit --no-fund` installed the source-only
development closure and `npm test` passed xo, AVA, and tsd, including all 15
AVA tests. The frozen checkout itself remained clean.

## Environment and closure

- Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc
- Base image:
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Candidate dependency closure: root-only npm lockfile v3 and an empty cache,
  stored as private artifact
  `sha256:54c0b32fe8cdd23d50a801a05d9553d855dfa496404002f0a9f29fa43b92658e`
- Candidate install uses `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Agent and verifier network mode is `no-network`; no static allowed hosts are
  declared. Only the trusted Oracle command receives run-scoped authorization
  for the exact `github.com` host needed to verify the frozen source.

## Task-local artifact refs

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| npm closure | `54c0b32fe8cdd23d50a801a05d9553d855dfa496404002f0a9f29fa43b92658e` | 444 |
| command plan | `a1ce120f5ee308f04ea88dc1891bc2199704d5c2c3957ae0839033e48efddbb4` | 248 |
| private 32-leaf tests and child adapters | `646a508a5efe562392587a0189692ea3b989acfce510461456e68e6da9dbc670` | 3618 |
| Oracle solve bundle | `c02d574eafcb4c0f7c7bec645dda501f72d414c9914bef059bbbb2003f34d618` | 2243 |

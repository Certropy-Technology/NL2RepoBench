# `p-retry` Provenance

- Upstream: `https://github.com/sindresorhus/p-retry`
- Revision: `35681f6c70f8ca2bdcb9542281147679184269fa`, peeled from
  annotated tag `v8.0.0`
- Tree: `9a124371b1b66a47c79badb8e65d67416271173a`
- Unprefixed git archive: 81,920 bytes,
  `sha256:3eabac5b48586a9a65714ad4cc4685a03705e3adcf3ee57d7ce9dabf5beb8278`
- License: MIT; frozen `license` file
  `sha256:5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Source package metadata:
  `sha256:d42f86b65c142997c38450a9512ed0525d84fdac96b9673a6d3a62c6e7114118`
- Runtime entry:
  `sha256:56233d1d87da3899c15639a0dc5756546184f311ddcd7e3e6de91450bed7c55c`
- Declaration entry:
  `sha256:7a4e8b85a9fef02b7db31646d91b3dbc12dd81f334c20ced9d8728876e19a329`
- Locked runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm,
  glibc `2.36`, `linux/amd64`
- Base image:
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Upstream baseline: three no-network runs each completed XO, 70 AVA
  leaves, and tsd with exit code 0. The first discarded harness attempt used a
  read-only mount that prevented XO from creating its cache; no source or test
  assertion failed in that attempt.
- Development baseline lock: npm v3 with 642 package entries, retained only in
  task-local authoring storage.
- Runtime closure: `is-network-error@1.3.2`, npm v3 lock
  `sha256:e20de62fe1faadd85bd26d0ca715c0defe8ad3cb737d606ae7e4c48729ba9343`,
  four cache files, and a successful fresh `--network none` offline install and
  ESM import.
- Oracle: trusted `solve.sh` fetches only the exact revision from `github.com`,
  asserts `FETCH_HEAD` and `HEAD`, regenerates the git archive, and verifies its
  digest before exposing source to `/workspace`. The model agent receives
  neither this solution bundle nor source-host authorization.

The authoring checkout, baseline closure, logs, and private artifact sources are
stored only under task-local
`.nl2repo/authoring-work/node-author-wave2-20260828/p-retry/`. Production
compilation resolves immutable private artifacts from this worktree's
`.nl2repo/artifacts/` CAS.

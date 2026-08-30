# `pretty-ms` Authoring Provenance

Status: `controls-passed`; ready for downstream Agent Run review.

## Source and license freeze

- Upstream: `https://github.com/sindresorhus/pretty-ms`
- Frozen revision: `93666b389e1ed07912b6c2466468da21d9f834ce`
- Commit tree: `9cb09c676dd9192336300e0f52a1db47233ccf0a`
- Commit message: `Add FAQ explaining formatted-difference rounding inconsistency`
- Source archive: `git archive --format=tar HEAD`
- Source archive SHA-256: `e2a108dc70512373b94d959c2084d44eef117e32091a43659705375986408dd4` (51,200 bytes)
- Tracked files: 13; no submodules or source modifications.
- License: MIT; license SHA-256 `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- Frozen source `package.json` SHA-256: `f31f46c44617f02ce9c5535c18646dc61e50cc668060420f0d654edfa1e4c871`.

## API and test inventory

The source exports one default function, `prettyMilliseconds`, with the
`number | bigint` input and `Options` declaration described in `instruction.md`.
The source also contains 27 AVA behavior tests and a TypeScript declaration
test. The exact Node 24.19.0/npm 11.17.0 image passed `npm test` (`xo`, AVA,
and `tsd`). The Harbor slice uses 30 deterministic `node:test` leaves over the
JSON-safe number path. BigInt remains documented as an upstream capability
outside the fixed JSON candidate boundary.

The private tests cover default unit decomposition, negative and zero values,
finite-number errors, seconds/milliseconds precision, compact and unit-count
selection, verbose pluralization, separate and sub-millisecond output, colon
notation precedence, hidden years/days/seconds, and option immutability.

## Runtime and dependency closure

- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc.
- Runtime image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Candidate runtime closure: exact `parse-ms@4.0.0`, installed by npm from a
  private integrity-checked v3 cache; no native packages and no lifecycle
  scripts are required.
- npm bundle: `sha256:fc8df9226bacdd04ae3fb969befb3d24cc63aec9d26ea12d3a483bcbff73acf8`, 11,250 bytes.
- Candidate and verifier phases use `no-network`; the Oracle alone receives an
  explicit `github.com` authorization for the exact revision fetch.

## Harbor and verifier

- Harbor: `0.21.0`; toolchain: `toolchain.node.lock.toml` with digest
  `sha256:aac76d5c1a4232c5c9c96870198475e0fed151793b60eeb830a7c053692dc8`.
- Command bundle: `sha256:3a0d5d438bfa114938040770c8c288320518bdaec8733dbd7f373f0c5cf0827f`, 261 bytes.
- Test bundle: `sha256:086f2a56063eec10d873105ac49705aa463144807b46cc9fc5b7db0a85e8ded9`, 1,738 bytes.
- Oracle bundle: `sha256:567d800c5272f7f9bbfe347980ae9688156eebc09783922ed648e77245e674dc`, 1,122 bytes.
- The separate verifier uses the locked Node subprocess boundary and
  verifier-owned `node-test-json-v1` grading. Private tests never import the
  candidate into the trusted test process.

## Evidence commands

```text
git clone https://github.com/sindresorhus/pretty-ms .nl2repo/authoring-work/pretty-ms/source
git -C .nl2repo/authoring-work/pretty-ms/source checkout --detach 93666b389e1ed07912b6c2466468da21d9f834ce
uv run nl2repo task validate-source catalog/sources/pretty-ms
uv run nl2repo task lint-network --tasks-root catalog/sources
uv run nl2repo harbor compile catalog/sources/pretty-ms --output .nl2repo/authoring-work/pretty-ms/compiled-current --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
uv run --frozen --project harbor-runner harbor run -p .nl2repo/authoring-work/pretty-ms/compiled-current/pretty-ms -a oracle --allow-agent-host github.com --job-name pretty-ms-oracle-current -o .nl2repo/authoring-work/pretty-ms/runs-current/oracle --n-concurrent 1 --yes
uv run nl2repo harbor prepare-control .nl2repo/authoring-work/pretty-ms/compiled-current/pretty-ms <kind> --output .nl2repo/authoring-work/pretty-ms/controls-current --toolchain toolchain.node.lock.toml
```

The local no-network reference subprocess probe collected and passed 30/30
leaves before the production compile. The fresh Harbor Oracle also passed
30/30. Empty, stub, forgery, install-script, loader-hook, bounded hang, and
offline controls completed with verifier-owned results and no public verifier
network. No Harbor model Agent Run was started in this lane.

## Residual risks

- This is one production Oracle run plus deterministic negative controls, not a
  cross-run stability experiment.
- BigInt calls and the full AVA/tsd development suite are outside the scored
  JSON boundary; the development suite passed independently and the supported
  number behavior is represented in the frozen 30-leaf slice.
- Review, model Agent Run, pilot, dataset projection, and publication remain
  integrator-stage gates.

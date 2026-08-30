# Widest-line Authoring Provenance

## Frozen source

- Upstream: `https://github.com/sindresorhus/widest-line`
- Revision: `d1f04193564d484ca6e24fd8d78d96545ccb0a83`
- Commit subject: `6.0.0`
- License: MIT; the frozen `license` file SHA-256 is
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- Exact source archive command: `git archive --format=tar HEAD`
- Source archive SHA-256:
  `39a6707282ade39a464de258151bb698e31daad5920fa7b40283ade60714aba7`.
- Frozen `package.json` SHA-256:
  `632e64cbe43d7448728426c8f47445653b63d0ecd545d1242d123164fc2b48dd`.
- No submodules; the runtime consists of `index.js` and `index.d.ts`.

## Environment remediation

The upstream repository intentionally contains `.npmrc` with
`package-lock=false` and only has a dependency range for `string-width`. A
separate lock probe removed that repository setting, resolved the production
closure to `string-width@8.2.2`, `get-east-asian-width@1.6.0`,
`strip-ansi@7.2.0`, and `ansi-regex@6.3.0`, and verified offline npm CI with
the generated lock and cache. The package's upstream AVA/XO test command passed
its one test and three assertions in the Node 22.23.1/npm 10.9.8 authoring
environment. Production gates use the locked Node 24.19.0/npm 11.17.0 image.

## Deterministic rescope

The upstream suite has one smoke test with three assertions. The production
contract expands this into 20 deterministic node:test leaves covering the same
API and its documented Unicode, ANSI, line-separator, empty-input, and error
boundaries. The private custom-json-v1 adapter constructs only JSON-safe string
or primitive inputs and invokes the candidate through the generic Node
subprocess boundary. The verifier owns collection, reporting, and reward.

## Network and isolation

Candidate and separate-verifier phases use no network and an empty static host
allowlist. The dependency cache is built into the verifier/agent image and
candidate installation runs with scripts disabled. Only the trusted Oracle
solution receives a run-scoped authorization for `github.com`, then asserts the
resolved commit and archive digest before copying the frozen runtime source.

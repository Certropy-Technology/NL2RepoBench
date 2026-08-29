# Authoring Provenance

- Mode: `author-one`; package ownership is restricted to this detached lane.
- Frozen upstream: `https://github.com/BridgeAR/safe-stable-stringify` at full
  commit `8a02137ac933eff57dd6e49beb9ee766fe8dd372`.
- The source archive and license bytes were generated and hashed from the
  detached checkout. The upstream package is MIT and has no runtime dependency.
- Upstream `test.js` is a tap suite with 63 top-level blocks. The Harbor
  collection is a 52-leaf `node:test` contract covering the public behavior and
  deterministic edge cases without exposing upstream test source or assertions.
- The model candidate receives only `instruction.md`. Private adapter, tests,
  Oracle source acquisition, dependency bundle, and control scripts are
  artifact-bound and are never available to the model run.
- Runtime policy is Node 24.19.0/npm 11.17.0 on the locked amd64 Bookworm image;
  agent and verifier execution are no-network. The Oracle alone receives the
  exact upstream host authorization during its one trusted source fetch.

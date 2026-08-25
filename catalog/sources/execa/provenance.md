# execa authoring provenance

- Frozen source: `https://github.com/sindresorhus/execa`
- Revision: `8017b279e19347efaf2587711c2d57dbd4330740`
- License: MIT (`license` in the frozen tree)
- Deterministic source archive: `.nl2repo/authoring-work/execa/source.tar`
- Archive SHA-256: `8ee157bba161a30aea54af36a1c85b95c02737d379a5b6ae482e099905f49115`
- Runtime probe: Node `v22.23.1`, npm `10.9.8` on the authoring host.
- Frozen source metadata: package `10.0.1`, ESM, Node `>=22`, 11 runtime exports
  in `index.js`, 446 tracked JavaScript files, 337 upstream test files, and 167
  fixture files.
- Upstream `npm install --ignore-scripts --package-lock-only` produced npm lockfile
  version 3; `npm ci --ignore-scripts --no-audit --no-fund` succeeded. The full
  upstream AVA suite exceeded the bounded 600-second authoring probe, so this
  task uses a separately documented 11-leaf `node:test` adaptation of the
  deterministic local process-execution behavior rather than claiming full-suite
  parity.
- The task's scored candidate has zero runtime dependencies. The trusted Oracle
  solution is a private contract implementation and does not install from npm;
  this keeps Agent and Verifier phases offline and prevents the model from
  receiving the frozen implementation.

## Production integration attempt

The private dependency, command, test, and Oracle payloads were normalized into
content-addressed archives without changing the frozen test bytes or the
11-leaf denominator. A production compile with `toolchain.node.lock.toml`,
private-artifact authorization, and no incomplete-output override succeeded.

One fresh Harbor matrix emitted technically valid receipts: Oracle passed
`11/11` with reward `1.0`; empty collected `0` with reward `0`; stub and forgery
each passed `0/11` with reward `0`; and each verifier wrote `network.json`.
The forged workspace grading file did not affect the verifier-owned result.

This matrix is not promoted. The Oracle Harbor process remained active past the
supervisor's 601-second orchestration bound after its grading receipt had been
written. The termination directive arrived after the process returned exit code
zero, but the campaign was explicitly declared non-promotable and no retry was
authorized. `production-evidence.json` records the bounded run and receipt
paths. The generated `catalog/tasks/execa` runtime is therefore absent and the
task remains `blocked`.

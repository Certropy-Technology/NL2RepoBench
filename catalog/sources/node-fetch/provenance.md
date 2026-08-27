# `node-fetch` Authoring Provenance

Status: `controls-passed` pending independent review and Agent Run Loop pilot.

## Frozen Source

- Upstream: `https://github.com/node-fetch/node-fetch`
- Revision: `8b3320d2a7c07bce4afc6b2bf6c3bbddda85b01f`
- Commit tree: `09a7e2f23c05315c950fde9d0422531bcd951c8f`
- Commit subject: `fix: Remove the default connection close header. (#1736)`
- Archive command: `git archive --format=tar HEAD | sha256sum`
- Archive SHA-256: `c54ad1e222b0dab09410542e9142b5374a63a72b2e5cc8e931b147559628265c`
- Submodules: none
- License: `MIT`; `LICENSE.md` SHA-256 is
  `3e2c11dcf3f17ab585baab8faba54772d7872f1c6e026022acd4b4006665efb0`.
- `package.json` SHA-256 is
  `42a19b8e334ab1a0503f0541df2143be17663bd042fdb4a3e1ac265bb2b0f473`.

The detached source tree contains 53 tracked files. It is not copied into the
agent environment; the private Oracle bundle alone contains a verified archive.

## Inventory And Adaptation

The pinned ESM package declares version `3.1.1`, root `src/index.js`, and
exports default `fetch`, `Headers`, `Request`, `Response`, `FetchError`,
`AbortError`, `isRedirect`, and form-data/blob helpers. It has three runtime
dependencies (`data-uri-to-buffer`, `fetch-blob`, `formdata-polyfill`) and a
Mocha-based development suite.

The original suite has deterministic object tests but also starts localhost
servers and exercises sockets, streams, compression, redirects, multipart
forms, abort handling, and other values that cannot cross the JSON subprocess
boundary. The task therefore traces 23 private `node:test` leaves to the
documented JSON-safe contracts for `Headers`, `Request`, `Response`, `data:`
fetches, and `isRedirect`. No assertion relies on a live listener or network.

Direct targeted source probes under Node `22.23.1`/npm `10.9.8` passed:

| command | result |
| --- | --- |
| `npm test -- test/headers.js` | 15 passing |
| `npm test -- test/response.js` | 28 passing |
| `npm test -- test/request.js` | 20 passing |

The full upstream suite was also probed under the required Node `24.19.0`/npm
`11.17.0` production image after resolving a local authoring lock. It failed
with exit `151`: the upstream local HTTP fixtures reported `ECONNREFUSED` and
151 network-facing leaves failed. This source/runtime incompatibility is
preserved as evidence; it is the reason the no-network task does not claim
full-suite parity.

## Dependency Closure

The upstream revision has no committed `package-lock.json` and its `.npmrc`
sets `package-lock=false`. A task-local authoring probe using the digest-pinned
Node 24 image generated an npm 11 lockfile v3 and populated an offline npm
cache with lifecycle scripts disabled. The generated lockfile SHA-256 is
`bd792a3e546526da4571ccf2134d02fce2c354e7ad79eac85821c7dde875a771`.

The private dependency artifact contains that runtime lockfile, a validated npm
cache, cached package metadata, and an integrity manifest. Candidate and Oracle
packages declare the same exact closure through the three public runtime roots;
the verifier installs it with `npm ci --offline --ignore-scripts`. No npm
command in the agent or verifier has registry egress.

## Traceability

| Contract area | Private leaf group | Source evidence |
| --- | --- | --- |
| Header mutation, lookup, ordering, raw values, validation | `headers-*` | `src/headers.js`, `test/headers.js` |
| Request normalization and rejection rules | `request-*` | `src/request.js`, `test/request.js` |
| Response status, body readers, factories, clone | `response-*` | `src/response.js`, `test/response.js` |
| Offline data URL fetch | `fetch-data-*` | `src/index.js` data URL branch |
| Redirect status classification | `redirect-*` | `src/utils/is-redirect.js` |

Every private leaf is mapped to behavior stated in `instruction.md`. Live
network and non-JSON behavior are explicitly excluded rather than silently
tested.

## Generated-Bundle Controls

The production compiler accepted this source with `toolchain.node.lock.toml`
and the task-local private artifact store. Both the digest-pinned agent and
separate verifier Docker images built successfully. Direct no-network execution
of the generated bundle produced verifier-owned receipts:

| case | valid | collection | reward | result |
| --- | --- | --- | --- | --- |
| Oracle archive | true | 23/23 passed | 1.0 | pass |
| empty workspace | true | 0 | 0.0 | pass |
| minimal stub | true | 4/23 passed | 0.173913 | pass |
| forged workspace reward | true | 4/23 passed | 0.173913 | pass |
| hanging candidate | true | 0 | 0.0 | pass |

Each receipt reports `public_network_available: false`. The Oracle setup
checks the archive digest before replacing the upstream development manifest
with the equivalent runtime-only production manifest and installing its frozen
runtime closure offline.

# Nock Authoring Provenance

## Frozen source

- Upstream: `https://github.com/nock/nock`
- Revision: `1ee467c68d601ddc22629d7a657061e6c27097c2`
- Revision date: 2026-07-30
- License: MIT (`package.json` and `LICENSE`)
- `sha256(git archive --format=tar <revision>)`: `8c54a05e667935a42b69be72e1a95d0fb027805068dcc11b0d42b654525e0918`
- Submodules: none

The trusted Oracle fetches only that full commit SHA, asserts `HEAD`, builds a Git archive, and verifies the archive digest before copying `index.js`, `lib/`, and `types/` into `/workspace`. The model task receives neither the Oracle bundle nor a source-host allowlist.

## Source baseline

The locked Node 24.19.0 image installed the committed upstream lock with npm 11.17.0 and lifecycle scripts disabled. Three independent `--network none` Mocha runs each collected 649 tests: 635 passed, 11 pending, and the same 3 failed. Two failures assert a resolver-specific `ENOTFOUND` value but receive Docker offline `EAI_AGAIN`; the third is an upstream Node 24 native-fetch response URL assertion. A normal-network run passed 637, left 11 pending, and retained only that fetch URL failure. The frozen source pass rate is therefore above 0.99 and the failures are stable and classified as environment/source compatibility rather than hidden model assertions.

## Runtime closure

The production-only template retains the upstream package name, version, engine range, files list, and three runtime dependency ranges. npm 11.17.0 resolved a v3 lock containing nine packages. All entries have SHA-512 integrity and registry tarball URLs; none declares an install script, native addon, OS/CPU restriction, git dependency, file dependency, or workspace dependency.

The private npm bundle contains the exact lock and a 39-file cache closure. It has been replayed with `npm ci --offline --ignore-scripts --no-audit --no-fund` under Docker `--network none`.

## Private verifier adaptation

The upstream tests cannot be copied directly into a trusted verifier because they import candidate code in process and include live DNS, proxy, recorder, filesystem, TLS, and timing behavior. The production denominator is a deterministic 38-leaf `node:test` adaptation covering the public in-process interception contract. Every leaf starts a bounded candidate subprocess as UID 10001, loads only the installed `nock` package, performs a synthetic `http` or `fetch` request, and returns bounded JSON to the trusted test process.

The adaptation covers package shape; method shorthands and generic intercept; body, query, header, auth, and regexp matching; static, JSON, synchronous, async, and full replies; headers and response metadata; cardinality; optional/persistent state; removal and cleanup; activation; disabled egress; error replies; definitions; filtering; and native fetch interception. Recorder/back/filesystem fixtures, live pass-through, streams/files, delays, TLS/proxy/Unix sockets, and IPv6 remain explicitly outside the public instruction.

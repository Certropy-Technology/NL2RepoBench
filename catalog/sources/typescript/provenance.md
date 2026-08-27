# TypeScript Native Preview Provenance

Status: remediation authoring. The source target is the exact candidate commit,
not a released `typescript` npm package.

## Source and license

- Upstream: `https://github.com/microsoft/TypeScript`.
- Revision: `d6c4afddb2c55f4a9dea7b59293a99a8fdea1799`.
- Tree: `1066897b6451c517d69834547aaa1491d94a78a4`.
- Subject: `Content mappers round 2 (#63936)`.
- Source archive: 263,444,480 bytes,
  SHA-256 `d3de9628ec8a782ccc5e0f0261a23fc642b9b20d5e614f78a324e5abf8b3be3b`.
- License: Apache-2.0; `LICENSE.txt` SHA-256
  `a7d00bfd54525bc694b6e32f64c7ebcf5e6b7ae3657be5cc12767bce74654a47`.

The repository root is private `@typescript/repo` version `0.0.0`; the target
package is private `@typescript/typescript`, also version `0.0.0`, and is the
native TypeScript preview described by its README.

## Environment and dependency probe

The locked image is Node 24.19.0/npm 11.17.0 on Debian Bookworm, linux/amd64,
with base image digest
`sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
The upstream lockfile is npm v3 with 432 package entries, including a
platform-specific native compiler package and 362 installed packages. A
network-enabled `npm ci --ignore-scripts --no-audit --no-fund` completed in 13
seconds. The package build then completed offline in one second with
`npm run -w @typescript/typescript build`, producing 2,611,744 bytes of `dist`.

Production rescope removes the development closure from the candidate package.
The scored distribution contains only the built ESM AST/scanner files, package
metadata, version helper, license, README, and an empty npm v3 runtime lock.
The candidate dependency bundle is therefore a complete zero-entry cache
closure; the source-development dependency closure is used only by the trusted
Oracle artifact and never by a model Agent.

## Behavioral evidence

The upstream SpanMap and WTF-8 tests collected 17 and passed 17 in three
independent no-network runs. The task-local JSON adapter contract collected 30
and passed 30 in a fresh no-network Node container as UID 10001.

The adapter is copied into a root-owned mode-0555 directory before candidate
execution. It bounds request/response sizes, validates enum and range inputs,
imports only the fixed package, and returns JSON-safe values.

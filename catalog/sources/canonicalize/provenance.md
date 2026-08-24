# `canonicalize` Authoring Provenance

Status: `packaged` / production vertical-slice passed.

The production task intentionally scopes the private boundary to ten
JSON-compatible canonicalization cases. Upstream object/callback and cycle
tests are not silently counted because they cannot be represented by the
JSON-only candidate client.

This audit records the evidence used for the task-local Node v2 source. It is
not a Harbor bundle, a private test package, or a publication approval.

## Candidate And Source Lock

- Candidate source: `https://github.com/erdtman/canonicalize`.
- Frozen revision: `c1b08c3771d681c8bd9c4d8765e00f2f717482f8`.
- Candidate report: `reports/npm-package-candidates.v1.md`.
- Commit subject: `4.0.0`.
- Commit timestamp: `2026-08-12T13:29:21+02:00`.
- Commit tree: `d75f8b2eff1d62946528f931965a8e109788ec30`.
- Source archive command: `git archive --format=tar HEAD | sha256sum` at the
  detached revision.
- Source archive SHA-256:
  `7436a1cb393e1e1b577c0066f2d9f2bc71666943d3ae740c19fc0b8a5ec60403`.
- The checkout had no submodules and no local modifications.

The archive digest is recorded in `task.toml` as the v2 `SourceLock` digest.
No upstream source files are copied into this task directory.

## Production Gate

- Production runtime: Node `24.19.0`, npm `11.17.0`, linux/amd64 image digest
  `sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Private npm v3 dependency/cache bundle: `sha256:911470dae44f1bcb844fd01523adf9f082db227f52e51d0695f2ad0a96ead73a`,
  validated with `validate_npm_dependency_bundle`.
- Production Harbor compile passed with `toolchain.node.lock.toml` and private
  artifact authorization.
- One Oracle gate passed: `valid=true`, collection `10`, reward `1.0`.
- Node control matrix passed: empty, stub, forgery, install-script, loader-hook,
  hang, and offline. See `reports/node-canonicalize-production-gate.v1.json`.

## License Revalidation

The pinned `package.json` declares `"license": "Apache-2.0"`, and the root
`LICENSE` is the Apache License, Version 2.0 text.

- `LICENSE` size: 11,357 bytes.
- `LICENSE` SHA-256:
  `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
- `package.json` SHA-256:
  `b4fe69cd7668c761bc1f0a6c41fcd3d4e53bc3c2d280b5d789fe5e6a6c6505d0`.

This is a source-license check, not a claim that a future generated package
or private dependency closure has completed legal review.

## Package And ESM Inventory

The pinned package metadata reports:

- name `canonicalize`, version `4.0.0`, and Node engine `>=18`;
- `type: module`;
- root export `.` with `import: ./lib/canonicalize.js` and
  `types: ./lib/canonicalize.d.ts`;
- `main: lib/canonicalize.js`, a matching `types` field, and a CLI `bin`
  entry point;
- zero runtime dependencies;
- four range-based development dependencies: `@eslint/js`, `c8`, `eslint`,
  and `globals`;
- upstream test command `node --test test/*.js`.

Relevant pinned-file hashes:

- `lib/canonicalize.js`:
  `4a909b5c7574ee55c37e372d47b54a37f9e36e217fc20b4d6451f5dc78cb87c1`.
- `lib/canonicalize.d.ts`:
  `5eba409e1fe34c86e46af829f1f236645b654e405e3377277b2baeb5e5352124`.
- `bin/canonicalize.js`:
  `cf81826eee228ef4d56f14f2272e635f38bc262dd4d0faa0e2b1065a0ae388f0`.

The source inventory contains 23 tracked files and 819 tracked lines. The
library implementation, declaration, and CLI entry together contain 93 lines.
The JSON pilot counts one public library API: the default `canonicalize`
export. The CLI is inventoried but excluded from the scored JSON contract.

## Upstream Test Revalidation

A clean detached checkout of the exact revision was run with the locked host
runtime versions Node `22.23.1` and npm `10.9.8`:

```text
node --test 'test/*.js'
# tests 40
# suites 8
# pass 40
# fail 0
# skipped 0
# todo 0
```

The development baseline is therefore 40 leaf tests. This observation does
not create a private test artifact and does not by itself satisfy the v2
production Oracle gate. No upstream test bytes are stored here.

## Lockfile And Dependency Closure

The exact upstream tree contains neither `package-lock.json` nor
`npm-shrinkwrap.json`. Its runtime dependency set is empty, but its development
ranges are not an immutable offline closure. The candidate report therefore
correctly requires a generated and pinned project lockfile.

The task records npm `10.9.8`, lockfile version `3`, `offline` installation,
and `ignore-scripts` policy. Before packaging, an authoring stage must:

- A clean `npm 10.9.8` lockfile-only probe generated a v3 lockfile with 154
  package entries and SHA-256
  `2419013eb1c287be6aefabf5e2bf51730a5ee21602614a8e97e5bdf1029d94d7`.
- The same generated lockfile failed `npm ci --offline --ignore-scripts` with
  an empty cache (`ENOTCACHED` for `yocto-queue`), demonstrating that lockfile
  generation alone is not an offline dependency closure.

1. resolve the intended package and any reviewed test tooling with the exact
   npm version;
2. generate a v3 `package-lock.json` and a content-addressed npm cache/tarball
   closure;
3. review integrity fields, registry provenance, lifecycle-script policy, and
   platform constraints; and
4. make the verifier consume that closure with
   `npm ci --offline --ignore-scripts --no-audit --no-fund`.

No generated lockfile, npm cache, tarball, registry credential, or unreviewed
resolution is included in this change. `dependencies.status = "unknown"` is
intentional and keeps production compilation fail-closed.

## Deterministic JSON Scope

The upstream library default export accepts general JavaScript values, while
its declaration returns `string | undefined` for values such as `undefined`.
The pilot intentionally narrows that surface to JSON-compatible values that
can cross the Node JSON subprocess boundary and requires a string result.

The public contract in `instruction.md` covers:

- recursive UTF-16 code-unit ordering of object member names;
- preservation of array order;
- compact JSON with no insignificant whitespace;
- deterministic RFC 8785 / ECMAScript number and string serialization;
- `-0` rendered as `0`; and
- rejection of non-canonical strings or non-finite numbers.

JavaScript-only values, custom `toJSON`, cycles, the CLI, filesystem access,
and network access are explicitly outside the scored scope. This is a pilot
scope decision, not a claim of complete upstream behavioral parity.

## Deliberate Omissions And Production Gate

This task-local source intentionally contains only declarative metadata,
public instruction, and this provenance record. It contains no `harbor/`
tree, Dockerfile, Oracle script, hidden test/command bytes, grader, reward
writer, private dependency artifact, npm cache, or generated package-lock.

Production remains blocked until all of the following are supplied and
reviewed outside this public task directory:

- an immutable npm dependency/cache closure and generated lockfile;
- private adapter-based tests and frozen command/collection evidence;
- a locked separate Node verifier and grader/report contract; and
- three valid stable Oracle runs plus empty, stub, forgery, and offline
  controls.

The Node toolchain is development-only, and this pilot is excluded from the
Python dataset and from any cross-language score or parity claim.

## Recommendation

Retain this task at `specified` for authoring review. Next, generate and audit
the exact npm v3 closure, then build private JSON-boundary tests from the
40-leaf upstream evidence. Do not publish, add a dataset entry, run Docker, or
run Oracle until the dependency, verifier, and control gates are complete.

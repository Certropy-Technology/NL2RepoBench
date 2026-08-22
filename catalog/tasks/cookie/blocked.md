# `cookie` Node authoring audit

Status: **blocked**. This directory contains one public, task-local evidence
record for the exact upstream revision. It is not a task descriptor, a Harbor
bundle, a private test bundle, an Oracle solution, or a publication approval.
No `task.toml`, `instruction.md`, hidden tests, verifier, Docker asset, npm
cache, dependency tarball, secret, shared dataset edit, or legacy projection is
included because the production gates below are not complete.

## Decision

Keep `cookie` blocked at the evidence stage. The frozen package is a feasible
small ESM runtime candidate, but the current checkout does not prove the
offline dependency closure or the candidate package boundary required for a
publishable task:

- the source package requires generated `dist/` files for its declared ESM
  export, while `dist/` is absent from the exact source archive and must be
  produced by a build toolchain;
- the committed npm lock is internally close but does not exactly agree with
  `package.json`, and a clean offline install of the full development closure
  fails on a missing cached tarball;
- the unchanged packed manifest contains lifecycle/build scripts rejected by
  the repository's candidate package validator;
- the upstream Vitest suite is a source baseline, not a private structured
  `node:test` bundle with a frozen verifier denominator; and
- `parseSetCookie` and the Set-Cookie serializer accept `Date` and callback
  values that the generic JSON subprocess contract cannot preserve as a
  reviewed, explicit projection.

The narrow runtime surface should be reconsidered only after these gaps are
resolved with versioned artifacts and a task-specific boundary. No Oracle or
publication claim is made here.

## Candidate and source lock

- Package: `cookie` `2.0.1`.
- Upstream: `https://github.com/jshttp/cookie`.
- Frozen revision:
  `51c485421a95ee796de6d8dab53a5ade0a20db8a`.
- Commit tree: `7beb9a2f1a9b3943c8e03c0e9fc8ce8a3e7126c1`.
- Parent: `84068f81120f1c603bfff085bf962a3747a0d540`.
- Commit subject/date: `2.0.1`, `2026-06-30T15:03:01-07:00`.
- The detached checkout had no submodules and was clean before the
  disposable build/test probes. The source tree has 27 tracked files, 11
  tracked TypeScript files, 531 lines in `src/index.ts`, and 959 lines across
  the four tracked spec files.

The source lock is an unprefixed Git archive from that exact revision. Three
independent `git archive --format=tar HEAD` outputs were byte-identical:

```text
archive bytes:   296960
archive members: 33
archive sha256:  e4f8342e3b6d89c5dc8d03e086d2f5faa8c5a09ca6f76b7ac9b4a06fa610d0b0
```

The archive contains the TypeScript source and package metadata but no
tracked `dist/` output. The exact source archive must remain the provenance
identity; generated distribution bytes must be recorded separately if this
candidate is reopened.

## License and archive review

The package declares MIT and the root `LICENSE` is present in the frozen
source:

```text
LICENSE bytes:        1175
LICENSE Git blob:     058b6b4efa3f45896ae691f2558a2a1aca05bebd
LICENSE sha256:       c02110eedc16c7114f1a9bdc026c65626ce1d9c7e27fd51a8e0feee8a48a6858
package.json blob:    7ea18a306041bd6ce84d1e3ed66a8e4fdb9ed57a
package.json sha256:  75cd16a27d7d0018a08dcbe46eef242f5cbaae4c47efd95979c77ddad59e5fac
```

The root source license and package declaration agree. This clears static
license eligibility only; it does not authorize redistribution of a generated
package or establish an immutable build artifact.

## ESM export and runtime boundary

The exact `package.json` declares:

```text
type:    module
exports: ./dist/index.js
files:   ["dist/"]
license: MIT
engines: node >=22
runtime dependencies: none
```

The public source declarations are four named ESM functions:

```text
parseCookie(str, options?)
parseSetCookie(str, options?)
stringifyCookie(cookie, options?)
stringifySetCookie(cookie, options?)
```

After the disposable build, Node `22.23.1` syntax-checked the generated
`dist/index.js` and imported the package as ESM. The observed namespace was:

```json
{
  "keys": [
    "parseCookie",
    "parseSetCookie",
    "stringifyCookie",
    "stringifySetCookie"
  ],
  "types": {
    "parseCookie": "function",
    "parseSetCookie": "function",
    "stringifyCookie": "function",
    "stringifySetCookie": "function"
  }
}
```

The normal JSON-compatible observations also worked in that child process:

```json
{
  "parse": {"foo":"bar","email":" \",;/"},
  "stringify": "foo=bar%20baz; empty=",
  "setParse": {"name":"key","value":"value","httpOnly":true,"secure":true,"sameSite":"lax","maxAge":3600},
  "setStringify": "key=value; Max-Age=3600; HttpOnly; Secure; SameSite=Lax"
}
```

The build was repeated outside this repository. Both generated
`dist/index.js` files had SHA-256
`b728aa01f45e9115920e2a92e2f3d71c1b5acfbb8bc1d702b87397860c4ba925`.
Deterministic build bytes do not clear the packaging gate: the exact source
archive has no `dist/`, and the build depends on development tooling that is
not available through a reviewed offline closure.

The generic runner can call direct named functions, but it JSON-serializes the
return value. A future task-specific adapter must make these boundaries
explicit:

- `parseCookie` accepts a string header and returns an object of string values;
  its `decode` option is a callback and is outside a JSON request;
- `stringifyCookie` accepts string-valued object members and returns a string;
  its `encode` option is a callback and is outside a JSON request;
- `parseSetCookie` returns a Set-Cookie record, but a valid `expires` value is
  a JavaScript `Date`, and missing/undefined fields are not JSON values; and
- `stringifySetCookie` accepts a `Date` for `expires` and callback-valued
  encoding options.

The current generic protocol has no reviewed cookie-specific date/error
projection and no private child adapter for multi-step or callback behavior.
Implicit `JSON.stringify` conversion of a `Date` to an ISO string must not be
treated as a frozen benchmark contract.

## Node 22 and npm metadata

The probes used Node `v22.23.1` and npm `10.9.8`. The upstream manifest only
requires `node >=22`; it does not pin the Node patch, npm version, OS, libc,
architecture, or an image digest. Those values therefore still need an
external, immutable environment lock before publication.

The package has eight development dependency roots and no runtime dependency
roots. The committed lock is npm lockfile version 3 with 281 package entries
(280 non-root entries). Every non-root entry has `resolved` and `integrity`
metadata, but the development closure includes 53 platform-constrained
entries and these install-script entries:

```text
node_modules/esbuild   0.27.7
node_modules/fsevents  2.3.3
```

The root lock has one exact manifest mismatch:

```text
package.json:      top-sites = "1.1.225"
package-lock.json: top-sites = "^1.1.225"
```

The lock digest is
`9375cb2ff84091a99fc55c167fe1cef040f5fa485ba0e890afdbe830fb97825f`.
The mismatch prevents treating the committed lock as the exact lock for the
source manifest, even though npm may proceed with an install.

The full development install was probed with the required offline command:

```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

It failed closed with `ENOTCACHED` for
`https://registry.npmjs.org/zod/-/zod-3.23.8.tgz`. A separate online probe
installed 225 packages, but that result does not establish offline closure.
No npm cache, tarball bundle, or dependency artifact was copied into this
task directory.

A temporary script-free, runtime-only adaptation (zero runtime dependency
roots) generated a one-entry npm 10.9.8 v3 lock and completed
`npm ci --offline` against an empty cache. That is feasibility evidence for a
future narrowed package, not evidence that the exact source package, build
toolchain, or verifier closure is ready. The temporary adaptation is not part
of this repository.

## Lifecycle and package validator

The exact manifest contains these scripts:

```text
bench, build, format, prepare, prepublishOnly, size, specs, test
```

The `files` allowlist only publishes `dist/`, so a candidate package requires
the generated build output. The packed manifest still contains the `scripts`
object. Running the repository's package safety validator against the local
packed artifact returned exit code `71`, the expected rejection for a package
manifest containing `scripts` (the validator also rejects workspaces,
`gypfile`, and `binary`).

This is a packaging-policy blocker, not a source behavior failure. Reopening
requires an explicit, reviewed candidate packaging adaptation that preserves
the ESM export and generated artifact identity while disabling arbitrary
lifecycle execution.

## Test evidence

The exact upstream suite is Vitest/TypeScript, not the production
`node:test` report contract. The full source command was run after a
disposable online install:

```text
npm test
```

It completed with four test files and `63740 passed`, with no failed or pending
tests. The report also recorded 98.2% statement coverage and 96.82% branch
coverage for `src/index.ts`.

Three independent Vitest JSON observations had the same result and normalized
leaf hash:

```text
total:   63740
passed:  63740
failed:  0
pending: 0
leaf hash: 74ac3cd981d4879d3b58d74e045ad6aa10d6c154204f1e75110543ef49891f2d
```

The stable source observation is useful behavior evidence, but it is not a
frozen production denominator. The suite includes generated `it.each` leaves,
snapshots, callbacks, Buffer-based test values, and Date values. No private
tests, structured verifier report, collection artifact, Oracle run, empty
control, stub control, forgery control, or offline verifier control exists in
this task-local directory.

## Reopen conditions

Reopen only after all of the following are versioned and reviewed:

1. An immutable Node 22/npm 10.9.8 environment lock with base image digest,
   architecture, libc, and build commands.
2. A manifest-consistent npm v3 lock and content-addressed offline closure
   for the exact build/runtime boundary, with platform and lifecycle policy
   checked.
3. A deterministic generated `dist/` artifact policy that does not expose
   candidate-controlled lifecycle scripts or unreviewed build inputs.
4. A cookie-specific child adapter and private `node:test` bundle defining
   JSON-safe input/output, Date/error projections, and the frozen denominator.
5. Three valid stable Oracle runs followed by empty, stub, forgery,
   installation-failure/hang, and offline controls.

Until then, this candidate remains `blocked` and must not be compiled,
published, or included in a benchmark score.

## Validation commands

The evidence above came from these disposable probes; none writes a task
artifact outside the directory named in this file:

```text
git -C /tmp/nl2repo-cookie-source rev-parse HEAD
git -C /tmp/nl2repo-cookie-source rev-parse HEAD^{tree}
git -C /tmp/nl2repo-cookie-source submodule status
git archive --format=tar HEAD (repeated three times and byte-compared)
sha256sum LICENSE package.json package-lock.json
node --version
npm --version
node --check dist/index.js
node --input-type=module (ESM namespace/export and JSON probes)
npm ci --offline --ignore-scripts --no-audit --no-fund (expected ENOTCACHED)
npm ci --ignore-scripts --no-audit --no-fund (online source probe)
npm run build (repeated and generated-byte compared)
npm test
vitest run . --reporter=json (three stable source observations)
node src/nl2repobench/verification/node/validate-package.mjs /tmp/cookie-2.0.1.tgz (expected exit 71)
```

No Docker, Harbor compilation, hidden-test materialization, Oracle, negative
control, shared catalog/index edit, or secret-bearing command was used.

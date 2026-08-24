# `jsonrepair` static Node v2 authoring audit

**Status: inventoried development evidence; the root string API is feasible,
but packaging and publication remain blocked.** This record covers only the
exact candidate revision and a proposed `jsonrepair(text) -> string` score
surface. It is not a Harbor task, a frozen specification, an offline
dependency artifact, or a publication approval.

No upstream test bytes, private tests, command plan, npm cache, generated
package, Dockerfile, verifier, Oracle solution/result, reward, credential, or
shared catalog edit is stored in this directory. Source and public release
probes were temporary and stayed outside the repository.

## Immutable source and license evidence

- Package: `jsonrepair`.
- Upstream: `https://github.com/josdejong/jsonrepair`.
- Requested and resolved revision:
  `4a80ed87fb1155db064945bc2aa4f6b4f4e89c27`.
- Commit tree: `45479b3cb98b4bcd5628c4d9bce3e3e7c9d4bf6f`.
- Parent: `b3bbf58249bfbc88ddec03aa33a868eaa50a8390`.
- Commit subject/date: `chore(release): 3.15.0`,
  `2026-07-03T19:43:47+02:00`.
- The detached checkout had no submodules and remained clean after inspection.
- The tree has 50 tracked files occupying 550,117 bytes. Repeated
  `git archive --format=tar HEAD` output was 604,160 bytes with SHA-256
  `b4245dabfaca974f251eca04bfe5f0d03c4886f2b30540e76395f3173af965c1`.
  Three independent archive streams produced the same digest.

License evidence is internally consistent:

- `package.json` declares `ISC`.
- `LICENSE.md` contains the ISC license and attributes Jos de Jong for
  2020-2026. It is 740 bytes, Git blob
  `91c70a1c578bcf47ec4abd987b7a16713814a78b`, with SHA-256
  `fd50f5abb7eeb614c8d1293b9f239a5238d7536e3a9a9a8929a082c82d12b3fd`.
- `package.json` is 2,978 bytes, Git blob
  `82fc1c2d1d179774fc28dc9cc6e472bdcb5efe09`, with SHA-256
  `9e366a13dddb4ff27a97135c862c6cdbe2791e1f467d423f0c0512f81c1439ba`.
- `package-lock.json` is 378,346 bytes, Git blob
  `04d16bebda965f2a39d030e635b97f57b5e1a232`, with SHA-256
  `f8737aac4e66a028610c487c39b63f19201b777990c5f0cc9b35a4af4794dfb2`.

These are provenance observations only. No source archive or upstream source
file was copied into this task-local record.

## Package and public API inventory

The locked manifest is `jsonrepair` version `3.15.0` with `type: module`. It
has no `dependencies`, `optionalDependencies`, or `peerDependencies`; all 20
declared dependencies are exact-version development dependencies. The
manifest has no `engines` constraint, so Node `22.23.1` and npm `10.9.8` are
task-level locks rather than upstream compatibility claims.

The package defines these conditional exports:

```text
.         import  -> ./lib/esm/index.js
.         require -> ./lib/cjs/index.js
.         types   -> ./lib/types/index.d.ts
./stream  import  -> ./lib/esm/stream.js
./stream  require -> ./lib/cjs/stream.js
./stream  types   -> ./lib/types/stream.d.ts
```

It also declares `main: lib/cjs/index.js`, `module: lib/esm/index.js`,
`browser: lib/umd/jsonrepair.min.js`, `types: lib/types/index.d.ts`, and the
`jsonrepair` CLI at `bin/cli.js`.

The root source entry exports two named bindings:

```text
jsonrepair(text: string) -> string
JSONRepairError           -> Error subclass with a numeric position field
```

There is no default root export. Temporary probes of the exact public release
showed that both `require("jsonrepair")` and `import("jsonrepair")` expose
`["JSONRepairError", "jsonrepair"]`, and that `jsonrepair` is callable under
both conditions. The scored API must select the named `jsonrepair` function;
it must not assume a default export or invoke the error class.

The regular source graph is only four local TypeScript files:

```text
src/index.ts
src/regular/jsonrepair.ts
src/utils/JSONRepairError.ts
src/utils/stringUtils.ts
```

Those files total 35,267 bytes and 1,281 physical lines. The graph has no
third-party import, Node builtin import, filesystem, network, subprocess,
loader, native addon, or mutable global state. This is the basis for retaining
the root function as a narrow Node v2 candidate.

The `./stream` subpath is materially different. It returns a Node `Transform`,
accepts chunk/buffer options, and imports `node:stream`. The CLI adds
filesystem, process-stream, overwrite, and shell-facing behavior. Stream,
CLI, UMD/browser, and direct error-class surfaces are outside this pilot.

## Generated build and release artifact evidence

No `lib/` file is tracked at the locked revision; `lib` is explicitly ignored
by `.gitignore`. Every package export target is therefore absent from the
source tree. The exact checkout cannot be treated as an installable package
without generating or otherwise obtaining release outputs.

The build pipeline is broad:

- `build:esm` uses Babel to compile TypeScript into `lib/esm` with source maps;
- `build:cjs` uses a separate Babel configuration and copies a nested
  `type: commonjs` manifest into `lib/cjs`;
- `build:umd` and `build:umd:min` use Rollup and UglifyJS;
- `build:types` uses TypeScript to emit declarations; and
- `build:validate` runs integration tests after the outputs exist.

Registry metadata for public `jsonrepair@3.15.0` records `gitHead` equal to
the requested revision. Its package archive has:

```text
SHA-1             03b4c15f313f0a6e6a1ccb66b6deeeb859e6f0c8
SHA-512 integrity sha512-wy8OTjwsJwQRnQJkKnMJJ9vcytRdBPAgIF/Hy6+s1dAj42BHMKiyL8JzEieIl3JY7idt8eyHwBWTO8mh/+mtwA==
archive bytes     113,286
files             70
expanded bytes    583,060
```

The archive's `package.json` is byte-identical to the source manifest. Its
generated layout contains 21 CJS files (217,754 bytes), 20 ESM files (212,980
bytes), five UMD files (122,442 bytes), and 20 declaration files (13,342
bytes). Representative generated SHA-256 values are:

```text
lib/cjs/index.js               1ced11eaae74715eaf6f0de41371f3a8daa255a591a57de5012edebb42f0770e
lib/esm/index.js               523d175b61d8517fd3ba90cd2f065c6ecd45f4c95ea7ac706a9d87ccaceb7faf
lib/umd/jsonrepair.js          484e1f24229f7aa130f0a84af5c220af6daaccea7537e284997f41732eb130ce
lib/umd/jsonrepair.min.js      ab265748396ce8e1f02f0222424129e949e37dd95de6156a38c7e2bf18ea1aee
lib/types/index.d.ts           e28233f3376849a7323ea6b55f716ac1071670e105e9e029d217e5dd164ce2e1
```

Direct CJS and ESM probes produced identical observations for an unquoted
object key/string, a truncated array, a fenced JSON block, a Python boolean,
and an empty-input error. This proves the published conditional exports are
usable and tied by registry metadata to the exact commit. It does not prove a
reproducible source build: no dependency install or build was run, and no
generated output is retained here. A later artifact stage must decide whether
and how the exact release output becomes reviewed Oracle provenance.

## Committed npm lock analysis

The committed lock is a manifest-aligned npm v3 development lock:

- top-level and root package metadata both say `jsonrepair` `3.15.0`;
- it contains 729 `packages` entries including the root, or 728 non-root
  entries;
- all 728 non-root entries are marked development-only;
- all 728 have `sha512-` integrity and HTTP(S) registry resolution;
- no entry is a git/file/workspace/link source, and all paths are under
  `node_modules/`;
- 73 entries are optional, 59 have OS constraints, 59 have CPU constraints,
  and six have libc constraints; and
- `node_modules/fsevents` declares an install script.

Representative platform packages include Biome, Rolldown, Rollup, Lightning
CSS, and `fsevents` binaries for multiple operating systems and architectures.
The repository's Node v2 dependency validator rejects platform fields and
install-script-bearing entries, so the committed development lock is not an
acceptable offline candidate-runtime closure.

The root function has zero runtime dependency roots. A future task can in
principle use a standalone root-only v3 runtime lock and empty npm cache, but
that closure must be generated under exact npm `10.9.8`, content-addressed,
reviewed, and stored through the approved private artifact path. This audit
did not generate a replacement lock, hydrate a cache, or run `npm ci`.

## Vitest and integration test inventory

The upstream framework is Vitest, not the required private `node:test`
framework. Static source inspection found the following leaf shape:

| Source area | Textual declarations | Expanded leaf shape |
| --- | ---: | ---: |
| `src/index.test.ts` | 79 | 157 |
| input/output buffer tests | 16 | 16 |
| streaming core/transform tests | 6 | 6 |
| `test-lib/lib.test.js` | 6 | 6 |
| `test-lib/cli.test.js` | 5 | 5 |
| **Total build-and-test shape** | **112** | **190** |

The difference comes from 78 declarations in `src/index.test.ts` nested under
`describe.each` for two implementations (regular and streaming), plus one
standalone streaming chunk test. The finite `test:it` source run therefore
has a static shape of 179 leaves. `build:validate` adds 11 post-build
integration leaves. No active skip, todo, failing, or only marker was found.

These numbers are static inventory, not executed collection, not a frozen
denominator, and not Oracle evidence. No dependency install, Vitest command,
build, or upstream suite was run in this static lane.

The source tests call TypeScript internals directly. Integration tests use
`node:child_process`, shell command strings, filesystem reads/writes and
replacement, streams, generated ESM/CJS/UMD outputs, and a CLI document larger
than 64 KiB. They cannot be copied unchanged into the trusted verifier or
counted as a Node v2 denominator. A later private `node:test` adapter must
select root-string assertions traceable to a public contract and call the
candidate only through the child boundary.

## Lifecycle and candidate package policy

The manifest contains 21 script keys. Its actual npm lifecycle hook is
`prepare: husky`; the remaining test, build, benchmark, formatting, and
release scripts are arbitrary development commands. The public release
retains the same script object even though it does not publish the development
source/toolchain.

The repository package validator rejects any candidate manifest containing a
`scripts` key. Running `validate-package.mjs` against the exact public release
archive exited 71 for this reason. Using `npm pack --ignore-scripts` prevents
execution but does not remove the forbidden metadata. Conversely, packing
the exact Git checkout with scripts ignored cannot produce usable root export
targets because the tracked tree has no `lib/` output.

A future task must explicitly require a clean candidate package with no
scripts, workspaces, registry configuration, native addons, loaders, or build
step. It must preserve the reviewed conditional exports and include runnable
package files before verifier installation. The unmodified upstream manifest,
development lock, and source tree cannot be silently reused as that package.

## JSON string-in/string-out subprocess boundary

The generic candidate child can call the narrow API with this request:

```json
{
  "package": "jsonrepair",
  "export": "jsonrepair",
  "args": ["{name: 'John'}"]
}
```

Against the exact public release, the current child returned:

```json
{"ok":true,"value":"{\"name\": \"John\"}"}
```

Empty input returned exit 1 with `error: candidate-call-failed`,
`exception_type: JSONRepairError`, and message
`Unexpected end of json string at position 0`. The generic projection omits
the error object's separate numeric `position` field.

The proposed task boundary is deliberately smaller than the complete npm
package:

**In scope**

- exactly one argument, a JavaScript/JSON string containing text to repair;
- a returned string containing the repaired JSON text, including the pinned
  whitespace and escaping behavior rather than only parsed-value equivalence;
- valid JSON passthrough and deterministic repairs for quoted/unquoted keys
  and strings, truncation, missing delimiters, comments, fenced blocks,
  Unicode, Python constants, newline-delimited values, and the other reviewed
  regular-function behaviors that fit the request/response limits; and
- normalized failures using exception type and message, unless a later
  reviewed adapter explicitly adds the numeric position field.

**Out of scope**

- `jsonrepair/stream`, `jsonrepairTransform`, Node streams, chunk/buffer
  configuration, backpressure, and internal buffer/core helpers;
- direct construction or identity checks of `JSONRepairError`;
- CLI arguments, stdin/stdout, files, overwrite behavior, shell redirection,
  and inputs above the child request limit;
- UMD/browser globals and PythonMonkey integration;
- `Buffer`, typed arrays, objects, arrays, numbers, booleans, `null`,
  callbacks, functions, classes, symbols, BigInts, cycles, and custom
  prototypes as the function argument; and
- arbitrary package/export names, loaders, paths, environment hooks, or
  candidate-owned reports.

The current child accepts requests up to 64 KiB, responses up to 256 KiB, and
up to 32 positional arguments. A task-specific adapter must narrow this to the
fixed package/export and exactly one string. The generic child tries CommonJS
first, so it exercises the CJS condition for this dual package. A later
separate-process check is required to prove the ESM export condition without
importing candidate code into the trusted test process.

## Decision and remaining gates

Retain `jsonrepair` as **development evidence for a root-function-only Node v2
task**. The API itself is a strong JSON subprocess fit, but this record does
not advance the task to `packaged`, `oracle-passed`, or `published`.

Before packaging:

1. Freeze the public specification to the named root `jsonrepair` function and
   explicit string/error/bounds behavior; exclude stream, CLI, browser, and
   class identity.
2. Define whether errors expose only type/message or also numeric position,
   and write every private assertion against that reviewed projection.
3. Produce a clean, no-scripts dual-export package and a standalone root-only
   v3 offline lock/cache artifact under npm `10.9.8`; do not reuse the
   development lock or registry archive as an implicit dependency bundle.
4. Add private adapter-owned `node:test` tests, an allowlisted command plan,
   automatic leaf collection, and independent CJS/ESM subprocess checks. Do
   not copy the Vitest suite or its fixtures into this public directory.
5. Establish reviewed exact-revision generated-output/Oracle provenance and
   then run the separate Node Oracle/control matrix in the authorized stage.

No Docker, Harbor compile, Oracle/control trial, hidden/private artifact
materialization, npm install/cache command, shared dataset/index change, or
secret use occurred in this audit.

## Static commands and probes run

All repository writes were limited to this evidence file. Temporary source
and public release files were created under `/tmp` and removed or left outside
the worktree; npm was queried only for its local version and was not used to
install, pack, or cache packages.

```text
git clone --filter=blob:none --no-checkout <upstream> /tmp/nl2repo-jsonrepair-source
git -C /tmp/nl2repo-jsonrepair-source checkout --detach 4a80ed87fb1155db064945bc2aa4f6b4f4e89c27
git show/status/submodule/ls-files/ls-tree/archive <read-only source inspection>
sha256sum/stat/git hash-object <source metadata and license files>
node <structured package-lock and manifest scans>
rg/find/wc <source, export, test, build, and lifecycle inventory>
node --version                     # v22.23.1
npm --version                      # 10.9.8
curl -o /tmp/... <public npm registry metadata and jsonrepair-3.15.0.tgz>
sha1sum/openssl/tar/sha256sum <temporary public release validation>
node validate-package.mjs <temporary public release tarball>  # exit 71
node / node --input-type=module <temporary CJS and ESM export probes>
node candidate_runner.mjs <bounded success and error requests>
git diff --check
```

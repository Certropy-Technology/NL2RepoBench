# Chalk Candidate Audit

Status: **blocked**. This task-local directory records evidence for an
evidence-first Node/npm candidate. It is not a Harbor bundle, private test
package, Oracle, dependency cache, verifier, or publication approval. The only
durable write root authorized for this audit is `catalog/tasks/chalk/`.

## Decision And Scope

The exact source and package contract are suitable for a bounded Node ESM
authoring pilot. The source has no runtime dependencies and its package entry
point is already JavaScript ESM. The official test suite, however, is an AVA
development suite with range-based dependencies and no committed npm lock.
The proposed JSONL boundary narrows formatting to explicit color levels and
JSON values so host terminal state does not become part of ordinary scoring.

Keep the task at lifecycle status `blocked`. The probes below establish source,
license, exports, source-only size, official behavior, and the unresolved
dependency/environment gaps. They do not establish a production test bundle,
frozen `node:test` denominator, separate verifier, Oracle, or controls.

## Source Lock

- Upstream: `https://github.com/chalk/chalk`.
- Resolution probe: `git ls-remote` returned
  `661317e6f91fe7c90306c2c48ea9354562ee9146` for `HEAD` and
  `refs/heads/main`. The revision was fetched and checked out detached; the
  branch name is provenance only.
- Commit subject: `6.0.0`.
- Commit timestamp: `2026-07-26T16:50:53+02:00`.
- Commit tree: `ff76edd5a4d5f70bc0a83259aec26686a43c27f7`.
- The detached tree has 35 tracked files and no tracked `.gitmodules` file.
- The archive command was:

  ```text
  git archive --format=tar HEAD
  ```

  Three independent archive streams were each `460800` bytes with SHA-256
  `0b041959f2c9516006566ed834208aaccf765e8d20f1b39efd8727e2d3844d80`.

No upstream source or test bytes are copied into this task directory.

## License Evidence

The frozen `package.json` declares `"license": "MIT"`, and the root `license`
file is the standard MIT grant.

- License path: `license`.
- License size: `1117` bytes.
- License Git blob:
  `fa7ceba3eb4a9657a9db7f3ffca4e4e97a9019de`.
- License SHA-256:
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- `package.json` Git blob:
  `cf57b6072000c48eef7fe432519e1c82b4ee3f56`.
- `package.json` SHA-256:
  `5a853fc6dc0c529bc126f97645989e9d60d06a2e9b20f66a6b48b0e8ef9da3ef`.

The declaration and license text agree. License review for a future private
development dependency closure remains separate and is not claimed here.

## Package And ESM Export Evidence

The frozen package metadata reports:

- name `chalk`, version `6.0.0`;
- `type: module`;
- root `exports` with `types: ./source/index.d.ts` and
  `default: ./source/index.js`;
- internal `#ansi-styles` and `#supports-color` imports;
- `files: ["source"]`, `sideEffects: false`, and Node engine `>=22`;
- no `dependencies` field entries;
- eleven range-based development dependencies for AVA, c8, XO, TypeScript,
  execa, and related tooling; and
- `.npmrc` containing `package-lock=false`.

An isolated Node `22.23.1` ESM probe with `TERM=dumb`, `LC_ALL=C.UTF-8`, and
`FORCE_COLOR=0` imported the package by its self-reference. The runtime
namespace exposed these value keys (including the compatibility aliases):

```text
Chalk backgroundColorNames backgroundColors chalkStderr colorNames colors
default foregroundColorNames foregroundColors modifierNames modifiers
supportsColor supportsColorStderr underlineColorNames
```

The default and `Chalk` values were functions, and the default function was
callable. The same default identity was reached through `./source/index.js`.
Node 22's synchronous ESM `require` interop also returned an ESM namespace with
`__esModule`; this is incidental runtime compatibility, not a requirement for
the task, which scores the ESM import boundary.

The package export probe produced these deterministic explicit-level results:

```json
{
  "level_0_red": "plain",
  "level_1_red": "\\u001b[31mplain\\u001b[39m",
  "level_3_rgb": "\\u001b[38;2;255;0;0mplain\\u001b[39m",
  "level_1_multiline": "\\u001b[31ma\\u001b[39m\\n\\u001b[31mb\\u001b[39m"
}
```

`npm pack --ignore-scripts --dry-run --json` listed 12 files: `license`,
`package.json`, `readme.md`, and the nine files below `source/`. The reported
unpacked size was `56029` bytes. This is packaging evidence only; no tarball is
retained.

## Source-Only Size

The source-only measurement excludes tests, docs, examples, media, package
metadata, and lockfiles:

| scope | files | physical LOC |
| --- | ---: | ---: |
| runtime JavaScript under `source/` | 5 | 793 |
| core runtime JavaScript excluding vendored files | 2 | 294 |
| vendored runtime JavaScript | 3 | 499 |
| TypeScript declarations under `source/` | 4 | 792 |
| all tracked `source/` files | 9 | 1585 |

The runtime JavaScript files are `source/index.js`, `source/utilities.js`,
`source/vendor/ansi-styles/index.js`, `source/vendor/supports-color/index.js`,
and `source/vendor/supports-color/browser.js`. This is a physical line count,
not a complexity or generated-code estimate. The eight tracked test files
contain 508 physical lines and are excluded from the source-only total.

## Official Test Evidence

The frozen official command is the package script:

```text
npm test
```

It runs `xo && c8 ava && tsc --noEmit --types node source/index.d.ts`.
Static inventory found 58 AVA declarations in six test modules:

| module | declarations |
| --- | ---: |
| `test/chalk.js` | 30 |
| `test/force-color.js` | 13 |
| `test/instance.js` | 7 |
| `test/level.js` | 4 |
| `test/no-color-support.js` | 1 |
| `test/visible.js` | 3 |
| **total** | **58** |

`test/_fixture.js` and `test/_force-color-fixture.js` are subprocess fixtures,
not AVA leaves. Official test coverage includes base calls, argument coercion,
style nesting, modifiers, foreground/background/underline colors, RGB/hex/ANSI
256 conversion, level propagation, visible output, CRLF handling, and isolated
`FORCE_COLOR`/argv detection.

With a disposable generated lock and network-populated npm cache, Node
`22.23.1` and npm `10.9.8` ran the unmodified command successfully:

```text
58 tests passed
```

The official command therefore has a valid development baseline. This does not
freeze a production `node:test` report or private adapter denominator. The
upstream AVA test bytes remain outside this repository.

## npm Lock And Offline Closure

The exact source contains no `package-lock.json` or `npm-shrinkwrap.json`, and
its `.npmrc` disables package-lock creation. The package itself declares no
runtime dependency roots, but the official development command requires its
range-based devDependencies.

For evidence only, npm `10.9.8` generated a disposable v3 lock using
`npm install --package-lock-only --ignore-scripts --no-audit --no-fund`. The
generated lock had:

- 522 non-root package entries;
- integrity metadata on all 522 entries;
- 28 optional platform entries;
- one `hasInstallScript` entry, `unrs-resolver@1.12.2`; and
- SHA-256 `a683665bbfbd421757de84bc73dd721b31e73bd93744733c763e88cb3ea8ca1b`.

The lock file was approximately 240 KiB and was deleted after the probe. An
empty-cache `npm ci --offline --ignore-scripts --no-audit --no-fund` failed
closed with `ENOTCACHED` for `zwitch-2.0.4.tgz`. After a temporary
network-backed install populated a disposable cache, the same offline command
completed and the cache occupied approximately 242 MiB; that cache and all
installed `node_modules` were deleted. This demonstrates a diagnostic npm
path, not a reviewed offline closure.

The candidate remains blocked until an authoring stage creates a
content-addressed npm v3 lock/cache artifact, reviews every integrity and
license, handles or rejects platform packages and install-script metadata, and
proves the exact verifier installation with no network. No cache or generated
lock is committed here.

## Terminal And Color Determinism

`source/vendor/supports-color/index.js` reads environment variables and
`process.argv` at module load, calls `tty.isatty(1)`/`tty.isatty(2)`, and has
platform-specific branches. Therefore importing the module before fixing the
environment makes the result host-dependent. Ordinary formatting must use an
explicit `new Chalk({level})`; capability detection belongs to an isolated
child launch.

Bounded probes used pipe stdout/stderr and no network. The following isolated
results were observed from `test/_force-color-fixture.js`:

| environment/argv | observed level |
| --- | ---: |
| `TERM=dumb`, no `FORCE_COLOR` | `0` |
| `TERM=dumb`, `FORCE_COLOR=0` | `0` |
| `TERM=dumb`, `FORCE_COLOR=1` | `1` |
| `TERM=xterm-256color`, `FORCE_COLOR=1`, argv `--color=256` | `2` |
| no `TERM`, `FORCE_COLOR=true`, `COLORTERM=truecolor` | `3` |

Three repeated explicit-level JSON formatting calls produced the same value:

```text
{"text":"\\u001b[31m\\u001b[1mhello 42 true  a,b\\u001b[22m\\u001b[39m"}
```

The double space before `a,b` is the specified result of joining the array's
string conversion as one argument after the preceding `null` argument. The
boundary records the required environment, ANSI policy, and forbidden output
in `candidate-boundary.json`. It preserves CRLF because Chalk's official test
requires styled CRLF to remain CRLF; it does not normalize library text to LF.

## JSON Boundary And Production Gate

The proposed child-side protocol accepts only bounded JSON values and returns
strings, arrays, objects, or the boolean `false`. It never transports a Chalk
function, builder, stream, callback, TTY, symbol, BigInt, or cyclic value.
Error responses contain only an ID, error type, and bounded message. The
trusted verifier must keep private tests and reports outside the candidate
workspace and must not parse candidate-written reward files.

The following production gates are unresolved:

1. no immutable Node 22 image and OS digest is recorded for this candidate;
2. no reviewed content-addressed npm v3 lock/cache closure exists;
3. no private `node:test` adapter, command plan, stable test IDs, or frozen
   structured collection report exists;
4. no separate verifier, Oracle, empty, stub, forgery, lifecycle, loader, hang,
   or offline control artifacts exist; and
5. the AVA 58-test development baseline has not been converted into a
   publication-approved metric denominator.

Do not publish, add a dataset entry, or claim Harbor parity from this audit.
Reopen only after those artifacts are reviewed and three independent valid
Oracle runs meet the repository's minimum gate.

## Validation Record

Completed read-only or disposable checks:

- exact full-SHA resolution, detached checkout, tree and tracked inventory;
- repeated source archive hashing and license/package/source file hashing;
- package metadata, ESM self-import, named export, explicit-level formatting,
  package dry-run, and JSON-safe repeated-output probes;
- source-only physical LOC inventory and official test declaration inventory;
- disposable network-backed official `npm test` baseline;
- disposable generated npm v3 lock metadata, empty-cache offline failure, and
  populated-cache offline install; and
- cleanup verification showing the disposable checkout has no generated lock,
  cache, `node_modules`, or working-tree changes.

Not run by design: Docker, Harbor compilation, private test authoring, Oracle,
negative controls, or publication. No private bytes, secrets, large caches,
Harbor files, or shared catalog files were added.

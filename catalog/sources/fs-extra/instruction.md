# Project Description

Build `fs-extra`, a CommonJS-first Node.js filesystem utility package that
combines promise-capable `fs` compatibility methods with deterministic helpers
for recursive copy, move, removal, directory creation, file/link creation, and
JSON files. The implementation starts from an empty workspace and must be safe
to install and execute without network access.

The scored behavioral surface is the documented extra-method API at the
package root and at `fs-extra/esm`. CommonJS compatibility with Node's `fs`
module is checked at the export-shape level plus representative promise and
callback calls; reimplementing Node's own full filesystem test suite is outside
the task.

## Natural Language Instruction

Create the `fs-extra` project from an empty `workspace/`. Implement the
filesystem extension methods and the selected CommonJS `fs` compatibility
surface described below. Preserve promise and callback forms, synchronous
variants, alias families, recursive tree behavior, symlink identity, JSON
formatting, and deterministic error propagation. The package must work from an
installed target rather than relying on the source checkout.

The public package has two entry paths: `require('fs-extra')` exposes the
CommonJS-compatible object and `import {copy} from 'fs-extra/esm'` exposes only
the extra methods. No CLI, watcher, browser integration, native addon, or
runtime network access is required.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux `amd64`, and a CommonJS package root.
- `package.json` must name the package `fs-extra`, use version `11.4.0`, set
  `main` to `./lib/index.js`, require Node `>=14.14`, and export exactly:

  ```json
  {
    ".": "./lib/index.js",
    "./esm": "./lib/esm.mjs"
  }
  ```

- Commit a `package-lock.json` with `lockfileVersion: 3`. The verifier installs
  the candidate with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- A dependency-free implementation is valid. If dependencies are used, the
  only available runtime packages are exact `graceful-fs@4.2.11`,
  `jsonfile@6.2.1`, and `universalify@2.0.1`; the lockfile must remain a closed,
  integrity-pinned npm v3 closure.
- Do not use npm workspaces, native addons, custom loaders, registry settings,
  lifecycle scripts, generated downloads, subprocesses, or network access.
  The package has no CLI.
- The CommonJS root must expose the documented extra methods below and the
  ordinary `fs` compatibility surface. Selected compatibility members include
  `access`, `appendFile`, `chmod`, `close`, `copyFile`, `cp`, `lstat`, `mkdir`,
  `open`, `read`, `readFile`, `readdir`, `realpath`, `rename`, `rm`, `stat`,
  `unlink`, `write`, `writeFile`, `writev`, `createReadStream`,
  `createWriteStream`, `constants`, and `promises`. Asynchronous CommonJS
  methods support promises when their callback is omitted.
- `fs-extra/esm` exposes only the extra methods as named exports and as one
  `default` object; it does not re-export Node's `fs` methods.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── lib/
│   ├── index.js
│   ├── copy/
│   ├── ensure/
│   ├── fs/
│   ├── json/
│   ├── mkdirs/
│   ├── move/
│   └── esm.mjs
└── README.md
```

`lib/index.js` is the CommonJS root and `lib/esm.mjs` is the named ESM
subpath. The implementation may split methods into the listed public-support
directories, but every documented root export must resolve from one of these
entry points. Do not place test, verifier, cache, or evaluator files in the
generated workspace.

# API Usage Guide

Use the package through these public entry paths:

```js
const fs = require('fs-extra');
const {copy, ensureDir, readJson} = require('fs-extra/esm');
import fsExtra from 'fs-extra';
```

All path arguments use Node `PathLike` values. Async methods return promises
when their callback is omitted and call a Node-style callback when supplied;
sync methods return directly or throw the original filesystem error.

All path arguments accept the path forms supported by Node's filesystem APIs.
Unless explicitly described otherwise, asynchronous methods return
`Promise<void>` when no callback is supplied and also accept an optional final
Node-style callback. Synchronous variants return `undefined` on success.

## Copy

```ts
function copy(
  src: PathLike,
  dest: PathLike,
  options?: CopyOptions | CopyFilter,
  callback?: (error?: Error) => void,
): Promise<void> | void;

function copySync(
  src: PathLike,
  dest: PathLike,
  options?: CopyOptions | CopyFilter,
): void;
```

Copy files, directories, and symbolic links recursively, creating destination
parents. `CopyOptions` supports:

- `overwrite` (or legacy `clobber`), default `true`;
- `errorOnExist`, default `false`, which throws/rejects when the destination
  exists and overwrite is disabled;
- `dereference`, default `false`, which follows symbolic links when true;
- `preserveTimestamps`, default `false`;
- `filter(src, dest)`, a boolean-returning callback; asynchronous `copy` also
  accepts a promise-returning filter.

With overwrite disabled and `errorOnExist` false, an existing destination file
is left unchanged. Directory modes, file modes, and symlink identity are
preserved where the platform permits it. Copying a path onto itself or copying
a directory into its own descendant rejects/throws instead of recursing.

```js
const fs = require('fs-extra');
await fs.copy('source', 'archive/source', {
  filter: source => !source.endsWith('.tmp'),
  preserveTimestamps: true,
});
```

## Empty and remove

```ts
function emptyDir(path: PathLike, callback?: Callback): Promise<void> | void;
function emptyDirSync(path: PathLike): void;
function remove(path: PathLike, callback?: Callback): Promise<void> | void;
function removeSync(path: PathLike): void;
```

`emptyDir` removes every child recursively while retaining the directory. If
the directory does not exist, it is created. `emptydir`/`emptydirSync` are
aliases. `remove` recursively deletes a file, link, or directory and succeeds
when the target is already absent.

## Directories and files

```ts
function ensureDir(
  path: PathLike,
  modeOrOptions?: number | {mode?: number},
  callback?: Callback,
): Promise<string | undefined> | void;
function ensureDirSync(
  path: PathLike,
  modeOrOptions?: number | {mode?: number},
): string | undefined;

function ensureFile(path: PathLike, callback?: Callback): Promise<void> | void;
function ensureFileSync(path: PathLike): void;
```

`ensureDir` recursively creates missing parents and succeeds if the target is
already a directory. Promise and synchronous forms return the first directory
path created, or `undefined` when no directory needed creation. Callback forms
receive that path as their optional result. `mkdirs` and `mkdirp`, and their
`Sync` forms, are aliases.
`ensureFile` creates missing parents and an empty file, but does not truncate an
existing file. `createFile` and `createFileSync` are aliases. Ordinary Node
filesystem errors such as `ENOTDIR` propagate when an intermediate component
is not a directory.

## Hard links and symbolic links

```ts
function ensureLink(src: PathLike, dest: PathLike, callback?: Callback): Promise<void> | void;
function ensureLinkSync(src: PathLike, dest: PathLike): void;
function ensureSymlink(
  src: PathLike,
  dest: PathLike,
  type?: 'file' | 'dir' | 'junction',
  callback?: Callback,
): Promise<void> | void;
function ensureSymlinkSync(
  src: PathLike,
  dest: PathLike,
  type?: 'file' | 'dir' | 'junction',
): void;
```

These methods create destination parents. They are idempotent when the existing
destination already refers to the same source, but propagate filesystem errors
for a missing source or conflicting destination. `createLink`,
`createLinkSync`, `createSymlink`, and `createSymlinkSync` are aliases. Relative
symlink targets retain normal platform-relative symlink semantics.

## Move

```ts
function move(
  src: PathLike,
  dest: PathLike,
  options?: {overwrite?: boolean; clobber?: boolean},
  callback?: Callback,
): Promise<void> | void;
function moveSync(
  src: PathLike,
  dest: PathLike,
  options?: {overwrite?: boolean; clobber?: boolean},
): void;
```

Move a file or directory, creating destination parents. Overwrite defaults to
`false`; an existing destination therefore rejects/throws with a destination
conflict unless `overwrite` or `clobber` is true. A cross-device rename falls
back to copy-with-timestamps followed by removal. Identical paths and moving a
directory into its descendant are rejected.

## Output files and path existence

```ts
function outputFile(
  file: PathLike,
  data: string | Uint8Array,
  options?: string | object,
  callback?: Callback,
): Promise<void> | void;
function outputFileSync(file: PathLike, data: string | Uint8Array, options?: string | object): void;
function pathExists(path: PathLike, callback?: (error: Error | null, exists: boolean) => void): Promise<boolean> | void;
function pathExistsSync(path: PathLike): boolean;
```

`outputFile` creates missing parent directories and otherwise follows
`writeFile` overwrite and encoding behavior. `pathExists` reports `false` for
an absent path rather than rejecting for `ENOENT`.

## JSON files

```ts
function readJson(file: PathLike, options?: JsonReadOptions, callback?: Callback): Promise<unknown> | void;
function readJsonSync(file: PathLike, options?: JsonReadOptions): unknown;
function writeJson(file: PathLike, value: unknown, options?: JsonWriteOptions, callback?: Callback): Promise<void> | void;
function writeJsonSync(file: PathLike, value: unknown, options?: JsonWriteOptions): void;
function outputJson(file: PathLike, value: unknown, options?: JsonWriteOptions, callback?: Callback): Promise<void> | void;
function outputJsonSync(file: PathLike, value: unknown, options?: JsonWriteOptions): void;
```

`readJson` parses UTF-8 JSON (including a leading byte-order mark). Invalid JSON
rejects/throws a `SyntaxError` by default; `{throws: false}` returns `null`.
Write options include `spaces` for indentation, `EOL` for line endings, and the
ordinary JSON `replacer`. The output ends with the selected `EOL`. `writeJson`
does not create parents; `outputJson` does. Capitalized `JSON` spellings are
aliases for every JSON method.

# Implementation Notes

- Filesystem operations are stateful but must be deterministic for a fixed
  starting tree. Preserve directory entry content, file bytes, JSON property
  order, and filter decisions; do not use clock or random values to decide
  behavior.
- Promise results and optional callbacks must settle exactly once. Callback
  forms return `undefined`; promise forms reject with the original filesystem
  or parse error rather than swallowing failures.
- Do not follow symlinks unless an API option explicitly requests it. Recursive
  operations must reject source/destination relationships that could overwrite
  or recurse into the source.
- The verifier creates bounded temporary trees inside a UID-isolated child and
  observes only JSON-safe projections of filesystem state. No candidate code is
  imported into the trusted verifier process.

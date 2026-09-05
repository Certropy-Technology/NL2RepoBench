# Build `chokidar`

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

## Project Description

Create an installable ESM npm package named `chokidar`, version `5.0.0`, from an
empty workspace. It watches files and directories and normalizes native
filesystem notifications into stable `add`, `addDir`, `change`, `unlink`, and
`unlinkDir` events. The package must work without a network service or native
addon.

This is a repository-generation task. Implement the behavior with your own
source files; do not copy the reference repository or its tests.

## Natural Language Instruction

Create `chokidar` from an empty workspace. Implement local file and directory
watching, event normalization, filtering, traversal, and watcher lifecycle
behavior specified below.

## Supports or Environment Configuration

- Node.js `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- ESM package semantics with `"type": "module"`; the package root is imported
  with `import chokidar, {watch, FSWatcher} from 'chokidar'`.
- Root files `index.js`, `index.d.ts`, `handler.js`, and `handler.d.ts` must be
  published. The root export must provide the default object `{watch, FSWatcher}`
  and named `watch` and `FSWatcher` exports.
- Runtime dependency `readdirp` must be declared with an exact `5.0.0` version.
  Include an npm v3 `package-lock.json` and make installation work with:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use CommonJS-only entry points, lifecycle scripts, workspaces, glob
  expansion, native addons, loaders, registry configuration, or runtime network
  access. The documented filesystem paths are ordinary local paths.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
├── handler.js
└── handler.d.ts
```

## API Usage Guide

### `watch(paths, options?)`

`watch(paths: string | string[], options?: ChokidarOptions): FSWatcher` creates
  a watcher, starts asynchronously tracking the requested path or paths, and
  returns the watcher immediately. A path may name an existing or future file
  or directory. An array watches every path. Paths are not glob patterns.

`options` is optional. The defaults are `persistent: true`,
`ignoreInitial: false`, `followSymlinks: true`, `usePolling: false`,
`ignorePermissionErrors: false`, `alwaysStat: false`, and `atomic: true` for
the fs.watch backend. `cwd` makes emitted paths relative to that directory.
`depth` limits recursive directory traversal, where `0` watches the requested
directory and its immediate entries. `interval` and `binaryInterval` control
polling intervals. `awaitWriteFinish` may be `true` or an object containing
`stabilityThreshold` and `pollInterval`; it delays add/change notifications
until file size is stable. `atomic` may be `false`, `true`, or a delay in
milliseconds.

`ignored` may be a path string, regular expression, matcher function, matcher
object `{path, recursive?}`, or an array of those values. A matching path is
excluded from scanning and events. Matcher functions receive the normalized
path and may receive a filesystem `Stats` object on the second call.

### `FSWatcher`

`new FSWatcher(options?: ChokidarOptions): FSWatcher` creates an initially empty
watcher. The object is an EventEmitter and the following methods return the same
watcher for chaining:

- `add(paths: string | string[]): FSWatcher` begins watching one or more paths.
- `unwatch(paths: string | string[]): FSWatcher` stops watching those paths and
  ignores their descendants for this watcher.
- `getWatched(): Record<string, string[]>` returns watched directory paths
  mapped to sorted child names. Without `cwd`, keys are absolute; with `cwd`,
  keys are relative and the root key is `.`.

`close(): Promise<void>` removes filesystem listeners, clears pending work, and
  removes event listeners. Repeated calls while closing return the same Promise.
After close, filesystem changes do not produce more watcher events.

### Events

Listeners can subscribe with `.on(event, listener)`. `ready` fires once after
the initial scan. `add` and `addDir` describe discovered files and directories;
`change` describes file content or metadata changes; `unlink` and `unlinkDir`
describe removals. Their listener signature is `(path, stats?)`, where `stats`
is available for add/change events when stat information exists. `all` receives
`(eventName, path, stats?)` for ordinary file and directory events. `raw` is a
low-level backend observation and `error` receives an Error. Event paths are
normalized strings using `/` separators; with `cwd`, they are relative.

Initial scanning emits `addDir` for matching directories and `add` for matching
files before `ready`, unless `ignoreInitial` is true. Recursive scanning honors
`depth`, filters, and symlink policy. `followSymlinks: false` watches the link
itself rather than recursively following its target. A delete followed quickly
by an add at the same path may be normalized to `change` when `atomic` is
enabled.

## Implementation Notes

Keep the package deterministic and ESM-compatible. Preserve chainable watcher
methods, sorted `getWatched()` children, relative path behavior, and the
distinction between ordinary events and `ready`, `raw`, and `error`. Use only
local filesystem behavior; do not fetch the upstream project or dependencies
during candidate installation or verification. The private evaluator exercises
the JSON-serializable behavior of the API through a child process, so native
watcher handles and callbacks must remain inside the candidate process.

## Examples

```js
import {watch} from 'chokidar';
const watcher = watch('src', {ignoreInitial: true});
watcher.on('add', path => console.log(path));
await watcher.close();
```

## Error Handling and Boundary Conditions

`close()` is idempotent and stops later events. Invalid paths report ordinary
watcher errors; event paths use normalized separators and respect `cwd`,
filters, depth, and symlink options.

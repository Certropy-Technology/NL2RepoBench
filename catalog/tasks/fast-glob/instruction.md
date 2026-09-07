# Project Description

Build the pinned ESM `fast-glob` package from an empty `workspace/`. Implement
local filesystem globbing, asynchronous/synchronous/stream results, task
generation, dynamic-pattern detection, escaping, filtering, and ordering.

# Natural Language Instruction

Create the package and implement every public function and option documented in
the API guide below. Preserve returned path forms, pattern precedence, and
filesystem boundary behavior.

# Supports or Environment Configuration

- Use Node.js 24.19.0 and npm 11.17.0 with the exact ESM metadata and frozen
  offline dependency closure in `task.toml`.
- This library has no CLI or network behavior. Agent, candidate, verifier,
  Oracle, and controls run with no network access.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── out/
    ├── index.js
    ├── managers/
    ├── providers/
    └── utils/
```

# API Usage Guide

The detailed API Usage Guide below is authoritative for functions, options,
task shapes, streams, path results, and ordering.

# Implementation Notes

Resolve only caller-selected local filesystem paths and keep results
deterministic. Do not use network or hidden global state.

# Examples

```js
import fg from 'fast-glob';
await fg('src/**/*.js', {cwd: '/workspace'});
```

```js
fg.sync(['*.js'], {cwd: '/workspace'});
```

# Error Handling and Boundary Conditions

```js
await fg('missing/**/*.js', {cwd: '/workspace'});
```

```js
fg.isDynamicPattern('src/**/index.js');
```

# fast-glob

## Project Description

Build an npm package named `fast-glob` that resolves glob patterns against the
filesystem and returns the matching entry paths. The package is a library only:
it exposes no CLI and no network behaviour. Consumers pass one pattern or an
array of patterns plus an options object, and receive the matched paths either
asynchronously or synchronously.

## Supports

- Node.js `^22.13.0 || >=24`, running on Linux x86-64.
- The package must be an ES module: `package.json` must declare
  `"type": "module"` and `"main": "out/index.js"`, and the runtime JavaScript
  must live under `out/`.
- `package.json` must declare `"name": "fast-glob"` and `"version": "4.0.0"`.
- A `package-lock.json` with `"lockfileVersion": 3` must be committed and must
  resolve every dependency you declare.
- `package.json` must not declare any npm lifecycle hook (`preinstall`,
  `install`, `postinstall`, `prepare`, `prepublish`, `prepublishOnly`,
  `publish`, `postpublish`). The package is installed with
  `npm ci --offline --ignore-scripts` and packed with `npm pack`, so the
  published tree must already contain runnable JavaScript. No build step runs
  during installation.
- The package must contain no native addon, no `binding.gyp`, and no
  `prebuilds/` directory.
- You may depend only on these packages, which are available in the offline npm
  cache: `@nodelib/fs.stat`, `@nodelib/fs.walk`, `glob-parent`, `merge2`,
  `micromatch`. Node built-in modules are not dependencies.

## API Usage Guide

All entries below are named exports of the package root
(`import { glob } from "fast-glob"`). Every exported function listed here must be
directly callable from the package root.

### `glob(patterns, options?) => Promise<string[]>`

- `patterns`: a string, or an array of strings. Each element is a glob pattern.
  A pattern prefixed with `!` is a negative (exclusion) pattern.
- `options`: an optional options object (see Options).
- Returns a promise resolving to an array of matched entry paths as strings.
  Paths are relative to `options.cwd` and use `/` as the separator.
- Result order is not guaranteed; callers that need a stable order must sort.
- Rejects with a `TypeError` when a pattern is not a string.
- A `cwd` that does not exist yields an empty array rather than a rejection,
  regardless of `suppressErrors`.

### `globSync(patterns, options?) => string[]`

Synchronous counterpart of `glob`. Same inputs, same result contents and same
ordering guarantees. Throws a `TypeError` when a pattern is not a string.

### `globStream(patterns, options?) => ReadableStream`

Streaming counterpart of `glob`, emitting one matched entry at a time.

### `generateTasks(patterns, options?) => Task[]`

Returns the internal traversal plan without touching the filesystem. Each `Task`
is an object with:

- `base` (string): the deepest static directory prefix shared by the task's
  patterns, relative to `cwd`; `"."` when there is no static prefix.
- `dynamic` (boolean): whether `base` was derived from a pattern containing glob
  metacharacters.
- `patterns` (string[]): every pattern belonging to the task, negative patterns
  included with their `!` prefix.
- `positive` (string[]): the task's positive patterns.
- `negative` (string[]): the task's negative patterns, with the leading `!`
  removed.

Patterns that share a base directory are grouped into one task; patterns with
different base directories produce separate tasks. Identical patterns are
collapsed into a single task.

### `isDynamicPattern(pattern, options?) => boolean`

Returns `true` when `pattern` contains glob metacharacters (for example `*`,
`**`, `?`, character classes, extglobs, or brace sets), and `false` when the
pattern is a literal path. Honours `braceExpansion`: with
`{ braceExpansion: false }`, a pattern whose only metacharacters are braces is
reported as static.

### `escapePath(path) => string`

Escapes glob metacharacters in `path` with backslashes so the result matches the
literal path. For example `"!abc"` becomes `"\\!abc"` and `"a(b)c"` becomes
`"a\\(b\\)c"`. A path with no metacharacters is returned unchanged.

### `convertPathToPattern(path) => string`

Converts a filesystem path into a pattern that matches it literally, escaping
glob metacharacters. On POSIX a plain relative path is returned unchanged;
`"a(b)c"` becomes `"a\\(b\\)c"`.

### `posix` and `win32`

Two namespace objects, each exposing platform-specific `escapePath` and
`convertPathToPattern`.

### Deprecated aliases

`async` (alias of `glob`), `sync` (alias of `globSync`) and `stream` (alias of
`globStream`) must also be exported.

## Options

| Option | Type | Default | Behaviour |
| --- | --- | --- | --- |
| `cwd` | string | `process.cwd()` | Directory patterns resolve against. |
| `absolute` | boolean | `false` | Return absolute paths, `/`-separated. |
| `onlyFiles` | boolean | `true` | Return only files. |
| `onlyDirectories` | boolean | `false` | Return only directories. When enabled, files are excluded. |
| `markDirectories` | boolean | `false` | Append `/` to directory results. |
| `dot` | boolean | `false` | Match entries whose name begins with `.`. |
| `unique` | boolean | `true` | De-duplicate results. |
| `deep` | number | `Infinity` | Maximum traversal depth; `deep: 1` restricts results to the `cwd` level. |
| `ignore` | string[] | `[]` | Exclusion patterns applied to results. |
| `braceExpansion` | boolean | `true` | Expand `{a,b}` brace sets. When `false`, braces are literal. |
| `caseSensitiveMatch` | boolean | `true` | Match case-sensitively. |
| `baseNameMatch` | boolean | `false` | Match a pattern without `/` against entry base names at any depth. |
| `globstar` | boolean | `true` | Give `**` recursive meaning. |
| `extglob` | boolean | `true` | Enable extended globbing. |
| `followSymbolicLinks` | boolean | `true` | Follow symbolic links while traversing. |
| `suppressErrors` | boolean | `false` | Suppress filesystem errors such as permission failures. |
| `throwErrorOnBrokenSymbolicLink` | boolean | `false` | Throw on a broken symbolic link. |
| `objectMode` | boolean | `false` | Return entry objects instead of path strings. |
| `stats` | boolean | `false` | Attach `fs.Stats` to entries. |
| `fs` | object | — | Custom filesystem method overrides. |
| `signal` | AbortSignal | — | Abort an in-flight search. |

## Implementation Notes

- `onlyFiles` defaults to `true`, so a bare `*` pattern returns only files.
  Setting `onlyDirectories: true` returns only directories; setting
  `onlyFiles: false` returns files and directories together.
- Dot entries are excluded unless `dot: true`, and this applies at every depth,
  so `**/*` with `dot: true` also matches entries inside dot-directories.
- `ignore` patterns are matched against the same relative paths that are
  returned, so `ignore: ["first/**"]` removes everything under `first`.
- With `baseNameMatch: true`, a pattern such as `*.ts` matches a file at any
  depth, and the returned path is still relative to `cwd`.
- With `absolute: true`, results are absolute paths joined from `cwd` with `/`
  separators.
- Given a directory containing `file.md`, `first/file.md`, `first/nested/file.md`
  and `second/file.md`, `glob("**/*.md")` returns those four paths in some order,
  while `glob("**/*.md", { deep: 1 })` returns only `file.md`.
- `generateTasks(["**/*.md", "!first/**"])` returns a single task whose
  `negative` array is `["first/**"]`.

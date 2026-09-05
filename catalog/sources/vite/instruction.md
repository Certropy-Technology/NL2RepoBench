# Build the scoped `vite` configuration utilities

```text
workspace/
├── package.json
├── package-lock.json
└── dist/node/index.js
```

## Project Description

Create an installable npm package named `vite` that implements a deterministic,
Node-only subset of Vite's public configuration utility API. This task covers
configuration composition, path and stylesheet detection, environment-file
loading, plugin ordering, and workspace-root discovery. It does not require a
development server, a production bundler, a browser, a CLI, or native addons.

Start from an empty workspace and write your own implementation. The evaluator
uses local files and JSON-safe values only. It does not contact an external
service or inspect an upstream implementation.

## Natural Language Instruction

Create this ESM package from an empty `workspace/`. Implement the documented
configuration, path, stylesheet, environment-file, alias, plugin-ordering,
and workspace-root utilities. Preserve local deterministic behavior and the
documented return shapes without implementing a development server.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64/glibc.
- The package must be an ES module. `package.json` must declare:
  - `"name": "vite"`;
  - `"version": "8.2.2"`;
  - `"type": "module"`;
  - a root export resolving to `./dist/node/index.js`.
- Commit a `package-lock.json` with `lockfileVersion: 3`.
- The package must have no runtime dependencies, optional dependencies,
  workspaces, native addons, `binding.gyp`, or npm lifecycle scripts. The
  verifier installs with `npm ci --offline --ignore-scripts`, then packages and
  installs the resulting tarball without network access.
- Export every function below as a named export from the package root. Include
  all runnable JavaScript under the package files selected by `npm pack`; no
  build step runs during installation.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── dist/node/
    ├── index.js
    └── shared/{config.js,constants.js,utils.js}
```

The root export resolves to `dist/node/index.js`; caller-created workspace
marker files are not package-owned resources.

## API Usage Guide

The public import path is the package root. Use named ESM imports such as
`import { normalizePath, mergeConfig } from 'vite'`; each function below is a
named export from `dist/node/index.js` and is available through the package
export map. The functions accept JSON-safe values except where a documented
filesystem path or environment-file read is required.

### `defineConfig(config)`

Return `config` unchanged. For JSON-safe object input, the returned value has
the same nested object and array shape.

```js
defineConfig({ base: '/app/', values: [1, 2] })
// => { base: '/app/', values: [1, 2] }
```

### `normalizePath(id)`

Normalize a POSIX-style path string. Resolve `.` and `..` segments, collapse
duplicate `/` separators, preserve an absolute leading `/`, and preserve a
meaningful trailing `/`.

```js
normalizePath('a/../b//c') // => 'b/c'
normalizePath('/a/./b/../c/') // => '/a/c/'
```

### `isCSSRequest(request)`

Return whether `request` ends in a supported stylesheet extension, optionally
followed by a query string. Supported extensions are `css`, `less`, `sass`,
`scss`, `styl`, `stylus`, `pcss`, `postcss`, and `sss`. A stylesheet extension
followed by another filename suffix is not a CSS request.

### `mergeAlias(left, right)`

Merge two alias schemas. Each input may be:

- an object mapping `find` strings to replacement strings; or
- an array of `{ find, replacement, customResolver? }` records.

If both inputs are objects, return an object containing both sets of keys and
let `right` overwrite duplicate keys. If either input is an array, normalize
both inputs to arrays and put the aliases from `right` before aliases from
`left`, preserving the order within each side. When an array record has a
string `find` ending in `/` and its replacement also ends in `/`, remove one
trailing slash from both. If one side is absent, return the other side.

### `mergeConfig(defaults, overrides, isRoot = true)`

Merge two plain configuration objects and return a new object.

- Ignore `null` and `undefined` override values.
- Recursively merge plain objects.
- Concatenate arrays in left-to-right order. When exactly one value is an
  array, treat the other value as a one-element array.
- At the root only, merge `input` specially:
  - two strings become an ordered two-element array;
  - strings and arrays concatenate in order;
  - object-shaped inputs merge by entry name, with the right side winning.
- Merge `alias` with `mergeAlias` when it appears at the root or under
  `resolve`.
- For `ssr.external`, `ssr.noExternal`, `resolve.external`, and
  `resolve.noExternal`, preserve `true` if either side is `true`.
- Treat each `environments.<name>.resolve` object like root `resolve` for these
  boolean controls.
- Nested `build.input` is an ordinary scalar setting and is overwritten by the
  right side rather than using the root input rule.
- Reject function-valued top-level arguments rather than invoking them.

### `resolveEnvPrefix(config)`

Read `config.envPrefix`. A missing value defaults to `"VITE_"`. Return a new
array containing the supplied string or the supplied string array in the same
order. Throw an error when any prefix is the empty string because that would
expose every environment variable.

### `sortUserPlugins(plugins)`

Accept an array containing plugin objects and one-level nested arrays of plugin
objects. Return `[pre, normal, post]`:

- plugins with `enforce: "pre"` go into `pre`;
- plugins with `enforce: "post"` go into `post`;
- all other plugins go into `normal`.

Flatten one array level and preserve the original relative order inside each
group. `undefined` produces three empty arrays.

### `loadEnv(mode, envDir, prefixes = "VITE_")`

Load environment variables from these files in order, when they exist:

1. `.env`
2. `.env.local`
3. `.env.<mode>`
4. `.env.<mode>.local`

Later definitions overwrite earlier definitions. Expand `$NAME` and `${NAME}`
references against the combined values. Return only keys beginning with one of
`prefixes`; `prefixes` may be a string or an ordered array of strings. Existing
matching process environment values take precedence over file values. Missing
files are ignored. Passing `false` as `envDir` loads no files. Reject `"local"`
as a mode name because it conflicts with the `.local` filename suffix.

```js
loadEnv('production', '/project')
// reads /project/.env, /project/.env.local,
// /project/.env.production, /project/.env.production.local
```

### `searchForWorkspaceRoot(current, root?)`

Walk upward from `current` and return the nearest directory containing any of:

- `pnpm-workspace.yaml`;
- `lerna.json`;
- `package.json` with a truthy `workspaces` field;
- `deno.json` or `deno.jsonc` with a truthy `workspace` field.

If no workspace marker is found, return `root`. When `root` is omitted, derive
it by walking upward to the nearest `package.json`, falling back to `current` if
none exists. Ignore unreadable and malformed JSON workspace marker files.

## Implementation Notes

- Keep all behavior deterministic and local to the process and filesystem.
- Do not execute config callbacks, start servers, bind ports, spawn package
  managers, or access the network.
- Preserve stable ordering in alias merges, plugin groups, prefix arrays, and
  root input arrays.
- Errors should be regular JavaScript `Error` or `TypeError` instances with a
  message that identifies the invalid condition.

## Examples

```js
import {normalizePath, mergeAlias, loadEnv} from 'vite';
normalizePath('src\\main.js');
mergeAlias([{find: 'app', replacement: './src'}], []);
loadEnv('development', '/tmp/project', 'VITE_');
```

Use `mergeConfig` and `sortUserPlugins` for local JSON-safe configuration
objects, preserving merge and ordering rules.

## Error Handling and Boundary Conditions

Missing environment files produce the documented empty result. Invalid alias,
config, or plugin shapes raise a regular JavaScript error. Workspace discovery
is bounded by the supplied root and never accesses a network.

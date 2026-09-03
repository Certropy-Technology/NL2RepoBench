# Build `locate-path`

## Project Description

Create an installable npm package named `locate-path`, version `8.0.0`, from an
empty workspace. It must provide asynchronous and synchronous helpers that find
the first path matching a requested filesystem type.

Do not copy upstream tests, development tooling, or repository metadata into the
generated package. The package must be usable after the verifier runs its
offline install.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64, and ESM via `"type": "module"`.
- `package.json` with the exact name and version, a safe ESM export map for
  `index.js` and `index.d.ts`, no development dependencies, and no lifecycle
  scripts.
- The sole direct runtime dependency is `p-locate` pinned to `6.0.0`; its npm
  lock must resolve `p-limit@4.0.0` and `yocto-queue@1.2.2` with integrity data.
- A v3 `package-lock.json` that supports
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- No native addons, workspaces, custom loaders, registry overrides, network
  access, random state, or timing-based result decisions.

## API Usage Guide

### `locatePath(paths, options?)`

Import the named export `locatePath` from `locate-path`. Its signature is:

```ts
export function locatePath(
  paths: Iterable<string>,
  options?: AsyncOptions,
): Promise<string | undefined>;
```

`paths` is consumed in iteration order. Resolve each path against `options.cwd`
and return the original path string for the first matching filesystem entry.
`cwd` accepts a string or a file `URL` and defaults to `process.cwd()`. The
default `type` is `'file'`; `'directory'` selects directories and `'both'`
selects either regular files or directories. Missing, inaccessible, or wrong
type entries are skipped.

`allowSymlinks` defaults to `true`. When false, inspect the link itself rather
than its target, so a symlink does not match a file or directory. `concurrency`
and `preserveOrder` are forwarded to the asynchronous search: concurrency must
be a positive integer or positive infinity, and preserveOrder defaults to true.
Invalid type values reject with `Error` and message
`Invalid type specified: <value>`. Invalid URL schemes reject with the native
`TypeError` from URL-to-path conversion. Errors thrown by the input iterator are
not swallowed.

### `locatePathSync(paths, options?)`

Import the named export `locatePathSync`. Its signature is:

```ts
export function locatePathSync(
  paths: Iterable<string>,
  options?: Options,
): string | undefined;
```

It has the same `cwd`, `type`, and `allowSymlinks` behavior, performs checks
synchronously, and does not accept asynchronous-only options. It returns
`undefined` when no candidate matches and preserves the original path spelling.

## Implementation Notes

The public root has exactly the two named functions `locatePath` and
`locatePathSync`; do not add a default export. Use asynchronous `stat` versus
`lstat` according to `allowSymlinks`, and synchronous counterparts for the sync
API. Prefer deterministic bounded iteration and let invalid option and iterator
errors retain their native constructor and message. The verifier creates all
fixture files and callbacks inside a separate unprivileged child; no callback,
URL object, symlink, or filesystem handle crosses that boundary.

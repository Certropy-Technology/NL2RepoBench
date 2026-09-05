# Project Description

Create an installable npm package named `locate-path`, version `8.0.0`, from
an empty workspace. It provides asynchronous and synchronous helpers that
search an iterable of path strings and return the first entry matching a
requested filesystem type. The returned spelling is the original iterable
value, not a normalized replacement.

# Natural Language Instruction

Create the `locate-path` project from an empty `workspace/`. Implement the two
named root exports `locatePath` and `locatePathSync`. Support string and file
URL working directories, file/directory/both filtering, symlink policy,
finite iterable inputs, and the asynchronous concurrency/order options.

The asynchronous function must preserve the package's first-match semantics
under the documented `preserveOrder` setting; the synchronous function must
perform equivalent filesystem classification without asynchronous-only
options. Keep invalid option and iterator errors observable. This is a small
filesystem utility package, not a CLI or a source/test copy.

# Supports

- Use Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
  The package declares Node engine compatibility `>=20`.
- `package.json` must identify `locate-path@8.0.0`, expose root `index.js` and
  the safe `index.d.ts` type entry, and declare the direct runtime dependency
  `p-locate@6.0.0` with its locked transitive `p-limit@4.0.0` and
  `yocto-queue@1.2.2` packages.
- Commit an npm v3 lockfile with integrity data. Offline installation must
  succeed with `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- No development dependencies, lifecycle scripts, native addons, custom
  loaders, registry overrides, random state, timing decisions, or network
  access are allowed. Agent, candidate, verifier, Oracle, and controls run with
  NoNetwork; runtime filesystem access is limited to caller-provided paths.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

`index.js` is the only public runtime module and exports exactly the named
helpers `locatePath` and `locatePathSync`; there is no default export.
`index.d.ts` declares both functions and their option shapes. `package.json`
contains the export map, package metadata, engine, and dependency declaration.
The lockfile records the complete offline runtime closure. Do not list hidden
tests, verifier adapters, fixtures, reports, or source archives as agent-owned
files.

The named package import is `locatePath`/`locatePathSync` from the root; the
public import names are not internal file paths.

# API Usage Guide

## `locatePath`

```ts
locatePath(
  paths: Iterable<string>,
  options?: AsyncOptions,
): Promise<string | undefined>
```

Consume `paths` in iteration order. Resolve each string against `options.cwd`
and return the original string for the first matching filesystem entry. `cwd`
is a string or file URL and defaults to `process.cwd()`. `type` defaults to
`'file'`; `'directory'` selects directories and `'both'` selects either
regular files or directories. Missing, inaccessible, or wrong-type entries
are skipped.

`allowSymlinks` defaults to `true`; false inspects the link itself rather than
its target, so a symlink does not match a file or directory. `concurrency` is a
positive integer or positive infinity, and `preserveOrder` defaults to true.
Invalid type values reject with `Error` and message
`Invalid type specified: <value>`. Invalid URL schemes retain the native
`TypeError` from URL-to-path conversion, and errors thrown by the input
iterator are not swallowed.

## `locatePathSync`

```ts
locatePathSync(
  paths: Iterable<string>,
  options?: Options,
): string | undefined
```

Use the same `cwd`, `type`, and `allowSymlinks` semantics synchronously. The
sync options do not accept asynchronous-only `concurrency` or
`preserveOrder`. Return `undefined` when no candidate matches and preserve the
original candidate spelling.

# Implementation Notes

- Use asynchronous `stat` versus `lstat` according to `allowSymlinks`, and
  synchronous counterparts for the sync API.
- Accept any finite iterable, including arrays, sets, and generators, while
  retaining iterator exceptions. Do not convert path values to a different
  public spelling.
- Keep result selection deterministic and bounded. No callback, URL object,
  filesystem handle, private report, or verifier state is part of the API.
- The package root exports only the two named helpers. Do not add a CLI,
  default export, browser behavior, or undocumented module entry.

# Examples

```js
import {locatePath, locatePathSync} from 'locate-path';

const first = await locatePath(['missing.txt', 'config.json'], {type: 'file'});
const same = locatePathSync(new Set(['config.json']), {type: 'file'});
```

```js
const directory = await locatePath(['cache', 'data'], {
  cwd: new URL('file:///tmp/project/'),
  type: 'directory',
  allowSymlinks: false,
});
```

# Error Handling and Boundary Conditions

- Empty iterables and lists with no matching entry resolve to `undefined`.
  Missing, inaccessible, and wrong-type entries do not terminate the search.
- `type` must be `file`, `directory`, or `both`; an invalid value rejects with
  the documented `Error` and message. A URL with an unsupported scheme keeps
  the native URL conversion `TypeError`.
- With `allowSymlinks: false`, file, directory, and broken symlinks are
  inspected as links and do not match target types. With the default true,
  valid targets may match.
- A throwing input iterator must reject/throw rather than being silently
  swallowed. No network, DNS, registry, current time, random state, or remote
  service may influence classification.

# Project Description

Build an installable ESM npm package named `parse-json`, version `8.3.0`, from
an empty workspace. It parses JSON and turns native syntax failures into
`JSONError` instances with useful file names and source code frames.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- A package with `"type": "module"` and a root export whose runtime and type
  entries are `./index.js` and `./index.d.ts`.
- Default export `parseJson` and named export `JSONError`.
- A committed npm lockfile with lockfile version 3. Installation is offline:
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Runtime dependencies only from the supplied private npm cache closure.
  Do not use native addons, workspaces, custom loaders, lifecycle hooks,
  registry overrides, generated downloads, or runtime network access.

# API Usage Guide

## `parseJson(string, reviver?, fileName?)`

**Import path:** package root.

**Signature:**

```js
parseJson(string, reviver?, fileName?)
```

`string` is JSON text accepted by `JSON.parse`. `reviver` has the same meaning
as the second argument to `JSON.parse`; when it is a string, it is interpreted
as `fileName` instead. `fileName` is optional metadata appended to a parsing
error message and exposed as `error.fileName`.

On valid JSON, return the parsed JSON-compatible value. Preserve native
`JSON.parse` semantics for objects, arrays, primitives, whitespace, and a
reviver callback. The function is synchronous and does not mutate its input.

On invalid JSON, throw a `JSONError`. The error wraps the native `SyntaxError`
as `cause`, has `name === "JSONError"`, and keeps the original `fileName`.
Its `message` adds a printable Unicode code point for unexpected-token errors,
adds `while parsing empty string` only for empty input, appends ` in <fileName>`
when a file name is set, and includes a source frame when a location can be
derived. Native Node error wording and line/column details are preserved.

## `JSONError`

**Import path:** package root.

`JSONError` is a public class for `instanceof` checks. Its legacy constructor
accepts a string message. The writable `message` property can be replaced;
the file name suffix and lazily computed `codeFrame` remain available.

The read-only `codeFrame` includes terminal highlighting when supported, while
`rawCodeFrame` never includes color escape sequences. Both use one-based line
and column locations and JavaScript UTF-16 offsets. For errors without a
location, the frame properties are `undefined`.

# Implementation Notes

Keep the package deterministic under `TZ=UTC` and offline execution. Do not
write files, spawn processes, read environment state, use the network, or
change global parser state. The evaluator calls the package only through a
bounded JSON child adapter; callbacks used for reviver coverage are created by
the trusted adapter and are not supplied as model input. Private tests and the
Oracle implementation are not part of the package to implement.

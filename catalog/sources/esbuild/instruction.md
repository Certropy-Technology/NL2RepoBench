## Project Description

Build a distributable npm package named `esbuild`, version `0.28.2`, that provides a small synchronous JavaScript and TypeScript transformation API. It is for Node.js programs that need to transform source text, produce one in-memory bundled output, format diagnostics, or inspect a build metafile.

Start from an empty workspace and create the complete installable package, not only loose functions. A consumer in another directory must be able to install the package and load it with `require("esbuild")`. The in-scope public surface is the four synchronous exports documented below: `transformSync`, `buildSync`, `formatMessagesSync`, and `analyzeMetafileSync`. Support JavaScript, TypeScript, and JSX transformation; CommonJS and ESM output selection; the documented synchronous build path; structured diagnostic formatting; and metafile analysis.

Do not implement or require the native esbuild executable, watch or serve mode, plugins, asynchronous APIs, a long-lived service, or the complete esbuild option universe. Do not rely on a network service, globally installed package, lifecycle script, or machine-specific absolute path. Results must be stable and inspectable across a JSON-oriented subprocess boundary.

## Supports

- **Runtime:** Node.js `24.19.0` on Linux `amd64` with glibc.
- **Package manager:** npm `11.17.0`.
- **Package metadata:** Create package name `esbuild`, version `0.28.2`, with a CommonJS-compatible `main` entry and a v3 `package-lock.json`. The main entry must export all four documented functions so `require("esbuild")` works from a clean consumer directory.
- **Dependencies:** No external runtime package is required. Prefer Node.js and its standard library. Do not add native addons or depend on globally installed software.
- **Installation:** The harness runs `npm ci --offline --ignore-scripts`, packs the package, and installs that tarball into an isolated consumer. The package must not need its source-directory working directory. A representative check is:

  ```text
  npm ci --offline --ignore-scripts
  npm pack --ignore-scripts
  # install the resulting tarball in a separate consumer directory
  node -e 'const e = require("esbuild"); console.log(typeof e.transformSync)'
  ```

- **Directory layout:** At minimum create the following (implementation module names may differ, but the entry and metadata must agree):

  ```text
  workspace/
  ├── package.json
  ├── package-lock.json
  ├── index.js
  └── lib/
      ├── transform.js
      ├── build.js
      ├── messages.js
      └── metafile.js
  ```

- **Harness setup:** The harness installs offline and invokes the synchronous exports from an isolated Node subprocess. Calls in scope do not need to create files; `buildSync` is exercised with `write: false`.
- **No network:** Agent, candidate, verifier, Oracle, and controls run without network access. Do not contact GitHub, npm, DNS, or external services at runtime. Do not add `postinstall`, `install`, `prepare`, workspace, or other lifecycle behavior required for correctness.

## API Usage Guide

All functions below must be properties of the object returned by `require("esbuild")`. They are synchronous: a successful call returns before completion, while invalid source or unsupported input throws an `Error` with a useful diagnostic message. Preserve deterministic output for identical inputs and options.

### `transformSync(input, options)`

**Import path and signature**

```js
const { transformSync } = require("esbuild");
transformSync(input, options = {});
```

`input` is JavaScript source text (string). `options` is an object and may be omitted. The supported option domain is:

- `loader`: one of `"js"`, `"ts"`, or `"jsx"`; JavaScript is the default.
- `minifySyntax`: boolean; when true, apply syntax-level simplification such as folding the numeric expression `1 + 2` to `3` without changing program meaning.
- `format`: `"cjs"` or `"esm"`. CommonJS output must contain a usable `module.exports` form; ESM output preserves an ES module form.
- `sourcemap`: `"inline"` to request an inline data-URL source-map comment, or omitted for no map.
- `sourcefile`: string source name used by the inline source map when `sourcemap: "inline"` is selected.

Return an object with a required `code` string. When an inline source map is requested, also return a string `map` field containing a JSON-compatible source map representation; the emitted `code` contains an inline `data:` source-map comment. Without that request, a `map` field need not be present. The function does not write files or mutate process-global state.

Output ordering follows source ordering and must be deterministic. Do not include timestamps, random names, or host-specific paths. Valid source produces no error diagnostic. Malformed JavaScript, malformed TypeScript, malformed JSX, or a non-object options value must throw an `Error` rather than return a successful result; the message should identify the syntax or option problem.

Ordinary example:

```js
const result = transformSync("const answer = 1 + 2;", { loader: "js", minifySyntax: true });
// result.code is a string containing executable JavaScript and the simplified expression.
```

Edge examples:

```js
const empty = transformSync("", { loader: "js" });
// empty.code is a string; the call succeeds without inventing a source file.
transformSync("const = ;", { loader: "js" }); // throws Error
```

### `buildSync(options)`

**Import path and signature**

```js
const { buildSync } = require("esbuild");
buildSync(options);
```

`options` must be an object. The supported in-memory build shape contains:

- `stdin`: an object with required string `contents` and `sourcefile`, plus optional `loader` (`"js"`, `"ts"`, or `"jsx"`).
- `write`: boolean; the documented call uses `false` and expects in-memory output rather than filesystem writes.
- `bundle`: boolean; when true, produce one output containing the stdin entry.
- `platform`: `"neutral"` for the documented platform-neutral build.
- `format`: `"cjs"` or `"esm"`, selecting the output module form.
- `metafile`: boolean; when true, include a JSON-compatible build description.

Return an object with an `outputFiles` array. Each output file represents generated text through a stable text or `contents` value and has enough information to identify the output. With `bundle: true`, the stdin entry is combined into one output. CJS output contains `module.exports`; ESM output remains an ES module form. If `metafile: true`, include a `metafile` object with `inputs` and `outputs` information describing the sourcefile and generated output. File and key ordering must be deterministic. `write: false` must not write output files or depend on the current directory.

An absent or malformed `stdin`, non-string contents/sourcefile, unsupported loader/format/platform, or invalid source must throw an `Error` with a diagnostic message. An empty `contents` string is valid and yields an output file. Ordinary example:

```js
const result = buildSync({
  stdin: { contents: "export const value: number = 3;", sourcefile: "entry.ts", loader: "ts" },
  write: false, bundle: true, platform: "neutral", format: "esm", metafile: true
});
// result.outputFiles is an array and result.metafile describes entry.ts and its output.
```

Edge examples:

```js
buildSync({ stdin: { contents: "", sourcefile: "empty.js" }, write: false, platform: "neutral" });
// succeeds with a deterministic outputFiles array
buildSync({ write: false }); // throws because stdin is missing
```

### `formatMessagesSync(messages, options)`

**Import path and signature**

```js
const { formatMessagesSync } = require("esbuild");
formatMessagesSync(messages, options);
```

`messages` is an array of message objects. Each message has string `text` and may have `location` containing a file name and line/column information. `options` is an object; the supported form is `{ kind: "error", color: false }`. Return an array of formatted strings in the same order as `messages`. For an error, include the `[ERROR]` marker, message text, and supplied file and line/column location when present. With `color: false`, do not add terminal color escape sequences. An empty array returns an empty array and does not write output or mutate the input.

Invalid non-array messages, malformed message objects, or unsupported option values should throw an `Error` instead of silently producing unrelated output. Ordinary and edge examples:

```js
const lines = formatMessagesSync([
  { text: "Unexpected token", location: { file: "src/app.js", line: 2, column: 7 } }
], { kind: "error", color: false });
// lines is a one-element array containing [ERROR], the text, and the location.
formatMessagesSync([], { kind: "error", color: false }); // []
```

### `analyzeMetafileSync(metafile, options)`

**Import path and signature**

```js
const { analyzeMetafileSync } = require("esbuild");
analyzeMetafileSync(metafile, options = {});
```

`metafile` may be either a JSON string or an object in esbuild metafile shape,
with `inputs` and `outputs` maps. `options` is an object; `{ color: false }`
requests plain text without terminal color escapes. Return a human-readable
string that names relevant input and output files. Preserve deterministic
ordering when multiple keys are present. The function is read-only and does
not access the filesystem or network. Invalid JSON, null, or a value without
the expected metafile structure must throw an `Error`; an object with empty
`inputs` and `outputs` is valid and returns a deterministic (possibly empty)
report.

```js
const report = analyzeMetafileSync(
  { inputs: { "entry.js": { bytes: 10 } }, outputs: { "out.js": { bytes: 10, inputs: { "entry.js": { bytesInOutput: 10 } } } } },
  { color: false }
);
// report includes both "entry.js" and "out.js".
analyzeMetafileSync("{\"inputs\":{},\"outputs\":{}}", { color: false }); // succeeds
```

## Implementation Notes

- Keep the root export names exact and make the package entry usable after
  tarball installation from another working directory. Do not expose a
  second incompatible calling convention through the same export.
- Treat transformation as source-to-source compilation: remove TypeScript
  type-only syntax while retaining executable JavaScript, accept JSX through
  the `jsx` loader, and preserve module semantics selected by `format`.
  Syntax simplification must not turn invalid input into a successful build.
- `buildSync` should compose the same transformation behavior as
  `transformSync`; its `stdin` sourcefile is the logical input name used in
  output and metafile data. Keep `write: false` entirely in memory.
- Source-map and metafile data are structured values. Serialize them with
  stable key and item ordering, and never embed wall-clock data, random IDs,
  or absolute host paths.
- Preserve message order and location information. `color: false` means
  output is suitable for plain JSON capture, without ANSI escape sequences.
- Small verifiable examples include transforming `const n: number = 1;` with
  the TypeScript loader, accepting `<div />` with the JSX loader, producing
  one CJS build from `stdin`, and reporting `entry.js` plus `out.js` from a
  metafile. The implementation may choose its own parsing and formatting
  strategy; do not copy source bodies or private tests.
- Invalid input should fail locally and synchronously with an informative
  error. Do not catch and suppress parser errors merely to return an empty
  result. Keep all documented operations offline, deterministic, and free of
  unintended filesystem or global-state side effects.

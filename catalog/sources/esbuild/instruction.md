# Project Description

Create a distributable npm package named `esbuild` at version `0.28.2`. It is a
small, synchronous JavaScript/TypeScript transformation and bundling API. The
package must work on Node.js 24.x on Linux amd64 with no network access at
runtime.

The evaluator installs your package with `npm ci --offline --ignore-scripts`,
then packs it and installs that tarball into an isolated consumer. Do not rely
on lifecycle scripts, globally installed packages, environment-specific paths,
or network access. Your package must expose a callable CommonJS API from its
declared `main` entry.

# Supports

- Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with glibc.
- A regular npm package containing a v3 `package-lock.json` with no external
  runtime dependencies.
- CommonJS loading through `require("esbuild")`.
- JSON-serializable arguments and return values for the functions listed below.
- Deterministic operation without writing files for the tested API calls.

# API Usage Guide

Implement these callable exports from the package main entry.

## `transformSync(input, options)`

Accept a JavaScript string and an options object. Return an object containing a
`code` string. With `{loader: "ts"}`, remove TypeScript type annotations while
preserving executable JavaScript. With `{loader: "js"}`, transform JavaScript.
With `{minifySyntax: true}`, perform syntax-level simplification such as
folding `1 + 2` to `3`. With `{loader: "jsx"}`, accept JSX syntax and emit
JavaScript. With `{format: "cjs"}`, emit a CommonJS module wrapper containing
`module.exports`. With `{format: "esm"}`, preserve an ES module form. With
`{sourcemap: "inline", sourcefile: "input.ts"}`, include an inline data URL
source map comment and return a string `map` field. Valid transformations do
not report errors or warnings.

Invalid source must throw an Error with a diagnostic message rather than
returning a successful result.

## `buildSync(options)`

Accept an options object with a `stdin` object containing `contents`,
`sourcefile`, and optionally `loader`; `write: false`; and `platform: "neutral"`.
Return an object with an `outputFiles` array. Each output file has text or
contents representing the generated module. When `bundle: true`, combine the
stdin entry into one output. When `format: "cjs"`, the generated output is a
CommonJS module containing `module.exports`. When `format: "esm"`, preserve an
ES module form. With `metafile: true`, return a JSON-compatible `metafile`
object describing the input and output.

## `formatMessagesSync(messages, options)`

Accept an array of message objects and `{kind: "error", color: false}`. Return
an array of formatted strings. An error message includes the `[ERROR]` marker,
the message text, and the supplied file and line/column location when present.

## `analyzeMetafileSync(metafile, options)`

Accept a JSON string or object in the esbuild metafile shape and an options
object such as `{color: false}`. Return a human-readable string that includes
the relevant input and output file names.

# Implementation Notes

- Keep the package entry and exports usable from a clean consumer directory;
  do not assume the evaluator runs from the package source directory.
- Do not add native addons, platform-specific package requirements,
  postinstall/install/prepare hooks, workspaces, shell scripts, or network
  calls. The evaluator intentionally disables lifecycle scripts.
- Keep output deterministic for identical inputs. Do not add timestamps,
  random identifiers, or machine-specific absolute paths to generated output.
- The evaluator checks behavior through a subprocess JSON boundary. It will
  exercise both successful and invalid-input cases, including TypeScript, JSX,
  syntax minification, source maps, CommonJS output, bundling, error messages,
  and metafile analysis.

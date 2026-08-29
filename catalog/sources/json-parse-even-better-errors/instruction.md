# Project Description

Build an installable CommonJS npm package named `json-parse-even-better-errors`,
version `6.0.0`, from an empty workspace. It should provide a drop-in style
JSON parser that keeps the normal JSON result on success and gives structured,
contextual parse errors on failure.

# Supports

- Node.js `24.19.0` with npm `11.17.0` on Linux x86-64.
- A CommonJS package with `package.json` fields `name`, `version`, and
  `main: "lib/index.js"`.
- A v3 `package-lock.json` matching the package metadata.
- No runtime dependencies, native addons, workspaces, network access, or
  lifecycle scripts. The package must install with
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- The package root must be callable through
  `require("json-parse-even-better-errors")`.

# API Usage Guide

## `parseJson(raw, reviver = undefined, context = 20) => any`

Import path: `require("json-parse-even-better-errors")`.

Parse a JSON string or a Node `Buffer`. A leading UTF-8 byte-order mark is
removed before parsing. On success, return the same JSON values as
`JSON.parse`, including support for a reviver function. For object and array
results, attach non-enumerable-in-JSON symbol-keyed metadata at
`Symbol.for("indent")` and `Symbol.for("newline")`:

- `indent` is the whitespace sequence inferred from the first indented line,
  or the empty string for compact non-empty structures.
- `newline` is the newline sequence inferred from the source, or the empty
  string when the source has no indentation. Empty `{}` and `[]` use newline
  `"\n"` (or the source newline) and default indent `"  "`.
- Primitive results do not receive symbol metadata.

The function is synchronous and deterministic. As with native `JSON.parse`,
primitive inputs that the runtime can coerce successfully (for example a
number) may be returned as-is; objects that cannot be coerced to JSON should
produce the wrapped `TypeError` described below. The `reviver` follows native
`JSON.parse` traversal and can delete properties by returning `undefined`.
The optional `context` controls the number of characters shown around a parse
error; the default is `20`.

## `parseJson.noExceptions(raw, reviver = undefined) => any | undefined`

Use the same input and reviver rules as `parseJson`, but return `undefined`
instead of throwing for any parse or input-type error. Valid JSON, including a
Buffer and a BOM-prefixed Buffer, is returned normally.

## `parseJson.JSONParseError`

The exported `JSONParseError` class extends `SyntaxError`. Parser failures
produce this class with:

- `code === "EJSONPARSE"`;
- `position`, a numeric error position when the runtime exposes one;
- `systemError`, the original native `SyntaxError`;
- a message containing the improved native error, a bounded input excerpt, and
  `"while parsing"` context;
- a stable `name` of `"JSONParseError"`, even if callers assign to `name`;
- `Symbol.toStringTag === "JSONParseError"`.

Calling `new parseJson.JSONParseError(nativeError, text, context, caller)`
must preserve the supplied original error and use `caller` to trim that helper
from the generated stack when provided.

# Implementation Notes

Keep the package zero-dependency and CommonJS-compatible. Do not use network
access, the clock, randomness, filesystem reads, or subprocesses. Preserve
native JSON value semantics and do not silently accept malformed JSON. Error
messages should remain bounded for long inputs, and non-string/non-Buffer
inputs should fail with a `TypeError` whose code is `EJSONPARSE`.

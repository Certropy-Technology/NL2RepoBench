# Project Description

Create an installable npm package named `jsesc`, version `3.1.0`, from an empty
workspace. It must expose a CommonJS function that converts JavaScript strings
and JSON-safe values into deterministic JavaScript source literals. It must also
provide the `jsesc` command-line program.

This is a behavior-focused contract derived from the pinned `jsesc` 3.1.0
project. Do not copy upstream source or tests into the generated repository.

# Supports

- Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `require('jsesc')` returns the callable function, and its `.version` is the
  string `3.0.2`; expose the same callable as the `.jsesc` property as well.
- `package.json` has `name: "jsesc"`, `version: "3.1.0"`, `main: "jsesc.js"`,
  and `bin: "bin/jsesc"`. Declare no runtime dependencies.
- A clean verifier can run `npm ci --offline --ignore-scripts --no-audit
  --no-fund`, then pack and install the package.
- Do not use network access, lifecycle hooks, native addons, workspaces, or
  current time/random state.

# API Usage Guide

## `jsesc`

**Import and signature:** `const jsesc = require('jsesc'); jsesc(value,
options?)`.

`value` may be a string, finite number, boolean, `null`, an array, or a plain
object when called through the scored child-process contract. Return a string of
JavaScript source. Preserve array order and own object property enumeration
order. A plain object is serialized recursively. The upstream-compatible
implementation may also support `bigint`, `undefined`, boxed primitives,
`Map`, `Set`, and Node `Buffer`; those native or non-JSON values are outside the
scored adapter boundary and are not required for the task's fixed test set.

String output uses single quotes only when `wrap` is true. Escape control
characters with JavaScript short escapes where available, use `\\xHH` for
other characters up to `U+00FF`, and use `\\uHHHH` for larger code units.
Surrogate pairs use two `\\uHHHH` escapes by default and `\\u{...}` when
`es6` is true. Lone surrogates are escaped as one `\\uHHHH`. NUL uses `\\0`
unless followed by a decimal digit, where it uses `\\x00`.

The options object supports these fields:

- `escapeEverything`: escape every character, including ASCII, with the
  shortest applicable escape form.
- `minimal`: preserve printable characters and Unicode except required syntax
  characters and whitespace separators.
- `isScriptContext`: escape `</script` and `</style` case-insensitively and
  escape `<!--` to `\\x3C!--` (or `\\u003C!--` in JSON mode).
- `quotes`: `single`, `double`, or `backtick`; invalid values fall back to
  `single`. `wrap` adds the selected quote around strings.
- `es6`: use code-point escapes for astral pairs.
- `json`: use double quotes, JSON escapes, and JSON-compatible `null` for
  non-representable values. An explicit `wrap` value overrides the JSON default.
- `compact`: default true. When false, arrays and objects use newlines and the
  `indent` string (default tab); `indentLevel` supplies the starting level.
- `lowercaseHex`: use lowercase hexadecimal digits.
- `numbers`: `decimal`, `binary`, `octal`, or `hexadecimal`; non-decimal
  integer output uses the corresponding prefix. BigInts retain a trailing `n`.

Examples:

```js
jsesc('föo ♥ 𝌆');
// 'f\\xF6o \\u2665 \\uD834\\uDF06'
jsesc('a𝌆b', {es6: true});
// 'a\\u{1D306}b'
jsesc({foo: 'bar'}, {compact: false, indent: ' '});
// "{\\n 'foo': 'bar'\\n}"
jsesc(42, {numbers: 'hexadecimal'});
// '0x2A'
```

## CLI

`bin/jsesc` accepts a string argument or one line from stdin. Support
`--single-quotes`, `--double-quotes`, `--wrap`, `--escape-everything`,
`--escape-etago`, `--es6`, `--lowercase-hex`, `--json`, `--object`, `--pretty`,
`--version`, and `--help` (with the corresponding short forms). `--object`
parses its argument as JSON before escaping; `--pretty` also selects object
mode and non-compact output. `--version` prints `v3.0.2`. Successful escaping
exits zero; malformed object JSON exits nonzero.

# Implementation Notes

Keep the package CommonJS-loadable on Node 24 and make the CLI executable.
The verifier calls the library in a bounded child process using JSON requests;
callbacks, cyclic values, Dates, symbols, regular expressions, arbitrary source
text, and the native/non-JSON values listed above are outside the scored
boundary. The hidden collection contains 48 deterministic leaves covering
package shape, strings, Unicode, option interactions, numbers, JSON-safe
recursive values, and CLI behavior. Keep the package self-contained and do not
fetch dependencies or source files at install or runtime.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── lib/esm/main.js
```

# Project Description

Build an installable npm package named `jsonc-parser`, version
`4.0.0-next.2`, from an empty workspace. The package parses JSON with comments
(JSONC), reports tolerant parse errors, computes JSON-safe modifications, and
formats JSONC text by returning textual edits.

This task covers a bounded, JSON-compatible slice of the package. It preserves
the meaningful parse/modify/format behavior that can cross a fixed subprocess
boundary without passing JavaScript functions or object identities.

# Natural Language Instruction

Create the ESM `jsonc-parser` package from an empty workspace. Implement the
root parse, diagnostic-name, modify, format, and apply-edits APIs with tolerant
JSON-with-comments parsing, JSON-safe path edits, safe formatting, stable UTF-16
offsets, and deterministic diagnostics. Keep callback-valued and scanner-only
surfaces outside the documented JSON boundary.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64`.
- An ESM package with `"type": "module"` and a root export whose import entry is
  `./lib/esm/main.js`.
- Package name `jsonc-parser` and version `4.0.0-next.2`.
- A scripts-stripped production distribution: `package.json` must not contain a
  `scripts`, `dependencies`, or `devDependencies` field. Runtime dependencies,
  native addons, loaders, workspaces, lifecycle hooks, registry configuration,
  and generated runtime downloads are not allowed.
- A committed npm lockfile using lockfile version 3. The zero-dependency package
  must install with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The package root must export callable `parse`, `printParseErrorCode`,
  `modify`, `format`, and `applyEdits` functions.
- All scored inputs and outputs are bounded JSON values. JSONC document text is
  data, not executable source. The verifier sends only fixed operation names,
  strings, numbers, booleans, nulls, arrays, and plain objects; it never sends
  source code, callbacks, JavaScript functions, or executable strings.

The scanner, tree/location helpers, visitor callbacks, custom insertion
callbacks, and values that JSON cannot represent are outside the scored slice.
They may be implemented, but they are not required.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── README.md
└── lib/
    └── esm/
        ├── main.js
        ├── parser.js
        ├── modify.js
        └── formatter.js
```

# API Usage Guide

## `parse(text, errors?, options?)`

**Import path:** package root.

**Signature:**

```js
parse(text, errors = [], options = {})
```

`text` is a JSONC string. Return the represented JSON-compatible value and
append parse diagnostics to the caller-provided `errors` array. Parsing is
fault tolerant: malformed documents should return as much value structure as
can be recovered while also reporting diagnostics. Empty input returns
`undefined` unless content is present; duplicate object keys keep the last
parsed value.

By default:

- line comments (`// ...`) and block comments (`/* ... */`) are accepted;
- trailing commas are diagnosed;
- empty content is diagnosed;
- ordinary JSON root primitives, arrays, and objects are accepted;
- a missing comma can be recovered when the following value/property is still
  recognizable; and
- extra tokens after one root value produce an end-of-file diagnostic while the
  first root value remains the result.

Supported options are JSON booleans:

| Option | Default | Behavior |
| --- | --- | --- |
| `disallowComments` | `false` | Comments still permit tolerant recovery but append `InvalidCommentToken`. |
| `allowTrailingComma` | `false` | When true, a comma immediately before `}` or `]` is accepted without a diagnostic. |
| `allowEmptyContent` | `false` | When true, empty input returns `undefined` without a diagnostic. |

Each diagnostic has this shape, with zero-based UTF-16 offsets and positions:

```js
{
  error: number,
  offset: number,
  length: number,
  startLine: number,
  startCharacter: number
}
```

The public error codes and `printParseErrorCode(code)` names are:

| Code | Name | Code | Name |
| ---: | --- | ---: | --- |
| 1 | `InvalidSymbol` | 9 | `EndOfFileExpected` |
| 2 | `InvalidNumberFormat` | 10 | `InvalidCommentToken` |
| 3 | `PropertyNameExpected` | 11 | `UnexpectedEndOfComment` |
| 4 | `ValueExpected` | 12 | `UnexpectedEndOfString` |
| 5 | `ColonExpected` | 13 | `UnexpectedEndOfNumber` |
| 6 | `CommaExpected` | 14 | `InvalidUnicode` |
| 7 | `CloseBraceExpected` | 15 | `InvalidEscapeCharacter` |
| 8 | `CloseBracketExpected` | 16 | `InvalidCharacter` |

For an unknown code, `printParseErrorCode` returns
`"<unknown ParseErrorCode>"`.

Examples:

```js
const errors = [];
parse('{ // note\n "enabled": true }', errors);
// { enabled: true }; errors is []

parse('{ "items": [], }', errors, { allowTrailingComma: true });
// { items: [] }
```

## `modify(text, path, value, options?)`

**Import path:** package root.

**Signature:**

```js
modify(text, path, value, options = {})
```

Return an array of textual edits against the original `text`. `path` is an
array of string property names and integer array indexes. The empty path
replaces the root value. A missing path is created using objects for string
segments and arrays for numeric segments.

`value` may be any JSON-compatible value. Passing JavaScript `undefined`
removes the selected property or array item; `null` is an ordinary replacement
value and must not be treated as deletion. The verifier's fixed JSON adapter
represents removal with a boolean operation flag and converts it to
`undefined` inside the child process. No executable value crosses the boundary.

Supported options:

```js
{
  formattingOptions?: FormattingOptions,
  isArrayInsertion?: boolean
}
```

- With `isArrayInsertion: true`, a numeric array path inserts at that index
  rather than replacing the existing item.
- A final array segment of `-1` appends.
- Without `formattingOptions`, newly serialized JSON values are compact.
- With formatting options, the changed region is formatted consistently with
  those options.
- Traversing through a scalar parent is an error rather than silently replacing
  unrelated structure.
- `getInsertionIndex` and all callback-valued options are outside this task.

Every returned edit has the shape `{ offset, length, content }`. Offsets and
lengths refer to the original input, are non-negative, and remain within the
input text.

## `format(documentText, range, options)`

**Import path:** package root.

**Signature:**

```js
format(documentText, range, options)
```

Return textual edits that adjust safe whitespace while preserving JSON/JSONC
tokens and comments. `range` is either `undefined` or
`{ offset, length }`; range offsets refer to the original document. A range
formats the complete lines touched by that range while leaving unrelated text
unchanged.

`FormattingOptions` supports:

| Field | Type and behavior |
| --- | --- |
| `tabSize` | Positive integer indentation width; the default width is 4. |
| `insertSpaces` | Use spaces when true; use tab characters when false. |
| `eol` | `"\n"`, `"\r"`, or `"\r\n"`; existing document line endings take precedence when detectable. |
| `insertFinalNewline` | Add one final line ending when true. |
| `keepLines` | Preserve existing line placement and repeated blank lines while normalizing indentation and safe intra-line spaces. |

Normal full-document formatting places non-empty object properties and array
items on separate lines, uses one space after `:`, removes unnecessary spaces
before `:`, and keeps empty arrays/objects compact. Comments are retained:
inline block comments keep a separating space, and line comments force the
following token onto a new line. On malformed input, do not reorder or delete
unknown tokens; only apply formatting where scanner state makes the edit safe.

## `applyEdits(text, edits)`

**Import path:** package root.

**Signature:**

```js
applyEdits(text, edits)
```

Apply edits to `text` and return the resulting string. The function must work
when non-overlapping edits are supplied out of offset order: sort a copy by
ascending offset and, for equal offsets, ascending length, then apply from the
end of the document. Do not mutate the caller's edit array. If two edits overlap
in the original document, throw `Error("Overlapping edit")`.

# Implementation Notes

- Reproduce the observable behavior described above, not generic strict
  `JSON.parse` behavior. Comments, tolerant recovery, parse diagnostics,
  formatting edits, and path-based modifications are core requirements.
- Keep edit offsets based on JavaScript string indexing (UTF-16 code units).
- Keep all behavior deterministic. Do not use network access, current time,
  random state, filesystem configuration, browser globals, or environment
  variables to change results.
- The scored adapter imports only the fixed package name and exposes fixed
  parse/modify/format/apply operations. It bounds request/response sizes and
  validates every option, path segment, range, and edit before invoking the
  package.

# Examples

```js
import { parse, modify, applyEdits } from 'jsonc-parser'
const errors = []
const value = parse('{ // note\n "a": 1 }', errors)
const edits = modify('{"a":1}', ['a'], 2)
assert.equal(applyEdits('{"a":1}', edits), '{"a":2}')
```

```js
import { format } from 'jsonc-parser'
format('{"a":1}', undefined, { tabSize: 2, insertSpaces: true })
```

# Error Handling and Boundary Conditions

- Invalid JSONC returns the recoverable value and appends structured
  diagnostics; unsupported error codes print `<unknown ParseErrorCode>`.
- Edits must stay within the original text and overlapping edits throw
  `Error("Overlapping edit")` without mutating the caller's array.
- UTF-16 offsets, comments, malformed tokens, and line endings remain stable;
  no filesystem, clock, subprocess, or network affects results.

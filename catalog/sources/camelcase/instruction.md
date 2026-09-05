# Project Description

Build an installable ESM npm package named `camelcase` from an empty workspace.
It converts dash, dot, underscore, and space separated text into camelCase or
PascalCase while handling Unicode letters and numeric boundaries.

# Natural Language Instruction

Create the `camelcase` package from an empty workspace. Implement the default
ESM conversion function, all documented options, and the package metadata and
entry files below. Preserve input immutability, Unicode handling, option
defaults, and deterministic string output.

# Supports

- Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with glibc.
- Package name `camelcase`, version `9.0.0`, and a default ESM export at the
  package root.
- A committed npm lockfile with `lockfileVersion: 3`.
- No runtime dependencies, lifecycle scripts, workspaces, native addons,
  loaders, registry configuration, or runtime network access.
- String input or a read-only array of strings. Evaluation uses a JSON child
  process and does not require a CLI.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

# API Usage Guide

Export the default function `camelCase` from the package root. Its signature is
`camelCase(input: string | readonly string[], options?: Options): string`.
Reject any other input type with a `TypeError` whose message explains that the
input must be `string | string[]`.

For a string, trim outer whitespace, preserve leading `_` and `$` characters,
collapse runs of `-`, `_`, `.`, and spaces, and uppercase the next identifier
character. Lowercase ordinary uppercase input as needed, while preserving
Unicode letters and non-separator punctuation. For an array, trim each element,
discard empty elements, join the remaining elements with `-`, and apply the
same rules. Empty strings and separator-only strings return the appropriate
empty string or semantic leading prefix.

Options are all optional and default to `false`, `false`, and `true` respectively:

- `pascalCase: boolean` uppercases the first output character after any leading
  `_` or `$` prefix. For example, `camelCase('foo-bar', {pascalCase: true})`
  returns `FooBar`.
- `preserveConsecutiveUppercase: boolean` keeps consecutive uppercase runs in
  their original form at word boundaries. For example,
  `camelCase('foo-BAR', {preserveConsecutiveUppercase: true})` returns `fooBAR`,
  while the default returns `fooBar`.
- `capitalizeAfterNumber: boolean` controls letters immediately following a
  numeric run. When true (the default), `foo2bar` becomes `foo2Bar`; when false,
  it becomes `foo2bar` and preserves the original case after the digits.
  Separators still create boundaries in either mode.
- `locale: false | string | readonly string[]` selects JavaScript locale case
  conversion. A locale string or non-empty locale array may produce locale-
  specific results such as `camelCase('lorem-ipsum', {locale: 'tr-TR'})`
  returning `loremİpsum`. `locale: false` uses Unicode default case conversion
  and must not call the locale-aware string methods.

Return a primitive string, do not mutate array inputs, and preserve punctuation,
emoji, zero-width joiners, and non-Latin text except where a documented
separator or case conversion applies.

# Implementation Notes

The package is ESM (`"type": "module"`) and must expose `index.js` and
`index.d.ts` through its root export. Keep the implementation deterministic under
`TZ=UTC`, though this API does not otherwise depend on time. Pack and install
entirely offline with lifecycle scripts disabled. The evaluator observes only
the documented default export through an isolated child process; private tests,
the Oracle implementation, and verifier internals are not part of the package
to implement.

# Examples

```js
import camelCase from 'camelcase';
camelCase('foo-bar'); // 'fooBar'
camelCase('foo-bar', {pascalCase: true}); // 'FooBar'
```

# Error Handling and Boundary Conditions

```js
camelCase([' foo ', '', 'bar']); // 'fooBar'
// Non-string, non-array input must throw TypeError; punctuation and Unicode
// characters remain stable except where documented case conversion applies.
```

The generated project must also expose package metadata consistently from the
root entry and declaration file. The lockfile must describe the same package
name and version, and installation must work offline with scripts disabled.
Options with omitted fields use the documented defaults. Results are ordinary
primitive strings and must not retain mutable references to array input.

The package root remains the only runtime entry point. The declaration file
must describe the default function and the options object without requiring a
TypeScript build at runtime. Separator handling is deterministic for ASCII and
Unicode input, and array input is read without mutation.

The implementation must preserve the distinction between an omitted option and
an explicit `false` option. It must not mutate an input array while trimming or
joining elements. Locale conversion is applied only when requested, and all
other case conversion uses JavaScript's ordinary Unicode string behavior.

Malformed option values should follow the package's normal JavaScript error
behavior and must not be silently converted to another option type. A caller
can invoke the default export repeatedly with different option objects; one
call's locale, capitalization, or array handling must not alter later calls.

The output remains a primitive string even when the input is an array. Preserve
leading semantic prefix characters, punctuation, emoji, and non-Latin letters
unless the documented separator or case-conversion rule explicitly changes
them.

# Build `string-width`

## Project Description

Create an installable npm package named `string-width`, version `8.2.2`, from an
empty workspace. Its default export measures the number of terminal columns
needed to display a string while handling ANSI escapes, Unicode grapheme
clusters, East Asian width, combining marks, Hangul jamo, and emoji.

## Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64` with glibc.
- ESM package semantics: `package.json` must declare `"type": "module"`.
- The package root must expose the default function using an export map with
  `types: "./index.d.ts"` and `default: "./index.js"`.
- Include `index.js`, `index.d.ts`, and a v3 `package-lock.json` consistent with
  the manifest. Runtime dependencies are exact pins for
  `get-east-asian-width@1.5.0` and `strip-ansi@7.1.2` (with the locked
  `ansi-regex@6.3.0` transitive package).
- A clean workspace must install and pack without network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

- Do not use native addons, workspaces, lifecycle hooks, custom loaders, or
  runtime network services. Do not put tests, verifier files, Oracle material,
  or npm cache data in the generated package.

## API Usage Guide

Import the default ESM export from the package root:

```js
import stringWidth from 'string-width';

stringWidth('hello'); // 5
stringWidth('你好'); // 4
stringWidth('\u001B[31mred\u001B[0m'); // 3
```

The complete runtime signature is:

```ts
stringWidth(string: string, options?: Options): number
```

For a non-string input, return `0`. For an empty string, return `0`. For
ordinary printable ASCII, the result is the number of characters. Count
full-width CJK characters as 2, ordinary Latin characters as 1, and ignore
control characters, tabs, combining-only clusters, variation selectors, and
default-ignorable characters. Combining marks attached to a visible base do
not add width. Halfwidth Katakana spacing marks and prolonged sound marks are
counted according to their East Asian width.

Grapheme-aware behavior is required: modern Hangul leading-vowel-trailing
jamo sequences form a width-2 syllable, emoji graphemes such as flags, skin
tone sequences, keycaps, and RGI ZWJ sequences are width 2, while a lone
regional indicator is width 1. Non-RGI text symbols follow their East Asian
width and variation-selector presentation. ANSI CSI and OSC sequences are
stripped by default before measuring.

`options` is an object with these optional booleans:

- `ambiguousIsNarrow` (default `true`): ambiguous East Asian characters such
  as `±`, `×`, and `÷` have width 1 when true and width 2 when false.
- `countAnsiEscapeCodes` (default `false`): when true, ANSI escape bytes are
  measured as ordinary non-control text instead of being stripped.

The function is synchronous, deterministic, and does not mutate input. It
must remain safe for long bounded strings and malformed lone surrogate input.

## Implementation Notes

Keep the package self-contained as a normal ESM library and provide the public
TypeScript declaration. Preserve Unicode code-point and grapheme semantics
without locale-dependent behavior. The scored verifier invokes only the
default export through a UID-separated JSON child process; JSON-compatible
strings, numbers, null, and the two boolean options are the scored boundary.
Filesystem objects, callbacks, symbols, custom prototypes, and cyclic object
graphs are outside that boundary. Do not copy the pinned upstream source or
tests.

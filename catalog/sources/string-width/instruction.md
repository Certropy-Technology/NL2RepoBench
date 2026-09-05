# Project Description

Create an installable npm package named `string-width`, version `8.2.2`, from an
empty workspace. Its default export measures the number of terminal columns
needed to display a string while handling ANSI escapes, Unicode grapheme
clusters, East Asian width, combining marks, Hangul jamo, and emoji.

## Natural Language Instruction

Create `string-width` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name and package-root import: `string-width`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: get-east-asian-width@1.5.0, strip-ansi@7.1.2, ansi-regex@6.3.0. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `53` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

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

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
import stringWidth from 'string-width';

stringWidth('hello'); // 5
stringWidth('你好'); // 4
stringWidth('\u001B[31mred\u001B[0m'); // 3
```

```javascript
stringWidth(string: string, options?: Options): number
```

```javascript
import api from 'string-width';
console.log(typeof api);
```

```javascript
const api = require('string-width');
console.log(typeof api);
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.

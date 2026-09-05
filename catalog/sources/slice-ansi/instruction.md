# Project Description

Build an installable npm package named `slice-ansi`, version `9.0.0`, from an
empty workspace. The package provides one ESM default export that slices a
terminal string by visible display columns while preserving ANSI styles,
OSC-8 hyperlinks, Unicode width, and grapheme-cluster boundaries.

This is a repository-generation task. Implement the documented behavior with
your own source and package files. Do not download, clone, or copy the pinned
upstream implementation or its tests.

## Natural Language Instruction

Create `slice-ansi` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name and package-root import: `slice-ansi`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: ansi-styles, is-fullwidth-code-point, get-east-asian-width. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `24` cases when that value is frozen in metadata;
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

### Default export `sliceAnsi`

**Import path:** the package root.

**Signature:**

```ts
export default function sliceAnsi(
  string: string,
  startSlice: number,
  endSlice?: number,
): string;
```

`string` is a JavaScript string that may contain ordinary text, ANSI/VT
control sequences, or OSC-8 hyperlinks. `startSlice` and `endSlice` are
zero-based visible-column boundaries. The returned value contains the
selected text and only the control sequences needed to preserve the active
formatting of that selection.

The function is synchronous, does not mutate its arguments, and returns a new
string. The documented JSON boundary supplies finite numeric indexes and
strings. Values outside that domain, including symbols, BigInt, cyclic data,
custom objects, and non-finite numbers, are not scored.

### Visible columns and boundaries

- Ordinary narrow graphemes count as one visible column.
- East Asian Fullwidth/Wide characters count as two columns.
- Emoji-style graphemes, regional-indicator flags, keycaps, skin-tone
  sequences, combining-mark sequences, Hangul Jamo sequences, and ZWJ emoji
  sequences remain intact and are not split.
- A grapheme whose full width would cross `endSlice` is excluded. If the
  boundary falls inside a two-column grapheme, neither part is returned.
- When `endSlice` is omitted, slicing continues to the end after applying the
  same grapheme-safe start rule. A `startSlice` inside a wide grapheme skips
  that grapheme.
- CRLF is one grapheme cluster and is preserved as both characters.
- Empty or out-of-range selections return the empty string. A selection with
  no visible text must not contain style or hyperlink control codes.

Examples:

```js
sliceAnsi('abcdef', 1, 4); // 'bcd'
sliceAnsi('A\u3042B', 0, 2); // 'A'
sliceAnsi('A\u3042B', 1, 3); // '\u3042'
sliceAnsi('Ae\u0301B', 1, 2); // 'e\u0301'
```

### ANSI and VT controls

Recognize and exclude from visible-column counting:

- 7-bit CSI sequences beginning with `ESC [` and 8-bit CSI (`U+009B`),
  including SGR parameters separated by semicolons or colons.
- SGR style starts and ends, including modifier, foreground, background, and
  truecolor forms. Active styles are reopened at the start of a non-empty
  slice and closed in reverse order at its end.
- SGR reset and style replacement. A later style in the same family replaces
  the previous active style; closing one family preserves other active
  families.
- Non-SGR CSI sequences, malformed/truncated CSI prefixes, and generic OSC,
  DCS, SOS, PM, APC, and standalone ST control strings as non-visible control
  text. Do not swallow ordinary visible text after an incomplete prefix.

Known or unknown SGR codes must remain in the returned control text when they
are part of the selected range. Unknown active codes are closed with a reset
when required to avoid leaking formatting.

### OSC-8 hyperlinks

Recognize hyperlinks introduced by either `ESC ]8;` or 8-bit OSC (`U+009D`
followed by `8;`). Accept BEL, `ESC \\`, and 8-bit ST (`U+009C`) terminators,
including URI parameters. Hyperlink control text is not visible. A non-empty
slice inside a hyperlink preserves its opening form and emits a matching
closing form. A slice containing only a hyperlink opening or closing emits no
empty hyperlink. Mixed opening and closing terminators are preserved when
possible, and a generated close uses the opening prefix and its terminator.

### Packaging

Keep the implementation self-contained behind the package root. Include a
matching TypeScript declaration for the default export. Do not expose a CLI or
copy upstream tests or a reference implementation. Keep the package root
independent of process-global state and external services.

## Implementation Notes

The frozen source's original AVA suite exercises 94 assertions and includes
randomized checks. The production contract is a deterministic 24-leaf
`node:test` slice covering package shape, ordinary and wide text, grapheme
boundaries, ANSI/SGR state, OSC-8 links, malformed controls, and stateless
repeatability. This is a documented boundary adaptation, not a claim of full
upstream test parity.

Use a bounded parser or tokenizer for control sequences and a deterministic
Unicode grapheme/width strategy. The public function accepts strings and
numeric slice bounds; it must not write reports or depend on files, services,
or process-global evaluation state.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
export default function sliceAnsi(
  string: string,
  startSlice: number,
  endSlice?: number,
): string;
```

```javascript
sliceAnsi('abcdef', 1, 4); // 'bcd'
sliceAnsi('A\u3042B', 0, 2); // 'A'
sliceAnsi('A\u3042B', 1, 3); // '\u3042'
sliceAnsi('Ae\u0301B', 1, 2); // 'e\u0301'
```

```javascript
import api from 'slice-ansi';
console.log(typeof api);
```

```javascript
const api = require('slice-ansi');
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

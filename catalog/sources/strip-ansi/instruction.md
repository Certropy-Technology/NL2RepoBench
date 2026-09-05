# Project Description

Build a complete installable npm package named `strip-ansi`, version `7.2.0`,
from an empty workspace. The package removes ANSI/VT terminal escape sequences
from strings while preserving all ordinary text.

This is a repository-generation task. Implement the described public contract
with your own package files; do not fetch or copy a reference repository.

## Natural Language Instruction

Create `strip-ansi` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name and package-root import: `strip-ansi`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: ansi-regex. Standard-library modules are not dependencies.
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

### Default export `stripAnsi(string)`

**Import path:** the package root.

**Signature:**

```ts
export default function stripAnsi(string: string): string;
```

The default export is a synchronous function. It removes every recognized
ANSI/VT control sequence from the supplied string and returns the remaining
text in its original order.

The required sequence families are:

- CSI sequences introduced by either `ESC [` (`\u001B[`) or the 8-bit CSI
  byte (`\u009B`). This includes SGR styling, semicolon- or colon-separated
  color parameters, erase/cursor commands, and private-mode commands.
- OSC control strings introduced by `ESC ]` (`\u001B]`) and terminated by
  BEL (`\u0007`), the two-character string terminator `ESC \\`, or the 8-bit
  ST byte (`\u009C`). The whole OSC control string is removed. This covers
  terminal titles and OSC 8 hyperlinks.

All matching sequences are removed, not only the first one. Ordinary ASCII,
Unicode, emoji, spaces, tabs, LF, CRLF, punctuation, and text between or around
the sequences must remain unchanged. Empty strings and strings without a
recognized control sequence are returned unchanged. Calls are stateless and
must return the same result when repeated.

If the argument is not a string, throw a `TypeError` with this exact message:

```text
Expected a `string`, got `<typeof value>`
```

Here `<typeof value>` uses JavaScript's `typeof` result, so `null`, arrays, and
plain objects report `object`.

Examples:

```js
import stripAnsi from 'strip-ansi';

stripAnsi('\u001B[4mUnicorn\u001B[0m');
// 'Unicorn'

stripAnsi('\u001B]8;;https://example.com\u0007Click\u001B]8;;\u0007');
// 'Click'

stripAnsi('\u009B31mred\u009B39m');
// 'red'
```

## Implementation Notes

Keep the public surface intentionally small: one default ESM function and its
declaration. Escape-sequence parsing must be bounded for ordinary string input
and must not mutate process-global regular-expression state between calls.
Preserve text exactly except for the recognized control sequences described
above.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
export default function stripAnsi(string: string): string;
```

```javascript
Expected a `string`, got `<typeof value>`
```

```javascript
import stripAnsi from 'strip-ansi';

stripAnsi('\u001B[4mUnicorn\u001B[0m');
// 'Unicorn'

stripAnsi('\u001B]8;;https://example.com\u0007Click\u001B]8;;\u0007');
// 'Click'

stripAnsi('\u009B31mred\u009B39m');
// 'red'
```

```javascript
const api = require('strip-ansi');
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

# Build `has-ansi`

## Project Description

Create a complete installable npm package named `has-ansi`, version `6.0.2`,
from an empty workspace. It is an ESM utility whose default export reports
whether a string contains an ANSI escape sequence. The evaluator uses a
JSON-safe child process and observes only the documented function result.

This is a repository-generation task. Implement the behavior with your own
package files; do not copy the pinned upstream source or tests.

## Supports

- Node.js `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- A package root with `"type": "module"`, package name `has-ansi`, version
  `6.0.2`, and an `exports["."]` map with a JavaScript default entry and a
  TypeScript declaration entry.
- A committed npm lockfile with `lockfileVersion: 3` and an offline clean
  install using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- The runtime dependency `ansi-regex` may be declared, but all dependencies
  must be represented by the lockfile. Do not use native addons, workspaces,
  custom loaders, registry configuration, or runtime network access.
- No lifecycle scripts that execute during installation. The verifier ignores
  lifecycle scripts and does not run a publish workflow.

## API Usage Guide

Export one default function from the package root:

```js
import hasAnsi from 'has-ansi';

hasAnsi('\u001B[4mUnicorn\u001B[0m'); // true
hasAnsi('cake'); // false
```

The signature is `hasAnsi(string: string): boolean`. It must return a primitive
boolean and must not mutate the input. Return `true` when the input contains at
least one ANSI terminal control sequence, including common SGR/CSI sequences
such as `\u001B[31m`, reset sequences, cursor controls, and OSC-style terminal
sequences. Return `false` for ordinary text, empty strings, whitespace,
Unicode text without controls, and literal backslash text such as
`"\\u001B[31m"`.

The function must detect a sequence anywhere in the string, including at the
start, end, between ordinary text, and across multiple lines. The detector
follows the accepted ANSI grammar, including CSI prefixes with numeric
parameters; a lone escape or an escape followed by a non-control character is
not enough. Inputs other than strings are outside the scored API contract and
may raise a normal JavaScript error.

## Implementation Notes

Use ESM semantics and expose `index.js` and `index.d.ts` through the package
root export. Keep the package deterministic and self-contained apart from its
declared npm dependency. The verifier launches a fresh child process for each
JSON request, with no network and with candidate code outside the trusted
`node:test` process. Private tests, the child adapter, the Oracle solution, and
verifier internals are not part of the package to implement.

## Natural Language Instruction

Build the package from an empty workspace. Implement the default root predicate,
package metadata, and declaration. Detect accepted ANSI escape sequences at
any position while preserving ordinary text and rejecting incomplete escapes.
Keep the synchronous API pure; do not add filesystem, process, TTY, or network
behavior.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

The package is ESM version `6.0.2`, rooted at `index.js`, with its declared
`ansi-regex` `6.3.0` runtime closure. Private test and verifier files are not
part of the generated workspace.

## Examples

```js
import hasAnsi from 'has-ansi';
hasAnsi('\u001B[31mred\u001B[0m'); // true
```

```js
import hasAnsi from 'has-ansi';
hasAnsi('plain text'); // false
```

## Error Handling and Boundary Conditions

- The result is a primitive boolean and the input is never mutated.
- Empty strings, ordinary Unicode, and the literal characters `\\u001B[31m`
  return `false`; valid CSI, SGR, cursor, OSC, C1, parameter, and intermediate
  forms follow the declared ANSI grammar.
- A lone escape or an incomplete sequence is not accepted. Non-string values
  are outside the scored input domain. All execution uses `network_mode=no-network`.

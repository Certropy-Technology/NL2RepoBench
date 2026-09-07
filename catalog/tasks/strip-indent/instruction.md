# Project Description

Build an installable ESM npm package named `strip-indent`, version `4.1.1`,
from an empty workspace. The package removes a common amount of leading spaces
and tabs from every line in a string and also provides a boundary-trimming
variant for template literals.

## Natural Language Instruction

Create `strip-indent` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name and package-root import: `strip-indent`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: no declared third-party runtime packages. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `32` cases when that value is frozen in metadata;
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

### Default export `stripIndent(string)`

**Import path:** the package root.

**Signature:**

```ts
export default function stripIndent(string: string): string;
```

The function examines every line that contains a non-whitespace character.
Among those lines, it finds the smallest number of consecutive leading ASCII
spaces and tab characters. It removes exactly that many leading spaces or tabs
from every line that has at least that many, and returns the resulting string.

Spaces and tabs each count as one character. They may be mixed. Empty and
whitespace-only lines do not determine the minimum indentation, but they are
otherwise preserved. A whitespace-only line loses the common prefix only when
it contains at least that many leading spaces or tabs. Newline characters,
including CRLF line endings, content characters, internal blank lines, and
trailing spaces after content are preserved. If there is no non-whitespace
line, or if any non-whitespace line begins at column zero, the original string
is returned unchanged.

```js
import stripIndent from 'strip-indent';

stripIndent('\talpha\n\t\tbeta'); // 'alpha\n\tbeta'
stripIndent('  alpha\n    beta'); // 'alpha\n  beta'
```

The input must be a primitive JavaScript string. Calling the function with a
non-string value throws `TypeError`. It does not coerce values and does not
mutate the input.

### Named export `dedent(string)`

**Import path:** the package root.

**Signature:**

```ts
export function dedent(string: string): string;
```

`dedent` first removes all leading and trailing lines that contain only ASCII
spaces or tabs. A boundary line includes its adjacent LF or CRLF newline. It
then applies the exact `stripIndent` behavior above. Whitespace-only lines in
the middle of the content are preserved, as are their remaining spaces or tabs
after common indentation is removed.

```js
import {dedent} from 'strip-indent';

dedent('\n\talpha\n\t\tbeta\n'); // 'alpha\n\tbeta'
```

An empty string or a string made only of boundary whitespace lines produces an
empty string. A non-string input throws `TypeError` without coercion.

## Implementation Notes

Use an ESM `package.json` with a safe root export to `index.js` and a matching
`index.d.ts`. Keep the runtime surface to the documented default and named
functions. JavaScript string length semantics apply to the leading ASCII space
and tab prefix. Other JavaScript whitespace characters are not counted as
indentation, and a line containing only whitespace is ignored when determining
the minimum.
The evaluator invokes each export through an isolated JSON child process.
Private tests and the Oracle implementation are not part of the package to
implement.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
export default function stripIndent(string: string): string;
```

```javascript
import stripIndent from 'strip-indent';

stripIndent('\talpha\n\t\tbeta'); // 'alpha\n\tbeta'
stripIndent('  alpha\n    beta'); // 'alpha\n  beta'
```

```javascript
export function dedent(string: string): string;
```

```javascript
import {dedent} from 'strip-indent';

dedent('\n\talpha\n\t\tbeta\n'); // 'alpha\n\tbeta'
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.

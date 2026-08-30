# Project Description

Build an installable ESM npm package named `strip-indent`, version `4.1.1`,
from an empty workspace. The package removes a common amount of leading spaces
and tabs from every line in a string and also provides a boundary-trimming
variant for template literals.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package root exposes one default function and the named `dedent`
  function, with matching TypeScript declarations.
- Commit an npm lockfile with `lockfileVersion: 3`. A clean verifier must be
  able to install the package without network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The package has no runtime dependencies. Do not add dependencies, workspaces,
  native addons, registry overrides, lifecycle scripts, or a CLI.
- Runtime behavior is synchronous, deterministic, stateless, and offline. Do
  not read files, use the clock or randomness, spawn processes, access a TTY,
  or access the network.

# API Usage Guide

## Default export `stripIndent(string)`

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

## Named export `dedent(string)`

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

# Implementation Notes

Use an ESM `package.json` with a safe root export to `index.js` and a matching
`index.d.ts`. Keep the runtime surface to the documented default and named
functions. JavaScript string length semantics apply to the leading ASCII space
and tab prefix. Other JavaScript whitespace characters are not counted as
indentation, and a line containing only whitespace is ignored when determining
the minimum.
The evaluator invokes each export through an isolated JSON child process.
Private tests and the Oracle implementation are not part of the package to
implement.

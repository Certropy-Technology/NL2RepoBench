# Build `hast-util-whitespace`

## Project Description

Create an installable npm package named `hast-util-whitespace`, version
`3.0.0`, from an empty workspace. The package provides one ESM utility for
recognizing HTML inter-element whitespace in either a string or a HAST-style
text node.

The implementation is evaluated through a separate subprocess verifier. The
verifier checks the public package boundary and deterministic behavior; it does
not require the upstream repository, its development tooling, or its tests to
be copied into the generated workspace.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must name version `3.0.0`, use ESM via `"type": "module"`,
  and expose `"./index.js"` as the package root.
- The package has no runtime dependencies. Use a v3 `package-lock.json` so a
  clean verifier can run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use lifecycle hooks, workspaces, native addons, custom loaders,
  browser globals, random state, current time, or network access.

## API Usage Guide

### `whitespace`

Import the named export from the package root:

```js
import {whitespace} from 'hast-util-whitespace'
```

Signature:

```ts
export function whitespace(thing: Nodes | string): boolean
```

For a string, return `true` exactly when every code unit is one of the five
ASCII HTML whitespace characters: space (`U+0020`), tab (`U+0009`), line feed
(`U+000A`), form feed (`U+000C`), or carriage return (`U+000D`). The empty
string is valid and returns `true`. Other control characters and Unicode
whitespace characters are not part of this set.

For an ordinary object representing a HAST node, return `true` only when its
`type` is exactly `"text"` and its string `value` satisfies the same rule.
Return `false` for other node types, including comments and elements, even if
their `value` consists only of ASCII whitespace.

The function is synchronous, has no side effects, preserves no state between
calls, and returns a primitive boolean. The named root export must be the only
public export. Inputs in the supported domain are ordinary JSON-compatible
strings and node objects; do not mutate them.

Examples:

```js
whitespace(' \t\n') // true
whitespace({type: 'text', value: '\f\r'}) // true
whitespace({type: 'comment', value: ' '}) // false
whitespace('\u00a0') // false
```

## Implementation Notes

Keep the package self-contained and make the root import work after npm
installation from a clean directory. Preserve the distinction between text
nodes and all other node types, and use the exact five-character ASCII set
above rather than a broad Unicode whitespace predicate. The package should
remain deterministic for repeated calls and should not require any filesystem,
TTY, callback, asynchronous, or external-service behavior.

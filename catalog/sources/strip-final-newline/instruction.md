# Build `strip-final-newline`

## Project Description

Create a complete installable npm package named `strip-final-newline`, version
`4.0.0`, from an empty workspace. The package removes the final newline from a
string or a byte-oriented `Uint8Array` without removing earlier newlines or
other trailing characters.

This is a repository-generation task. Implement the described behavior with
your own files; do not fetch or copy a reference repository or its tests.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package root must be importable with `import stripFinalNewline from
  'strip-final-newline'`.
- `package.json` must identify version `4.0.0`, use `"type": "module"`, and
  export `./index.js` as the default root export with `./index.d.ts` as its
  type entry in the exports map.
- Commit a package lockfile with `lockfileVersion: 3`. A clean verifier runs:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The runtime package has no dependencies. Do not use native addons, npm
  workspaces, custom loaders, lifecycle hooks, generated downloads, or network
  access.
- Runtime behavior is deterministic and local. Do not inspect the filesystem,
  environment, clock, randomness, subprocesses, or network.

## API Usage Guide

### Default export `stripFinalNewline(input)`

**Import path:** the package root.

**Signature:**

```ts
export default function stripFinalNewline<T extends string | Uint8Array>(input: T): T;
```

For a string, remove one final line-feed character (`\\n`, U+000A) when it is
present. If that line feed is immediately preceded by a carriage return
(`\\r`, U+000D), remove the CRLF pair together. Remove only the final newline
sequence: for example, `"a\\n\\n"` becomes `"a\\n"`, and `"a\\n\\r\\n"`
becomes `"a\\n"`. A string without a final LF, including one ending in a lone
CR, is returned unchanged.

For a `Uint8Array`, apply the same rule to bytes: LF is `0x0A` and CR is
`0x0D`. Preserve every earlier byte in order. The result must remain a
`Uint8Array`; when bytes are removed, it may be a view over the original
storage, so callers must not assume it is copied. When no final LF is present,
the input object may be returned as-is.

The function must throw an `Error` whose message states `Input must be` for
values outside the supported string and `Uint8Array` inputs. In particular,
booleans, `DataView`, and multi-byte typed arrays are invalid. Do not coerce
invalid values.

Examples:

```js
import stripFinalNewline from 'strip-final-newline';

stripFinalNewline('foo\nbar\n\n');
//=> 'foo\nbar\n'

const bytes = new TextEncoder().encode('foo\nbar\n');
new TextDecoder().decode(stripFinalNewline(bytes));
//=> 'foo\nbar'
```

## Implementation Notes

Keep the public surface to one default ESM function and its TypeScript
declaration. Preserve the input type and byte order, avoid trimming spaces or
other control characters, and keep the implementation independent of global
mutable state and external resources.

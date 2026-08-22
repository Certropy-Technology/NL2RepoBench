# Build `canonicalize`

## Project Description

Build an installable npm package named `canonicalize`, version `4.0.0`, that
produces deterministic canonical JSON text for signing, hashing, and other
content-addressed uses. The package must be implementable from an empty
workspace and must expose the public library API described below.

The scored library contract is the JSON-compatible subset of the upstream
package. It deliberately excludes JavaScript-only values and side-effecting
entry points so that calls can cross a bounded JSON subprocess boundary.

## Supports

- Run on Node `22.23.1` with npm `10.9.8` on `linux/amd64`.
- Use ESM package semantics (`"type": "module"`). The package root must be
  importable as `canonicalize` through an `exports["."]` entry with an
  `import` condition. Preserve the upstream type declaration condition when a
  declaration file is provided; do not add a CommonJS `require` export for the
  scored API.
- Provide a committed npm lockfile using lockfile version 3. The manifest and
  lockfile must agree, and a clean environment must support
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Have no runtime dependencies, native addons, workspaces, custom loaders,
  registry configuration, or lifecycle scripts. The verifier will not run
  install or build scripts.
- Keep the implementation and package metadata inside the generated package;
  do not depend on a checkout path, network service, current time, or random
  source.

The upstream command-line binary and its network-oriented README examples are
outside this pilot's scored API. They must not be needed by the library
contract or by tests.

## API Usage Guide

### `canonicalize`

**Import path:** the package default export from `canonicalize`.

**Signature:**

```js
canonicalize(value)
```

**Input:** one JSON value, recursively composed only of `null`, booleans,
finite JSON numbers, strings containing no unpaired surrogate code units,
arrays of JSON values, and objects whose values are JSON values. Object member
names follow the same no-unpaired-surrogate rule. Values such as `undefined`,
non-finite numbers, symbols, functions, `BigInt`, class instances, `Date`,
custom `toJSON` methods, and cyclic references are outside this contract.

**Return:** a string containing the canonical JSON representation. For every
in-scope value the result is a string, not an object or byte array.

**Ordering and determinism:**

- Object member names are sorted recursively by their UTF-16 code-unit order.
- Array order is preserved; arrays are not sorted.
- The output contains no insignificant whitespace and has no trailing newline.
- Repeated calls with the same JSON value produce byte-for-byte identical
  strings, regardless of object insertion order. The input value is not
  mutated.
- JSON string escaping follows JSON serialization rules. Valid surrogate pairs
  are preserved; lone surrogate code units are rejected because they are not
  valid canonical JSON strings.
- Number formatting follows the RFC 8785 / ECMAScript JSON serialization
  rules. In particular, `-0` is rendered as `0`; non-finite JavaScript numbers
  are not accepted by this contract.

**Errors:** out-of-domain JavaScript values are not scored as ordinary JSON
inputs. If the function receives a non-finite number or a string/member name
with an unpaired surrogate, it must raise an ordinary `Error` rather than
returning invalid canonical JSON. The exact error message is not part of this
contract.

**Examples:**

```js
import canonicalize from "canonicalize";

canonicalize({ b: 2, a: 1 });
// '{"a":1,"b":2}'

canonicalize({ outer: { z: false, a: null }, list: [3, 1] });
// '{"list":[3,1],"outer":{"a":null,"z":false}}'

canonicalize(-0);
// '0'
```

## Implementation Notes

- Reproduce the observable JSON behavior of the pinned upstream
  `canonicalize` package, whose library entry point is an ESM default export.
  Do not copy the upstream implementation into this instruction.
- Keep the root export unambiguous: importing `canonicalize` must resolve to
  the library function, not to a test helper or CLI process.
- A v3 lockfile is part of the repository-generation task even though the
  pinned upstream checkout has no lockfile. Generate and review it as a
  separate authoring step; do not assume registry access during installation.
- Do not add hidden tests, verifier code, grader output, reward files, or
  private dependency-cache bytes to the generated candidate repository.

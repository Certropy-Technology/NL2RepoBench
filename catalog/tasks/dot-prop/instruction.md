# Build `dot-prop`

## Project Description

Create a complete installable npm package named `dot-prop`, version `10.2.0`,
from an empty workspace. The package is an ESM utility for reading, writing,
deleting, checking, and enumerating nested object properties addressed by dot
paths. It also converts between path strings and path-segment arrays and can
unflatten a flat object.

This is a repository-generation task. Implement the behavior with your own
source files; do not copy the reference repository or its tests.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- ESM package semantics. The package root must be importable with
  `import {getProperty, setProperty, hasProperty, deleteProperty, escapePath, parsePath, stringifyPath, deepKeys, unflatten} from 'dot-prop'`.
- A committed npm v3 lockfile must make the package installable from a clean
  checkout with:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The runtime package has no required runtime dependencies. Do not use git,
  file, workspace, native-addon, or network dependencies, and do not add
  lifecycle hooks that execute candidate code during installation.
- The scored behavior is deterministic and local. Prototype-pollution paths,
  cyclic object graphs, sparse arrays, and deeply nested paths are in scope;
  external services and filesystem persistence are not.

## API Usage Guide

### `getProperty(object, path, defaultValue?)`

Import from `dot-prop`. `object` may be an object, array, function, or
`undefined`; `path` is a string or an array of string/number segments. Return
the value at the path, or `defaultValue` when the path cannot be resolved.
Existing `undefined`, `null`, `false`, `0`, empty strings, and `NaN` are values,
not missing values. A non-object input is returned unchanged when no default is
provided, and returns the default when one is provided. A missing intermediate
object returns the default. Invalid path types are treated as non-resolvable.

String paths use `.` separators, backslash escaping, bracket indexes such as
`users[0].name`, and dot indexes such as `users.0.name`. Canonical non-negative
integer segments without leading zeros are numeric indexes; other strings stay
string keys. The path components `__proto__`, `prototype`, and `constructor`
are invalid and must not be traversed.

### `setProperty(object, path, value)`

Mutate and return the original object. Create missing containers, choosing an
array when the next segment is a numeric index and an object otherwise.
Replace a missing or primitive intermediate value as needed. Preserve existing
objects, arrays, functions, and instances when traversing them. Return the
original non-object unchanged, and ignore an empty or invalid path. Do not allow
the three disallowed prototype-related path components.

### `hasProperty(object, path)` and `deleteProperty(object, path)`

`hasProperty` returns a boolean for reachable properties, including inherited
properties and properties whose value is `undefined`; sparse-array holes are
not properties. `deleteProperty` mutates only an own property and returns
whether deletion occurred. Deleting an array element leaves a hole and keeps
the array length. Both accept string or segment-array paths and reject invalid
inputs safely.

### Path conversion helpers

- `escapePath(path)` accepts a string and prefixes backslashes to backslashes,
  dots, and opening brackets so the result addresses one literal key.
- `parsePath(path)` returns an ordered `Array<string | number>`. It supports
  escaping, empty segments, bracket indexes, dot indexes, literal empty
  brackets (`[]`), and rejects malformed indexes with a `TypeError` or `Error`.
  Disallowed components return an empty array.
- `stringifyPath(pathSegments, options?)` accepts only an array of strings and
  numbers and returns an escaped path. Numbers that are non-negative integers
  use bracket notation by default; `{preferDotForIndices: true}` uses dot
  notation for non-first indexes. Non-integer, negative, and leading-zero
  string values remain string keys. Invalid segment types throw `TypeError`.

### `deepKeys(object)` and `unflatten(object)`

`deepKeys` returns deterministic depth-first paths for leaves and for empty
objects/arrays, but does not return non-empty containers themselves. It skips
symbol properties, supports sparse arrays, treats functions as traversable
objects, and must terminate on cyclic references without overflowing the
stack. Paths must round-trip through the other helpers.

`unflatten` accepts an object whose keys are dot-prop paths and returns a new
nested object using the same escaping, array-index, conflict, and security
rules. Later entries may replace an earlier primitive with a container. A
non-object input returns a new empty object.

## Implementation Notes

- Keep the public entry point at `index.js` and expose the package through a
  normal ESM `package.json` with a matching `index.d.ts` when providing types.
- Preserve insertion order for `deepKeys`, JavaScript property semantics for
  inherited reads, and deterministic return shapes.
- The evaluator invokes the package through a separate child process and JSON
  adapter. Do not assume trusted verifier code can import candidate files
  directly, and do not write verifier-owned reports from the package.
- Installation is offline and lifecycle scripts are ignored. Do not run
  `npm install`, `npm ci`, `git clone`, `curl`, or `wget` as part of the package
  implementation or evaluation behavior.

# Build `uuid`

## Project Description

Build an installable npm package named `uuid`, version `14.0.2`, for RFC 9562
UUID generation, parsing, formatting, validation, and version inspection. The
implementation starts from an empty workspace and must reproduce the
observable behavior of the pinned upstream `uuidjs/uuid` revision described in
the task metadata.

The scored surface is a JSON-compatible subset of the package API. It keeps
UUID strings, numbers, booleans, and hexadecimal byte strings at the process
boundary, while the package itself continues to use the upstream `Uint8Array`
signatures for byte-oriented APIs. JavaScript-only callbacks, typed-array
identity, mutable internal state, and browser behavior are outside this task's
boundary.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use ESM package semantics with `"type": "module"`.
- Make the package root importable as `uuid` through this export shape:

  ```json
  {
    "exports": {
      ".": {
        "node": {
          "types": "./dist/index.d.ts",
          "default": "./dist-node/index.js"
        },
        "default": "./dist/index.js"
      },
      "./package.json": "./package.json"
    }
  }
  ```

  The Node condition is the scored path. Do not add a CommonJS `require`
  condition for the root API.
- Export these named root bindings: `MAX`, `NIL`, `parse`, `stringify`, `v1`,
  `v1ToV6`, `v3`, `v4`, `v5`, `v6`, `v6ToV1`, `v7`, `validate`, and `version`.
  `v3.DNS`, `v3.URL`, `v5.DNS`, and `v5.URL` must expose the standard DNS and
  URL namespace UUID strings.
- Include a v3 `package-lock.json` that agrees with `package.json`. A clean
  verifier environment must support:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

  The verifier owns the reviewed npm cache closure. Do not depend on a
  registry, a checkout path, `npx`, a global loader, current working
  directory, or a network service at run time.
- Do not require runtime dependencies, native addons, workspaces, browser
  globals, lifecycle hooks, or generated files that are absent from the
  submitted package. The verifier will not run install, prepare, prepack, or
  build scripts. A candidate may submit already-built JavaScript and type
  declarations; any development-only compiler is outside the runtime API.
- Do not add a CLI, hidden tests, grader, reward writer, Oracle files, npm
  cache/tarball bytes, credentials, or private verifier material to the
  generated candidate repository.

## API Usage Guide

### Constants

**Import path:** named exports from `uuid`.

```js
import { MAX, NIL } from 'uuid';
```

- `NIL` is the lowercase string
  `00000000-0000-0000-0000-000000000000`.
- `MAX` is the lowercase string
  `ffffffff-ffff-ffff-ffff-ffffffffffff`.
- The constants are ordinary strings and are not mutable package state.

### `validate`

**Import path:** `validate` from `uuid`.

**Signature:**

```js
validate(uuid)
```

**Input:** a UUID candidate. The scored JSON input is a string; non-string
JSON values are accepted by the JavaScript function and return `false` rather
than throwing.

**Return:** a boolean. Valid values are the hyphenated UUID form with a
version nibble from `1` through `8` and an RFC variant nibble from `8` through
`b`, case-insensitively, plus the `NIL` and `MAX` constants. Unhyphenated
32-character strings, malformed hex, an unsupported version nibble, and an
unsupported variant return `false`.

**Examples:**

```js
validate('109156be-c4fb-41ea-b1b4-efe1671c5836'); // true
validate('109156bec4fb41eab1b4efe1671c5836'); // false
validate('not-a-uuid'); // false
validate(null); // false outside the scored string input
```

`validate` must not mutate its input or any global state.

### `version`

**Import path:** `version` from `uuid`.

**Signature:**

```js
version(uuid)
```

**Input and return:** accept a valid UUID string and return its numeric
version nibble. `NIL` returns `0` and `MAX` returns `15`. Invalid strings and
non-string values throw a `TypeError` with the upstream invalid-UUID behavior.

### `parse` and `stringify`

**Import paths:** named exports `parse` and `stringify` from `uuid`.

**Signatures:**

```js
parse(uuid)                 // Uint8Array with exactly 16 bytes
stringify(bytes, offset?)   // lowercase hyphenated UUID string
```

`parse` accepts a valid hyphenated UUID string, including uppercase input, and
returns the 16 bytes in network order. Invalid input throws `TypeError`.
`stringify` formats 16 UUID bytes as lowercase hexadecimal with hyphens. Its
optional offset selects a 16-byte window in the supplied `Uint8Array`; an
invalid byte array or out-of-range window throws according to the upstream
`TypeError`/`RangeError` behavior. The scored transport uses offset `0` only.

Parsing and formatting are inverse operations for valid values:

```js
const bytes = parse('0f5abcd1-c194-47f3-905b-2df7263a084b');
stringify(bytes); // '0f5abcd1-c194-47f3-905b-2df7263a084b'
```

### Namespace UUID generation: `v3` and `v5`

**Import paths:** named exports `v3` and `v5` from `uuid`.

**Signatures:**

```js
v3(name, namespace)
v5(name, namespace)
```

`name` is a string or UTF-8 byte sequence in the upstream API. `namespace`
is a UUID string or a 16-byte sequence. The scored JSON boundary uses a name
string and a namespace UUID string. The result is a lowercase UUID string.
`v3` uses the RFC name-based MD5 construction and version 3; `v5` uses the
RFC name-based SHA-1 construction and version 5. The same name and namespace
produce the same result across processes and calls.

The function properties are stable namespace constants:

```js
v3.DNS === '6ba7b810-9dad-11d1-80b4-00c04fd430c8';
v3.URL === '6ba7b811-9dad-11d1-80b4-00c04fd430c8';
v5.DNS === '6ba7b810-9dad-11d1-80b4-00c04fd430c8';
v5.URL === '6ba7b811-9dad-11d1-80b4-00c04fd430c8';
```

Invalid namespaces and byte sequences with a length other than 16 throw. The
exact error wording is not part of the JSON contract.

### Time and random UUID generation: `v1`, `v4`, `v6`, and `v7`

**Import paths:** named exports `v1`, `v4`, `v6`, and `v7` from `uuid`.

All four functions return a lowercase UUID string when called without a
destination buffer. Buffer destinations and callback-valued `rng` options are
outside the JSON contract.

#### `v4`

```js
v4(options?)
```

With no options, use a cryptographically secure random source and return a
version 4 UUID. An `options.random` 16-byte sequence is accepted by the
upstream API and determines all non-version/variant bits; the JSON adapter
represents it as a 32-hex-digit `random_hex` string. A short sequence throws.
The adapter creates a fresh byte sequence for each call, so upstream masking
of version and variant bits is not observable as input mutation.

#### `v1`

```js
v1(options?)
```

Generate an RFC version 1 time-based UUID. The JSON-compatible options are:

- `msecs`: finite integer milliseconds since the Unix epoch;
- `nsecs`: integer in the range `0..9999`;
- `clockseq`: integer in the range `0..16383`;
- `node_hex`: 12 hexadecimal digits for the six-byte node identifier; and
- `random_hex`: 32 hexadecimal digits used for default node/clock data.

Set the time, sequence, node, and random inputs needed by a test when an exact
result is required. With omitted options the upstream function uses current
time, secure random bytes, and process-local monotonic state.

#### `v6`

```js
v6(options?)
```

Generate the reordered version 6 representation of the version 1 timestamp
fields. It accepts the same JSON options as `v1`, returns a version 6 UUID,
and preserves lexicographic ordering for explicitly increasing timestamps.

#### `v7`

```js
v7(options?)
```

Generate an RFC version 7 Unix-time UUID. The JSON-compatible options are:

- `msecs`: finite integer milliseconds, represented in the UUID timestamp;
- `seq`: integer in the unsigned 32-bit range; and
- `random_hex`: 32 hexadecimal digits for the random input.

Supplying all three values makes the result deterministic. Omitting values
uses current time, secure random bytes, or the upstream sequence rules.

The functions must set the RFC version and variant bits exactly as the pinned
upstream implementation does. Default results are checked structurally, not
against a fixed UUID value.

### `v1ToV6` and `v6ToV1`

**Import paths:** named exports `v1ToV6` and `v6ToV1` from `uuid`.

```js
v1ToV6(uuidString)
v6ToV1(uuidString)
```

For the scored string form, each function accepts a valid UUID string and
returns the corresponding lowercase string representation. These are field
reorderings, not new random UUID generators. Invalid input throws.

## JSON Boundary

The word `generate` in this section names a verifier transport operation; it
is not an additional root export. A verifier-owned child adapter maps one
bounded JSON request to one named package export and maps the result back to
JSON. The candidate package must not add a custom server or CLI to implement
this transport.

The transport uses these representations:

| Operation | JSON input | JSON result |
| --- | --- | --- |
| `generate` version 1, 4, 6, or 7 | version number plus the JSON options above | UUID string |
| `generate` version 3 or 5 | name string and namespace UUID string | UUID string |
| `parse` | UUID string | lowercase 32-hex `bytes_hex` string |
| `stringify` | lowercase or uppercase 32-hex `bytes_hex` string | UUID string |
| `validate` | JSON value, normally a string | boolean |
| `version` | UUID string | number |
| `v1ToV6` or `v6ToV1` | UUID string | UUID string |

The adapter converts `random_hex` and `node_hex` to fresh `Uint8Array` values
before calling the real export. It converts `parse` and `stringify` byte
values at the boundary; the public package signatures remain the typed-array
signatures documented above. A successful response must be JSON-safe and must
not contain a `Uint8Array`, `Buffer`, function, `BigInt`, `Date`, or object
handle.

Inputs are limited to JSON null, booleans, finite numbers, strings, arrays,
and plain objects. Reject or classify as outside the scored contract any
callback, `Uint8Array` supplied directly by a caller, `Buffer`, `BigInt`,
symbol, function, Date, RegExp, custom class, cyclic value, or non-finite
number. The adapter must bound request and response size and terminate a
call that exceeds its time limit.

Errors cross the boundary as a structured error name and message. Preserve
the upstream distinction between `TypeError`, `RangeError`, and ordinary
`Error` where it is observable; do not make exact error text a substitute for
the behavior contract.

## Crypto, Time, and Determinism Policy

- `v3` and `v5` are deterministic for the same name and namespace. They are
  suitable for exact expected-value assertions.
- `v4` without options, and `v1`, `v6`, and `v7` calls that omit random or time
  inputs, are intentionally nondeterministic. They use Node's secure Web
  Crypto source and/or current time. Do not snapshot their default UUIDs.
- Deterministic tests for `v4` use `random_hex`. Deterministic tests for `v1`
  and `v6` provide explicit time, sequence/node, and random fields as needed.
  Deterministic tests for `v7` provide `msecs`, `seq`, and `random_hex`.
- Default-generation tests may assert format, RFC version, variant, UUID
  validity, monotonic ordering where the API promises it, and that a bounded
  pair of calls differs. They must not require a particular random value or
  assume that wall-clock time advances between separate child processes.
- Do not replace secure randomness with `Math.random`, a fixed global seed, a
  host identifier, or a network service. Do not monkey-patch `crypto` in the
  candidate package.
- The upstream v1/v6/v7 state helpers and callback injection paths are useful
  source tests but are not part of the JSON transport. A verifier must use
  explicit options when it needs repeatable bytes and must run stateful probes
  in one deliberately bounded process.

## Implementation Notes

- Reproduce the observable behavior of the pinned `uuid` revision, not a
  generic UUID implementation and not a copied source tree.
- Keep the package root export unambiguous. The Node export must resolve to
  the Node build and the fallback default export must resolve to the browser
  build path named in `package.json`; the scored runtime uses the Node path.
- The official upstream test suite is evidence for the source behavior. Its
  tests import internal modules, construct typed arrays, mock crypto, and
  exercise stateful or browser-adjacent paths. A future private test adapter
  must select only assertions traceable to this public JSON contract and
  freeze its own leaf denominator before packaging.
- Do not include hidden tests, private npm closure bytes, Oracle material,
  verifier code, reward files, credentials, or generated Harbor assets in the
  candidate repository.

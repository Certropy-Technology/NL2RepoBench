# Build `js-yaml`

## Project Description

Create an installable npm package named `js-yaml`, version `5.4.0`, from an
empty workspace. It is an ECMAScript module that parses YAML 1.2 documents into
JSON-compatible JavaScript values and serializes JSON-compatible values back to
deterministic YAML text.

This is a repository-generation task. Reproduce the documented behavior with
your own package files. Do not copy the pinned upstream source or its tests.

## Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64` with glibc.
- The package root is importable as `js-yaml` using ESM named imports. The
  package must contain `"type": "module"`, a safe `exports` entry for `.`, and
  a v3 `package-lock.json` whose root name and version agree with the package.
- A clean verifier installs the candidate with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The scored package has no runtime dependency. It must not need a registry,
  network service, native addon, custom loader, workspace, environment-specific
  path, lifecycle hook, current time, or random state.
- Candidate and verifier code is exercised through a bounded JSON subprocess;
  therefore all scored inputs and outputs must be representable as JSON.
- The CLI, browser bundle, TypeScript declarations, custom schema/tag objects,
  callback iterators, `Map`/`Set` results, functions, cycles, and other
  JavaScript-only values are outside this task. The package may still expose
  extra APIs, but the contract below is the only scored surface.

## API Usage Guide

### `load`

**Import path:** `load` named export from `js-yaml`.

**Signature:** `load(input, options?)`

`input` is a YAML string. The returned value is a JSON-compatible scalar,
array, object, or null. Mapping keys in the scored cases are strings. The
default schema is the YAML 1.2 core schema: plain null, boolean, integer, and
finite float scalars resolve to their corresponding JavaScript values; ordinary
text remains a string. Quoted scalars always remain strings. Nested block and
flow collections, comments, quoted escapes, literal/folded block scalars,
anchors, aliases, explicit core scalar tags, and document markers must work.

The default object mapping behavior must not mutate global prototypes. Inputs
that would create cyclic output through an alias are outside the JSON contract.
Duplicate mapping keys and unsupported tags must raise the package's normal
`YAMLException` class rather than silently selecting an arbitrary value.

`options` is optional. The scored JSON-compatible fields are:

- `filename`: string used in diagnostic context;
- `json`: boolean that enables JSON-compatible duplicate-key behavior where
  supported by the upstream API.

Schema objects, warning callbacks, custom tags, and other non-JSON option
  values are outside the contract.

Examples:

```js
import { load } from 'js-yaml'

load('name: Ada\nroles:\n  - admin\n  - reviewer\n')
// { name: 'Ada', roles: ['admin', 'reviewer'] }

load('payload: { enabled: true, count: 3, empty: null }')
// { payload: { enabled: true, count: 3, empty: null } }
```

### `loadAll`

**Import path:** `loadAll` named export from `js-yaml`.

**Signature:** `loadAll(input, options?)`

Parse a YAML stream and return an array of JSON-compatible documents. An empty
stream returns `[]`; one stream can contain several `---` separated documents.
The same scalar, collection, alias, comment, tag, duplicate-key, and error
rules as `load` apply to each document. The deprecated callback iterator form is
outside the contract and must not be needed by the implementation.

### `dump`

**Import path:** `dump` named export from `js-yaml`.

**Signature:** `dump(value, options?)`

Serialize recursively composed JSON values (null, booleans, finite numbers,
strings, arrays, and plain objects) to YAML. Return a string with a trailing
newline for a collection or scalar document. Object insertion order and array
order are preserved by default. Keys and values must be quoted when YAML
syntax requires it, while normal readable scalars should remain plain.

The scored JSON-compatible options are:

- `flowLevel`: integer `-1` or greater; collections at that depth and below
  use flow notation;
- `indent`: integer from 1 through 10 controlling block indentation;
- `seqNoIndent`: boolean controlling indentation of block sequence items;
- `sortKeys`: boolean; `true` sorts mapping keys lexicographically;
- `flowBracketPadding`: boolean adding spaces inside flow collection brackets;
- `flowSkipCommaSpace`: boolean omitting spaces after flow commas;
- `flowSkipColonSpace`: boolean omitting spaces after flow mapping colons;
- `quoteFlowKeys`: boolean quoting flow mapping keys;
- `quoteStyle`: `"single"` or `"double"` for quoted strings;
- `forceQuotes`: boolean forcing strings to be quoted;
- `lineWidth`: finite number controlling block scalar wrapping.

Invalid option types must raise `TypeError` or the package's documented error
class. Cycles, functions, dates, regular expressions, non-finite numbers,
custom `toJSON`, and other values outside the JSON input domain are not scored.

Examples:

```js
import { dump } from 'js-yaml'

dump({ service: { name: 'api', ports: [8080, 8081] } })
// service:\n  name: api\n  ports:\n    - 8080\n    - 8081\n

dump({ z: 1, a: 2 }, { sortKeys: true })
// a: 2\nz: 1\n
dump({ a: [1, 2] }, { flowLevel: 0 })
// {a: [1, 2]}\n
```

### Errors and determinism

`load` on an empty input or a multi-document stream must throw a
`YAMLException`. Malformed flow collections, duplicate keys, and unknown tags
must also fail with a structured exception. Error messages should include a
useful line/column marker and, when `filename` is supplied, the filename.

The same JSON input and options must produce byte-for-byte identical `dump`
output across repeated calls and processes. No network access or mutable
process-global state may affect the result.

## Implementation Notes

The verifier installs and packs the candidate package from the empty workspace,
then invokes only the named exports through the package root. Keep the public
entry point and package metadata self-contained. Do not rely on the verifier's
private tests, adapter, reward files, source checkout, or any network access.
The scored contract is this bounded deterministic JSON slice, not complete
parity with every upstream schema, tag, AST event, CLI behavior, or development
tool.

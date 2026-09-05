# Project Description

Build an installable Node.js package named `canonicalize` from an empty
workspace. It provides deterministic JSON Canonicalization Scheme (JCS-style)
serialization for JSON-compatible values.

# Natural Language Instruction

Build `canonicalize` from an empty workspace. Implement the default ESM
function and deterministic JSON Canonicalization behavior for primitives,
arrays, objects, Unicode strings, and cycles as specified below.

# Supports or Environment Configuration

- Node.js `22.23.1` and npm `10.9.8`.
- An ESM package whose public entry point exports a default `canonicalize`
  function.
- No network access at runtime and no lifecycle scripts required at install.
- The package is named `canonicalize`, version `2.0.0`, and uses a v3
  `package-lock.json` that agrees with `package.json`.
- Install from the repository root with `npm ci --offline --ignore-scripts
  --no-audit --no-fund`; there are no runtime dependencies in the scored
  projection.
- Agent, candidate, verifier, Oracle, and controls operate with no access to
  GitHub, npm, DNS, or external services.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

# API Usage Guide

Import path: `import canonicalize from 'canonicalize'` or the package root's
default ESM export. The complete signature is:

```ts
export default function canonicalize(value: unknown): string;
```

## `canonicalize(value)`

Import the default export from the package root. The function returns a string
containing canonical JSON:

- Object keys are ordered lexicographically by their UTF-16 property order.
- Arrays preserve order and recursively canonicalize their values.
- JSON primitives use JSON-compatible spelling; `null` returns `"null"`.
- Undefined or symbol values in arrays become `null`; those object properties
  are omitted.
- Non-finite numbers and strings containing lone UTF-16 surrogates throw an
  `Error` with a descriptive message.
- Nested objects and repeated non-circular references are supported. Circular
  references must throw instead of recursing forever.

The function is evaluated through a JSON request/response boundary. The public
contract therefore covers JSON-compatible values, strings containing Unicode,
and deterministic errors; callbacks and arbitrary executable object methods are
outside this task's boundary.

Objects are traversed without changing their own properties. Sort keys by the
JCS UTF-16 ordering rule at each object level, preserve array order, and emit
the shortest permitted JSON number representation. Strings must use valid
Unicode JSON escaping, and a repeated reference is legal unless it closes the
currently active recursion path as a cycle. Repeated calls with equivalent
decoded JSON values return equal strings and do not retain mutable state.

# Implementation Notes

Keep the package ESM-compatible and expose the default function from the root
entry point. Do not require a network service, native addon, generated runtime
download, or custom test runner. Preserve deterministic output and the exact
error behavior described above.

Keep the implementation self-contained in the package root. Do not expose a
CLI, filesystem cache, source endpoint, custom loader, or test-only export.
The generated project must work when installed rather than only when executed
from its checkout. Use ordinary ECMAScript object and array semantics for the
JSON-safe input boundary and fail explicitly for values that cannot be
represented by canonical JSON.

# Examples

```js
import canonicalize from 'canonicalize';
canonicalize({b: 2, a: 1}); // '{"a":1,"b":2}'
canonicalize([true, null, 3]); // '[true,null,3]'
```

```js
import canonicalize from 'canonicalize';

canonicalize({z: [3, 2], a: 'é'});
// '{"a":"é","z":[3,2]}'
```

```js
import canonicalize from 'canonicalize';

canonicalize({nested: {b: 2, a: 1}});
// '{"nested":{"a":1,"b":2}}'
```

# Error Handling and Boundary Conditions

`canonicalize(null)` returns `'null'`. Non-finite numbers, lone surrogates,
and circular references throw a descriptive `Error` rather than producing
ambiguous output.

```js
canonicalize(null); // 'null'
// canonicalize(NaN) and canonicalize({self: value}) for a cyclic value throw.
```

Empty arrays and objects produce `[]` and `{}`. Array entries that are
undefined or symbols serialize as `null`, while equivalent object properties
are omitted according to JSON serialization rules. A lone surrogate, NaN,
positive infinity, negative infinity, or an active recursion cycle raises an
`Error`; the implementation must not hang or emit non-canonical JSON.

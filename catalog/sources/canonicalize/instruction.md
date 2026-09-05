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

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

# API Usage Guide

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

# Implementation Notes

Keep the package ESM-compatible and expose the default function from the root
entry point. Do not require a network service, native addon, generated runtime
download, or custom test runner. Preserve deterministic output and the exact
error behavior described above.

# Examples

```js
import canonicalize from 'canonicalize';
canonicalize({b: 2, a: 1}); // '{"a":1,"b":2}'
canonicalize([true, null, 3]); // '[true,null,3]'
```

# Error Handling and Boundary Conditions

`canonicalize(null)` returns `'null'`. Non-finite numbers, lone surrogates,
and circular references throw a descriptive `Error` rather than producing
ambiguous output.

```js
canonicalize(null); // 'null'
// canonicalize(NaN) and canonicalize({self: value}) for a cyclic value throw.
```

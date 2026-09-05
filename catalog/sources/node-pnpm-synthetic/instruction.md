# Project Description

Create an installable ESM package named `node-pnpm-synthetic` from an empty
workspace. It is a bounded pnpm adapter fixture with deterministic JSON
normalization, stable serialization, and array-summary behavior. The runtime
surface consists of three synchronous named exports from one root module.

This is a synthetic development task. Its upstream source identity and
production lock/store evidence are not frozen, so the specification describes
the local fixture contract without claiming production readiness.

# Natural Language Instruction

Build the complete pnpm project under `workspace/`. The implementation must:

1. expose `normalize`, `stableStringify`, and `summarize` from the ESM root;
2. parse JSON strings and recursively sort object keys;
3. produce deterministic compact JSON without reordering arrays;
4. summarize empty and non-empty arrays with a stable return shape;
5. include a pnpm v9 lockfile and zero runtime dependencies; and
6. work entirely offline without lifecycle scripts or generated runtime files.

# Supports or Environment Configuration

- Runtime: Node.js `22.23.1`, Debian bookworm, `linux/amd64`, glibc.
- Package manager: pnpm `9.15.0`.
- Distribution and import name: `node-pnpm-synthetic`.
- Module format: ESM through `"type": "module"`.
- Lock format: `pnpm-lock.yaml`, lockfile version `9`.
- Runtime dependencies: none.
- Build requirements: Node and pnpm already supplied by the environment.
- Install using pnpm's frozen, offline, scripts-disabled mode.
- Do not declare lifecycle scripts, workspaces, native addons, custom loaders,
  registry configuration, or install-time downloads.
- Agent, candidate, verifier, Oracle, controls, and runtime use NoNetwork.
  GitHub, npm, PyPI, Go proxy, DNS, and external services are unavailable.
- The production pnpm store closure is not yet frozen. Do not fetch one or
  present this discovered fixture as a published task.

# Project Directory Structure

```text
workspace/
├── package.json       # package name, ESM mode, and root export
├── pnpm-lock.yaml     # pnpm lockfile version 9
└── index.js           # normalize, stableStringify, and summarize
```

No CLI, secondary export, native binary, resource file, or build output is
required. Package loading after installation must resolve `index.js` directly.

# API Usage Guide

```js
import {
  normalize,
  stableStringify,
  summarize,
} from 'node-pnpm-synthetic';
```

## `normalize(value)`

```ts
function normalize(value: string): JsonValue;
```

Parse the JSON document in `value`. Recursively construct each object with its
keys in lexicographic order. Recursively process arrays while preserving their
element order. Return scalars as the values represented by JSON.

The function is synchronous and stateless. Invalid JSON throws a normal
`Error`. It neither mutates external state nor performs I/O. Calling it twice
with the same text returns structurally equal values in the same key order.

## `stableStringify(value)`

```ts
function stableStringify(value: JsonValue): string;
```

Return compact JSON text for a JSON value. Sort keys at every object depth,
retain array order, and include no insignificant whitespace. Two objects with
the same recursively represented keys and values serialize identically even
if their insertion order differs.

Only JSON-compatible values are required. Functions, `undefined`, symbols,
BigInts, cyclic references, accessors, and custom prototypes are outside this
fixture contract. The input must not be mutated.

## `summarize(values)`

```ts
function summarize(values: JsonValue[]): {
  count: number;
  first: JsonValue | null;
  last: JsonValue | null;
};
```

Return a new object containing the number of elements and the endpoint values.
For an empty array, return `count: 0`, `first: null`, and `last: null`. For a
non-empty array, preserve the exact first and last JSON values. Do not sort,
consume, or modify the source array.

# Implementation Notes

- Keep package loading independent of repository-relative paths.
- Apply one recursive object-key ordering rule throughout the package.
- JavaScript object keys are strings in this JSON-only contract.
- Preserve arrays, duplicate values, Unicode strings, booleans, numbers, and
  null according to JSON parsing and serialization rules.
- Keep all runtime code in the declared root module; no build step is needed.
- Do not add undeclared packages merely to sort keys.
- Do not add evaluator material, reference implementations, or package-manager
  cache content to the candidate project.

# Examples

Ordinary normalization:

```js
normalize('{"b":2,"a":1}');
// {a: 1, b: 2}
```

Nested deterministic output:

```js
stableStringify({outer: {z: 0, a: true}, list: [2, 1]});
// '{"list":[2,1],"outer":{"a":true,"z":0}}'
```

Array summaries:

```js
summarize([{id: 1}, {id: 2}]);
// {count: 2, first: {id: 1}, last: {id: 2}}

summarize([]);
// {count: 0, first: null, last: null}
```

# Error Handling and Boundary Conditions

- Empty or malformed JSON text passed to `normalize` throws `Error`.
- JSON text representing `null`, `false`, `0`, or `""` returns that value and
  is not interpreted as absence.
- Empty objects and arrays normalize and serialize without special markers.
- Duplicate object names use the JSON parser's retained value, then key order
  is normalized.
- `stableStringify` does not promise behavior for cyclic or non-JSON values.
- `summarize` rejects a non-array rather than silently coercing it.
- No operation may inspect the clock, random source, filesystem, registry, or
  network; results depend only on arguments.

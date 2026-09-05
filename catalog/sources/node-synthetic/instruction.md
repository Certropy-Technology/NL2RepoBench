# Project Description

Create an installable ESM package named `node-synthetic` from an empty
workspace. It is a deliberately small Node foundation fixture that normalizes
JSON values, serializes them deterministically, and summarizes arrays of JSON
values. The package exposes three synchronous functions from one root module.

This is a synthetic development task, not a frozen upstream reimplementation.
Its source identity and production dependency/image closure are not yet known,
so completing this project does not imply production publication status.

# Natural Language Instruction

Build the complete package in `workspace/` rather than returning a single code
fragment. The result must:

1. install as the npm package `node-synthetic`;
2. expose `normalize`, `stableStringify`, and `summarize` as named ESM exports;
3. recursively sort object keys without changing array order;
4. keep all inputs and outputs within the JSON data model;
5. include package metadata and a root-only npm v3 lockfile; and
6. run deterministically without filesystem, clock, random, or network input.

# Supports or Environment Configuration

- Runtime: Node.js `22.23.1` on Debian bookworm, `linux/amd64`, glibc.
- Package manager: npm `10.9.8`.
- Module format: ESM, declared with `"type": "module"`.
- Distribution and import name: `node-synthetic`.
- Install command: `npm ci --offline --ignore-scripts`.
- Lock format: `package-lock.json`, lockfile version `3`.
- Runtime dependencies: none.
- Build requirements: none beyond Node and npm already present.
- Do not declare lifecycle scripts, workspaces, native addons, custom loaders,
  registry configuration, or install-time code generation.
- Agent, candidate, verifier, Oracle, and controls use NoNetwork execution.
  Runtime access to GitHub, npm, DNS, Go proxy, PyPI, and external services is
  forbidden.
- The task remains a development fixture because its production closure is not
  frozen; do not attempt to repair that by fetching packages or source.

# Project Directory Structure

```text
workspace/
├── package.json         # ESM package metadata and root export
├── package-lock.json    # npm v3 root-only lockfile
└── index.js             # all three named runtime exports
```

`package.json` must point the package root at `index.js`. No CLI, resource
directory, generated file, or secondary export is required.

# API Usage Guide

Import all APIs from the package root:

```js
import {normalize, stableStringify, summarize} from 'node-synthetic';
```

## `normalize(value)`

```ts
function normalize(value: string): JsonValue;
```

`value` is a JSON document encoded as a JavaScript string. Parse it and return
the represented JSON value. For every plain JSON object, sort keys
lexicographically and apply the same normalization recursively to its values.
Preserve array element order and recursively normalize each element. Preserve
JSON strings, finite numbers, booleans, and `null` as their parsed values.

The function is synchronous, does not mutate caller-owned state, and has no
side effects. Invalid JSON throws a regular `Error` rather than returning a
sentinel. Equal JSON input text produces structurally equal output every time.

## `stableStringify(value)`

```ts
function stableStringify(value: JsonValue): string;
```

Accept a JSON value and return compact JSON text with object keys sorted
recursively. Do not include insignificant whitespace. Preserve array order,
scalar values, and nesting. The output is deterministic for structurally equal
JSON values regardless of object insertion order.

The function is synchronous and does not mutate its argument. Inputs outside
the JSON data model are outside this bounded contract; do not add custom
serialization for functions, symbols, BigInts, cyclic graphs, or prototypes.

## `summarize(values)`

```ts
function summarize(values: JsonValue[]): {
  count: number;
  first: JsonValue | null;
  last: JsonValue | null;
};
```

Accept an array of JSON values and return a new object. `count` is the array
length. For a non-empty array, `first` and `last` are the first and last input
elements. For an empty array, both are `null`. The property order is `count`,
`first`, then `last`.

The function does not reorder or mutate the input array. Non-array inputs are
invalid and should fail rather than being silently coerced.

# Implementation Notes

- Define the JSON domain as null, booleans, finite numbers, strings, arrays,
  and objects whose values are recursively in the same domain.
- Use one recursive normalization rule for both `normalize` and
  `stableStringify` so ordering remains consistent across modules and calls.
- Sort object keys only; never sort array elements.
- Return newly constructed object containers during recursive normalization.
- Keep the package surface to the three named exports.
- Keep evaluation independent of current working directory after installation.
- Do not include tests, evaluator files, reference source, or cache material in
  the package structure.

# Examples

Ordinary parsing and key normalization:

```js
normalize('{"z":1,"a":{"d":4,"b":2}}');
// {a: {b: 2, d: 4}, z: 1}
```

Deterministic serialization:

```js
stableStringify({z: 1, a: [3, {y: 2, x: 1}]});
// '{"a":[3,{"x":1,"y":2}],"z":1}'
```

Non-empty and empty summaries:

```js
summarize(['a', {n: 2}, false]);
// {count: 3, first: 'a', last: false}

summarize([]);
// {count: 0, first: null, last: null}
```

# Error Handling and Boundary Conditions

- `normalize('')` and malformed documents such as `'{'` throw `Error`.
- `normalize('null')` returns `null`; it is not treated as missing input.
- Empty objects and arrays remain `{}` and `[]`.
- Duplicate object keys follow the JSON parser's ordinary last-value behavior,
  after which the retained keys are sorted.
- Array order and duplicate array values are preserved.
- `summarize([])` returns null endpoints and does not read absent indices.
- `summarize` must reject non-array input rather than treating it as iterable.
- Calls must not read environment variables or contact any host.

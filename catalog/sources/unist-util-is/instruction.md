# Build `unist-util-is`

## Project Description

Create a complete installable npm package named `unist-util-is`, version
`6.0.1`, from an empty workspace. The package is an ESM utility for recognizing
unist-style nodes and applying reusable tests to them. It exposes exactly two
named functions, `is` and `convert`, and has no default export.

This is a repository-generation task. Implement the behavior with your own
source files; do not copy a reference implementation or upstream tests into the
repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- Use ESM with `"type": "module"`. The package root must expose exactly the
  named exports `is` and `convert` through the safe in-package export
  `"./index.js"`.
- Include nonempty TypeScript declarations for the public API and list the
  exact runtime dependency `@types/unist@3.0.3`.
- Include a committed npm v3 `package-lock.json` consistent with
  `package.json`. The package must install from a clean checkout with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The evaluator provides the exact `@types/unist@3.0.3` npm closure in an
  offline cache. Do not use lifecycle hooks, native addons, custom loaders,
  workspaces, registry configuration, network access, filesystem state,
  current time, or randomness.

## API Usage Guide

The public test domain uses ordinary JavaScript values, unist node objects, and
real callback functions. A node-like value is any non-null object with a
present `type` property. For a nullish test, the `type` value itself is not
coerced or restricted further.

### `is(node, test, index, parent, context)`

Import path and signature:

```js
import {is} from 'unist-util-is'

is(
  node?: unknown,
  test?: Test,
  index?: number | null,
  parent?: Parent | null,
  context?: unknown
): boolean
```

`Test` is one of:

```ts
type Test =
  | ReadonlyArray<Record<string, unknown> | TestFunction | string>
  | Record<string, unknown>
  | TestFunction
  | string
  | null
  | undefined

type TestFunction = (
  this: unknown,
  node: Node,
  index?: number,
  parent?: Parent
) => boolean | undefined | void
```

The function first validates the test and optional position arguments, then
returns `false` when `node` is not node-like. For a node-like value:

- A null or undefined test passes.
- A string test uses exact, case-sensitive `node.type === test` matching and
  does not coerce either side.
- An object test is a subset match. Every enumerable property in the test is
  compared to the corresponding node property with strict `===` equality.
  Extra node properties are ignored. Nested objects therefore match only when
  they are the same reference; a missing property compares equal to an
  expected `undefined` value.
- An array test is an ordered, short-circuiting OR over its string, object, and
  function entries. An empty array fails.
- A function test is called once with `context` as `this` and with the exact
  node, normalized index, and normalized parent. Its return value is converted
  to boolean; `false`, `undefined`, and no return all fail.

The optional position arguments form a pair. Null and undefined mean absent.
When present, `index` must be a non-negative finite number, and `parent` must be
a node-like parent with a `children` value. Supplying only one of them throws.
Invalid test, index, or parent input throws `Error` with these messages:

```text
Expected function, string, or object as test
Expected positive finite index
Expected parent node
Expected both parent and index
```

Examples:

```js
const node = {type: 'strong', children: [{type: 'text', value: 'A'}]}
const parent = {type: 'paragraph', children: [node]}

is(node, 'strong')
// => true

is(node, {type: 'strong'})
// => true

is(node, ['emphasis', 'strong'])
// => true

is(node, function (value, index, owner) {
  return this.enabled && value.type === 'strong' && index === 0 && owner === parent
}, 0, parent, {enabled: true})
// => true
```

### `convert(test)`

Import path and signature:

```js
import {convert} from 'unist-util-is'

convert(test?: Test): Check

type Check = (
  this: unknown,
  node?: unknown,
  index?: number | null,
  parent?: Parent | null
) => boolean
```

Create the same test once and return a reusable synchronous check. Invalid
tests throw immediately. The returned check assumes its inputs are already
valid: a nullish test creates an unconditional check that returns `true`, even
for an omitted or non-node value. Checks created from string, object, function,
or array tests reject non-node-like values before applying the test. A function
test receives the returned check's `this` value; non-number indexes are
normalized to `undefined`, and a nullish parent is normalized to `undefined`.
Unlike `is`, the converted check does not enforce the index/parent pair.

```js
const isHeading = convert(['heading', {role: 'heading'}])

isHeading({type: 'heading', depth: 2})
// => true

isHeading({type: 'paragraph', children: []})
// => false
```

## Implementation Notes

Both functions are synchronous, deterministic, and must not mutate the node,
test, parent, array, callback, or context. Keep the root importable without a
build step. The evaluator packs and installs the submitted repository, then
constructs callbacks and invokes the public API only in bounded UID/GID 10001
child processes. Trusted verifier code never imports candidate files, and the
candidate cannot write verifier-owned reports or reward files.

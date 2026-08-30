# Build `unist-util-visit-parents`

## Project Description

Create an installable ESM npm package named `unist-util-visit-parents`, version
`6.0.2`, from an empty workspace. The package performs depth-first preorder
traversal of unist-compatible syntax trees and gives each visitor the complete
ordered stack of ancestors. It supports filtering, reverse traversal, early
exit, child skipping, sibling-index control, and in-place tree mutation.

The task covers package-root runtime behavior and TypeScript declarations. It
does not require the upstream documentation, formatting, coverage, or
development toolchain. Do not copy upstream source or tests into the generated
repository.

## Supports

- Run on Node.js `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must use the exact package name and version above, set
  `"type": "module"`, expose one safe ESM package-root entry, and reference an
  existing TypeScript declaration entry.
- The package root exports exactly the named runtime identifiers `CONTINUE`,
  `EXIT`, `SKIP`, and `visitParents`. It has no default export and no CLI.
- Declare these exact runtime dependencies and no others:

  ```json
  {
    "@types/unist": "3.0.3",
    "unist-util-is": "6.0.1"
  }
  ```

- Commit an npm v3 lockfile. A clean verifier must be able to install it with
  no network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not declare development dependencies, npm scripts, workspaces, native
  addons, custom loaders, registry settings, or lifecycle hooks.
- Runtime behavior is synchronous, deterministic, and offline. It must not use
  files, subprocesses, browser globals, the network, randomness, locale, or the
  clock.

## Bounded Evaluation Contract

The verifier never imports candidate JavaScript into its trusted process. An
unprivileged, bounded child imports the installed package and constructs
visitor callbacks and `unist-util-is` tests from allowlisted JSON descriptors.
It returns only a cycle-free JSON projection of visit order, ancestor order,
sibling indexes, action outcomes, and the mutated tree.

Scored input trees contain plain JSON objects, at most 2,048 nodes, and at most
1,000 levels. Each node has a string `type`; parent nodes have a `children`
array. Requests are at most 64 KiB and responses at most 512 KiB. No source
text, arbitrary executable callback, accessor, custom prototype, symbol,
BigInt, cyclic value, or native object crosses the boundary.

## API Usage Guide

### Action constants

```ts
export const CONTINUE: true
export const EXIT: false
export const SKIP: 'skip'
```

`CONTINUE` continues normally. `EXIT` stops the entire traversal immediately.
`SKIP` prevents traversal of the current node's children but continues with
the next sibling.

### `visitParents`

```ts
import type {Node, Parent} from 'unist'
import type {Test} from 'unist-util-is'

export type Action = true | false | 'skip'
export type Index = number
export type ActionTuple = [
  (Action | null | undefined | void)?,
  (Index | null | undefined)?
]
export type VisitorResult =
  | Action
  | ActionTuple
  | Index
  | null
  | undefined
  | void
export type Visitor<Visited extends Node = Node, Ancestor extends Parent = Parent> = (
  node: Visited,
  ancestors: Ancestor[]
) => VisitorResult

export function visitParents<Tree extends Node, Check extends Test>(
  tree: Tree,
  test: Check,
  visitor: Visitor,
  reverse?: boolean | null
): undefined

export function visitParents<Tree extends Node>(
  tree: Tree,
  visitor: Visitor,
  reverse?: boolean | null
): undefined
```

The real declarations may use more precise conditional generic types for
`BuildVisitor`, matched descendants, and inferred ancestors. Export the public
types `Action`, `ActionTuple`, `BuildVisitor`, `Index`, `Test`, `Visitor`, and
`VisitorResult` in addition to the four runtime identifiers.

`tree` is visited in depth-first preorder: node, then each child subtree from
left to right. With `reverse: true`, visit the node and then child subtrees from
right to left. The root visitor receives `[]`. Every other visitor receives a
new ordered array from the root through the direct parent; the current node is
not included. Array entries are the actual ancestor objects, so visitors may
mutate them.

The optional `test` follows the `unist-util-is` `Test` contract. It may be a
type string, a partial node object, a predicate, an array of tests, `null`, or
`undefined`. A predicate receives `(node, index, parent)`, where root `index`
and `parent` are `undefined`. Only matching nodes call `visitor`, but filtering
never prunes traversal by itself.

`visitor` may return:

- `undefined`, `null`, or `CONTINUE` to continue normally;
- `EXIT` to stop every remaining visit;
- `SKIP` to omit the current node's descendants;
- an integer sibling index to select the next sibling after the current
  node's descendants are processed;
- an action tuple such as `[SKIP]` or `[CONTINUE, nextIndex]`.

A next index smaller than zero or greater than or equal to the current
parent's `children.length` ends traversal of that parent's remaining children.
In reverse mode indexes still identify absolute positions in `children`.

Visitors may mutate the current node, its children, or ancestors. Children and
next siblings inserted before their turn are visited. When removing the
current or an already visited sibling, return the adjusted next index to avoid
skipping or repeating nodes. For compatibility, replacing the current node in
its parent's array does not replace the node already captured by the active
walk: unless `SKIP` is returned, the original node's descendants are still
visited.

Example:

```js
import {SKIP, visitParents} from 'unist-util-visit-parents'

const tree = {
  type: 'root',
  children: [
    {type: 'section', hidden: true, children: [{type: 'text', value: 'a'}]},
    {type: 'text', value: 'b'}
  ]
}

visitParents(tree, function (node, ancestors) {
  console.log(node.type, ancestors.map((ancestor) => ancestor.type))
  if (node.hidden) return SKIP
})
```

The function returns `undefined`. It does not swallow errors: exceptions from
tests or visitors propagate unchanged. Calls missing a usable visitor fail
with `TypeError`; no separate argument-validation API is required.

## Implementation Notes

Preserve node and ancestor object identity, child order, and all unrelated
fields. Do not attach parent pointers or retain process-global traversal state.
Traversal must handle at least 1,000 nested nodes within the task limits.
Package-root export shape, action values, overload behavior, filter semantics,
visit order, ancestor stacks, mutation behavior, and declaration presence are
observable.

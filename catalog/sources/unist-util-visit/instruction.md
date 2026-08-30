# Project Description

Build the `unist-util-visit` package as an offline ESM npm package. It provides
depth-first traversal of unist-compatible syntax trees and lets callers select
nodes and control traversal from a visitor callback.

# Supports

- Node.js ESM package metadata with package name `unist-util-visit`.
- A package-root export from `index.js` with the named exports `visit`,
  `CONTINUE`, `EXIT`, and `SKIP`.
- A candidate-owned `adapter.mjs` file, included in the published package, for
  the JSON callback bridge described below. The adapter is needed because a
  function callback cannot cross the verifier's JSON boundary.

# API Usage Guide

## Package exports

Import from the package root with:

```js
import {CONTINUE, EXIT, SKIP, visit} from 'unist-util-visit'
```

`CONTINUE`, `EXIT`, and `SKIP` are the traversal action values. Preserve their
identity and make them usable as return values from a visitor.

## `visit(tree[, test], visitor[, reverse])`

`visit` accepts a unist `Node` or `Parent` object as `tree`. A parent has a
`children` array containing child nodes. Traversal is depth-first and
pre-order: a node is visited before its descendants. With `reverse` set to
`true`, child order is traversed from right to left while the root remains the
first visited node.

The two-argument form is `visit(tree, visitor[, reverse])`. The three-argument
form is `visit(tree, test, visitor[, reverse])`. `test` may be a node type
string, an array of node type strings, a plain object matcher, or another
predicate accepted by `unist-util-is`. A visitor receives
`(node, index, parent)`, where `index` and `parent` are `undefined` for the
root. The visitor may mutate the node or parent.

The visitor return value controls traversal. Returning `CONTINUE` or
`undefined` continues normally. Returning `SKIP` skips the matched node's
descendants but continues with later siblings. Returning `EXIT` ends the whole
walk. Returning an integer or `[CONTINUE, integer]` changes the next sibling
index according to the package's traversal contract. A visitor can also return
`[SKIP]` when it needs an action tuple.

The function returns `undefined` after a completed walk or an early exit. It
should throw a `TypeError` when no callable visitor is supplied. Do not add
network, filesystem, CLI, native-addon, or global-state behavior.

## `adapter.mjs` JSON bridge

The adapter reads one JSON object from stdin and writes one JSON object to
stdout. It must accept a request with `tree`, optional `test`, optional
`reverse`, and optional callback controls. It must record each callback as
`{type,index,parentType}` and return `{ok:true, visits, calls, tree}`. Supported
controls are `skipType`, `exitAfter`, `restartOnceType`, `jumpAtType`,
`jumpIndex`, `predicateIndexAtLeast`, and `markVisited`. The adapter must use
the package's own `visit` and action exports; it must not reimplement traversal.

# Implementation Notes

Use Node.js ESM syntax and keep the package root export shape exact. Runtime
dependencies must be declared in `package.json` and locked in the supplied
package-lock contract. The verifier installs with npm offline and lifecycle
scripts disabled, so the package must pack and install without running a build
step. Keep declarations compatible with the runtime implementation, but the
scored contract is the JavaScript behavior above.

The evaluator supplies JSON-compatible trees and values only. Preserve input
order, root-before-descendants order, reverse ordering, callback indices,
parent references represented by their type, and deterministic results across
independent requests.

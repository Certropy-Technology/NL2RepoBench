# Traceability

| Leaves | Contract | Evidence |
| --- | --- | --- |
| 1 | ESM package root exposes `visit`, `CONTINUE`, `EXIT`, `SKIP` | package metadata and adapter export check |
| 2-4 | preorder traversal, callback index, immediate parent | `contract.test.mjs` traversal and metadata checks |
| 5-7 | reverse ordering and string/array/object tests | type-filter and reverse leaves |
| 8-10 | predicate selection and CONTINUE/undefined behavior | predicate and continuation leaves |
| 11-14 | SKIP, EXIT, restart index, explicit next index | action-control leaves |
| 15-20 | leaf/empty trees, mutation, field preservation, Unicode, determinism | bounded JSON tree leaves |
| 21-24 | combined reverse/filter/action behavior and unmatched nodes | composition leaves |
| 25-30 | stable sibling ordering, parent identity, later siblings, response envelope | boundary and repeatability leaves |

The private tests exercise only JSON-compatible trees and callback controls
specified in `instruction.md`. They do not expose private dependencies, source
fetch endpoints, hidden implementation details, arbitrary module names, or
unbounded callbacks.

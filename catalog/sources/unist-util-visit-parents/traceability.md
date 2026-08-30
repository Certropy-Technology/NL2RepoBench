# `unist-util-visit-parents` traceability

Frozen source revision: `f06035e9161f25119fb68d178167c30003d32dfb`
(`6.0.2`). The verifier contains 50 flat `node:test` leaves.

| Leaf range | Public contract | Source/test basis |
| --- | --- | --- |
| 1-7 | exact named runtime exports, constant values, package identity, exact dependency pins, restricted package metadata, declarations | package metadata, `index.d.ts`, upstream public-API and type tests |
| 8-13 | `undefined` return, preorder/reverse order, complete ancestors, sibling index, leaf-root behavior | upstream traversal tests and public algorithm contract |
| 14-22 | null/no filter, string/array/partial/predicate tests, predicate index/parent/data arguments, filtered reverse order | `unist-util-is` dependency contract and upstream filter tests |
| 23-25 | `CONTINUE`, tuple continue, null result | documented `VisitorResult` normalization |
| 26-29 | direct and tuple `EXIT`, forward and reverse global termination | upstream stop tests |
| 30-32 | direct and tuple `SKIP`, forward and reverse child pruning | upstream skip tests |
| 33-38 | numeric and tuple next indexes, bounds, revisit, reverse absolute indexes | upstream sibling-index tests and public `Index` contract |
| 39-45 | appended children/siblings, removal of next/current/previous siblings, ancestor mutation, current-node replacement compatibility | public mutation notes and upstream mutation behavior |
| 46 | bounded 1,000-node nesting | upstream deep-tree regression, reduced to the documented verifier budget |
| 47-49 | missing tree/visitor errors and visitor exception propagation | upstream error tests and ordinary callback exception semantics |
| 50 | deterministic repeated traversal | synchronous stateless public contract |

The boundary constructs callbacks and predicates only inside the unprivileged
candidate child. Trusted tests compare JSON projections and never import the
candidate package or hold candidate-created objects.

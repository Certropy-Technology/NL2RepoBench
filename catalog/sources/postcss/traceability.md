# `postcss` Traceability

The private deterministic `node:test` contract has 32 unique leaves. Each
leaf invokes an installed candidate package as UID 10001 through the bounded
JSON adapter; trusted test code never imports candidate JavaScript.

| Public contract | Verifier coverage | Leaves |
| --- | --- | ---: |
| package metadata, CommonJS/ESM-root shape, helper and class exports, Processor version | inspect response | 1 |
| parse node kinds, ordering, values, comments, at-rules, importance, whitespace | cycle-free parse projections and CSS | 8 |
| parse errors, positions, escaped/quoted text, nested containers | bounded parse/error responses | 4 |
| constructors, append/prepend/insert/remove/replace, selectors, clone, fromJSON | allowlisted mutation scenarios | 9 |
| walker source order and declaration matching | mutation walk scenarios | 1 |
| process visitor descriptors, warnings, sync and async behavior | processor scenarios | 9 |
| **Total** | fixed collection | **32** |

The frozen upstream suite is used to prove the revision's baseline. The
production verifier deliberately adapts a specified package-root slice rather
than copying the entire development suite; every private assertion maps to a
documented operation above. Custom syntax hooks, maps, arbitrary callbacks and
the deprecated plugin factory are explicitly excluded in the instruction and
have no hidden behavioral assertions.

# `yoctocolors` Traceability

Frozen source revision: `a02a16ec36fbd58a0848e95598fb4913c54c7591`
(`2.2.0`). The upstream AVA suite passes 78/78 in the locked Node 24.19.0
runtime; XO and the TSD assertion also pass.

| Leaf range | Public contract | Source/test basis |
| --- | --- | --- |
| 1-61 | every named formatter emits its exact opening code, text, and closing code when enabled | upstream table-driven formatter assertions and exported API inventory |
| 62-74 | nested foreground/background/modifier/underline styles, repeated styles, shared SGR 22/24 closes, and literal close sequences restore the outer style | upstream nesting and regression assertions |
| 75-78 | JavaScript coercion, empty input, equivalent default namespace, and `FORCE_COLOR=0` no-op behavior | upstream runtime assertions and fixture child |
| 79 | exact package identity, ESM root map, files, engines, dependency-free contract, named/default export inventory | frozen package metadata and runtime module inventory |
| 80 | `Format` type plus exact declaration/runtime formatter agreement and index re-exports | frozen `index.test-d.ts`, `index.d.ts`, and `base.d.ts` |

Reverse traceability is explicit:

- `Supports` maps to leaf 79, the compiler's npm v3 offline installer, and the
  task network/dependency gates.
- Every API table row maps to exactly one of leaves 1-61.
- Every nesting and close-code rule in `Implementation Notes` maps to leaves
  62-74.
- Color detection, coercion, empty input, default exports, and declarations map
  to leaves 75-80.
- CommonJS, dynamic color factories, terminal control, and platform-specific
  console adaptation are publicly excluded and have no hidden assertions.

All leaves invoke candidate behavior in a bounded UID 10001 child. The trusted
test process receives only JSON-safe strings or bounded metadata projections.

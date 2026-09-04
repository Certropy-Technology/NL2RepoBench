# `remeda` traceability

Frozen upstream revision: `ebd0be24a3407315c8b2242eebae504e0d06f8c8`, tree
`a66f99a942a5a2e243e77292e44e18e6af184178`.

| Test group | Public contract | Upstream basis |
| --- | --- | --- |
| package shape | package name/version, ESM root, selected named exports | `packages/remeda/package.json`, `src/index.ts` |
| array data-first | map/filter/take/drop/chunk/unique/difference/partition | corresponding `packages/remeda/src/*.ts` implementations and runtime tests |
| array data-last | groupBy/indexBy/zip/range/reverse/sortBy | corresponding overloads and `purry` dispatch behavior |
| numeric and objects | arithmetic, aggregates, clamp, pick/omit/merge/pipe | corresponding source implementations and runtime tests |
| predicates and strings | deep equality, type predicates, case conversion, truncation | corresponding source implementations and runtime tests |
| errors and immutability | range error, chunk error, non-mutation/fresh output | documented error and copy semantics |

The private adapter is required because callbacks and the package's full export
surface cannot be represented as a safe JSON-only trusted-process import. Every
scored operation is described in `instruction.md`; type-level tests, random
generators, timers, and non-JSON object behavior are intentionally excluded.

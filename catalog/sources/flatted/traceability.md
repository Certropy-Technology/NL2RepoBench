# `flatted` traceability

Frozen revision: `e6f5ca700c4ca8104a6a83472c8219e267bd5e84`
(`flatted@3.4.4`). The upstream package exposes four public root functions and
its assertion-based baseline passes with full statement, branch, function, and
line coverage. The production verifier freezes 35 named `node:test` leaves.

| Leaf range | Public contract | Frozen source/test basis |
| --- | --- | --- |
| 1 | package identity, exports, declarations, zero runtime closure | `package.json`, `types/index.d.ts` |
| 2-5 | primitive roots and empty containers | upstream primitive and empty-value assertions |
| 6-12 | self cycles, mutual cycles, aliases, nested graphs, literal index-like strings | upstream recursive array/object and restructuring assertions |
| 13-15 | array and function replacers | upstream callback and property-allowlist assertions |
| 16-18 | numeric/string indentation and Date `toJSON` behavior | upstream JSON-compatible optional argument and Date assertions |
| 19-24 | primitive parsing, circular reconstruction, alias reconstruction, special strings | upstream parse/roundtrip assertions |
| 25-28 | reviver transform/delete/root behavior and invalid JSON | upstream reviver assertions and native parse contract |
| 29-30 | complex roundtrip and deterministic property-order wire format | upstream nested/restructure exact-string assertions |
| 31-34 | `toJSON` and `fromJSON` tables and identity | upstream `RecursiveMap` helper assertions |
| 35 | helper roundtrip and repeated-call/input immutability | helper API and statelessness contract |

Every scored leaf maps to `instruction.md`. The verifier does not score browser
globals, PHP/Python/Go ports, benchmarks, filesystem fixtures, non-JSON class
state, sockets, functions as data, symbols as data, or arbitrary executable
callbacks supplied over the verifier boundary.

# `mdast-util-phrasing` Traceability

The private contract independently adapts the frozen upstream behavior and
expands the public type inventory into individual deterministic leaves.

| Public specification area | Private leaf families | Frozen source authority |
| --- | --- | --- |
| exact root export and process isolation | `exports exactly phrasing`, `uid 10001`, `gid 10001` | `index.js`, upstream public API test, verifier boundary contract |
| omitted, null, primitive, array, and malformed object inputs | `undefined`, `null`, primitive leaves, empty/invalid type leaves | upstream public API tests and `unknown` parameter contract |
| 16 accepted mdast/extension node types | one leaf for each documented exact type | frozen `lib/index.js` type inventory |
| unknown and case-sensitive types | `unknown type`, `case-sensitive type` | exact string matching behavior |
| flow and ambiguous nodes | `paragraph`, `heading`, `list`, `html`, nested text under paragraph | upstream tests plus README's explicit `html` exclusion |
| field independence and no mutation | `extra fields do not affect result or mutate input` | pure predicate contract and package `sideEffects: false` |

The trusted `node:test` process imports only `test_client.mjs`. Each request
launches a UID/GID 10001 child with an empty environment apart from bounded
runtime paths. That child loads the installed package and returns JSON. No
candidate object, function, source text, or report path crosses into trusted
code.

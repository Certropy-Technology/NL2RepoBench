# UUID private leaf slice

The private adapter exposes only the JSON representations documented by the
public instruction. It converts hexadecimal byte fields to array-like values
before the candidate subprocess call and converts `parse` results back to a
lowercase `bytes_hex` value. The candidate is always reached through the
locked runtime subprocess boundary.

The 12 leaves are traceable to these public instruction sections:

| Leaf area | Instruction contract |
| --- | --- |
| validation and version | `validate`; `version` |
| byte conversion | `parse` and `stringify`; JSON Boundary |
| name-based UUIDs | Namespace UUID generation: `v3` and `v5` |
| version 4 generation | Time and random UUID generation: `v4`; Crypto, Time, and Determinism Policy |
| version 1 generation | Time and random UUID generation: `v1` |
| version 6 generation | Time and random UUID generation: `v6` |
| version 7 generation | Time and random UUID generation: `v7` |
| field conversions | `v1ToV6` and `v6ToV1` |
| invalid namespace | Namespace UUID generation: `v3` and `v5`; JSON Boundary errors |

The denominator is the 12 top-level `node:test` leaves in
`contract.test.mjs`, frozen before packaging. The slice intentionally excludes
browser-only tests, callback and typed-array identity paths, mutable state
helpers, CLI behavior, and nondeterministic default UUID snapshots.

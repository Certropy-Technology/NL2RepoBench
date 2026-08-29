# Traceability

| Contract area | Public requirement | Private verification |
| --- | --- | --- |
| Package shape | CommonJS `range-parser` 1.2.1 with `index.js` entry | `package-shape` leaf and npm pack/install boundary |
| Input validation | Non-string `str` throws the documented TypeError | `rejects non-string headers` |
| Header parsing | Unit separator, `=`, explicit/open/suffix positions | `parses ...` leaves covering each form |
| Status sentinels | `-2` malformed, `-1` unsatisfiable | malformed and unsatisfiable leaf group |
| Numeric boundaries | End cap, suffix clamp, zero-size behavior | cap, suffix, and zero-size leaves |
| Multiple members | Invalid members ignored when a valid member exists; order preserved | mixed-member and order leaves |
| Combination | Overlap and adjacency merge; disjoint intervals and first-index order | combination leaves |
| Isolation | Candidate calls use a UID-separated, bounded JSON subprocess | private `test_client.mjs` and generated separate verifier runtime |
| Network | Agent and verifier are no-network | task network policy and offline control |

The private collection is intentionally an independently authored `node:test` contract rather than a copy of the upstream Mocha test file. Every public API behavior above has at least one corresponding private leaf, and the collection is frozen at 37 leaves.

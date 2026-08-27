# Public Contract Traceability

The private `node:test` bundle has a fixed collection of 71 unique leaves.
Every leaf invokes a named public function from `instruction.md` through a
JSON subprocess boundary. Coverage is allocated as follows:

| Public behavior group | Leaves |
| --- | ---: |
| Numeric functions | 14 |
| Sequence construction and slicing | 16 |
| Set-style and pairing functions | 6 |
| Object reads, writes, and merges | 20 |
| Equality and sequence observations | 10 |
| String functions | 5 |
| **Total** | **71** |

The verifier never imports candidate code into the trusted process. Its private
adapter starts a bounded subprocess as the candidate user, requests one named
root export with JSON arguments, and receives JSON output. Assertions cover
only direct-call behavior published in the instruction; no hidden leaf depends
on callbacks, currying, internal module paths, ESM builds, package metadata
beyond the documented package identity, or access to upstream source.

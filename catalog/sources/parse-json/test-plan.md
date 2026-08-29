# Frozen Test Plan

The private `node:test` verifier contains 33 unique leaves. Candidate code is
loaded only by a bounded child process running as the non-root `candidate` UID.
The child serializes errors and creates fixed reviver callbacks locally.

| Behavior group | Leaves |
| --- | ---: |
| Package identity and export shape | 1 |
| Successful JSON values and whitespace | 6 |
| Filename overload and deterministic calls | 4 |
| JSONError type, cause, messages, and code point details | 10 |
| Raw/source code frames and line endings | 5 |
| Legacy class and fixed reviver behavior | 4 |
| **Frozen total** | **33** |

Collection is derived from unique TAP leaves and must equal 33. The verifier
owns report normalization, the fixed denominator, and reward calculation.

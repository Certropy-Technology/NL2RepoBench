# yargs Frozen Test Plan

The private verifier has one `node:test` file with 42 unique leaves. Candidate
code is imported only by a verifier-owned child adapter running as UID 10001.
The trusted test process communicates with that child using one bounded JSON
request and response per call.

| Behavior group | Leaves |
| --- | ---: |
| Package and helper export shape, UID boundary | 1 |
| Basic argv, short/long options, types, arrays, counts, defaults, aliases | 11 |
| Choices, required arguments, arity, implications, and strictness | 9 |
| Parser configuration, separator handling, Unicode | 7 |
| Coercion, checks, middleware, async parity | 8 |
| Commands and help | 4 |
| `hideBin` and direct `Parser` helper behavior | 2 |
| **Frozen total** | **42** |

The runner derives collection from unique TAP leaves and grades only the
verifier-owned structured report. Collection mismatch fails closed.

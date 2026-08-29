# `fs-extra` Traceability

The private verifier has 50 unique `node:test` leaves. Every leaf invokes the
installed candidate as UID 10001 through a task-specific child adapter. The
trusted test process never imports candidate JavaScript and receives only
bounded JSON projections of temporary filesystem state.

| Public contract | Verifier coverage | Leaves |
| --- | --- | ---: |
| package metadata, CommonJS/ESM entrypoints, extra export inventory, selected `fs` compatibility | manifest and export-kind projections plus promise read | 7 |
| `ensureDir`, directory aliases, `ensureFile`, file aliases, hard links, symbolic links | nested temporary-tree state, inode/link identity, idempotency | 10 |
| `outputFile`, `pathExists`, `emptyDir`, `remove`, async/sync aliases | file bytes, parent creation, absent targets, retained/removed directories | 8 |
| JSON read/write/output methods, aliases, formatting, invalid JSON behavior | raw bytes and parsed JSON projections | 10 |
| `copy`/`copySync`, recursion, filter, conflicts, symlinks, timestamps, self-copy guards | isolated source/destination trees and normalized errors | 8 |
| `move`/`moveSync`, parents, overwrite/conflicts, self/descendant guards | isolated source/destination trees and normalized errors | 6 |
| optional Node-style callback compatibility | output, existence, and copy callback settlement | 1 |
| **Total** | fixed collection | **50** |

Reverse traceability is explicit:

- `Supports` maps to package metadata, entrypoint, export-shape, offline install,
  and compiler network/dependency checks.
- Every extra-method family in `API Usage Guide` has at least one async or sync
  behavioral leaf, and aliases documented as supported are checked.
- Copy and move options and error relationships have dedicated leaves rather
  than relying on happy-path recursion alone.
- Promise and callback requirements are both exercised.
- Cross-device mounts, Windows junction/case behavior, special devices, and the
  complete Node `fs` behavior suite are publicly excluded and have no hidden
  behavioral assertions.

The 731-pass upstream baseline proves the frozen reference revision is healthy.
The 50-leaf verifier is a reviewable 0-to-1 package contract, not a copy of the
upstream test suite.

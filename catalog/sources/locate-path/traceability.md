# `locate-path` Traceability

The frozen upstream suite has two AVA leaves plus one TypeScript declaration
check. The private verifier freezes 45 deterministic `node:test` leaves so the
filesystem contract is checked independently at its public API boundary.

| Public contract | Private coverage |
| --- | --- |
| ESM package identity, version, export map, declaration, exact dependency and scripts policy | Package inventory leaf |
| Async iterable, Set, generator, cwd string/URL, missing and empty inputs | Async filesystem leaves |
| Sync iterable, Set, generator, cwd string/URL, missing and empty inputs | Sync filesystem leaves |
| File, directory, both, original path spelling, inaccessible/non-string entries | Type and path leaves |
| Symlink follow/default and `allowSymlinks: false` for file, directory, broken links | Symlink leaves |
| Invalid type, invalid URL scheme, iterator exceptions, async concurrency and preserveOrder | Boundary/error leaves |

The trusted test process imports only `test_client.mjs`. It sends allowlisted
scenario names to a candidate child running as UID 10001 with bounded CPU,
process, file descriptor, wall-time, and JSON output limits. Fixture creation,
URL construction, callbacks, and filesystem operations happen in that child.
The verifier owns collection, network proof, grading, and reward files.

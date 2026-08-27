# Socket.IO Authoring Provenance

- Upstream: `https://github.com/socketio/socket.io`
- Revision: `ae7fb46e08c5ed964b4a1ea8b1703e816511598e`
- Package: `packages/socket.io`, version `4.8.3`
- License: MIT
- `git archive` SHA-256: `c3d386e859d6d51c8eb2672f1cec9db6bba05eba3cfc9bc35e5aef649f0b85eb`
- Locked runtime: Node 24.19.0, npm 11.17.0, Debian bookworm, amd64

The authoring baseline installed the exact monorepo lock, compiled all declared
workspaces, and then ran the 12 platform-neutral Socket.IO upstream test modules
three times with container networking disabled. Every run collected and passed
194 tests. The upstream `test/uws.ts` module is excluded because its frozen
prebuilt native addon requires glibc 2.38 while the locked image uses glibc
2.36; this is an environment adaptation, not a source patch.

The scored verifier uses 12 `node:test` leaves mapped to the public instruction:
exports, connection/event acknowledgement, namespace middleware, rooms,
broadcast exclusion, inventory/bulk room operations, outgoing acknowledgements,
ack timeout, forced disconnect, dynamic namespaces, custom path, and close.
Each call enters a candidate-owned subprocess running as UID 10001. Hidden test
files are copied only into the separate verifier image and are never placed in
the agent environment.

The npm closure contains a v3 lock and 21 pure-JavaScript transitive packages.
Every lock entry has an npm integrity and HTTPS resolution. The closure has no
workspace/file/git links, lifecycle scripts, native markers, platform selectors,
shell scripts, `.npmrc`, or `node_modules` tree. A strict offline `npm ci`, pack,
and clean-prefix install passed with the locked npm version.

The Oracle bundle is private. Its solution extracts a hash-recorded Debian git
runtime into `/tmp`, performs a certificate-verified fetch of only the frozen
revision from `github.com`, checks the resolved SHA and reproducible archive
digest, verifies the hash-recorded prebuilt reference package, and materializes
that package into `/workspace`. The bundle is uploaded only for trusted Oracle
runs; model runs receive neither the solution nor source-host authorization.

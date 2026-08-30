# Authoring Provenance

## Source freeze

- Upstream: `https://github.com/syntax-tree/unist-util-visit`
- Revision: `5d601df684ca7341646d6b57eb0f20fdfe277bc2`
- Package version: `5.1.0`
- License: MIT, root `license` file
- Git archive SHA-256: `sha256:d59ced4aa115b1ba3769a58fa82ffed6ea6f2b06cecc80cc846504399b1367ab`

The source archive was produced from the full commit after a depth-one fetch and
the resolved commit was asserted before archiving. The archive and upstream Git
worktree remain under task-local `.nl2repo/authoring-work/`; only hashes and
opaque private artifact references enter the source catalog.

## Runtime and dependencies

The task uses the locked Debian bookworm Node 24 image and npm 11.17.0 on
linux/amd64 with glibc. Candidate dependencies are the exact runtime closure
`@types/unist@3.0.3`, `unist-util-is@6.0.0`, and
`unist-util-visit-parents@6.0.2`. The closure is represented by an npm v3
package lock and integrity-checked private npm cache. Candidate and verifier
execution are no-network; only the trusted Oracle receives the exact GitHub
host authorization needed by `solve.sh`.

## Verifier boundary

The verifier runs `node:test` in a separate environment. Tests never import the
candidate package. They invoke the candidate-owned `adapter.mjs` through the
bounded JSON subprocess runner, and the adapter calls the package's own
callback-based API. Candidate UID, request/response limits, sanitized
environment, no-addons mode, process limits, and network isolation are enforced
by the generated verifier runtime.

## Collection and scope

Thirty deterministic leaf tests cover the documented package exports, preorder
and reverse traversal, node tests, callback metadata, action values, mutation,
and bounded edge cases. TypeScript declaration tests and upstream formatting or
coverage tooling are not part of the JSON runtime contract.

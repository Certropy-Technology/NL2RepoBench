# `strtok3` authoring provenance

## Source and license freeze

- Upstream: `https://github.com/Borewit/strtok3`.
- Frozen revision: `acac939a405a6dfebcf3fe9b9caba3641c491c95`
  (`10.3.5`), tree `e7e037b8869e7e3358c77cc2131fd13cb30a29dd`.
- Unprefixed `git archive --format=tar` SHA-256:
  `07d655e73200185f3c76b21a86538e09fddb9e3971bc907641d1929bdfa3c54c`
  (337,920 bytes).
- `LICENSE.txt` is MIT, SHA-256
  `c33959fabde25a1b6161d8e0fdc6fdcea1fc48095fe0bd51043247bfd214287f`.
- The revision contains 42 tracked files and no submodules.

The private Oracle solution fetches only the full revision, asserts
`FETCH_HEAD`, recreates the unprefixed archive, and verifies its digest. It then
uses the source-derived compiled distribution frozen in the private Oracle
bundle. The model Agent never receives the Oracle bundle or source-host
authorization.

## API and tests

The public Node root provides buffer, Blob, WHATWG stream, Node stream, and
file factories plus tokenizer state/read/peek/token/seek/lifecycle methods.
The original TypeScript source compiled successfully and the full upstream
Mocha suite passed 329/329 on the host probe. The production verifier freezes
44 independent public-contract leaves and uses a task-specific child adapter
for non-JSON JavaScript objects.

## Environment and dependencies

- Locked runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm,
  linux/amd64, glibc.
- Node image digest:
  `sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Exact runtime closure: `@tokenizer/token@0.3.0`, npm lockfile v3, private
  integrity-described cache, install scripts disabled.
- Agent and verifier are no-network. No static source, registry, or provider
  host appears in task metadata.

## Verifier boundary

The separate verifier rejects unsafe package tar members and lifecycle hooks,
installs from the frozen npm cache, and invokes candidate code as UID 10001.
Trusted `node:test` communicates with a fixed one-shot child protocol. The
child constructs typed arrays, Blobs, streams, temporary files, and token
objects; responses are bounded JSON. Grading, collection, network evidence,
JUnit, and reward remain verifier-owned.

Production compile, Oracle, controls, final receipt hashes, and residual risks
are recorded in `production-evidence.json` after the corresponding commands
have actually completed. Independent review, model Agent Run, dataset
integration, and publication are outside this lane.

# `p-timeout` Provenance

## Immutable source and license

- Upstream: `https://github.com/sindresorhus/p-timeout`
- Revision: `245066ef7daa5e74024d5b6a188ae599a1b7bfdf` (`v7.0.1`)
- Tree: `7a5a9d78f118e174e8ba4b5b21956be9003c9891`
- Unprefixed archive command: `git archive --format=tar HEAD | sha256sum`
- Archive SHA-256: `4f8e9a6fa4d0b1f3db355bfec23fe3fb646abdf062e112455a78bf756eeca151`
- Archive size: 40,960 bytes; seven tracked files; no submodules.
- Root `license` and `package.json` declare MIT. License SHA-256:
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.

## Environment and upstream baseline

- Locked runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm glibc,
  `linux/amd64`.
- Base image:
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- A fresh authoring-only install in that image installed 622 development
  packages and completed `xo && ava && tsd` with exit code 0; AVA passed all
  20 leaves. Development dependencies are not part of the task runtime.

## Deterministic adaptation and private closure

The candidate package has zero runtime dependencies. Its private npm v3 bundle
contains only a version-3 package lock, an empty npm cache, and a manifest pinned
to npm `11.17.0`. The task-specific verifier has 35 leaves and invokes candidate
behavior only through an unprivileged child-side adapter. Its first complete
Node 24 `--network none` probe passed 35/35 in 2.5 seconds.

- npm dependency bundle:
  `sha256:3625eb167b3d1cd4320c05e07fc855e6a807ab749346afaf87e51c21a20d4174`
- command-plan bundle:
  `sha256:10e70a89b271a2cd71d8dbaa6848530c6550ac4d87e65ae87d7332265e5eedd9`
- private test bundle:
  `sha256:b34fb24beac30111081257fc3f29bbea22026963c3f7a5e75a4e0fe84c65801d`
- Oracle bundle:
  `sha256:bb482d9ee73627eb8bd7c69237cf64a8f06dae934fa6087254a30169d0f20aa4`

The Oracle `solve.sh` initializes an empty Git repository, fetches only the
declared full revision, asserts `FETCH_HEAD`, creates an unprefixed archive,
strictly checks its SHA-256, and then writes a scripts-free zero-dependency
package manifest and v3 lock. Only the Oracle run receives a run-scoped
`github.com` authorization; the model Agent and verifier remain no-network.

## Production authoring gates

- Source validation and task-wide network lint exited 0. Network lint reported
  zero errors and no `p-timeout` finding.
- Two production compiles from the specified source were byte-identical. The
  compiled bundle contained 74 manifest-bound files with zero integrity
  mismatches.
- Harbor `0.21.0` Oracle exited 0 with `valid=true`, 35/35 passed, reward 1.0,
  and `public_network_available=false`.
- Empty and install-script controls exited 0 with the allowed installation
  exception and reward 0. Stub and forgery each collected 35 leaves, passed 6,
  and scored `0.17142857142857143`; the forged workspace reward had no effect.
  Call-hang and network-attempt controls each collected 35, passed 3, scored
  `0.08571428571428572`, and remained bounded with public network unavailable.
- The focused shared Node foundation suite passed 49/49. These are Oracle and
  deterministic controls, not a model Agent Run or publication approval.

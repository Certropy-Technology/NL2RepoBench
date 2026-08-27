# jsdom authoring provenance

- Upstream: `https://github.com/jsdom/jsdom`
- Frozen revision: `52be38ea0ce303b0756c7086ce8b3b9d74b0553b`
- `git archive` SHA-256: `ff4dd76eced724319ff27c9a57f3de19e73d366e2705b504955cf62efddc6eb5`
- License: MIT, verified from `LICENSE.txt` at the frozen revision.
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm amd64/glibc.
- Base image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.

The upstream tree does not commit its generated Web IDL/CSS output. Authoring
ran the frozen `prepare` Wireit graph once after an `npm ci --ignore-scripts`
in the pinned image, with the build stage offline. The resulting 287-file,
5,952,266-byte overlay is bundled only with the trusted Oracle. The Oracle
verifies the exact Git archive and every packaging overlay input before writing
the workspace. Its runtime manifest removes development dependencies, optional
Canvas, and lifecycle scripts without changing implementation behavior.

The private verifier uses a custom fixed-operation JSON subprocess adapter and
39 deterministic `node:test` leaves. It does not import candidate code in the
trusted process. Network-, filesystem-, Canvas-, image-, browser-, and WPT-only
surfaces are outside this release's public scored contract.

# own-keys authoring provenance

- Upstream: `https://github.com/ljharb/own-keys.git`
- Revision: `20620ebfd195d384d85fc134e29cc4916297a92f`
- Tree: `41cda75f31f03048490f5d73e3366d7e33f7f2de`
- Package: `own-keys@1.0.2`
- License: MIT, `LICENSE` SHA-256
  `5e325595b4ea8cfec3802f545b1def5d7b73e4a5b8e9ba63e32a320f67732292`
- Unprefixed `git archive --format=tar HEAD` SHA-256:
  `be351a99690d1692929f1e4c5c08aba84010cee56973f16156716eab5fa0e816`
- Runtime: Node.js `24.19.0`, npm `11.17.0`, Debian bookworm,
  `linux/amd64`.
- Base image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.

The upstream functional command `npm run tests-only` passed 5/5 under the
pinned runtime. Standalone TypeScript checking passed. The combined `npm run
lint` command exited 3 after six warning-only ESLint findings because its
postlint `attw -P` command failed inside `npm pack`; the raw task-local log is
retained under `.nl2repo/authoring-work/node-author-wave2-20260828/own-keys/evidence/`.

The candidate runtime lock contains 16 integrity-bearing npm packages and was
validated by a clean `npm ci --offline --ignore-scripts --no-audit --no-fund`.
The verifier runs in a separate environment. Trusted code never imports the
candidate; a bounded child-side adapter runs as UID/GID `candidate`, constructs
non-JSON JavaScript values, and returns typed JSON observations.

The Oracle bundle does not contain upstream implementation bytes. Its
`solve.sh` fetches only the full frozen revision from `github.com`, asserts the
resolved commit, regenerates and verifies the source archive digest, and copies
the reference root implementation into the offline candidate package. The
model Agent receives no source-host authorization.

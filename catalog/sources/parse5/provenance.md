# `parse5` Authoring Provenance

## Source and license freeze

- Upstream: `https://github.com/inikulin/parse5`.
- Revision: `e05c47c8caf2eda4c5136310e6f94e7f00c83380`.
- Package: `parse5@8.0.1`.
- Root `git archive` SHA-256:
  `27a205e827436e03acc87f91d6b1d57e209bf14267c48ed443813ff734113437`
  (3,860,480 bytes).
- Submodule `test/data/html5lib-tests`:
  `a9f44960a9fedf265093d22b2aa3c7ca123727b9`, archive SHA-256
  `58c8063ff052b8443e501d42530c23ec4321a9fac44843bf3d6c38dbdae4229d`.
- Submodule `test/data/html5lib-tests-fork`:
  `11c3216c8ec790dbda1494a84f580e0ea41d55a1`, archive SHA-256
  `e2d2c0a0c64d73b13a179dc448bf15443730d051b7f487a2fb954d588a9f1a63`.
- License: MIT; root `LICENSE` SHA-256
  `8c535800331e1e4439835555b3f9edc7fe9dee2fab0d8bbbd5a982e8b8343d4d`.

The initial archive-only baseline correctly failed collection for three suites
because Git archives do not contain submodule worktrees. The complete freeze
then ran three independent `npm ci --offline`, TypeScript build, and Vitest
runs in the locked production image. Every run collected and passed 19,325
tests across 15 files.

## API and test inventory

- Root runtime exports: `ErrorCodes`, `Parser`, `Token`, `Tokenizer`,
  `TokenizerMode`, `defaultTreeAdapter`, `foreignContent`, `html`, `parse`,
  `parseFragment`, `serialize`, and `serializeOuter`.
- Root type exports include parser/serializer options, default-tree node types,
  and tree-adapter interfaces.
- The `parse5` workspace package contains 22 TypeScript/JavaScript source files
  and 11,091 lines, including seven package-local test files. The full repository
  fixture tree contains 264 files and 7,388,331 bytes after submodule freeze.
- The production verifier freezes 54 package-root leaves. See
  `traceability.md` for bidirectional coverage.

## Environment and dependency closure

- Runtime image:
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64,
  glibc.
- Runtime dependency: exact `entities@8.0.0`, resolved by the frozen upstream
  lock and allowed as the task's only optional runtime package.
- Private npm v3 closure:
  `sha256:c7f8cec816b6dfc4eb30b391d8cde524c90c2284e83ed3cefe16f0d220914254`
  (266,240 bytes). It contains a lockfile, six content-addressed npm cache
  files, and per-file SHA-256 records.
- The closure passes `validate_npm_dependency_bundle` and a clean
  `npm ci --offline --ignore-scripts --no-audit --no-fund` probe.
- Candidate and verifier runtime network mode is `no-network`; package source,
  registry, and provider hosts are absent from task metadata.

## Verifier and Oracle boundary

- Separate verifier, no-network execution, candidate UID 10001.
- Candidate source is bounded-copied, installed from the private cache with
  scripts disabled, packed, validated, and installed in a candidate-owned site.
- Trusted `node:test` never imports candidate code. Each leaf invokes a bounded
  candidate child and receives only a cycle-free tree/string/metadata projection.
- Command-plan bundle:
  `sha256:ff24615a926405b2fa2d1bde2ccbb0816fc0a5d3364f4585da23888979c665cf`
  (10,240 bytes).
- Private test bundle:
  `sha256:139c4f72fea52dc4823c0be2c99db5bca6df3001772b0c0d69ed27ec2eb79eed`
  (30,720 bytes).
- Private Oracle bundle:
  `sha256:2430c9964c8ce92efe00b0235d6b19c197de002d7a5103355b47766d52a97a69`
  (8,878,080 bytes). Its solution verifies root source, both submodule archives,
  and the derived package archive before populating `/workspace`.

## Production evidence

- The production compile under `toolchain.node.lock.toml` completed with all
  four private artifacts resolved from `.nl2repo/artifacts`.
- A transient first Harbor Oracle attempt reached the verifier but failed its
  candidate npm step before collection. A retry on the same task content
  completed with `valid=true`, 54/54 leaves passed, reward `1.0`, and no public
  verifier network.
- Empty and install-script controls scored `0`; stub and forgery controls each
  scored `3/54` (`0.055555...`), and the forged workspace reward was ignored.
  The timeout control produced a bounded `ETIMEDOUT` collection error and
  reward `0`. The offline replay collected all 54 leaves with public network
  unavailable.
- Machine-readable paths, commands, digests, and residual risks are recorded in
  `production-evidence.json` and the task-local authoring handoff.

No Harbor model Agent run was performed in this lane.

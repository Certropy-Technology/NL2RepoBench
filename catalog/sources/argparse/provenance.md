# Argparse Authoring Provenance

## Immutable source and license

- Upstream: `https://github.com/nodeca/argparse`
- Revision: `e9eb9de652dc3f101b7320ceb682c60f407e2af6`
- Tree: `e94af4f37d9f2fce41907cb9d4fc8cd597b1ed5f`
- `git archive --format=tar <revision>` SHA-256:
  `de70bd9568e9eda8f5c8fd92684852cfa90ef490f52a451393c3675c586055c9`
- Archive size: 645,120 bytes; 19 tracked files; no submodules.
- `LICENSE` SHA-256: `ab745c5061d1dea43a3885e5b4b6befc7e983954954775c5736debeefcdfd89b`.
  The package declares PSF-2.0.

The codeload archive for the same immutable revision was independently fetched
for Oracle authoring and has SHA-256
`67b1e74b3890d3781ce4bec8649243514d052125763cec16fa865ac6324786c8`,
size 117,481 bytes. The Oracle verifies this digest before extracting it.

## Baseline and environment

The pinned source baseline used Node `24.19.0`, npm `11.17.0`, Debian bookworm,
linux/amd64, glibc, and base image
`docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
`npm ci` and `node --test` were executable. The upstream suite collected 1,830
leaves, passed 1,824, and failed six `FileType` expected-throw cases. The
failure log is retained task-locally and is not treated as an infrastructure
failure or an Oracle result.

## Dependency closure

The frozen source has no runtime dependencies. Its 286 non-root lock entries
are dev-only tooling and are not part of the candidate closure. The production
candidate bundle therefore contains a v3 lock with an empty package set and an
empty npm cache. npm install and npm pack remain offline and ignore scripts.

## Oracle adaptation

The private Oracle solution fetches only the exact revision from
`codeload.github.com`, checks the codeload digest, extracts the verified tree,
and checks the source file manifest. It removes development metadata, keeps the
upstream `lib/` runtime and declaration files, and writes a matching
scripts-free package manifest and zero-dependency npm v3 lock. The source host
is authorized only for the trusted Oracle run; the model and verifier remain
offline.

## Private artifacts

The exact dependency, command-plan, private-test, and Oracle bundle references
are recorded in `task.toml` after ingestion into the local content-addressed
artifact store:

- npm zero-dependency bundle: `sha256:4434d109c04b59e6ad4510059d6ef306d7d1e0bd4d55bdba404e4c7b2f9af925` (388 bytes)
- command plan: `sha256:ecade7e4a7652dc33367d2c5ce2971815591d9ae5bc4482e009eb1fa3af6552a` (176 bytes)
- private tests: `sha256:150b54a87f2a14f15029ae0dad06e3783dd32434c62f7faf389c872026ad06b5` (4069 bytes)
- Oracle bundle: `sha256:f1b6ef33cee9e1dd01dbebfabc7c4218688f3872e9ab1d8a2c3ec2d7f94918a3` (2632 bytes)

Private tests and Oracle bytes never enter `catalog/sources/argparse`.

## Final authoring gates

- Source validation passed with status `controls-passed`; current source digest is
  `sha256:1e752dbc94dc3113795a86701fba4afc94791a5f7df4ebd03aaf29dba6dda1ad`.
- Network lint passed with zero task errors. The repository-wide command reported
  unrelated warnings for other sources; no `argparse` finding was emitted.
- Production compile passed using `toolchain.node.lock.toml`, `.nl2repo/artifacts`,
  and `--allow-private`. The task-local generated bundle manifest is
  `sha256:7586cdb76978b5e7508f0ef7915baaef267531d123f9f5aaeae4032f7195f8d0`.
- A fresh Harbor 0.21 Oracle run on that compiled bundle completed with
  `valid=true`, `31/31` collected/passed, reward `1.0`, and a no-network verifier
  receipt. Fresh stub and forgery controls collected all 31 leaves and scored
  `0.0`; earlier task-local runs additionally covered empty, install-script,
  loader-hook, hang, and offline controls.
- No model Agent Run was started. Review, pilot, and publication remain outside
  this authoring lane.

# jsonrepair blocked remediation record

Status: **blocked**. The source revision and ISC license are frozen, and the
locked Node image is available. Production execution is not authorized because
the candidate package cannot yet be installed from a complete approved npm
cache while runs are offline.

## Source freeze

- Upstream: `https://github.com/josdejong/jsonrepair`
- Revision: `4a80ed87fb1155db064945bc2aa4f6b4f4e89c27`
- Git archive SHA-256: `sha256:b4245dabfaca974f251eca04bfe5f0d03c4886f2b30540e76395f3173af965c1`
- License: ISC, `LICENSE.md`, SHA-256 `sha256:fd50f5abb7eeb614c8d1293b9f239a5238d7536e3a9a9a8929a082c82d12b3fd`
- Candidate image: Node `24.19.0`, npm `11.17.0`,
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`

## Remediation evidence

Failure class: **environment**.

The exact locked image was run with `--network none`, an empty npm cache, and
the source checkout. The command exited `1`; npm reported `ENOTCACHED` for
`yocto-queue@0.1.0`. The captured output is hash-bound in
`evidence/remediation.txt` and referenced by `production-evidence.json`.

## Reopen condition

Materialize and review a complete private npm cache for every integrity entry
in the committed lock under Node `24.19.0`/npm `11.17.0`. Rerun
`npm ci --offline --ignore-scripts --no-audit --no-fund` in the pinned image;
only after it passes may a clean package adaptation, private `node:test`
adapter, frozen denominator, separate verifier, Oracle, and controls be
created.

No `catalog/tasks/jsonrepair` runtime was created.

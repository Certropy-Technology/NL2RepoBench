# `hast-util-whitespace` Provenance

- Upstream: `https://github.com/syntax-tree/hast-util-whitespace`
- Frozen revision: `22b88c3f4d51f3777929758e980c257a2838a4b2` (`3.0.0`)
- Git archive: `sha256:d012e1fee404e631ad5a5b5aa3f338b413417e73f80b53d5d0c0e7a469f8e1be`, 30,720 bytes
- License: MIT; frozen `license` file digest
  `sha256:ca4662cb5d1b738fbe5350c0d5485ba11773b4b7208974082ae6e129a52d631d`
- Upstream tree: 13 files, no submodules, one public named function, six
  original nested test cases.
- Locked runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm glibc,
  `linux/amd64`.
- Production adaptation: the upstream package metadata declares
  `@types/hast` for JSDoc tooling only. The Harbor contract is runtime-only,
  so the private Oracle packaging removes that non-runtime dependency and
  development scripts while retaining the frozen implementation files. The
  candidate contract correspondingly has an empty npm dependency closure.

The source clone, archive and private bundles are retained only under the
task-local `.nl2repo/authoring-work/hast-util-whitespace/` directory during
authoring. They are not part of the public instruction or Agent environment.

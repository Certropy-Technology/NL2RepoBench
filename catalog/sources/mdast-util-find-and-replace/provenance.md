# Authoring Provenance

- Task: `mdast-util-find-and-replace`
- Upstream: `https://github.com/syntax-tree/mdast-util-find-and-replace`
- Revision: `fd73ef856ab4f7b6326e3255aea36f439b75e2d5`
- Git tree: `7972508b1cf0195e57799effef402311b1469811`
- Package: `mdast-util-find-and-replace@3.0.2`
- License: MIT; frozen `license` SHA-256
  `dd1081884a92952802f4803110a6bb543acea9a814c786d58605b4c1219b5ebb`
- Git archive: 51,200 bytes; SHA-256
  `be821926713dee556bca6f0aa2cff873a8fef69d142f438327e84f08cf2d57d9`
- Runtime: digest-pinned Node `24.19.0`, npm `11.17.0`,
  `linux/amd64`, Debian bookworm/glibc
- Agent runtime git: `2.39.5`, Debian package
  `1:2.39.5-0+deb12u3`
- npm closure: v3 lock with four direct exact dependencies and one transitive
  package (`@types/unist@3.0.3`); lifecycle scripts ignored; private cache
  artifact SHA-256
  `cde2303142b36ec9b1f3f5a40973748bbca59c70e5c1808a6da19a8cf52f2767`
- Private verifier: 48 flat `node:test` leaves; test artifact SHA-256
  `bb83e1b66bbd37c370e415c68d33262795cc92529845603b1cb0b5ca40d26c36`
- Oracle bundle: exact-revision fetch, commit assertion, archive digest
  assertion, package normalization, frozen lock and declarations; SHA-256
  `729739e81da7f099ce0ed2170fe184deb56f4bae2a8114fc554e42b812c44cb1`

Authoring probes used the claimed commit in a task-local checkout. After a
one-time dependency install, `npm run build` and `npm run test-api` were replayed
with Docker network disabled under the pinned Node image. Build exited 0,
type-coverage reported success, and the upstream suite passed 25/25 entries
(24 behavioral subtests). Production compile, Oracle, and control receipts are
recorded separately in `production-evidence.json` after those gates run.

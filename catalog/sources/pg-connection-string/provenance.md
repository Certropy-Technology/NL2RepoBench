# Source Provenance: `pg-connection-string`

- Upstream: `https://github.com/brianc/node-postgres`
- Frozen revision: `c9e57617bc92c2ded23a75345f50eadc527bd131`
- Git archive SHA-256: `87330e434dc4d6c02e9f662910d7fcc81af2cc9bbb7bf97d08f72046766c43a6`
- Package path: `packages/pg-connection-string`
- Package version: `2.14.0`
- License: MIT; package `LICENSE` SHA-256:
  `2244b5486c4427001b6756a87b9a297d427c111dcc3ba64a097492a8979c23d0`
- Package metadata SHA-256:
  `a573b84797e1ba474df8f3c4b7195709cb25531e7a34a7c424d1678cf414e615`
- Main implementation SHA-256:
  `6523b5d5ad961775b9befa691edccf8080a79da52b91142834f9e6f6d75eb5e3`
- Upstream Yarn lock SHA-256:
  `b5a8defca8d6b9458da0c58abf8ab7d7abd35b9e3cb6eefd530339de9550d2df`

The authoring checkout is detached at the frozen revision and has no
submodules. The package's original TypeScript/Mocha suite was remediated in a
task-local npm probe because Corepack/Yarn was unavailable in the host image:
`npm install --ignore-scripts --no-audit --no-fund` followed by its test
command passed 79 tests and the upstream 100% coverage gate. The production
task has no runtime dependency roots, so its private npm v3 closure contains a
minimal package root and empty npm cache only.

# get-east-asian-width Authoring Provenance

## Source and license lock

- Upstream: `https://github.com/sindresorhus/get-east-asian-width`
- Frozen revision: `75cd90f988bb24afc6e9889485acf21fe86076f8` (`1.6.0`)
- `git archive --format=tar <revision>` SHA-256:
  `b412e8d6253a64848848d2b2e9a1e397b7668505d78c43a1c6583a29ec413593`
- Archive size: 245,760 bytes; 18 tracked files; no submodules.
- Root `license` SHA-256:
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- Root `package.json` SHA-256:
  `d263e50dd1a43aee9acda4d7f066e66b0d0bde1f2852ea6e7153750a5e3a3e52`.

The archive includes the generated Unicode lookup data. The Oracle uses this
private source material only after the exact archive digest is verified.

## Baseline and environment

The pinned production environment is Node `24.19.0`, npm `11.17.0`, Debian
bookworm, linux/amd64, glibc, and base image
`sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
The upstream package has no runtime dependencies. Its development metadata
declares AVA, TypeScript, XO, outdent, and simplify-ranges, but those ranges
are not part of the candidate closure.

The exact upstream AVA suite contains seven test cases. A direct authoring
probe with the checkout and Node `22.23.1` failed before collection because
`ava` was absent. This is retained as a dependency-probe result; the private
contract has 24 deterministic leaves and does not silently treat the failed
probe as a passing test result.

## Adaptation boundary

The scored contract keeps the two documented named exports and safe-integer
inputs that cross a JSON subprocess. It omits private helper exports, the
networked Unicode-data build script, and non-JSON JavaScript values. Unknown
safe integers map to `neutral`/width `1`, matching the frozen runtime
behavior; invalid input fails with `TypeError`.

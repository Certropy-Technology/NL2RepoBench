# yargs Authoring Provenance

## Immutable source and license

- Upstream: `https://github.com/yargs/yargs`
- Revision: `2a4378bdc2eac9cf7d0cdfe0a52b1b25f779806a`
- Tree: `ff2d1aefe96cc9e091a1b204e0b26428baff35cc`
- Subject: `Add FUNDING.yml with funding sources`
- `git archive --format=tar <revision>` SHA-256:
  `3f687bc9c8904b92fecad8d73b002e879fa1d7b10543666b4daddfcdfaf4c565`
- Archive size: 1,454,080 bytes; 172 tracked files; no submodules.
- License: MIT. `LICENSE` SHA-256:
  `2f1a503bfab84b3ba7393627308b3274501e459e3b5185bbb56bbf16cb1602d4`.

The exact codeload archive is 290,251 bytes with SHA-256
`39e592f3246a8bf8833eaf5cd173b5abc9030cd901dfdbc96bae7c68161c1260`.
All 172 regular file paths and SHA-256 values are identical to the unprefixed
Git archive tree; the normalized content-manifest SHA-256 is
`9dc6d159d42fd5a41e8aa760b05e8e32818eb50bf3c4b6f04a9daacb7fdb7a41`.

## Upstream baseline

In the pinned Node image, three independent archive extractions each ran a
clean npm install, TypeScript build, and upstream Mocha suite. Every run exited
0 with 839 passing tests. Logs and hashes are retained under the task-local
`.nl2repo/authoring-work/yargs/logs/` directory.

## Environment and npm closure

- Image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc.
- Runtime closure: 14 npm package entries beneath the root lock, all with
  registry resolutions and SHA-512 integrity. No Git source, native addon,
  platform selector, or install script is present.
- The cache was seeded through the exact packed Oracle package so both
  candidate `npm ci` and clean-prefix package installation work with
  `--offline --ignore-scripts`.

## Oracle adaptation

The Oracle solution fetches only the exact revision from
`codeload.github.com`, verifies the codeload archive digest, extracts it, and
checks all 172 source file hashes before adapting it. The adaptation copies
TypeScript output built from the verified source, removes development and
lifecycle metadata, pins the six direct runtime dependencies exactly, and
installs the matching runtime-only v3 lock. It does not change runtime source
behavior. The source host is granted only to `-a oracle`; model runs remain
offline.

## Private artifacts

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| npm lock/cache closure | `de7bee323ff2986972f9981474e4f3e2eb99b28b8fe082eed3ed0097491ec776` | 1,187,840 |
| command plan | `a832562812d78324c3ac1b16a15a9ab97c6e9e92ad7de119f2da7bb997be8661` | 10,240 |
| private tests and adapter | `9195c764a5dba3758c36b47ea05bf6182741f3c67550c2ea837cb40f7f2c9963` | 30,720 |
| Oracle solution | `0569279fcd0e247fb4a56082847fb7bf1ed3e7d0ec9101215093e6a0654de53a` | 430,080 |

The local no-network replay performed candidate packaging and installation,
collected exactly 42 leaves, and passed 42/42 with no collection error.

# Source Freeze

- Package: `basic-ftp` 6.2.0
- Upstream: `https://github.com/patrickjuchli/basic-ftp`
- Revision: `9cbc5cf23cb2b62231bc1822a868138e4772d4e5`
- Raw `git archive` SHA-256: `sha256:e7998232ed9c801ef5b2277b8164c74d7595317bbbb08f57ef8dc1c8aca27364`
- Exact codeload archive SHA-256 used by the Oracle: `sha256:515fbf4bfc6fed25ed9b58d5ef72d9d67cbe13cb4a2b6ca5abdcff4435ae092e`
- License: MIT; frozen `LICENSE.txt` SHA-256 `sha256:5b417c1f5ee996875e86b4959851c94e102edbbb3c68199bd3336c7351c924f9`
- Submodules: none

The raw archive was created from the complete commit tree, not the cloned
working tree. The clone had unrelated pre-existing edits after checkout; those
edits were excluded from every source and Oracle artifact.

The upstream package has no runtime dependencies. Its development closure at
the frozen revision contains TypeScript, ESLint, Node types, and testcontainers,
but the production task deliberately ships a zero-runtime-dependency package
and an empty, validated npm v3 verifier closure.

# Source Freeze

- Upstream: `https://github.com/prompt-toolkit/python-prompt-toolkit`
- Revision: `583b3412c792a5cc9f01adde603679f3824a88f3`
- Commit subject: `Release 3.0.53`
- Commit timestamp: `2026-07-26T22:58:05+02:00`
- Commit tree: `482947dab7944cdfaaa248b80b10aac052440c7c`
- Archive command: `git archive --format=tar 583b3412c792a5cc9f01adde603679f3824a88f3`
- Archive SHA-256: `sha256:b9dda9618cc8482f22128b28e60b095bb7eb95926e1c17276da2d4eeccc8feb0`
- Archive size: `6,031,360` bytes
- License: BSD-3-Clause; frozen `LICENSE` file SHA-256 is
  `sha256:303574d9bdd85c757d6025017942bf17baeedf2778f62bd7f425d07d880f4c4a`.

The source was fetched once into task-local authoring work using the exact
commit SHA, then its commit identity, tree, archive SHA-256, and byte count
were checked before creating the local private Oracle bundle. The Oracle never
fetches source at runtime. The full archive remains intact in that private
bundle; no upstream assertions were deleted to create the scored slice.

The frozen runtime is CPython 3.12.14 on Debian 12 linux/amd64 using
`python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
The private build lock pins `setuptools==80.10.2` and `wcwidth==0.8.1` with
all package hashes and is installed only during Docker image construction.

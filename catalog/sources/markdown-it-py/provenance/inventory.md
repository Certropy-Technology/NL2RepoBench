# `markdown-it-py` inventory

## Frozen source

- Upstream: `https://github.com/executablebooks/markdown-it-py`
- Revision: `bff75edcd7e6ce68f417803361d6e9f1223ad373`
- Commit date: `2026-07-08T02:37:28-07:00`
- License: MIT; the frozen `LICENSE` bytes are retained in the source archive.
- Unprefixed `git archive --format=tar HEAD`: 1,474,560 bytes,
  SHA-256 `16144aa1aa730efe92e175a3677d0546f571049f612a20452f47136dead1f88c`.
- No submodules.

## Static and runtime inventory

The deterministic scanner found 72 implementation Python files, 5,316
implementation lines, 357 public symbols, 393 imports, 17 test files, and 91
test functions. It reported no syntax diagnostics. The full upstream test
collection is 981 tests; with the declared testing, linkify, and plugins
extras installed, Python 3.12.11 ran **981 passed**.

The first base-only probe had 73 optional plugin fixture failures. Installing
the upstream optional testing closure (`mdit-py-plugins`, `linkify-it-py`, and
`uc-micro-py`) repaired those failures; these packages are intentionally not
runtime requirements of the scored task. The production verifier therefore
uses the core parser and deterministic local extension API only.

Risk flags are `dynamic-execution` from parser rule callbacks and
`external-service` from optional linkification integrations. The scored
adapter runs candidate code as an unprivileged UID 10001 child, and no live
service or network result is used.

## Dependency remediation

The upstream build backend is Flit. The candidate install path uses
`--no-build-isolation`, so `flit-core==3.12.0` is included in the private
hash-locked build closure together with the required runtime `mdurl==0.1.2`.
The lock was generated with `uv pip compile --generate-hashes`; no wheelhouse
or vendored distributions are used. The final task image is
`python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.

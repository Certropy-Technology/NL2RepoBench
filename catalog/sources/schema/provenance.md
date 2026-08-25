# `schema` production authoring provenance

## Frozen authority

- Upstream: `https://github.com/keleshev/schema`
- Revision/tag: `7434a6b3c9cd1672f0d491ed45114054750627af` / `v0.7.8`
- Tree: `878672fe16c4bfa905edc48698cbfc2ae19bacc2`
- Commit date: `2025-10-11T16:11:46+03:00`
- `git archive --format=tar` SHA-256:
  `2579256cf635a4053aaf5b0abb64f0ab403b3cb4a319e2fa8f0879e9682c5e8f`
- Submodules: none.
- License: MIT (`LICENSE-MIT` in the frozen tree).

The frozen implementation is 961 physical lines in `schema/__init__.py`. Its
single upstream test module collects 118 tests and passed 118/118 on CPython
3.12.14 before adaptation. The local Oracle bundle stores that exact source
archive and verifies the same digest before extraction; it performs no network
fetch or functional patch.

## Environment and closure

The pinned image is `python:3.12-slim` at
`sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
At this Python version the upstream conditional `contextlib2` dependency does
not apply, so the package has no third-party runtime dependency. Setuptools
80.10.2 and wheel 0.45.1 form the complete build closure. The private lock was
generated with `uv pip compile --python-version 3.12 --generate-hashes
--no-annotate --no-header`; pip accepted it with `--require-hashes` in the
pinned image. Dependencies are installed only during image build.

## Bounded verifier

The 30-leaf `custom-json-v1` contract adapts deterministic assertions from the
frozen upstream tests. It covers package surface, validation dispatch,
transformations, mapping/container behavior, defaults, hooks, forbidden and
exclusive keys, error taxonomy/content, JSON decoding composition, and the
documented deterministic draft-07 generator surface.

The trusted parent reads expectations before making them root-only, runs each
scenario as UID 10001 with resource limits and process cleanup, and compares
JSON observations. Only the child imports candidate code. Callables and hooks
are allowlisted fixtures built inside the child; no source, import path,
callable, or arbitrary object crosses the JSON boundary.

Stress, filesystem examples, recursive references, randomized hash-reference
IDs, custom inheritance internals, and unbounded JSON Schema behavior are
excluded and are not hidden requirements.

## Production controls

Harbor 0.21.0 ran the strict production bundle without
`--allow-incomplete`. Final receipts are path- and SHA-bound in
`production-evidence.json`:

- Oracle: valid, collected/passed 30/30, reward 1.0;
- empty workspace: valid candidate installation failure, reward 0.0;
- importable package/API stub: valid, collected 30, passed 0, reward 0.0;
- importable forged workspace/trusted-path reward attempt: valid, collected
  30, passed 0, reward 0.0 despite candidate-owned reward files and import-time
  writes;
- every Oracle/control verifier network probe reported
  `public_network_available=false`.

The lifecycle is `controls-passed`. Reviews, model pilots, publication, shared
catalog changes, commits, and pushes were not performed.

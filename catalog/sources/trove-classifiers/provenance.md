# Trove Classifiers authoring provenance

- Upstream: `https://github.com/pypa/trove-classifiers`
- Frozen revision and tag: `71cb041f383cee31668d07e3302d2b09d10471a8`,
  `2026.6.1.19`
- Commit time: `2026-06-01T15:40:38-04:00`; Unix epoch `1780342838`
- Source tree: `c3c5aac244eb6892c631fc449d555f8dd82db75b`
- Canonical `git archive --format=tar` size: 92,160 bytes
- Canonical source SHA-256:
  `cf3257e1a57e7dddf0e883955c5bfb579fcd5bea3d154b6ab43748b7b78454ca`
- License: Apache-2.0; tracked `LICENSE` SHA-256:
  `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`
- Upstream baseline: CPython 3.12.14, pytest 9.1.1, 18 collected and 18
  passed with container networking disabled.
- Production runtime: CPython 3.12.14 on Debian 13 amd64 from the digest-pinned
  `python:3.12-slim` compiler image.
- Fresh verifier image: `nl2repobench/trove-classifiers-verifier:authoring-current`,
  image ID `sha256:1f66e052888ebb1b4db955f612fd7add4ecf5127b88a2a5dda7bcf489faf1852`.
- Private dependency closure: `calver==2025.10.20`,
  `setuptools==80.10.2`, and `wheel==0.45.1`, with six SHA-256 hashes.
- A fresh digest-pinned authoring image replayed the lock with
  `pip --require-hashes`. A subsequent `--network none` container installed the
  source with `PIP_NO_INDEX=1`, `--no-deps`, and `--no-build-isolation`.
- `calver` reads `SOURCE_DATE_EPOCH`; freezing it to the commit epoch reproduces
  distribution version `2026.6.1.19` instead of a wall-clock-dependent build.
- The trusted Oracle alone fetches the full SHA, asserts `HEAD`, creates the
  canonical archive, and checks the source digest before candidate installation.
- Fresh Harbor 0.21.0 evidence on 2026-08-30: Oracle 35/35 at reward 1.0;
  stub, forgery, and call-hang controls 1/35; empty and install-hang controls
  completed as bounded installation exceptions at reward 0. Every separate
  verifier network probe reported `public_network_available=false`.
- Large source, build, CAS, and run artifacts stay under task-local `.nl2repo/`.

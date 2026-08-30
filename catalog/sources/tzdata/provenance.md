# tzdata authoring provenance

- Upstream: `https://github.com/python/tzdata`
- Frozen revision: `6c7fa78dc6b8fc9bf5301a0a1052d336f7efa192`
- Commit tree: `80b4be5f1b4ce623e55060004aae69e26d534bc7`
- Commit date: `2026-08-04T11:44:35+02:00`
- Nearest release tag: `2026.3`; frozen revision describes as `2026.3-2-g6c7fa78`.
- Canonical source archive: raw `git archive --format=tar` bytes, 1,208,320 bytes, SHA-256 `5b4ac0fb237db87b95008d329ec1d038b3e86513ee6c11c51098f7bcc20a51b0`.
- License: Apache-2.0. Frozen `LICENSE` SHA-256 is `df58f69ea88683035d720b5375bcef0cf5aeaa98a1d098d572e0992c378deb46`.
- Package version: `2026.3`; IANA data version: `2026c`.
- Frozen package tree: 598 named TZif files, six ancillary zoneinfo text resources, 21 resource-package markers, and a 598-line `tzdata/zones` manifest.
- Locked runtime: CPython 3.12.14 on Debian 13 amd64, image `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
- Build closure: exact `setuptools==80.10.2` and `wheel==0.45.1`, four allowed SHA-256 distribution hashes, lock SHA-256 `90a80e01203c275711b283f26c56ef906501fd427bc02887dfc36f046c96aeae`.
- Upstream baseline: `30 passed, 598 subtests passed` with pytest 9.1.1. The initial read-only source mount failed because setuptools writes `src/tzdata.egg-info`; copying the frozen checkout to a writable temporary directory remediated the environment mismatch.
- Offline candidate install probe: after replaying the hash lock, `PIP_NO_INDEX=1 pip install --no-deps --no-build-isolation` built and installed `tzdata==2026.3` successfully.
- Oracle source acquisition exists only in the private trusted solution. It fetches the full revision, asserts `FETCH_HEAD`, recreates the canonical Git archive, and validates its SHA-256 before extracting into `/workspace`.
- Large source/build/run material and complete logs remain under `.nl2repo/authoring-work/tzdata/` and `.nl2repo/runs/`; public catalog files contain compact audit facts and immutable private artifact references only.

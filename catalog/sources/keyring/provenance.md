# Keyring authoring provenance

- Upstream: `https://github.com/jaraco/keyring`
- Frozen revision: `7603e7cadc254b4c6e3fc2b2f0916a005e78087d`
- Nearest release: `v25.7.0`; the frozen revision is eight commits later and resolves to `25.7.1.dev8+g7603e7cad` with `setuptools_scm`.
- Source tree: `f2d1f775e4da7f12e0dafceaea017d0d3702ce35`.
- Source archive: canonical `git archive --format=tar` bytes, 235,520 bytes, SHA-256 `30dfe6cd4dcf67495e2ff1d8a3196593b5263f8d9180fe2cabc5cdc3582815a9`.
- License: MIT, declared by the frozen `pyproject.toml` project metadata. The commit does not track a `LICENSE` file; `coherent.licensed` generates a 1,076-byte MIT license during build with SHA-256 `9755a18519666e5f0f4cae3daad3d7012bcae48a600b31237d75e9fe134e6683`.
- Upstream baseline: Python 3.12.11, 130 collected tests, `34 passed, 94 skipped, 2 xpassed`; skipped cases require platform credential services or unavailable platform backends.
- Production runtime: Python 3.12.14 on Debian 13 amd64 from the digest-pinned compiler image.
- Private dependency closure: 14 exact packages and 170 SHA-256 hashes; verifier runtime installation is offline after image build.
- The private lock was replayed with `pip install --require-hashes`: all 14 packages resolved at their declared versions. With that closure preinstalled, `PIP_NO_INDEX=1 pip install --no-deps --no-build-isolation` built and installed the frozen source as `keyring==25.7.1.dev8+g7603e7cad` without runtime network access.
- The installed wheel contains `keyring/py.typed` and all declared console, backend, and devpi entry points. The two tracked `backend_complete` shell files remain source-development assets in this revision and are not installed as wheel package data.
- Oracle source acquisition occurs only inside the trusted Oracle solution. It fetches the full revision, asserts `HEAD`, recreates the canonical archive, and checks its SHA-256 before exposing the checkout to candidate installation.
- Large source/build/run material and full command logs remain under `.nl2repo/authoring-work/python-author-wave2-20260828/keyring/` and `.nl2repo/runs/`; public catalog files contain only compact provenance and immutable references.

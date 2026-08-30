# Frozen Inventory

- Upstream: `https://github.com/jaraco/zipp`
- Revision: `29a7a55c6bac1a6f705b54135dbea82d03e997c3`
- Git tree: `f5415027858404491bc1203ac61f72045f50882d`
- Git describe: `v4.1.0`
- Distribution version: `4.1.0`
- License: MIT, declared by the frozen `pyproject.toml`. The source tree has no
  license file, so the Oracle adds the canonical SPDX MIT text only after the
  exact Git archive digest is verified.
- Git archive: 38 regular files, 112,640 bytes,
  `sha256:64c592a33b2a8e3cdd190b6bba014888aca0fe094f345c42a4c52a7fdd7e92f6`.
- Runtime: Python `>=3.10`; evaluated with CPython 3.12.14 on
  Debian 12 amd64.
- Native extensions: none.
- Runtime dependencies: none.
- PEP 517 backend: `setuptools.build_meta` with `setuptools_scm` and
  `coherent.licensed` build plugins.

## Source Surface

The runtime tree contains `zipp/__init__.py`, `zipp/glob.py`,
`zipp/_functools.py`, and compatibility modules under `zipp/compat/`. The
declared root export is `Path`. Root compatibility classes `CompleteDirs` and
`FastLookup` support implicit directory synthesis and cached read-only lookup.
The overlay module projects `zipp.Path` into a module-like copy of `zipfile`.

The implementation uses only the standard library. Its observable risk surface
is bounded local filesystem and ZIP I/O: in-memory and on-disk archives,
path-like inputs, ZIP member streams, Unix symlink mode bits, pickle, and
glob-regex translation. It has no network, subprocess, database, browser,
native, random, locale, or external-service behavior.

## Test Inventory

The frozen repository has 61 collected upstream test methods on CPython 3.12.14.
`tests/test_path.py` completed with 55 passed, one version-gated encoding-warning
skip, and 96 passing unittest subtests. The complete suite produced 59 passed,
one skipped, and one failure in an upstream `@flaky` empirical Big-O classifier;
the deterministic path behavior all passed. The slim runtime omits CPython's
`test.support`, so the source-only probe supplied a minimal `FakePath` and
`temp_dir` compatibility module matching the two imported helpers.

The production verifier freezes 38 deterministic leaves. It does not score the
timing classifier and does not import candidate code in the trusted process.

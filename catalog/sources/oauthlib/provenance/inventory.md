# Source And Test Inventory

- Upstream: `https://github.com/oauthlib/oauthlib`
- Frozen revision: `40b0ab56da3682c2484a4b78bbff309f8025d950`
- Commit date: `2026-07-14T23:42:53+02:00`
- Distribution: `oauthlib==3.4.0`
- License: BSD-3-Clause; `LICENSE` SHA-256 is
  `sha256:0028aa4763a8a0b09ca4c68d585263474cf9aaa6ec69ffbef3a31a9eccdd3b91`.
- Reproducible unprefixed `git archive --format=tar HEAD`: 1,935,360 bytes,
  SHA-256 `sha256:7d459f401eb8595ad42c7a77edfb0ee17b67acf27213812d1c13a1ed505d7c2b`.
- No submodules.
- Static inventory: 75 implementation Python files, 12,492 implementation
  lines, 77 test Python files, and 9,489 test lines. AST inventory found 414
  implementation functions and 116 classes; tests contain 616 functions and
  89 classes.
- Runtime dependencies are empty for the core package. The upstream test
  baseline used pytest 9.1.1, pytest-cov 7.1.0, pytest-subtests 0.15.0,
  blinker 1.4, cryptography 50.0.1, and PyJWT 2.13.0.
- An isolated Python 3.12.11 run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`,
  `pytest -c /dev/null tests`, and the optional test extras passed **703**
  tests, **2** tests were skipped, and **21** subtests passed (exit code 0).
- The production denominator is a fixed 42-leaf custom-json-v1 behavioral
  subset. It covers package metadata/debug state, common encoding and request
  helpers, OAuth1 normalization/signing/header preparation, OAuth2 scope/URI
  helpers, grant/token parsing and preparation, bearer placement, and client
  state/request construction. Network calls, callbacks, RSA/JWT extras, and
  server validators are intentionally excluded from the deterministic subset.

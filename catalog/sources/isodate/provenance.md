# Provenance and Remediation

- Upstream `https://github.com/gweis/isodate`, frozen at
  `17cb25eb7bc3556a68f3f7b241313e9bb8b23760`.
- The commit timestamp is `2024-10-09T11:49:36+10:00`; the checkout has 29
  tracked files, no submodules, 1,362 source Python lines, and 946 test Python
  lines.
- License bytes are BSD-3-Clause from the upstream `LICENSE` file, SHA-256
  `ce5fe4893fb6ab843de77b367bfa9db974d7b00ab9033fcca8d7760a97fe1b43`.
- Unprefixed `git archive --format=tar` digest is
  `sha256:50b897e1c615278d8f9add946f74635564c500d01503793a0663f615eedf8622`.
- The selected commit has no committed `src/isodate/version.py`; this is the
  generated setuptools-scm module. In the full Git checkout it resolves to
  `0.7.3.dev3+g17cb25eb7`. The trusted Oracle validates the archive, then writes
  that deterministic version module and replaces only the Git-less
  `setuptools-scm` fallback version before installing. This prevents the wheel
  build from replacing the frozen version with `0.0.0.dev0`.
- Static import audit found no third-party runtime dependency. Hash-locked
  `packaging==26.3`, `setuptools==80.9.0`, and `setuptools-scm==9.2.0` build
  dependencies are private and installed only at image build.
- Python 3.12.11 with pytest 8.4.2 collected 280 upstream cases and passed
  280/280. The production execution environment is Python 3.12.14 on
  digest-pinned Debian 12 images.
- The production verifier uses 34 unique child-side scenarios because trusted
  pytest cannot import candidate code. It retains coverage of parsing,
  formatting, calendar arithmetic, timezone protocol, value semantics, and
  generated version behavior while keeping trusted reports candidate-inaccessible.

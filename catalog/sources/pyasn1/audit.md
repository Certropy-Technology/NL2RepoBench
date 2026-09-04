# pyasn1 authoring audit

- Upstream: `https://github.com/pyasn1/pyasn1`
- Revision: `8003397013f6c0e0eabbd2605770477acbc2dc44`
- Git tree: `209111189438390eb90c999488be48ab5e32cbb5`
- License: BSD-2-Clause, `LICENSE.rst` SHA-256 `2aad5fc00f705c4a1addb83eed10a6a75d286a3779f0cf8519d87e62bc4735fd`
- Source archive SHA-256: `c832e9d224c0a29d2f195f4472045279a9f5a0b02d793da257ab82e4e952586f`
- Package version: `0.6.4`
- Upstream test collection: 1261 tests, `python3 -m unittest discover -s tests -p 'test*.py'`, exit 0.
- Runtime: CPython 3.12.14, Debian 12 amd64, no third-party runtime dependency.
- Verifier: custom-json-v1, separate child process, 34 fixed leaves.
- Network: NoNetwork for Agent, candidate, verifier, Oracle, and controls; source and private closures are injected as digest-locked artifacts.

The repository is pure Python. Its upstream test suite is broad and unittest-driven,
so this production contract selects deterministic public behavior that can cross a
bounded JSON child-process boundary without importing candidate code into trusted
verifier state.

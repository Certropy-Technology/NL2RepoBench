# Provenance

- Upstream: `https://github.com/nhairs/python-json-logger`
- Revision: `806dba9d9642fbec4c8538b625494c96b288ce59`
- Commit tree: `12f9ad14d340d3bcd269e9ea889732cb400a3b6d`
- Source archive: `sha256:b53ce02a9d27ed2c29c7452f4abed9d28cc85d0c75ae9aa4195224276bbd08eb`, 174080 bytes
- License: BSD-2-Clause; `LICENSE` SHA-256 `sha256:18ea95179e3a5e0e24eb6ce16c40fbfbe23133c2502933a2f75f8a3e1a055b54`, 1329 bytes
- Runtime: CPython 3.12.14, Debian 12 amd64, pinned `python:3.12.14-slim-bookworm` digest
- Build closure: `setuptools==80.9.0`, private lock `sha256:d978dd32c7d5c8bb3a1f40f9b05fe68f34fb24bef1ae4bd9b3c60af6fb1f87fd`, 189 bytes
- Baseline command: `uv run --with pytest==9.0.2 --with freezegun==1.5.5 --with tzdata==2025.2 pytest -c /dev/null -q tests`; exit 0, 218 passed
- A preliminary invocation without `-c /dev/null` inherited the integration root coverage configuration and exited 4 before collection; this was an environment/configuration issue, corrected by explicit source-local pytest configuration.
- All production runtime stages are NoNetwork; private verifier and Oracle bundles are recorded in `task.toml` by digest and size.

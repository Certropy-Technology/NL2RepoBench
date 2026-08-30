# Provenance

- Upstream: `https://github.com/pallets/werkzeug`
- Revision: `0005c79e09bae5f4cc2bd8ccd468d7dafe24a455`
- Source archive: `sha256:239273928c7e07cb69a74fa21305921f41901f59b7e7d188eb46c47e9855ae4c`
- License: BSD-3-Clause, `LICENSE.txt` SHA-256 `3b49dcee4105eb37bac10faf1be260408fe85d252b8e9df2e0979fc1e094437b`
- Python baseline: 3.12.14 on Debian 12 amd64, digest-pinned `python:3.12.14-slim-bookworm`
- Full upstream baseline: `uv run pytest -q --disable-warnings --basetemp=/tmp/wz` -> 1045 passed, exit 0
- Runtime dependency: exact `MarkupSafe==3.0.3`; build backend: exact `flit_core==3.12.0`
- Agent/verifier network: no-network; source fetch is Oracle-only and revision/digest checked.

# Environment remediation probe

- Python: `3.12.11`
- uv: `0.11.32`
- OS/runtime target: Debian 12 compatible `linux/amd64`, CPython 3.12
- Baseline command: `uv pip install --python <venv> -r candidate-requirements.lock.txt`; then `uv pip install --no-deps -e upstream`
- Selected upstream test probe: querystring, models, transform, streaming, and webhook signature tests
- Probe result: `232 passed`, exit code `0`
- Candidate runtime/build closure: 20 hash-locked distributions; pytest and pytest-asyncio were installed separately for authoring-only baseline execution and are not candidate runtime dependencies.
- Risk adaptation: all network, provider, websocket, TLS, file-upload and optional backend tests are excluded from the deterministic contract and documented in `api-inventory.json` and `test-inventory.json`.

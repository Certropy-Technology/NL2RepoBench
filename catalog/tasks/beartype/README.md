# `beartype` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:24d3c123052a0b30aee44759a502dd0d7dbfb0b74bee50e9fe8dfdb990e339ee`
- Toolchain lock: `sha256:230a7dd32d1de931a868d75901ea4f340882cf1aad24e61ee7918543075ab366`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `182`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

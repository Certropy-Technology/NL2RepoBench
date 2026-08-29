# `markdown-it-py` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:b41b57964b66147013428c7b2a2415217f7a6be8083445fe85d9532af1303cbf`
- Toolchain lock: `sha256:230a7dd32d1de931a868d75901ea4f340882cf1aad24e61ee7918543075ab366`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `24`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

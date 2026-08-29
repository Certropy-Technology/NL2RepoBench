# `mdurl` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:fb593cdddeda181556263f1314d3a15d5ee49e3ebbe5f2411c37618ecc6695ba`
- Toolchain lock: `sha256:230a7dd32d1de931a868d75901ea4f340882cf1aad24e61ee7918543075ab366`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `199`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

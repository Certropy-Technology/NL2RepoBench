# `jsonpointer` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:82b9a0c9d76ae515e093192b1d20c42829b08e8841ab107e298ab42c9bc16dd2`
- Toolchain lock: `sha256:108a340a148d391577c9587e795de8108ded4464fc68546305809254b118c614`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `28`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

# `sympy` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:3ef74fe1d052b9620d9d2ccb69e4a42fa63c0f33ec25b4c555a575068509d096`
- Toolchain lock: `sha256:108a340a148d391577c9587e795de8108ded4464fc68546305809254b118c614`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `25`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

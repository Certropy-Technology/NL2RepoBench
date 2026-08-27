# `pyrsistent` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:bacaa9b0ad5c470df9fddbe30c787eb4dd543840c68635a448d086955660ae90`
- Toolchain lock: `sha256:108a340a148d391577c9587e795de8108ded4464fc68546305809254b118c614`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `72`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

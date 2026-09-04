# `idna` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:2dadcd9ee233aee06d9ecd874ed6cf39cec3ba11014f45e7e0c6710042eadd4a`
- Toolchain lock: `sha256:e54be279a86caa843480b583d388ff7e6c977605b505448ba54549621be5ed68`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `25`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

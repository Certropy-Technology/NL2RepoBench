# `fonttools` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:54875bd21f8589aed191cd2be67198fea7d98e77aebba012ab2b9738c7fe61af`
- Toolchain lock: `sha256:e54be279a86caa843480b583d388ff7e6c977605b505448ba54549621be5ed68`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `60`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

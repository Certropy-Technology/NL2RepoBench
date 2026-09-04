# `fsspec` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:db057ecef85203ae4a9f2444665c5715e614a8ee9160991fd2533a3c5ca19098`
- Toolchain lock: `sha256:e54be279a86caa843480b583d388ff7e6c977605b505448ba54549621be5ed68`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `18`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

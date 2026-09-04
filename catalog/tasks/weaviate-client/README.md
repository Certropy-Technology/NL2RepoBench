# `weaviate-client` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:e7946e0f578f5416b3ab0bac104462a2f2f4d654dbd7e3bb409ae9565de2233a`
- Toolchain lock: `sha256:e54be279a86caa843480b583d388ff7e6c977605b505448ba54549621be5ed68`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `94`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

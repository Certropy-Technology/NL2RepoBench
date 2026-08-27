# `pydantic-settings` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:51509d0d9643c2014ecc57076645db5d4be4ef1d1682caa0394c817bd25d450e`
- Toolchain lock: `sha256:108a340a148d391577c9587e795de8108ded4464fc68546305809254b118c614`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `20`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

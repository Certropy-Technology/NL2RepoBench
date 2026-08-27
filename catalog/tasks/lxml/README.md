# `lxml` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:88c3a2565cd5032339bc75dd84a9e363c942a138167b3c47f8191ef862c2c31a`
- Toolchain lock: `sha256:108a340a148d391577c9587e795de8108ded4464fc68546305809254b118c614`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `8`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

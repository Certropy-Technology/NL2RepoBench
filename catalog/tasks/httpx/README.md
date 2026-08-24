# `httpx` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:746f45ea4e69879b785ee6f58a88bc3c6be5ebbd08369cb4759608364d02f8c0`
- Toolchain lock: `sha256:f4effe9ffc4b8a0dc0762b3dfce2d575f03bcf4df7c2755c2157cd36b35eb4ff`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `24`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

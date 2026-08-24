# `pss` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:f217d8184bc4e3b2f5c195db57fed4311e70dcb3b3d89a80924ee7d900152f97`
- Toolchain lock: `sha256:f4effe9ffc4b8a0dc0762b3dfce2d575f03bcf4df7c2755c2157cd36b35eb4ff`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `46`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

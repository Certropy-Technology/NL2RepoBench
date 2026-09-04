# `opentelemetry-semantic-conventions` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:f2db52e4ca605723572cfe4cf863bc00a4438a27f6014a86327eac1f892dd607`
- Toolchain lock: `sha256:230a7dd32d1de931a868d75901ea4f340882cf1aad24e61ee7918543075ab366`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `18`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

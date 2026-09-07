# `pyperf` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:4e961bd37946bdae6cd68c4b1024731ab997c5215bf47a7ee572a887b9cd398f`
- Toolchain lock: `sha256:230a7dd32d1de931a868d75901ea4f340882cf1aad24e61ee7918543075ab366`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `153`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

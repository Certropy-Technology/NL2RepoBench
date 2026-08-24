# `schedule-master` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:fbd3a33efe32b58583a2c3dd48b2a2ed27be4a04a33e1628d114acae5ba76fee`
- Toolchain lock: `sha256:f4effe9ffc4b8a0dc0762b3dfce2d575f03bcf4df7c2755c2157cd36b35eb4ff`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `81`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

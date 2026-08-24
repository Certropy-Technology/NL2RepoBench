# `pythonprojecttemplate` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:aede01fc1b8b8715b7c245fd491cbf84ec380a5c657ca845b3c1b16aae655f47`
- Toolchain lock: `sha256:f4effe9ffc4b8a0dc0762b3dfce2d575f03bcf4df7c2755c2157cd36b35eb4ff`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `36`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

# `pyperclip` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:99a256f3d94ffad7a9d786d4d6924e9300c4a44d4bc29694c08b53c6d47787d5`
- Toolchain lock: `sha256:f4effe9ffc4b8a0dc0762b3dfce2d575f03bcf4df7c2755c2157cd36b35eb4ff`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `10`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

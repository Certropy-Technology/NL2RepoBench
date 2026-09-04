# `shellingham` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: production
- Canonical manifest: `sha256:5b920e235f9548e32d5f811eab730f18e79d263aa49eead2918f8400f964d350`
- Toolchain lock: `sha256:e54be279a86caa843480b583d388ff7e6c977605b505448ba54549621be5ed68`
- Metric: `fixed-test-pass-rate-v1`
- Expected tests: `24`
- Verifier: separate environment, no network

Run with Harbor 0.21.0:

```bash
uv run --frozen --project harbor-runner harbor run -p . -a oracle
```

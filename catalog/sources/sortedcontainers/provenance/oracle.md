# Oracle And Control Evidence

The strict Harbor 0.21.0 bundle compiled without `--allow-incomplete` and used
only the local private Oracle source archive. No reference source was fetched
at runtime and no model agent was run.

- Oracle: `valid=true`, `collected=30`, `passed=30`, `failed=0`, reward `1.0`.
- Empty: `valid=true`, candidate installation failed as a model outcome, reward
  `0.0`.
- Stub: `valid=true`, `collected=30`, `passed=0`, `failed=30`, reward `0.0`.
- Forgery: `valid=true`, `collected=30`, `passed=0`, `failed=30`, reward `0.0`;
  candidate-written reward and verifier paths did not affect trusted grading.
- Offline: every verifier probe reported `public_network_available=false` and
  both `pypi.org:443` and `1.1.1.1:443` unreachable.

Exact commands, receipt paths, and SHA-256 values are recorded in the sibling
`production-evidence.json`. Review and pilot stages were not run and are not
claimed.

# Authoring Audit

- Candidate: `fonttools`
- Upstream: `https://github.com/fonttools/fonttools`
- Revision: `e7e00f1b16aef6ede850206df3c100ccde27b2d3`
- License: MIT, from `LICENSE` (SHA-256 `6787208f83f659ccbc2223b2fde952ffa6f7e8aca62f1a8a2bf5bc51bb1b2383`)
- Git archive digest: `sha256:2c7719e06724e5f34b4677eb4e7a5cb17a9cdee1225f829b2881b097d61d666c`
- Static inventory: `api-inventory.json` and `test-inventory.json` in task-local authoring work; scanner digest `sha256:199bc565192da925cddda9ec9b4a3678b2179bf0e5da68ccefd1bfdbe38dc8b2`.
- Runtime: Python 3.12.14 on Debian 12 amd64, digest-pinned `python:3.12.14-slim-bookworm`.
- Build: setuptools `80.9.0` and wheel `0.45.1`, with the complete hash-locked build closure stored as a private lock artifact. `FONTTOOLS_WITH_CYTHON=0` disables optional native extensions deterministically.
- Run policy: agent and verifier `no-network`; the Oracle alone receives a run-scoped authorization for the exact upstream host in order to fetch and digest-check the frozen archive.
- Verifier: private `custom-json-v1`, 60 unique leaves, candidate code imported only by the UID-isolated child runner.

## Remediation notes

1. The first local install probe failed because the project environment had no pip (`exit 1`, `No module named pip`). This was an authoring-tool environment issue, not a task blocker.
2. A Python 3.12 probe with setuptools `65.5.1` failed during metadata generation because `pkgutil.ImpImporter` was removed (`exit 2`). The lock was upgraded to setuptools `80.9.0`.
3. A Python 3.12 probe with only setuptools `80.9.0` and wheel failed because setuptools' core build path required `jaraco.functools` (`exit 2`). The resolved `setuptools[core]` closure is now hash locked and the pure-Python package build succeeds.
4. The upstream suite is too broad for a transparent root pytest import boundary and contains optional native/external integrations. The bounded adapter is documented and traceable to upstream tests; the excluded optional areas are not claimed as supported behavior.

5. The generic custom-json-v1 runner was corrected to accept pytest-style exit code 1 when the emitted fixed-leaf report is valid. The fonttools stub control initially exposed this gap as a verifier-internal error; after the fix it collected 60 leaves and scored 2/60, while the forgery control scored 0/60 with verifier-owned grading.

6. Final Harbor 0.21 Oracle execution passed 60/60 with reward 1.0. Empty, timeout, stub, forgery, and writable offline replays completed with network probes false; the current receipts and hashes are recorded in `production-evidence.json`.

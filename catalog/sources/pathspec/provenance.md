# Source Freeze

- Upstream: `https://github.com/cpburnz/python-pathspec`
- Revision: `df3de4595df6e8a1cfa5782b01926b4fe461a864`
- Frozen commit date: `2026-08-25T21:33:47-04:00`
- Git archive (`git archive --format=tar HEAD`) SHA-256:
  `0d8c72748d26926b3b0e7a3a983dd3135e9ad4b462388408a1bafc936a0236d9`
- Package metadata: `pathspec` version `1.1.1`, `requires-python >=3.9`.
- Build backend: `flit_core.buildapi`, build requirement `flit-core >=3.2,<5`.
- License: MPL-2.0 is the distributable composite license at this revision;
  `LICENSE-MPL-2.0` SHA-256 is
  `fab3dd6bdab226f1c08630b1dd917e11fcb4ec5e1e020e2c16f83a0a13863e85` and
  `LICENSE-MIT` SHA-256 is
  `d242056285735cde7a0ed4513a50138f67feb6cacc002189f8f8b0ff0c2fb84c`.
- Upstream test probe: 197 passed, 276 skipped native-backend cases; 197 tests
  collected for the available dependency set.
- Native optional backends are intentionally outside the deterministic contract.

The authoring checkout is under
`.nl2repo/authoring-work/python-author-wave2-20260828/pathspec/source`.
Evaluation uses no-network agent and verifier execution. Only the trusted
Oracle recipe is permitted to fetch the exact revision from the exact upstream
host, then it verifies the Git commit and archive digest before extraction.

## Verification record

- Harbor 0.21.0 production compile completed with `--allow-private` and without
  `--allow-incomplete`; task-local bundle manifest SHA-256 is
  `8097f570b5544c8dddd0b75cba38dae8a2aa56b8650bfb73d436f9e81cfcea6e`.
- The custom-json-v1 verifier collected the frozen 43 leaves. Local adapter
  smoke passed 43/43, and the trusted Harbor Oracle passed 43/43 with reward
  `1.0` and `public_network_available=false`.
- Empty, stub, forgery, install-hang, and call-hang controls completed without
  Harbor exceptions. Stub, forgery, and call-hang collected 43 leaves and
  passed 0; empty and install-hang exercised the documented candidate
  installation failure exception. The forgery result remained verifier-owned.
- Source validation and network lint completed with exit code 0. The full
  machine-readable receipts, artifact hashes, commands, and residual risks are
  in `production-evidence.json` and the task-local `.nl2repo/runs/` tree.

# P2 Unified Verifier State Audit

Checked checkout: detached `a6aff109c849b790390018c2adf2b4a0eaae4d17` plus
the post-review fixes in this worktree.
Checked worktree: `/home/ayi/dev/NL2RepoBench-p2-unified-verifier`
Checked on: 2026-08-25

This report is an evidence index for the accepted P2 slice objective. The
unrelated 186-source production campaign is intentionally out of scope; its
publication checks remain blocked rather than being represented by synthetic
vertical-slice evidence.

## P2 status

| Area | Status | Evidence / boundary |
| --- | --- | --- |
| Canonical leaf report/evaluator | implemented | `src/nl2repobench/verification/leaf_report.py`, `evaluator.py`, `metric_contract.py`; Node and Go paths delegate to the canonical evaluator. |
| Framework normalizers | implemented | `verification/normalize/pytest_junit.py`, `node_test_json.py`, `go_json.py`; normalization is separate from scoring. |
| Failure taxonomy | implemented | `verification/taxonomy.py` provides runtime-neutral failure classes and reason mapping. |
| Explicit runtime dispatch | implemented | `verification/registry.py` and required `--runtime` dispatch Python, Node and Go; unknown runtimes fail closed. |
| Shared Harbor writer/compiler | implemented foundation | `harbor/task_writer.py` owns deterministic manifests and complete verifier-runtime copying; adapters own runtime-specific Docker/test plans. |
| pnpm adapter | slice pass | pnpm v9 lock/integrity/lifecycle validation, compiler, Node registry, Python canonical runtime delegation, seven Harbor controls, offline network proof, and provenance-bound evidence pass. |
| Go Modules adapter | slice pass | pinned Go toolchain, offline module closure, typed bridge/proxy, candidate UID/process/output/timeout isolation, seven Harbor controls, offline network proof, and provenance-bound evidence pass. |
| Additional package manager | blocked/not selected | No manager beyond pnpm and Go Modules was needed or selected. |
| One-run Oracle contract | current | All P2 controls use exactly one Oracle run. `--oracle-runs != 1` is rejected; historical three-run evidence is not merged. |
| Release publication | blocked | Both slices intentionally report `status=pass` with `release_status=blocked` until reviewed lifecycle/image/store publication evidence exists. |

## Current Harbor evidence

### pnpm / Node synthetic slice

Evidence directory: `reports/node-pnpm-synthetic-controls-v1/`

- Oracle: `1.0`, `valid=true`, fixed denominator, zero exceptions.
- Offline Oracle: `1.0`, `valid=true`, `public_network_available=false`.
- Empty: `0.0`.
- Stub and forgery: `0.125`, `valid=true`; candidate reward files do not control grading.
- Install failure: `0.0`, `model/candidate-installation-failed`.
- Call hang: `0.0`, `model/candidate-call-failed`.
- `provenance` binds source, implementation, toolchain, control script, slice
  verifier and compiled bundle manifest hashes.

### Go Modules / google/uuid slice

Evidence directory: `reports/go-google-uuid-controls-v1/`

- Source revision: `0f11ee6918f41a04c201eceeadf612a377bc7fbc`.
- Source archive digest: `sha256:e24d1eb2f3787e8e47cacff5c9ef5e7286ef6406a22da2da036fd2a19fa5c049`.
- Oracle: `1.0`, `valid=true`, fixed denominator, zero exceptions.
- Offline Oracle: `1.0`, `valid=true`, `public_network_available=false`.
- Empty: `0.0`.
- Stub, forgery, install failure and call hang: `0.0`, `valid=true`, model
  failure taxonomy; forged reward is ignored.
- The generated candidate validation uses the locked Go version rather than a
  hardcoded version, and the verifier compose projection explicitly uses
  `network_mode: none`.
- `provenance` binds source, implementation, toolchain, control script, slice
  verifier and compiled bundle manifest hashes.

## Integrity and regression gates

The following final commands passed in this checkout:

- `uv run pytest -q`: 340 passed, coverage 80.44%.
- `uv run ruff check src tests scripts`: passed.
- `uv run mypy src/nl2repobench`: passed for 81 source files.
- `uv run python scripts/verify_p2_contract.py`: passed; only
  `fixed-test-pass-rate-v1` is generated.
- `uv run nl2repo task lint-network --include-generated`: 0 errors.
- `uv run pytest -q -p no:cacheprovider --no-cov tests/test_no_vendor_install.py`: passed.
- Both `verify_p2_vertical_slices.py` commands passed with all controls,
  network-isolated and provenance-bound gates true.
- Structured JSON/TOML parse checks and `git diff --check`: passed.
- `git diff --name-only -- test_files`: zero paths.

## Deliberate non-goals and residual blockers

- No changes were made to `test_files/`, public instructions, hidden tests,
  historical score interpretation, or the main worktree's dirty changes.
- The 186-source production validator/evidence contract is not claimed as
  passed because its required input and publication artifacts are outside this
  P2 slice objective.
- Release remains blocked for pnpm and Go pending reviewed lifecycle,
  production image and store publication evidence.
- Historical planning documents may mention three Oracle attempts; executable
  P2 scripts and checked evidence use the current one-run contract.

# P2 Unified Verifier State Audit

Checked checkout: detached `1d2927a67428afe62ae8e7bd27f42b918ae655af`
Checked worktree: `/home/ayi/dev/NL2RepoBench-p2-unified-verifier`
Checked on: 2026-08-24

This report records the current checkout rather than treating the proposed P2
document as a claim about repository state. The main worktree's uncommitted
changes were not copied into this checkout.

## Baseline Facts

- `catalog/sources`: 188 directories, 119 source `task.toml` files (including
  the pnpm and Go vertical-slice fixtures added by this goal).
- `catalog/tasks`: 91 generated task directories, all with the five basic tree
  files; no source-to-canonical manifest set is present.
- `test_files`: 104 legacy projection directories; this goal does not modify
  them.
- Source lifecycle counts among source manifests: discovered 61, blocked 25,
  packaged 4, oracle-passed 23, controls-passed 1.
- Source-only directories without `task.toml` are evidence records, not
  runnable tasks. They are not silently promoted to valid tasks.
- The continuation's 186-source production input and its validator scripts are
  absent at this baseline; those checks are therefore `blocked`, not passed.
- No `.github/workflows` directory is present in this checkout.
- Host-only tests that require `harbor-runner/.venv` or generated network
  policy files cannot be used as P2 evidence until those environment artifacts
  are materialized.

## P2 Status

| Area | Status | Evidence / boundary |
| --- | --- | --- |
| P2-0 golden behavior baseline | blocked | No complete golden fixture set or private artifact store exists in this checkout. Existing v1 snapshots must remain unchanged. |
| P2-1 canonical leaf report/evaluator | implemented | `verification/leaf_report.py`, `verification/evaluator.py`, `verification/metric_contract.py`; Python and Node wrappers delegate to the evaluator. |
| P2-2 framework normalizers | implemented | `verification/normalize/pytest_junit.py` and `verification/normalize/node_test_json.py`; normalizers do not score. |
| P2-3 failure taxonomy | implemented with archive boundary | `verification/taxonomy.py` is runtime-neutral; old enum modules remain only as serialized historical read/write boundaries and map into the canonical taxonomy before evaluation. |
| P2-4 metric contract semantics | implemented | Canonical evaluator reads passed/denominator status sets and collection policy; source and generated task views now produce only `fixed-test-pass-rate-v1`. Historical `excluded_statuses` cannot enter the current evaluator, and `skipped` remains in the frozen denominator. |
| P2-5 explicit verifier dispatch | implemented | `verification/registry.py` and required `--runtime` route Python, Node and Go explicitly. Unknown runtimes fail closed; generated Python/Node/Go verifier scripts pass the runtime identity. |
| P2-6 shared compiler/task writer | implemented foundation | `harbor/task_writer.py` owns instruction, bounded bundle/tree, deterministic manifest and canonical verifier-runtime copying. Runtime-specific Dockerfiles/test scripts remain in adapters as intended. |
| P2-7 pnpm adapter | partial/pass slice | `package_managers/pnpm.py`, `harbor/pnpm_compiler.py`, Node+pnpm registry, v9 lock/store validator, synthetic compile and unified metric pass. One-run Harbor Oracle reward 1.0 and empty reward 0.0 are archived in `reports/node-pnpm-synthetic-controls-v1/`; broader reviewed store/image publication remains outside this baseline. |
| P2-8 Go Modules | slice pass, release blocked | `go-modules` identity, closure validator, typed bridge, supervisor, compiler, pinned `go-google-uuid` source/closure, Oracle x1 and empty/stub/forgery/install-failure/call-hang controls pass in `reports/go-google-uuid-controls-v1/`; the verifier explicitly reports slice `status=pass` separately from `release_status=blocked` until catalog lifecycle/environment publication gates are complete. |
| Additional package manager | blocked | No extra manager is selected; scope remains at most one after pnpm evidence. |
| One-run Oracle contract | current | Repository policy and validators describe one Oracle run; historical x3 evidence is not regenerated or merged. |
| Stale controls/CI blockers | implemented for P2 | `summarize_phase2_controls.py` consumes the current one-run `oracle-1` contract; `.github/workflows/p2-contract.yml` guards ruff, mypy, complete pytest, P2 contract, no-vendor and network lint. Harbor production jobs remain separately archived/manual. |

The selected real pnpm candidate is `parse-npm-tarball-url` 5.0.0 at
`1cf57de3b5451ba2efd42fe8ed4eb8ede6f0f706`. Its source audit is retained at
`catalog/sources/parse-npm-tarball-url/blocked.md`. It is not silently converted
to npm: the real slice remains blocked until its reviewed pnpm v9 store,
private tests and source-build contract are frozen. The runnable synthetic
slice proves the adapter/registry boundary independently of that authoring
blocker.

## Continuation Contract Status

The injected eight-check production contract targets a later checkout state:
it requires 186 source records, `reports/harbor-production-input-v1.json`,
three validator scripts, and a production gate report. None of those artifacts
exist at `1d2927a`; the checks cannot honestly be made to exit zero from this
baseline without importing unrelated later work or fabricating evidence. The
implementation will keep this distinction explicit and will only report a
production check as passed when its source, command output, and immutable
artifact are present.

## Baseline Commands

- `uv run pytest -q`: 337 passed with coverage 80.46% after the unified evaluator/runtime migration.
- `uv run ruff check src tests/test_unified_verifier.py`: passed.
- `uv run mypy src/nl2repobench`: passed with no issues in 76 source files.
- `uv run python scripts/verify_p2_contract.py`: passed; source truth now emits only `fixed-test-pass-rate-v1` (generated legacy projections are reported separately).
- `uv run python scripts/verify_p2_vertical_slices.py --runtime go --package-manager go-modules --oracle-runs 1 --jobs-dir /tmp/nl2-go-controls-final/jobs`: passed; Oracle 1.0, empty 0, stub 0, forgery 1, install-failure 0, call-hang 0, all with zero Harbor exceptions.
- `uv run python scripts/verify_p2_vertical_slices.py --runtime node --package-manager pnpm --oracle-runs 1`: passed from archived jobs; Oracle 1.0, empty 0, zero Harbor exceptions.
- `uv run --frozen --project harbor-runner harbor run -p /tmp/nl2-go-harbor/go-google-uuid -a oracle`: passed, reward 1.0, exceptions 0.
- `uv run --frozen --project harbor-runner harbor run -p /tmp/nl2-go-harbor/go-google-uuid -a nop`: passed control, reward 0.0, exceptions 0.
- Full baseline pytest before P2 edits: 317 passed, 1 failed because the clean
  checkout contains a task directory without `task.toml`.

## Non-Goals Preserved

- No changes to `test_files/`, public instructions, hidden tests, historical
  score interpretation, or the main worktree's dirty files.
- The continuation's production-catalog checks remain explicitly blocked at
  this baseline because the required 186-source input, validator scripts and
  gate report do not exist here; P2 slice evidence is not substituted for
  those unrelated release checks.
- No manual edits to generated golden output to conceal a compiler regression.
- No fallback from pnpm to npm and no direct trusted-process linking of a Go
  candidate.

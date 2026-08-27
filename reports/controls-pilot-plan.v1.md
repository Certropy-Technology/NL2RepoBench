# Research: NL2RepoBench legacy Harbor controls pilot

> **Historical plan.** This document records the pre-execution static review at
> commit `93b38e2`. Oracle/nop attempts were subsequently run for
> `markupsafe`, `schedule-master`, and `unidecode`; exact structured outcomes
> are in `reports/controls-pilot-results.v1.md`. No stub, forgery, call-hang, or
> offline control passed. Current `retrying` and `schedule-master` task TOMLs do
> contain `[verifier.environment] network_mode = "no-network"`, but the pilot
> generated no trusted runtime `network.json`, so offline evidence remains
> absent.

**Artifact note:** The requested repository filename is `reports/controls-pilot-plan.v1.md`. The original no-edit lane left the checkout untouched; its runtime-authoritative artifact was:

`/root/.pi/agent/sessions/--root-NL2RepoBench--/subagent-artifacts/outputs/1467eea8-55d9-4675-aa22-f403b0ba1ffa/controls-pilot.md`

## Summary

A bounded eight-task controls pilot is reasonable as a **plan**, but none of the current legacy projections should run controls yet. The selected set covers easy, medium, and hard tasks plus synchronous, stateful/time-based, CLI, async-I/O, shell/filesystem, Unicode-table, and terminal-rendering shapes. Four tasks have some Oracle evidence; two have explicit three-run evidence, while the remaining evidence is report-only and must be reconciled against current bundle hashes.

The main blockers are structural rather than model-related: real task bundles contain no task-local `controls/*.sh` or compiler-generated `bundle.manifest.json`; most verifier scripts use direct in-process pytest, make candidate-controlled files/logs writable, trust candidate-provided JUnit content, and do not provide per-call cleanup. Therefore stub/call-hang/forgery controls cannot yet be interpreted safely. No Docker, Harbor, pytest, Oracle, or control run was executed.

## Findings

### 1. Harbor 0.21.0 contract versus the checked-in legacy projections

Harbor 0.21.0 task schema `1.4` expects an instruction, task metadata, an environment, a `solution/solve.sh`, and a verifier `tests/test.sh`; a separate verifier image should contain the verifier script and private tests, and the verifier must write `/logs/verifier/reward.json`. Separate verifier network policy is declared independently under `[verifier.environment]`. [Harbor task structure](https://www.harborframework.com/docs/tasks) [Harbor v0.21.0](https://github.com/harbor-framework/harbor/releases/tag/v0.21.0)

The repository’s pinned toolchain agrees with that contract:

- `toolchain.lock.toml`: Harbor `0.21.0`, task schema `1.4`;
- runner: `uv run --frozen --project harbor-runner harbor`;
- platform: `linux/amd64`;
- digest-pinned base images.

However, the current real-task bundles are legacy projections, not outputs of the current production compiler:

- `src/nl2repobench/harbor/compiler.py::prepare_control_bundle()` only accepts `stub`, `forgery`, `install-hang`, `workspace-invalid`, and `call-hang`.
- It requires `task_root/controls/<kind>.sh`.
- It then requires and refreshes `task_root/bundle.manifest.json`.
- The recursive task-tree audit at commit `93b38e23650de47f52ad97d23ef0ffbbfe3c3303` found control scripts only under `catalog/tasks/ministats/harbor/controls/`; no real-task control directory was present.
- The selected real-task trees have no `bundle.manifest.json`.

Therefore this command is a **planned command only**, not an executed result:

```bash
uv run nl2repo harbor prepare-control \
  catalog/tasks/retrying/harbor \
  stub \
  --output .nl2repo/controls-pilot-v1/retrying \
  --toolchain toolchain.lock.toml
```

Static inspection predicts that it cannot produce a valid compiler control bundle until a staged bundle has both a manifest and task-local control scripts. `tests/test_harbor_compiler.py` tests this workflow only against the synthetic `ministats` fixture, not the legacy projections. [Compiler](src/nl2repobench/harbor/compiler.py) [Compiler tests](tests/test_harbor_compiler.py)

### 2. Shared verifier security blocker

The real-task verifier files were generated from the legacy-image template in `scripts/gen_harbor_from_legacy.py`. The template:

1. Copies `/workspace` to `/tmp/candidate`;
2. Replaces candidate tests with a verifier fixture;
3. Writes a candidate-path `.pth` override;
4. Executes pytest directly in the verifier process;
5. Runs `chown -R candidate:candidate /tmp/candidate /logs/verifier`;
6. Reads candidate-produced `/logs/verifier/junit.xml`;
7. Computes reward from the JUnit XML.

Representative paths:

- `catalog/tasks/retrying/harbor/tests/test.sh`
- `catalog/tasks/retrying/harbor/tests/grade.py`
- `catalog/tasks/jsonlines/harbor/tests/test.sh`
- `catalog/tasks/arguably/harbor/tests/test.sh`
- `catalog/tasks/aiofiles/harbor/tests/test.sh`
- `catalog/tasks/markupsafe/harbor/tests/test.sh`
- `catalog/tasks/unidecode/harbor/tests/test.sh`
- `catalog/tasks/rich-click/harbor/tests/test.sh`
- `catalog/tasks/schedule-master/harbor/tests/test.sh`
- `scripts/gen_harbor_from_legacy.py`

Consequences:

- **Forgery:** candidate code can potentially alter candidate-owned test files, JUnit output, and verifier logs. The generic grader trusts JUnit testcase elements and does not verify report provenance or root ownership.
- **Call hang:** there is no per-API candidate subprocess boundary or cumulative candidate-call budget. A hanging function can hang the whole pytest process until the outer Harbor deadline.
- **Process cleanup:** detached children are not reliably terminated after each API call.
- **Plugin/import attacks:** the generic template does not consistently use `python -I`, disable pytest plugin autoload, or isolate candidate imports.
- **Private-test exposure:** generic fixture copies are made writable by the candidate; `arguably` and `aiofiles` also have task-local fixture trees that should be treated as private artifacts, not public task data.

The production compiler instead uses `candidate_client`, `candidate_runner`, root-owned trusted result paths, integrity snapshots, bounded subprocess calls, and UID cleanup. [Phase 2 verifier contract](docs/phase2-harbor-verifier.zh-CN.md) [Candidate client](src/nl2repobench/verification/candidate_client.py) [Candidate runner](src/nl2repobench/verification/candidate_runner.py)

**Decision:** all three requested control types are blocked for all selected tasks until the verifier is migrated or hardened. A task-local control script alone is insufficient.

### 3. Recommended bounded selection

The following eight tasks cover the requested difficulty and shape range while retaining the user-suggested candidates. “E3” means explicit three-run Oracle evidence; “E1-report” means a valid Oracle score appears in an older report but is not currently bound to a task/bundle content digest; “P” means static packaged evidence only.

All selected bundles declare approximately 2 CPUs, 4096 MB agent memory, 8192 MB storage, 600 s verifier timeout, and 300 s candidate total timeout. `autojump` declares a 90 s candidate-install timeout; the others generally declare 60 s.

| Tier | Task | Difficulty / tests | Shape | Evidence | Recommendation |
|---|---|---:|---|---|---|
| 1 | `retrying` | Easy / 23 | Single-module synchronous decorator and retry controller | **E3**: three valid `23/23`, reward `1.0` runs in `/root/.pi/agent/sessions/--root-NL2RepoBench--/subagent-artifacts/9ffacaad-fbaa-4a76-a7fe-d9330cab273a_worker_0_output.md`; lifecycle is `oracle-passed` | First task after verifier repair |
| 1 | `schedule-master` | Medium / 81 | Stateful scheduler, time calculations, timezone handling | **E3**: three valid `81/81`, reward `1.0` runs in handoff `41b425ce-6397-4ea7-80c7-d16ae1f61888` | First stateful/time-based task after verifier repair |
| 1 | `arguably` | Medium / 70 | Decorator-driven CLI parser, subprocess/IO fixtures, async command support | **E1-report**: `reports/harbor-pilot-status.v1.{json,md}` reports `70/70`; current catalog lifecycle remains `discovered` | Re-run Oracle and bind evidence before controls |
| 1 | `aiofiles` | Medium / 211 | Async file API, threadpool wrappers, filesystem and tempfile operations | **E1-report**: status report reports `211/211`; current catalog lifecycle remains `discovered` | Re-run Oracle; requires async adapter for call-hang |
| 2 | `markupsafe` | Easy / 39 | `str` subclass, escaping, formatting, C/pure-Python fallback | **P** only; `license_spdx = "unknown"`, collection source is `unknown`, lifecycle `discovered` | Hold until license/collection/Oracle evidence is frozen |
| 2 | `autojump` | Medium / 23 effective | Shell integration, manual installer, filesystem/database paths | **P**: provenance is strong, but the worker explicitly recorded no Docker/Harbor/Oracle/control run | Good shape probe after fresh Oracle and verifier repair |
| 2 | `unidecode` | Hard / 65 | Dynamic Unicode block tables, transliteration API, console entry point | **P** only; `license_spdx = "unknown"`, collection source `unknown`, lifecycle `discovered` | Defer until source/license/Oracle gate |
| 2 | `rich-click` | Hard / 139 | Click-compatible wrappers, Rich terminal rendering, themes/grouping | **P** only; `license_spdx = "unknown"`, collection source `unknown`, lifecycle `discovered` | Defer until dependency/license/Oracle gate |

Immutable verifier image references recorded by `/root/NL2RepoBench/.nl2repo/conversion-loop/state.json`:

- `retrying@sha256:1302235420db9d34955c42273ebaf23df8bbee31ceeaf3c336347f54b64146fe`
- `schedule-master@sha256:903e864b08437cacb1dbf4305f6ecc1443d09c6af7a714e2d81c4c5fee2d6677`
- `arguably@sha256:93563ba710a490978afdb11275583ac8357492bd41821a28d8b5fb9eccb84751`
- `aiofiles@sha256:c2c5990b82801b434d40d0be1fb21ae8b914a2336ff2486ebc7ea622924e4e7a`
- `markupsafe@sha256:9a385b240fa9430e853999c19e0bfe3a648287dd19f5c41e3d16ff18d3407d76`
- `autojump@sha256:85f4553300641c5771c1853dcf827857a7cde366f391383ba682d809f826a4e5`
- `unidecode@sha256:941e1824c14fd13d4d67c457badbd2eaf2ed39459ee75582e9f9bf31f340a795`
- `rich-click@sha256:8f091fb134fce469a442c928a3a8494510e3ff68c7e88b2c1378aff8c813d241`

`jsonlines` is the best reserve swap for `markupsafe`: Easy, 27 tests, a compact `Reader`/`Writer`/`open` API, and an older report-backed `27/27` Oracle result. It was omitted from the capped eight to retain all six user-suggested shape probes.

### 4. Package/API information and control suitability

The public instructions provide enough information to draft a package-specific stub for all eight. This does **not** mean the controls are executable or that hidden behavior is fully specified.

| Task | Usable public package/API information | Stub control design | Call-hang target | Forgery control |
|---|---|---|---|---|
| `retrying` | Strong. Single `retrying.py`; exports `retry`, `Retrying`, `RetryError`, `Attempt` | Write `setup.py`/metadata and a single module whose public calls raise `NotImplementedError` | `Retrying.call` and a decorated function; simple synchronous target | Generic adversarial build-backend/sitecustomize/JUnit script, but verifier must be hardened |
| `schedule-master` | Strong. `schedule` package; `Scheduler`, `Job`, `every`, `run_pending`, `run_all`, `CancelJob` | Write package skeleton and public state attributes | `Scheduler.run_pending`/`Job.run`; requires a persistent process adapter because state is not JSON-serializable | Same generic attack; current direct pytest boundary is insufficient |
| `arguably` | Strong API inventory: `command`, `run`, `subtype`, IO helpers, command fixtures | Write `arguably` package and minimal metadata; preserve CLI import paths | Decorated command or `arguably.run`; likely needs module/CLI adapter and captured stdout/stderr | Generic attack; fixture tree must be root-owned/private |
| `aiofiles` | Strong but broad: `src/aiofiles`, `threadpool`, `os`, `tempfile`, async streams | Write async package skeleton and minimal awaitable methods | `aiofiles.threadpool.open`, async read/write, or async OS call; requires an async task-local adapter | Generic attack; direct pytest cannot provide per-call timeout |
| `markupsafe` | Strong compact API: `Markup`, `escape`, `escape_silent`, `soft_str`, `_native`/`_speedups` | Easy package skeleton under `src/markupsafe` | `escape` or `Markup` operations | Generic attack, but task remains provenance/license blocked |
| `autojump` | Strong behavior-only specification: `bin.autojump_*`, `install.py`, shell assets | Must create `bin/`, installer, and shell-compatible files; not a normal wheel-only stub | `python install.py --dry-run` or `bin.autojump.main`; use a bounded CLI wrapper | Custom installer-aware script; bespoke verifier still lacks candidate API isolation |
| `unidecode` | Moderate-to-strong API, but large dynamic table surface (`x000.py` etc.) | Skeleton must include package entry point, `__main__`, utility module, and enough table import paths to collect | `unidecode.unidecode` or console command; string return is adapter-friendly | Generic attack, after license/Oracle and private fixture work |
| `rich-click` | Moderate. `RichCommand`, `RichGroup`, `RichContext`, decorators, rendering modules | Skeleton must expose `src/rich_click` and Click-compatible symbols; dependencies must be locked | Click command invocation or console/module runner; rendering objects are not JSON-friendly | Generic attack; requires Click/Rich dependency closure and CLI adapter |

The existing compiler control interface requires a separate file for every selected task:

```text
<staged-task>/harbor/controls/stub.sh
<staged-task>/harbor/controls/call-hang.sh
<staged-task>/harbor/controls/forgery.sh
```

No selected task currently has these files. The script bodies may be templated for the standard Python package cases, but `aiofiles`, `schedule-master`, `autojump`, and `rich-click` require task-local adapters or entry-point handling.

### 5. Declared legacy test commands

These are the declared contracts in each source `task.toml`. They are recorded for planning only and were not executed.

| Task | Declared setup/test command | Declared effective count |
|---|---|---:|
| `retrying` | `pip install -e .`; `pytest --continue-on-collection-errors test_retrying.py` | 23 |
| `schedule-master` | `pytest --continue-on-collection-errors test_schedule.py` | 81 |
| `arguably` | `pip install -e .`; `pytest --continue-on-collection-errors test` | 70 |
| `aiofiles` | `pip install -e .`; `pytest --continue-on-collection-errors tests` | 211 |
| `markupsafe` | `pip install -e .`; `pytest --continue-on-collection-errors tests` | 39 |
| `autojump` | `python install.py`; `pytest --continue-on-collection-errors tests` | 23 effective; provenance records 32 collected, skips/xfails excluded |
| `unidecode` | `pip install -e .`; `pytest --continue-on-collection-errors tests` | 65 |
| `rich-click` | `pip install 'setuptools>=45'`; `pip install click`; `pip install --no-build-isolation -e .[dev]`; `pytest --continue-on-collection-errors tests` | 139 |

### 6. Concrete blockers

| Severity | Path(s) | Finding and consequence |
|---|---|---|
| **Blocker** | `src/nl2repobench/harbor/compiler.py`; every selected `catalog/tasks/*/harbor/` | `prepare_control_bundle()` requires `controls/<kind>.sh` and `bundle.manifest.json`; neither exists in the real legacy projections. |
| **Blocker** | `scripts/gen_harbor_from_legacy.py`; selected `harbor/tests/test.sh` and `grade.py` | Direct in-process pytest, candidate-writable test/log trees, trusted JUnit parsing, no per-call process cleanup. Forgery and call-hang results would not be meaningful. |
| **High** | `catalog/tasks/*/task.toml` | Dependencies are generally `status = "unknown"` and no hash-locked wheelhouse/private test/oracle artifacts are declared. Production compiler mode should reject these gaps. |
| **High** | `reports/harbor-pilot-status.v1.{json,md}`, `docs/phase2-harbor-verifier.zh-CN.md`, `docs/benchmark-operations-guide.zh-CN.md`, `catalog/datasets/nl2repobench-harbor-pilot/dataset.toml`, selected `task.toml` files | Historical active-task counts and lifecycle states disagree. Current counts must be queried from versioned manifests/state rather than copied from a pilot snapshot; Oracle evidence must be rebound to current bundle and image digests. |
| **High** | `catalog/tasks/retrying/harbor/task.toml`, `catalog/tasks/schedule-master/harbor/task.toml` | `[verifier.environment] network_mode = "no-network"` is absent. Under Harbor’s separate-verifier resolution, the verifier can inherit the top-level public baseline. Existing Oracle evidence for these two tasks must not be called offline evidence until the generated projection is corrected. |
| **High** | `catalog/tasks/arguably/harbor/tests/fixture/`, `catalog/tasks/aiofiles/harbor/tests/fixture/` | Test fixture bytes are present in task-local trees. They must be treated as private artifacts and checked for agent visibility/leakage before any pilot publication. |
| **Medium** | `src/nl2repobench/verification/candidate_client.py`, `candidate_runner.py` | The candidate protocol is JSON/subprocess based. Stateful scheduler objects, async file handles, callbacks, and Rich/Click objects require task-local RPC/CLI adapters; direct API calls cannot be assumed serializable. |
| **Medium** | `catalog/tasks/markupsafe/task.toml`, `unidecode/task.toml`, `rich-click/task.toml` | `license_spdx = "unknown"` and collection provenance is not frozen; these are shape probes, not first-wave controls. |

## Expected commands

### Static, no-Docker preflight

These commands are safe to run in an isolated worktree and should precede any Harbor job:

```bash
for id in retrying schedule-master arguably aiofiles markupsafe autojump unidecode rich-click; do
  uv run nl2repo task validate-source "catalog/tasks/$id"
done

find catalog/tasks -path '*/harbor/controls/*.sh' -print
find catalog/tasks -path '*/harbor/bundle.manifest.json' -print

bash -n catalog/tasks/<task-id>/harbor/tests/test.sh
python -m py_compile catalog/tasks/<task-id>/harbor/tests/grade.py
```

Expected static interpretation:

- `controls/*.sh` should currently show only the synthetic `ministats` controls.
- Real-task `bundle.manifest.json` files are absent from the legacy projections.
- No static command should modify `catalog/tasks` or `test_files`.

### Oracle gate

Use a new, unique jobs directory for each attempt. Do not overwrite prior evidence:

```bash
uv run --frozen --project harbor-runner harbor run \
  -p catalog/tasks/retrying/harbor \
  -a oracle \
  --jobs-dir .nl2repo/runs/controls-pilot-v1/retrying/oracle-1
```

Repeat serially as `oracle-2` and `oracle-3` for each selected task. Existing E3 evidence may be used as a lead, but a fresh run is required after any verifier, task TOML, fixture, or image change.

Required Oracle gate:

- three independent `valid=true` results;
- stable collection and fixed denominator;
- reward at least `0.80`;
- preserve `grading.json`, `reward.json`, JUnit/collection evidence, network evidence, and image/bundle hashes.

### Control staging

Do not add controls to the canonical checkout in this lane. Create an isolated staging copy, add the three task-local scripts there, and compile from that copy.

For development-only fixtures with complete local test assets:

```bash
uv run nl2repo harbor compile \
  "$STAGE/catalog/tasks/<task-id>" \
  --output "$STAGE/build/harbor" \
  --toolchain toolchain.lock.toml \
  --allow-incomplete
```

`--allow-incomplete` must be labeled development-only. It is not sufficient for image-backed tasks whose private tests, dependencies, or Oracle artifacts are absent. The preferred production route is to materialize private test/dependency/Oracle artifacts from the immutable legacy image, hash them, and compile without `--allow-incomplete`.

After a valid compiled bundle exists:

```bash
uv run nl2repo harbor prepare-control \
  "$STAGE/build/harbor/<task-id>" \
  stub \
  --output "$STAGE/build/controls" \
  --toolchain toolchain.lock.toml
```

Repeat with `call-hang` and `forgery`. Do not manually replace `solution/solve.sh` in a canonical bundle as a substitute for compiler preparation.

### Serialized control execution

```bash
uv run --frozen --project harbor-runner harbor run \
  -p "$STAGE/build/controls/<task-id>-stub" \
  -a oracle \
  --jobs-dir .nl2repo/runs/controls-pilot-v1/<task-id>/stub

uv run --frozen --project harbor-runner harbor run \
  -p "$STAGE/build/controls/<task-id>-call-hang" \
  -a oracle \
  --jobs-dir .nl2repo/runs/controls-pilot-v1/<task-id>/call-hang

uv run --frozen --project harbor-runner harbor run \
  -p "$STAGE/build/controls/<task-id>-forgery" \
  -a oracle \
  --jobs-dir .nl2repo/runs/controls-pilot-v1/<task-id>/forgery
```

Also run the empty/nop baseline before the adversarial controls:

```bash
uv run --frozen --project harbor-runner harbor run \
  -p "$STAGE/build/harbor/<task-id>" \
  -a nop \
  --jobs-dir .nl2repo/runs/controls-pilot-v1/<task-id>/nop
```

Expected acceptance properties, not measured results:

- Oracle: valid, stable, reward ≥ 0.80.
- Nop/empty: valid and near zero.
- Stub: valid and low; exact score is task-dependent.
- Call-hang: verifier completes before task deadline, reports timeout/model behavior, and leaves no candidate processes.
- Forgery: trusted test/grader/reward files remain intact; forged candidate output cannot raise reward.
- Offline: `network.json` proves verifier public-network availability is false.

## Safe serialized execution plan

1. **Freeze inputs.** Record the current commit, selected task IDs, immutable image references, source-task content hashes, and this plan version.
2. **Reconcile Oracle evidence.** Treat only the explicit retrying/schedule evidence as E3. Re-run all eight tasks if any bundle or verifier bytes differ; re-run the report-only arguably/aiofiles evidence even if their image digest matches.
3. **Build isolated staging copies.** Use a temporary directory or separate worktree. Never edit canonical `catalog/tasks`, `test_files`, dataset manifests, or shared configuration.
4. **Repair the verifier contract first.**
   - Move hidden tests and dependencies into private, digest-addressed artifacts.
   - Make tests/grader/report paths root-owned and immutable to candidate code.
   - Use `python -I -B`, disable pytest plugin autoload, and isolate candidate imports behind `candidate_client`.
   - Add per-call timeout, cumulative budget, process-group termination, and UID cleanup.
   - Add `[verifier.environment] network_mode = "no-network"` to any staged task that lacks it, especially `retrying` and `schedule-master`.
5. **Add controls only in staging.**
   - `stub.sh`: package-specific public API skeleton, no network and no access to verifier paths.
   - `call-hang.sh`: bounded sleep/hang only in the target API or CLI operation; use async-aware code for `aiofiles`.
   - `forgery.sh`: build-backend, `sitecustomize`, pytest-plugin, forged-JUnit, forged-reward, and `os._exit` attempts modeled on `ministats`, without copying hidden test bytes.
6. **Run static checks.** Parse TOML, run shell syntax checks, compile grader/adapters, inspect file modes, and verify no secrets or hidden tests enter the agent image.
7. **Run one task at a time.** Recommended order: `retrying`, `schedule-master`, `arguably`, `aiofiles`, then `autojump`, `markupsafe`, `unidecode`, `rich-click`. Within each task: Oracle ×3, nop, stub, call-hang, forgery, offline verification.
8. **Persist after every job.** Save the complete Harbor job directory, `grading.json`, `reward.json`, collection/JUnit files, network evidence, integrity records, and a manifest containing task/control/image hashes.
9. **Stop on invalid infrastructure.** Do not continue to later controls if collection is unstable, `valid=false`, verifier network is available, trusted files change, or a process remains after cleanup.
10. **Report controls separately from model results.** This pilot must not launch model trials and must not claim any control passed until the structured artifacts satisfy the gates.

## Sources

### Kept

- [Harbor Task Structure](https://www.harborframework.com/docs/tasks) — authoritative schema, reward-file, artifact, and separate-verifier contract.
- [Harbor v0.21.0 release](https://github.com/harbor-framework/harbor/releases/tag/v0.21.0) — confirms the requested Harbor version.
- `toolchain.lock.toml` — repository-pinned Harbor runner, schema, image platform, and lock digests.
- `docs/phase2-harbor-verifier.zh-CN.md` — repository’s intended candidate subprocess, integrity, network, and control semantics.
- `src/nl2repobench/harbor/compiler.py` — actual control-preparation and production compilation behavior.
- `tests/test_harbor_compiler.py` — executable expectations for generated separate verifiers and control bundles.
- `scripts/gen_harbor_from_legacy.py` — actual legacy projection generator and shared verifier template.
- Selected `catalog/tasks/<task-id>/task.toml`, `instruction.md`, Harbor task files, verifier scripts, provenance files, Oracle worker artifacts, and `/root/NL2RepoBench/.nl2repo/conversion-loop/state.json`.

### Dropped

- Generic search-result commentary and third-party benchmark discussions; they were not needed once official Harbor documentation and repository code were available.
- The older `reports/harbor-pilot-status` data was not dropped, but it is treated only as stale/report-only evidence because it is not content-hash bound to the current task source.

## Gaps

- No Docker/Harbor execution was allowed in this lane, so there are no current control results.
- Hidden test and dependency artifact provenance is still image-backed or unknown for most selected tasks.
- The current status report, dataset manifest, task lifecycle fields, and conversion state disagree; a parent integrator must reconcile versions and hashes.
- Stateful, async, and Rich/Click APIs need task-local adapters before `candidate_client` can test call hangs safely.
- The production compiler will require private artifact references and hash-locked dependency closure; development `--allow-incomplete` output must not be presented as production parity.
- License evidence remains unresolved for `markupsafe`, `unidecode`, and `rich-click`.

## Supervisor coordination

No supervisor decision was required. The report is intentionally a static audit and execution plan; no controls are claimed to have passed.

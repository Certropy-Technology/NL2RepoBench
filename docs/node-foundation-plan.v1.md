# Code Context

> **Historical design record — superseded.** This file describes the former additive
> Python-v1/Node-v2 plan. The current implementation direction is the clean-break
> unified contract in [`unified-contract-migration-adr.zh-CN.md`](unified-contract-migration-adr.zh-CN.md).
> Do not use the additive v2 compatibility instructions below for new authoring or
> migration work.

## Files Retrieved

1. `src/nl2repobench/domain/models.py:21-337,422-481` - v1 schema, Python-only environment/dependency/test fields, publication gaps.
2. `src/nl2repobench/authoring/catalog.py:54-73,146-189,297-345` - declarative source parsing, manifest compilation, Python/pytest scaffold defaults.
3. `src/nl2repobench/harbor/compiler.py:55-101,144-243,262-317,343-543` - Harbor generation, pip/wheelhouse verifier, pytest script, runtime copying.
4. `src/nl2repobench/harbor/models.py:42-82` - Python verifier lock and exact pytest/pip command plan.
5. `src/nl2repobench/verification/models.py:13-76` - pytest/JUnit failure and grading models.
6. `src/nl2repobench/verification/grader.py:16-178` - fixed-denominator grading and JUnit validation.
7. `src/nl2repobench/verification/candidate_install.py:16-143` - UID 10001 pip installer supervisor.
8. `src/nl2repobench/verification/candidate_client.py:44-227` and `candidate_runner.py:35-159` - Python-only subprocess boundary.
9. `src/nl2repobench/verification/command_plan.py:12-35` - fail-closed pytest/pip protocol validation.
10. `src/nl2repobench/verification/run_pytest.py:10-35`, `pytest_plugin.py:24-71`, `junit.py:14-41` - trusted pytest runner, collection report, XML parser.
11. `src/nl2repobench/verification/workspace_copy.py:67-107`, `network_check.py:11-54`, `integrity.py` - reusable artifact/security primitives.
12. `tests/test_metadata_models.py`, `tests/test_harbor_compiler.py`, `tests/test_verifier.py`, `tests/test_candidate_boundary.py` - current golden and security contracts.
13. `docs/npm-node-task-feasibility.md:1-82` - existing Node pilot boundaries and npm constraints.
14. `toolchain.lock.toml:1-24`, `verifier/requirements.lock.txt:1-60`, `harbor-runner/pyproject.toml:1-10`, `pyproject.toml:1-63` - current toolchain ownership.
15. `examples/harbor/ministats/*` - Python-only Harbor example; its mutable base and legacy grader are not production patterns.

## Key Code

The current v1 schema is hard-coded at `domain/models.py:21` and `RecordModel.schema_version` at lines 61-66. Changing it in place would alter existing manifests, JSON schemas, and content digests.

Python-only fields:

```python
# domain/models.py:168-208
EnvironmentLock.python_version

# domain/models.py:228-257
DependencyBundle.installer: Literal["uv", "pip", "system", "unknown"]

# domain/models.py:260-301
TestManifest.framework: Literal["pytest"]
```

`TaskMetadata.language` defaults to `"python"` (`domain/models.py:314-320`) and is not cross-validated against the environment. `TaskManifest.publication_gaps()` (`domain/models.py:439-473`) recognizes only `fixed-test-pass-rate-v1`.

The main compiler blockers are:

- `HarborCompiler._write_verifier()` (`harbor/compiler.py:160-243`) always installs Python requirements with pip and copies `nl2repobench` into Python site-packages.
- `_validate_dependency_bundle()` (`harbor/compiler.py:262-317`) requires `requirements.lock.txt`, hashed requirements, and root-level wheels.
- `_test_script()` (`harbor/compiler.py:388-514`) invokes Python network checks, `candidate_install`, `run_pytest`, JUnit copying, and `--pytest-exit-code`.
- `_copy_verifier_runtime()` (`harbor/compiler.py:516-543`) copies only Python files.
- `VerifierCommandPlan` (`harbor/models.py:62-68`) and `verification/command_plan.py:12-35` accept only `pytest-subprocess-boundary-v1` and `pip-target-no-deps-v1`.
- `candidate_install.py:67-94` launches `python -I -B -m pip`.
- `candidate_client.py` and `candidate_runner.py` import Python modules and expose Python module/console operations.
- `verification/grader.py:49-166` parses JUnit and validates pytest exit codes.
- `verification/models.py:13-29` names all report failures around pytest/JUnit and exposes `pytest_exit_code`.

Reusable unchanged or nearly unchanged:

- `workspace_copy.copy_workspace()` for bounded, root-owned, read-only workspace ingestion.
- `network_check.py` for dual hostname/numeric offline probes.
- `integrity.py` for trusted-file snapshots.
- `_extract_private_bundle()` for bounded tar extraction, after adding npm-specific content validation.
- Harbor schema `1.4`; canonical schema v2 must not be confused with Harbor task schema.

## Architecture

### Compatibility Strategy

Use an additive canonical v2 path. Keep v1 Python models, schemas, lock, compiler behavior, and verifier protocol byte-compatible.

Recommended additions:

```text
src/nl2repobench/domain/models_v2.py
src/nl2repobench/verification/node_candidate_install.py
src/nl2repobench/verification/node_candidate_client.py
src/nl2repobench/verification/node/*.mjs
schemas/v2/*.json
toolchain.node.lock.toml
catalog/sources/node-synthetic/
```

`CatalogCompiler.load_task()` must inspect raw TOML `schema_version` before invoking the v1 Pydantic model, then route to `DeclarativeTaskSourceV2`. A v2 file must never be parsed through the v1 `Literal["1.0"]` model.

Keep the current Python `toolchain.lock.toml` unchanged. Use a separate `toolchain.node.lock.toml` so the existing Harbor lock and v1 output digests are not silently invalidated.

### Minimal v2 Records

```python
class RuntimeProfileV2:
    language: Literal["python", "node"]
    runtime: Literal["cpython", "node"]
    version: str                    # exact Node patch, not "22"
    package_manager: Literal["uv", "pip", "npm", "none"]
    package_manager_version: str | None
    architecture: Literal["linux/amd64"]
    libc: Literal["glibc", "musl"]

class EnvironmentLockV2:
    status: ProvenanceStatus
    os_name: str | None
    base_image: str | None
    base_image_digest: str | None
    runtime: RuntimeProfileV2 | None
    network_mode: Literal["public", "no-network", "allowlist"] | None

class DependencyBundleV2:
    status: ProvenanceStatus
    ecosystem: Literal["python", "npm"]
    consumer: Literal["candidate-runtime", "verifier-runtime"]
    artifact: ArtifactRef | None
    lockfile_name: Literal["requirements.lock.txt", "package-lock.json"]
    lockfile_version: str
    package_manager: Literal["uv", "pip", "npm"]
    package_manager_version: str
    install_mode: Literal["offline"]
    lifecycle_scripts: Literal["ignore-scripts"]
    packages: tuple[str, ...] = ()

class TestManifestV2:
    framework: Literal["node:test"]
    report_format: Literal["node-test-json-v1"]
    expected_total: int
    expected_total_source: Literal["frozen-collection"]
    commands_artifact: ArtifactRef
    test_bundle: ArtifactRef
```

For Node publication, require:

- exact Node 24 LTS patch and npm version for production; Node 22 is retained only
  by the development synthetic fixture;
- digest-pinned image;
- `linux/amd64` and explicit libc;
- `metadata.language == runtime.language == "node"`;
- `framework == "node:test"`;
- private test/command artifacts;
- offline dependency bundle;
- metric `node-test-leaf-pass-rate-v1`.

Existing `EnvironmentLock.python_version` remains in v1. Legacy Python manifests with unknown provenance cannot be upgraded to published v2 records without explicit backfill.

### npm Dependency Bundle

Use a private deterministic tar archive:

```text
package-lock.json
npm-cache/
bundle.manifest.json
```

For the synthetic zero-dependency task, the archive still contains a v3 package-lock root and an empty cache. Do not bypass the known-artifact requirement.

Add `_validate_npm_dependency_bundle()` beside the current wheelhouse validator. It must reject:

- links, devices, shell scripts, `.npmrc`, `node_modules`, and unexpected files;
- non-UTF-8 or non-v3 lockfiles;
- git, `file:`, `workspace:`, `link:`, registry overrides, and native-addon dependencies for this slice;
- missing integrity metadata or cache entries;
- npm-version mismatch;
- size/member/path violations.

The current compiler installs `DependencyBundle` contents globally in the verifier while candidate install uses `pip --no-deps`; this role is ambiguous. v2 must explicitly mark the bundle consumer. For Node, it is a candidate-runtime offline cache, not an implicit global dependency pool.

### Candidate Install Protocol

Add an allowlisted protocol:

```json
{
  "schema_version": "2.0",
  "runner": "node-test-subprocess-boundary-v1",
  "candidate_install": "npm-pack-offline-v1",
  "report_format": "node-test-json-v1",
  "test_root": "/tests/private"
}
```

Trusted sequence:

1. Copy `/workspace` through existing `workspace_copy`.
2. Run `npm ci --offline --ignore-scripts --no-audit --no-fund --cache=/opt/npm-cache` under UID 10001.
3. Run `npm pack --ignore-scripts` into a private temporary directory.
4. Validate the generated tar before extraction.
5. Install the tar with `npm install --offline --ignore-scripts --no-audit --no-fund --cache=/opt/npm-cache --prefix=/tmp/candidate-site`.
6. Record setup status and stdout/stderr, enforce limits, kill the process group, and rescan UID 10001 until quiescent.

The first slice must not execute lifecycle or build scripts. No arbitrary command strings may be introduced.

### Node Subprocess Boundary

Add a Node-specific client/runner rather than modifying the Python importer to load JavaScript.

The child process must:

- run the exact locked `/usr/local/bin/node`;
- use UID/GID 10001, sanitized `env -i`, fixed cwd, fixed `PATH`, `HOME`, and `TMPDIR`;
- remove `NODE_PATH`, `NODE_OPTIONS`, preload/loader variables, registry configuration, and extra CA variables;
- use `--no-addons`;
- accept one bounded JSON request and emit one bounded JSON response;
- allow only fixed package/export names, never arbitrary filesystem paths, eval, shell, loader, or test options;
- enforce CPU, memory, FD, process, file, output, per-call, and cumulative limits.

Root hidden tests must call only this adapter. They must never import candidate code in the trusted test process.

### Test Report and Grader

Use a verifier-owned JSON report:

```json
{
  "schema_version": "2.0",
  "framework": "node:test",
  "report_format": "node-test-json-v1",
  "collected": 8,
  "tests": [
    {"test_id": "api-normalize", "status": "passed", "duration_ms": 4}
  ],
  "collection_errors": [],
  "runner_exit_code": 0
}
```

Count only leaf tests. Validate unique IDs and `len(tests) == collected`. Derive counts from individual cases; never trust aggregate reporter fields.

`node-test-leaf-pass-rate-v1`:

- `passed` is the only passing status.
- `failed`, `error`, `skipped`, and `todo` remain in the denominator.
- Collection errors and count mismatch are invalid verifier results.
- Exit code 0 is valid only without failed/error cases.
- Exit code 1 is valid when failed/error cases exist.
- Any other trusted runner exit is abnormal verifier failure.
- Reward is `clamp(passed / frozen_total, 0, 1)`.
- Candidate workspace/pack/install/call failure: `valid=true`, model failure, reward 0.
- Missing/malformed/mismatched report, network access, integrity failure, or abnormal trusted runner: `valid=false`, verifier failure.

Keep `grade_verification()` for v1 pytest/JUnit. Add `grade_node_test_report()` and v2 report models. Extend the CLI with `--report` and `--runner-exit-code`, while retaining v1 flags.

### Compiler Changes

Add one runtime branch in `HarborCompiler.compile_task()`:

```text
v1/Python -> current compiler path
v2/Node   -> Node environment, npm dependency, Node runner, and report path
```

The Node branch must:

- use digest-pinned Node agent/verifier images;
- generate a separate no-network verifier;
- use a digest-pinned Node 24/npm verifier with the separately locked pure-Node grader/helper tree;
- copy only trusted Node helpers and v2 grader files;
- keep private tests out of the agent image and build layers;
- write and runtime-validate the v2 command plan;
- snapshot/verify private tests, command plan, Node helpers, Python grader, and final report;
- emit Harbor `reward.json` and canonical v2 `grading.json`.

`_write_task_toml()` remains Harbor schema `1.4`, but may add metadata fields for `language`, `runtime`, `runtime_version`, `package_manager`, `test_framework`, and metric ID.

No root `pyproject.toml`, root `uv.lock`, or `harbor-runner/uv.lock` dependency is needed. If `.mjs` files are packaged inside the Python wheel, add explicit Hatch package-data inclusion and a wheel smoke test.

## Start Here

Start with `domain/models.py:21-337` and add v2 records without changing v1 serialization. Then implement the Node branch beside `harbor/compiler.py:160-243` and `388-543`. Implement the v2 report/parser beside `verification/models.py:13-76` and `verification/grader.py:49-166` before writing the Node installer/client.

## Security Boundary

- Agent image contains only digest-pinned Node 24/npm and an empty `/workspace`.
- Verifier is a separate no-network environment with private tests mode 0500 and root-owned logs.
- Candidate workspace is copied with existing bounded regular-file checks.
- npm cache is verifier-owned, read-only to candidate, and used only with explicit `--offline`.
- Candidate runs only as UID 10001 with sanitized environment, fixed protocol, no addons, and process/resource limits.
- Candidate cannot write `/tests/private`, `/tmp/trusted-results`, `/logs/verifier`, the grader, or final reward.
- Validate `npm pack` tar members before extraction.
- Trusted report path is atomic, bounded, root-owned, and integrity-snapshotted.
- `network_check.py` must prove both hostname and numeric network probes are unavailable.
- Do not download Node, npm, Python wheels, or packages from a task Dockerfile without locked build artifacts.

## Tests and Golden Fixtures

Add:

- v2 model tests for runtime/profile mismatch, exact Node/npm versions, npm lock/cache validation, `todo` semantics, and v1 digest compatibility.
- catalog tests for v2 dispatch, canonical output, runtime/test mismatch, and unchanged v1 output.
- compiler tests for Node Dockerfile, command plan, npm archive validation, hidden-asset exclusion, deterministic output, and malicious candidate tarballs.
- verifier tests for all-pass, partial-pass, skip/todo, duplicate IDs, collection errors, count mismatch, malformed/missing report, exit mismatch, install failure, network failure, and integrity failure.
- candidate-boundary tests for sanitized environment, output bounds, timeout/cleanup, read-only cache, ignored lifecycle scripts, tar traversal, links, `.npmrc`, and loader injection.
- Node runtime tests for real `node:test` leaf collection and report generation in the pinned image.

Golden fixtures:

```text
schemas/v2/task-manifest.schema.json
schemas/v2/declarative-task-source.schema.json
schemas/v2/test-report.schema.json
schemas/v2/grading-result.schema.json
schemas/v2/harbor-toolchain-lock.schema.json
tests/fixtures/node-v2/manifest.json
tests/fixtures/node-v2/command-plan.json
tests/fixtures/node-v2/reports/*.json
tests/fixtures/node-v2/dependencies/
tests/fixtures/node-v2/candidate-tars/
tests/fixtures/node-v2/golden-bundle/
toolchain.node.lock.toml
catalog/sources/node-synthetic/
```

Synthetic task: plain JavaScript ESM, eight frozen leaf tests, no dependencies, no lifecycle scripts, no native modules, and API calls only through the adapter. Use separate dataset ID `nl2repobench-node-pilot-v1`.

Validation commands:

```bash
uv run pytest tests/test_metadata_models.py tests/test_catalog.py \
  tests/test_harbor_compiler.py tests/test_verifier.py \
  tests/test_candidate_boundary.py tests/test_node_runtime.py
uv run ruff check .
uv run mypy
uv run nl2repo schema export --output /tmp/nl2repo-schemas
uv run nl2repo task validate-source catalog/sources/node-synthetic
uv run nl2repo task compile catalog/sources/node-synthetic --output /tmp/node-catalog
uv run nl2repo harbor compile catalog/sources/node-synthetic \
  --toolchain toolchain.node.lock.toml --output /tmp/node-harbor
uv run --frozen --project harbor-runner harbor run \
  -p /tmp/node-harbor/node-synthetic -a oracle
```

Run empty, stub, forgery, install-script, loader-hook, hang, and offline controls. The current campaign Oracle must pass one run with collection matching the frozen denominator, `valid=true`, and reward at least 0.80; target is 1.0. Cross-run stability requires a separate experiment version.

## Explicit Out of Scope

- Jest, Vitest, Mocha, tap, TypeScript, ts-node, Babel, bundlers, dual ESM/CJS, and arbitrary loaders.
- Workspaces, monorepos, git/file/workspace dependencies, private registries, browser/Electron, remote services, native addons, node-gyp, and optional platform binaries.
- Lifecycle/build scripts, arbitrary candidate test commands, candidate reporters, candidate test roots, registry configuration, `NODE_PATH`, and `NODE_OPTIONS`.
- General npm registry/cache proxying or lockfile generation during verification.
- Direct trusted-process `require()`/`import()` of candidate code.
- Rewriting the legacy importer, `test_files`, OpenHands harness, existing `ministats`, or the 104-task Python dataset.
- Cross-language score aggregation, parity claims, scheduler/DAG work, or broad Node ecosystem publication.
- Adding Node dependencies to Python `pyproject.toml`, root `uv.lock`, or Harbor runner lock.

## Residual Risks

- The production lane intentionally does not depend on a Python grader; the pure-Node
  helper/grader tree is content-hash locked, but a real candidate vertical slice must
  still pass Oracle and controls before publication.
- npm `_cacache` and package-lock behavior are version-sensitive and must be tied to one exact npm patch.
- `node:test` event/reporter behavior must be tested in the exact locked Node image.
- ESM resolution and JSON serialization need an explicit public contract.
- The synthetic zero-dependency task validates the protocol, not broad npm ecosystem support.
- The candidate remains isolated by process/container controls, not a general JavaScript sandbox.

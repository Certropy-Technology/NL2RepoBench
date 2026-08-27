"""Development-only Node/npm Harbor compiler.

The v1 ``HarborCompiler`` remains Python-only. This compiler is selected by the
CLI for a v2 Node source and refuses production output from an unlocked Node
image/toolchain.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.models import ArtifactRef
from nl2repobench.domain.models_v2 import DeclarativeTaskSourceV2, TaskManifestV2
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.files import atomic_write
from nl2repobench.verification.node_command_plan import EXPECTED_NODE_PLAN

from .bundle_io import (
    BundleLimits,
)
from .models_v2 import load_node_toolchain_lock
from .node_dependencies import NodeDependencyError, validate_npm_dependency_bundle
from .task_writer import (
    TaskWriterError,
    copy_python_verifier_runtime,
    copy_tree,
    extract_private_bundle,
    write_file_manifest,
    write_instruction,
)


class NodeHarborCompileError(ValueError):
    """Raised when a v2 Node task cannot be safely compiled."""


class NodeHarborCompiler:
    """Generate a schema 1.4 development bundle without Docker execution."""

    MAX_BUNDLE_MEMBERS = 10_000
    MAX_BUNDLE_MEMBER_BYTES = 512 * 1024 * 1024
    MAX_BUNDLE_TOTAL_BYTES = 2 * 1024 * 1024 * 1024

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        try:
            self.toolchain = load_node_toolchain_lock(toolchain_path)
        except ValueError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        self.toolchain_path = toolchain_path
        self.artifact_resolver = artifact_resolver
        harbor_lock = toolchain_path.parent / self.toolchain.harbor.lock_file
        if not harbor_lock.is_file():
            raise NodeHarborCompileError(f"Harbor runner lock is missing: {harbor_lock}")
        digest = f"sha256:{hashlib.sha256(harbor_lock.read_bytes()).hexdigest()}"
        if digest != self.toolchain.harbor.lock_sha256:
            raise NodeHarborCompileError("Harbor runner lock digest does not match Node toolchain")
        if self.toolchain.status == "locked":
            runtime_digest = self._node_runtime_digest()
            if runtime_digest != self.toolchain.node_runtime_sha256:
                raise NodeHarborCompileError(
                    "locked Node toolchain runtime helper digest does not match"
                )
        requirements = toolchain_path.parent / self.toolchain.verifier_requirements_lock
        if not requirements.is_file():
            raise NodeHarborCompileError(f"verifier requirements lock is missing: {requirements}")
        if self.toolchain.verifier_requirements_sha256 is not None:
            digest = f"sha256:{hashlib.sha256(requirements.read_bytes()).hexdigest()}"
            if digest != self.toolchain.verifier_requirements_sha256:
                raise NodeHarborCompileError(
                    "verifier requirements lock digest does not match Node toolchain"
                )
        self.verifier_requirements_path = requirements

    @staticmethod
    def _node_runtime_digest() -> str:
        runtime_root = Path(__file__).parents[1] / "verification/node"
        digest = hashlib.sha256()
        for path in sorted(path for path in runtime_root.rglob("*") if path.is_file()):
            relative = path.relative_to(runtime_root).as_posix().encode("utf-8")
            digest.update(relative)
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        return f"sha256:{digest.hexdigest()}"

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        if not isinstance(source, DeclarativeTaskSourceV2):
            raise NodeHarborCompileError("Node compiler accepts only schema_version=2.0 sources")
        if source.harbor is None:
            raise NodeHarborCompileError("Node task source is missing [harbor] settings")
        if self.toolchain.status != "development-only" and allow_incomplete:
            raise NodeHarborCompileError(
                "allow_incomplete is only valid for development toolchains"
            )

        with tempfile.TemporaryDirectory(prefix="nl2repo-node-canonical-") as temporary:
            root = Path(temporary)
            compiled = CatalogCompiler(FileArtifactStore(root / "artifacts")).compile_task(
                source_dir, root / "canonical"
            )
            manifest = compiled.manifest
        if not isinstance(manifest, TaskManifestV2):
            raise NodeHarborCompileError("Node source did not produce a v2 manifest")
        gaps = manifest.publication_gaps()
        if gaps and not allow_incomplete:
            raise NodeHarborCompileError(
                "Node production output is unsupported until locked artifacts are supplied: "
                + ", ".join(gaps)
            )
        if self.toolchain.status == "development-only" and not allow_incomplete:
            raise NodeHarborCompileError(
                "Node toolchain is development-only; pass allow_incomplete for a fixture bundle"
            )

        final_root = output_root / manifest.task_id
        if final_root.exists() or final_root.is_symlink():
            raise NodeHarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary_root = Path(tempfile.mkdtemp(prefix=f".{manifest.task_id}-", dir=output_root))
        try:
            self._write_instruction(source_dir, source.instruction, temporary_root)
            self._write_environment(manifest, temporary_root)
            self._write_verifier(source_dir, manifest, temporary_root, allow_incomplete)
            self._write_solution(
                source_dir, manifest.oracle_bundle, temporary_root, allow_incomplete
            )
            self._write_controls(source_dir, temporary_root)
            self._write_task_toml(manifest, temporary_root)
            self._write_readme(manifest, temporary_root, allow_incomplete)
            self._write_bundle_manifest(manifest, temporary_root, allow_incomplete)
            os.rename(temporary_root, final_root)
        except Exception:
            shutil.rmtree(temporary_root, ignore_errors=True)
            raise
        return final_root

    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
    ) -> Path:
        """Create a supported Node control without mutating the source bundle."""

        if kind not in {"stub", "forgery", "timeout"}:
            raise NodeHarborCompileError(f"unsupported control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if not script.is_file():
            raise NodeHarborCompileError(f"control script is missing: {script}")
        target_name = f"{task_root.name}-{kind}"
        target = output_root / target_name
        if target.exists() or target.is_symlink():
            raise NodeHarborCompileError(f"control output already exists: {target}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{target_name}-", dir=output_root))
        try:
            self._copy_tree(task_root, temporary)
            solve = temporary / "solution/solve.sh"
            atomic_write(solve, script.read_bytes())
            os.chmod(solve, 0o755)
            self._refresh_bundle_manifest(temporary, kind)
            os.rename(temporary, target)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        return target

    def _write_controls(self, source_dir: Path, task_root: Path) -> None:
        controls = source_dir / "harbor/controls"
        if controls.is_dir():
            self._copy_tree(controls, task_root / "controls")

    def _write_instruction(self, source_dir: Path, relative: str, task_root: Path) -> None:
        try:
            write_instruction(source_dir, relative, task_root)
        except TaskWriterError as exc:
            raise NodeHarborCompileError(
                str(exc).replace("instruction", "Node instruction", 1)
            ) from exc

    def _write_environment(self, manifest: TaskManifestV2, task_root: Path) -> None:
        image = self.toolchain.images.agent_base
        dockerfile = f"""FROM --platform=linux/amd64 {image}

WORKDIR /workspace
"""
        atomic_write(task_root / "environment/Dockerfile", dockerfile.encode())

    def _write_verifier(
        self,
        source_dir: Path,
        manifest: TaskManifestV2,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        tests_root = task_root / "tests"
        tests_root.mkdir(parents=True)
        runtime_root = tests_root / "runtime"
        runtime_root.mkdir()
        node_runtime = Path(__file__).parents[1] / "verification/node"
        self._copy_tree(node_runtime, runtime_root / "node")
        self._write_python_verifier_runtime(tests_root)
        atomic_write(
            tests_root / "command-plan.json",
            json.dumps(EXPECTED_NODE_PLAN, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        )

        dependencies_root = tests_root / "dependencies"
        dependencies_root.mkdir()
        if manifest.dependency_bundle.artifact is not None and not allow_incomplete:
            self._extract_private_bundle(manifest.dependency_bundle.artifact, dependencies_root)
        else:
            self._write_empty_npm_bundle(dependencies_root)
        try:
            validate_npm_dependency_bundle(
                dependencies_root,
                expected_npm_version=self.toolchain.runtime.npm_version,
            )
        except NodeDependencyError as exc:
            raise NodeHarborCompileError(str(exc)) from exc

        private_root = tests_root / "private"
        if manifest.tests.test_bundle is not None and not allow_incomplete:
            self._extract_private_bundle(manifest.tests.test_bundle, private_root)
        else:
            fixture = source_dir / "harbor/tests"
            if not fixture.is_dir():
                raise NodeHarborCompileError("development Node task is missing harbor/tests")
            self._copy_tree(fixture, private_root)

        image = self.toolchain.images.verifier_base
        python_image = self.toolchain.images.verifier_python_base
        dockerfile = f"""FROM --platform=linux/amd64 {image} AS node-runtime
FROM --platform=linux/amd64 {python_image}

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \\
  && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

COPY python-runtime /opt/nl2repobench-runtime
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \\
  -r /tmp/verifier-requirements.lock.txt
COPY dependencies /opt/npm-bundle
COPY runtime /tests/runtime
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0500 private /tests/private
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \\
  && chmod -R 0555 /opt/nl2repobench-runtime \\
  && chmod -R 0500 /tests/private \\
  && chmod -R 0555 /tests/runtime
WORKDIR /tests
"""
        atomic_write(tests_root / "Dockerfile", dockerfile.encode())
        atomic_write(
            tests_root / "docker-compose.yaml", b"services:\n  main:\n    network_mode: none\n"
        )
        atomic_write(tests_root / "test.sh", self._test_script(manifest).encode())
        os.chmod(tests_root / "test.sh", 0o755)

    def _write_python_verifier_runtime(self, tests_root: Path) -> None:
        try:
            copy_python_verifier_runtime(tests_root / "python-runtime")
        except TaskWriterError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        atomic_write(
            tests_root / "verifier-requirements.lock.txt",
            self.verifier_requirements_path.read_bytes(),
        )

    def _write_empty_npm_bundle(self, root: Path) -> None:
        atomic_write(
            root / "package-lock.json",
            b'{"lockfileVersion":3,"packages":{"":{"name":"node-synthetic","version":"2.0.0"}}}\n',
        )
        (root / "npm-cache").mkdir()
        manifest = {
            "schema_version": "1.0",
            "ecosystem": "npm",
            "lockfile_version": "3",
            "package_manager": "npm",
            "package_manager_version": self.toolchain.runtime.npm_version,
            "install_mode": "offline",
            "lifecycle_scripts": "ignore-scripts",
            "cache_entries": [],
            "files": [],
        }
        atomic_write(
            root / "bundle.manifest.json", json.dumps(manifest, sort_keys=True).encode() + b"\n"
        )

    def _write_solution(
        self,
        source_dir: Path,
        oracle_bundle: ArtifactRef | None,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        solution_root = task_root / "solution"
        if oracle_bundle is not None and not allow_incomplete:
            self._extract_private_bundle(oracle_bundle, solution_root)
        else:
            fixture = source_dir / "harbor/solution"
            if not fixture.is_dir():
                raise NodeHarborCompileError("development Node task is missing harbor/solution")
            self._copy_tree(fixture, solution_root)
        solve = solution_root / "solve.sh"
        if not solve.is_file() or solve.is_symlink():
            raise NodeHarborCompileError("Node Oracle bundle must contain solve.sh")
        os.chmod(solve, 0o755)

    def _write_task_toml(self, manifest: TaskManifestV2, task_root: Path) -> None:
        assert manifest.harbor is not None
        runtime = manifest.environment_lock.runtime
        metadata = {
            "difficulty": manifest.metadata.difficulty,
            "category": manifest.metadata.category,
            "tags": list(manifest.metadata.tags),
            "language": "node",
            "runtime": "node",
            "runtime_version": runtime.version
            if runtime is not None
            else self.toolchain.runtime.runtime_version,
            "package_manager": "npm",
            "test_framework": "node:test",
            "metric_contract": manifest.metric.contract_id,
            "expected_test_count": manifest.tests.expected_total,
            "canonical_manifest_digest": manifest.content_digest(),
            "toolchain_lock_digest": self.toolchain.content_digest(),
        }
        data: dict[str, Any] = {
            "schema_version": self.toolchain.harbor.task_schema,
            "artifacts": [manifest.harbor.workspace_artifact],
            "task": {
                "name": f"nl2repobench/{manifest.task_id}",
                "version": manifest.version,
                "description": manifest.harbor.description,
                "authors": [{"name": "NL2RepoBench"}],
                "keywords": list(manifest.harbor.keywords),
            },
            "metadata": metadata,
            "agent": {"timeout_sec": manifest.harbor.agent_timeout_sec},
            "verifier": {
                "timeout_sec": manifest.harbor.verifier_timeout_sec,
                "environment_mode": "separate",
                "network_mode": "no-network",
                "environment": {
                    "network_mode": "no-network",
                    "build_timeout_sec": 600.0,
                    "cpus": 1,
                    "memory_mb": max(1024, manifest.harbor.memory_mb // 2),
                    "storage_mb": max(4096, manifest.harbor.storage_mb * 2),
                },
            },
            "environment": {
                "network_mode": manifest.harbor.agent_network_mode,
                "build_timeout_sec": 600.0,
                "cpus": manifest.harbor.cpus,
                "memory_mb": manifest.harbor.memory_mb,
                "storage_mb": manifest.harbor.storage_mb,
            },
        }
        if manifest.harbor.agent_network_mode == "allowlist":
            # Harbor only accepts allowed_hosts in allowlist mode. The catalog
            # schema has already restricted these to exact registry hostnames.
            data["environment"]["allowed_hosts"] = list(manifest.harbor.agent_allowed_hosts)
        atomic_write(task_root / "task.toml", tomli_w.dumps(data).encode())

    def _test_script(self, manifest: TaskManifestV2) -> str:
        assert manifest.harbor is not None
        expected = manifest.tests.expected_total
        return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json \
  /logs/verifier/report.json /logs/verifier/network.json
rm -rf /tmp/candidate-source /tmp/candidate-site /tmp/npm-cache

NETWORK_CHECK='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime");'
NETWORK_CHECK+='from nl2repobench.verification.network_check import main; main()'
if ! python3 -I -c "$NETWORK_CHECK" --output /logs/verifier/network.json; then
  node /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason verifier-network-available \\
    --output /logs/verifier
  exit 0
fi

install -d -o candidate -g candidate -m 0700 /tmp/npm-cache
cp -a /opt/npm-bundle/npm-cache/. /tmp/npm-cache/
chown -R candidate:candidate /tmp/npm-cache

if ! node /tests/runtime/node/copy_workspace.mjs \\
  --source /workspace \\
  --destination /tmp/candidate-source; then
  node /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-workspace-rejected \\
    --output /logs/verifier
  exit 0
fi
mkdir -p /tmp/candidate-site /tmp/candidate-site/home /tmp/candidate-site/tmp
chown -R candidate:candidate /tmp/candidate-source /tmp/candidate-site
if ! runuser -u candidate -- \\
  env PATH=/usr/local/bin:/usr/bin:/bin \\
  /usr/local/bin/node /tests/runtime/node/install_candidate.mjs \\
    --source /tmp/candidate-source \\
    --target /tmp/candidate-site \\
    --cache /tmp/npm-cache; then
  node /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-installation-failed \\
    --output /logs/verifier
  exit 0
fi
tarball=$(find /tmp/candidate-site -maxdepth 1 -name '*.tgz' -type f | head -1)
if [[ -z "$tarball" ]] || ! node /tests/runtime/node/validate-package.mjs "$tarball"; then
  node /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-installation-failed \\
    --output /logs/verifier
  exit 0
fi

export NODE_CANDIDATE_SITE=/tmp/candidate-site
export NODE_TEST_CLIENT=/tests/private/test_client.mjs
if ! node /tests/runtime/node/validate-command-plan.mjs \\
  --path /tests/command-plan.json; then
  node /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason verifier-internal-error \\
    --output /logs/verifier
  exit 0
fi
runner_exit_code=0
node /tests/runtime/node/run_tests.mjs \\
  --tests /tests/private \\
  --candidate /tmp/candidate-site \\
  --expected {expected} \\
  --output /logs/verifier/report.json || runner_exit_code=$?
if [[ "$runner_exit_code" -eq 70 ]]; then
  node /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-call-failed \\
    --output /logs/verifier
  exit 0
fi
node /tests/runtime/node/grade-report.mjs \\
  --expected {expected} \\
  --report /logs/verifier/report.json \\
  --runner-exit-code "$runner_exit_code" \\
  --output /logs/verifier
exit 0
"""

    def _extract_private_bundle(self, reference: ArtifactRef, destination: Path) -> None:
        try:
            extract_private_bundle(
                reference,
                destination,
                artifact_resolver=self.artifact_resolver,
                limits=BundleLimits(
                    max_members=self.MAX_BUNDLE_MEMBERS,
                    max_member_bytes=self.MAX_BUNDLE_MEMBER_BYTES,
                    max_total_bytes=self.MAX_BUNDLE_TOTAL_BYTES,
                ),
            )
        except TaskWriterError as exc:
            raise NodeHarborCompileError(str(exc)) from exc

    def _copy_tree(self, source: Path, destination: Path) -> None:
        try:
            copy_tree(source, destination)
        except TaskWriterError as exc:
            raise NodeHarborCompileError(str(exc)) from exc

    def _write_readme(
        self, manifest: TaskManifestV2, task_root: Path, allow_incomplete: bool
    ) -> None:
        mode = "development-only fixture" if allow_incomplete else "production"
        text = f"""# `{manifest.task_id}` Harbor Bundle

Generated by the additive Node/npm compiler.

- Mode: {mode}
- Node runtime: `{self.toolchain.runtime.runtime_version}`
- npm: `{self.toolchain.runtime.npm_version}`
- Image lock: `{self.toolchain.status}`
- Metric: `{manifest.metric.contract_id}`
- Expected leaf tests: `{manifest.tests.expected_total}`
- Verifier: separate environment, no network

This task is excluded from the Python dataset.
"""
        atomic_write(task_root / "README.md", text.encode())

    def _write_bundle_manifest(
        self, manifest: TaskManifestV2, task_root: Path, allow_incomplete: bool
    ) -> None:
        payload = {
            "task_id": manifest.task_id,
            "task_version": manifest.version,
            "mode": "development" if allow_incomplete else "production",
            "canonical_manifest_digest": manifest.content_digest(),
            "toolchain_lock_digest": self.toolchain.content_digest(),
        }
        write_file_manifest(task_root, payload=payload, schema_version="2.0")

    def _refresh_bundle_manifest(self, task_root: Path, kind: str) -> None:
        path = task_root / "bundle.manifest.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise NodeHarborCompileError(f"invalid source bundle manifest: {path}: {exc}") from exc
        payload["mode"] = f"control-{kind}"
        payload.pop("files", None)
        payload.pop("schema_version", None)
        write_file_manifest(task_root, payload=payload, schema_version="2.0")

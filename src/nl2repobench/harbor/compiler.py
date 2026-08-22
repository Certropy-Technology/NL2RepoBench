"""Compile a declarative task into a deterministic Harbor 0.21 bundle."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import tempfile
from pathlib import Path

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.models import ArtifactRef, TaskManifest
from nl2repobench.storage.artifacts import LocalArtifactResolver
from nl2repobench.storage.files import atomic_write

from .bundle_io import (
    BundleArchiveError,
    BundleArchiveIOError,
    BundleLimits,
    BundleTreeError,
    BundleTreeSourceError,
    copy_bundle_tree,
    extract_bundle_archive,
)
from .models import VerifierCommandPlan, load_command_plan, load_toolchain_lock


class HarborCompileError(ValueError):
    """Raised when a task cannot safely become a Harbor bundle."""


class HarborCompiler:
    """Generate Harbor files without executing Docker or contacting a registry."""

    MAX_BUNDLE_MEMBERS = 10_000
    MAX_BUNDLE_MEMBER_BYTES = 512 * 1024 * 1024
    MAX_BUNDLE_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
    MAX_DEPENDENCY_LOCK_BYTES = 4 * 1024 * 1024

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        self.toolchain_path = toolchain_path
        self.toolchain = load_toolchain_lock(toolchain_path)
        self.artifact_resolver = artifact_resolver
        harbor_lock = toolchain_path.parent / self.toolchain.harbor.lock_file
        if not harbor_lock.is_file():
            raise HarborCompileError(f"Harbor runner lock is missing: {harbor_lock}")
        harbor_lock_digest = f"sha256:{hashlib.sha256(harbor_lock.read_bytes()).hexdigest()}"
        if harbor_lock_digest != self.toolchain.harbor.lock_sha256:
            raise HarborCompileError("Harbor runner lock digest does not match toolchain.lock.toml")

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        if source.harbor is None:
            raise HarborCompileError("task source is missing [harbor] execution settings")
        with tempfile.TemporaryDirectory(prefix="nl2repo-harbor-") as temporary:
            from nl2repobench.storage.artifacts import FileArtifactStore

            temporary_root = Path(temporary)
            compiled = CatalogCompiler(
                FileArtifactStore(temporary_root / "artifacts")
            ).compile_task(source_dir, temporary_root / "canonical")
            manifest = compiled.manifest
            if not isinstance(manifest, TaskManifest):
                raise HarborCompileError(
                    "schema_version=2.0 Node tasks require toolchain.node.lock.toml"
                )

        gaps = manifest.publication_gaps()
        if gaps and not allow_incomplete:
            raise HarborCompileError(f"task is not publishable: {', '.join(gaps)}")

        final_root = output_root / manifest.task_id
        if final_root.exists() or final_root.is_symlink():
            raise HarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary_root = Path(tempfile.mkdtemp(prefix=f".{manifest.task_id}-", dir=output_root))
        try:
            self._write_instruction(source_dir, source.instruction, temporary_root)
            self._write_environment(manifest, temporary_root)
            self._write_verifier(source_dir, manifest, temporary_root, allow_incomplete)
            self._write_solution(
                source_dir,
                manifest.oracle_bundle,
                temporary_root,
                allow_incomplete,
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
        """Create a stub/forgery Oracle bundle without mutating the source task."""

        if kind not in {
            "stub",
            "forgery",
            "install-hang",
            "workspace-invalid",
            "call-hang",
        }:
            raise HarborCompileError(f"unsupported control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if not script.is_file():
            raise HarborCompileError(f"control script is missing: {script}")
        target_name = f"{task_root.name}-{kind}"
        target = output_root / target_name
        if target.exists() or target.is_symlink():
            raise HarborCompileError(f"control output already exists: {target}")
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

    def _write_instruction(self, source_dir: Path, relative: str, task_root: Path) -> None:
        source = source_dir / relative
        atomic_write(task_root / "instruction.md", source.read_bytes())

    def _write_environment(self, manifest: TaskManifest, task_root: Path) -> None:
        image = self.toolchain.images.agent_base
        dockerfile = f"""FROM --platform=linux/amd64 {image}

WORKDIR /workspace
        """
        atomic_write(task_root / "environment/Dockerfile", dockerfile.encode())
        profile = manifest.harbor
        assert profile is not None
        if profile.agent_network_mode == "no-network":
            compose = """services:
  main:
    network_mode: none
"""
            atomic_write(task_root / "environment/docker-compose.yaml", compose.encode())

    def _write_verifier(
        self,
        source_dir: Path,
        manifest: TaskManifest,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        tests_root = task_root / "tests"
        tests_root.mkdir(parents=True)
        self._copy_verifier_runtime(tests_root / "runtime")
        requirements = self.toolchain_path.parent / self.toolchain.verifier.requirements_lock
        if not requirements.is_file():
            raise HarborCompileError(f"verifier requirements lock is missing: {requirements}")
        requirements_data = requirements.read_bytes()
        requirements_digest = f"sha256:{hashlib.sha256(requirements_data).hexdigest()}"
        if requirements_digest != self.toolchain.verifier.requirements_sha256:
            raise HarborCompileError(
                "verifier requirements lock digest does not match toolchain.lock.toml"
            )
        atomic_write(tests_root / "requirements.lock.txt", requirements_data)

        dependencies_root = tests_root / "dependencies"
        if allow_incomplete:
            dependencies_root.mkdir(parents=True)
            atomic_write(dependencies_root / "requirements.lock.txt", b"")
            command_plan = VerifierCommandPlan(
                runner="pytest-subprocess-boundary-v1",
                candidate_install="pip-target-no-deps-v1",
            )
        else:
            dependency_artifact = manifest.dependency_bundle.artifact
            command_artifact = manifest.tests.commands_artifact
            if dependency_artifact is None or command_artifact is None:
                raise HarborCompileError(
                    "production task requires dependency and command artifacts"
                )
            self._extract_private_bundle(dependency_artifact, dependencies_root)
            self._validate_dependency_bundle(dependencies_root)
            command_plan = self._resolve_command_plan(command_artifact)
        atomic_write(
            tests_root / "command-plan.json",
            canonical_json(command_plan) + b"\n",
        )

        private_root = tests_root / "private"
        if manifest.tests.test_bundle is not None:
            self._extract_private_bundle(manifest.tests.test_bundle, private_root)
        elif allow_incomplete:
            self._copy_tree(source_dir / "harbor/tests", private_root)
        else:
            raise HarborCompileError("production task requires tests.test_bundle")

        image = self._verifier_image(manifest, allow_incomplete)
        dockerfile = f"""FROM --platform=linux/amd64 {image}

COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock.txt

COPY dependencies /opt/candidate-dependencies
RUN python -m pip install \
  --no-cache-dir \
  --no-index \
  --find-links /opt/candidate-dependencies \
  --require-hashes \
  -r /opt/candidate-dependencies/requirements.lock.txt

COPY runtime/nl2repobench /usr/local/lib/python3.12/site-packages/nl2repobench
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0555 test.sh /tests/test.sh
COPY --chmod=0500 private /tests/private

RUN useradd --uid 10001 --create-home candidate \
  && chmod -R 0500 /tests/private \
  && chmod -R 0555 /usr/local/lib/python3.12/site-packages/nl2repobench
WORKDIR /tests
"""
        atomic_write(tests_root / "Dockerfile", dockerfile.encode())
        verifier_compose = """services:
  main:
    network_mode: none
"""
        atomic_write(tests_root / "docker-compose.yaml", verifier_compose.encode())
        atomic_write(tests_root / "test.sh", self._test_script(manifest).encode())
        os.chmod(tests_root / "test.sh", 0o755)

    def _verifier_image(self, manifest: TaskManifest, allow_incomplete: bool) -> str:
        if allow_incomplete:
            return self.toolchain.images.verifier_base
        environment = manifest.environment_lock
        if environment.base_image is None or environment.base_image_digest is None:
            raise HarborCompileError("production verifier image is not locked")
        image_name = environment.base_image.split("@", 1)[0]
        return f"{image_name}@{environment.base_image_digest}"

    def _resolve_command_plan(self, reference: ArtifactRef) -> VerifierCommandPlan:
        if self.artifact_resolver is None:
            raise HarborCompileError("private artifact resolver is required")
        try:
            return load_command_plan(self.artifact_resolver.resolve(reference).read_bytes())
        except (OSError, ValueError) as exc:
            raise HarborCompileError(str(exc)) from exc

    def _validate_dependency_bundle(self, root: Path) -> None:
        lock = root / "requirements.lock.txt"
        if not lock.is_file() or lock.is_symlink():
            raise HarborCompileError("dependency bundle must contain requirements.lock.txt")
        data = lock.read_bytes()
        if len(data) > self.MAX_DEPENDENCY_LOCK_BYTES:
            raise HarborCompileError("dependency requirements lock exceeds size limit")
        try:
            lines = data.decode("utf-8").splitlines()
        except UnicodeDecodeError as exc:
            raise HarborCompileError("dependency requirements lock is not UTF-8") from exc

        requirements: dict[str, bool] = {}
        current: str | None = None
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("--hash=sha256:"):
                if current is None:
                    raise HarborCompileError("dependency hash has no pinned requirement")
                requirements[current] = True
                continue
            if stripped.startswith("-") or " @ " in stripped or "://" in stripped:
                raise HarborCompileError("dependency lock contains a forbidden directive")
            match = re.match(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)==[^\s;\\]+", stripped)
            if match is None:
                raise HarborCompileError("dependency lock contains an unpinned requirement")
            current = re.sub(r"[-_.]+", "-", match.group(1).casefold())
            requirements[current] = "--hash=sha256:" in stripped

        missing_hashes = sorted(name for name, has_hash in requirements.items() if not has_hash)
        if missing_hashes:
            raise HarborCompileError(
                "dependency requirements lack sha256 hashes: " + ", ".join(missing_hashes)
            )

        wheel_distributions: set[str] = set()
        for path in root.rglob("*"):
            if not path.is_file() or path == lock:
                continue
            if path.parent != root:
                raise HarborCompileError(
                    f"dependency wheel must be at wheelhouse root: {path.relative_to(root)}"
                )
            if path.suffix != ".whl":
                raise HarborCompileError(f"dependency bundle contains non-wheel file: {path.name}")
            distribution = path.name.split("-", 1)[0]
            wheel_distributions.add(re.sub(r"[-_.]+", "-", distribution.casefold()))
        missing_wheels = sorted(
            name for name in requirements if name not in wheel_distributions
        )
        if missing_wheels:
            raise HarborCompileError(
                "dependency wheelhouse is incomplete: " + ", ".join(missing_wheels)
            )

    def _write_solution(
        self,
        source_dir: Path,
        oracle_bundle: ArtifactRef | None,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        solution_root = task_root / "solution"
        if oracle_bundle is not None:
            self._extract_private_bundle(oracle_bundle, solution_root)
        elif allow_incomplete:
            self._copy_tree(source_dir / "harbor/solution", solution_root)
        else:
            raise HarborCompileError("production task requires oracle_bundle")
        solve = solution_root / "solve.sh"
        if not solve.is_file():
            raise HarborCompileError("Oracle bundle must contain solve.sh")
        os.chmod(solve, 0o755)

    def _write_controls(self, source_dir: Path, task_root: Path) -> None:
        controls = source_dir / "harbor/controls"
        if controls.is_dir():
            self._copy_tree(controls, task_root / "controls")

    def _write_task_toml(self, manifest: TaskManifest, task_root: Path) -> None:
        profile = manifest.harbor
        assert profile is not None
        data = {
            "schema_version": self.toolchain.harbor.task_schema,
            "artifacts": [profile.workspace_artifact],
            "task": {
                "name": f"nl2repobench/{manifest.task_id}",
                "version": manifest.version,
                "description": profile.description,
                "authors": [{"name": "NL2RepoBench"}],
                "keywords": list(profile.keywords),
            },
            "metadata": {
                "difficulty": manifest.metadata.difficulty,
                "category": manifest.metadata.category,
                "tags": list(manifest.metadata.tags),
                "metric_contract": manifest.metric.contract_id,
                "expected_test_count": manifest.tests.expected_total,
                "canonical_manifest_digest": manifest.content_digest(),
                "toolchain_lock_digest": self.toolchain.content_digest(),
            },
            "agent": {"timeout_sec": profile.agent_timeout_sec},
            "verifier": {
                "timeout_sec": profile.verifier_timeout_sec,
                "environment_mode": "separate",
                "network_mode": profile.verifier_network_mode,
                "environment": {
                    "network_mode": profile.verifier_network_mode,
                    "build_timeout_sec": 600.0,
                    "cpus": 1,
                    "memory_mb": max(1024, profile.memory_mb // 2),
                    "storage_mb": max(4096, profile.storage_mb * 2),
                },
            },
            "environment": {
                "network_mode": profile.agent_network_mode,
                "build_timeout_sec": 600.0,
                "cpus": profile.cpus,
                "memory_mb": profile.memory_mb,
                "storage_mb": profile.storage_mb,
            },
        }
        atomic_write(task_root / "task.toml", tomli_w.dumps(data).encode())

    def _test_script(self, manifest: TaskManifest) -> str:
        expected = manifest.tests.expected_total
        metric = shlex.quote(manifest.metric.contract_id)
        profile = manifest.harbor
        assert profile is not None
        install_timeout = profile.candidate_install_timeout_sec
        candidate_total_timeout = profile.candidate_total_timeout_sec
        return f"""#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json
rm -rf /tmp/candidate /tmp/candidate-site /tmp/candidate-build /tmp/trusted-results
mkdir -p /tmp/trusted-results
chmod 0700 /tmp/trusted-results

if ! python -m nl2repobench.verification.network_check \
  --output /logs/verifier/network.json; then
  python -m nl2repobench.verification.cli \
    --expected {expected} \
    --metric-contract {metric} \
    --reason verifier-network-available
  exit 0
fi

if ! python -I -m nl2repobench.verification.command_plan \
  --path /tests/command-plan.json; then
  python -I -m nl2repobench.verification.cli \
    --expected {expected} \
    --metric-contract {metric} \
    --reason verifier-internal-error
  exit 0
fi

python -I -B -m nl2repobench.verification.workspace_copy \
  --source /workspace \
  --destination /tmp/candidate \
  > /logs/verifier/copy-stdout.txt \
  2> /logs/verifier/copy-stderr.txt
copy_exit_code=$?
if [[ "$copy_exit_code" -ne 0 ]]; then
  copy_reason=artifact-copy-failed
  if [[ "$copy_exit_code" -eq 20 ]]; then
    copy_reason=candidate-workspace-rejected
  fi
  python -m nl2repobench.verification.cli \
    --expected {expected} \
    --metric-contract {metric} \
    --reason "$copy_reason"
  exit 0
fi

chown -R candidate:candidate /tmp/candidate
python -I -B -m nl2repobench.verification.candidate_install \
  --source /tmp/candidate \
  --target /tmp/candidate-site \
  --timeout-sec {install_timeout} \
  --status /logs/verifier/candidate-install.json \
  > /logs/verifier/install-stdout.txt \
  2> /logs/verifier/install-stderr.txt
install_exit_code=$?
if [[ "$install_exit_code" -ne 0 ]]; then
  install_reason=candidate-installation-failed
  if [[ "$install_exit_code" -eq 70 ]]; then
    install_reason=verifier-internal-error
  fi
  python -m nl2repobench.verification.cli \
    --expected {expected} \
    --metric-contract {metric} \
    --reason "$install_reason"
  exit 0
fi

python -I -m nl2repobench.verification.process_cleanup --uid 10001
python -I -m nl2repobench.verification.integrity snapshot \
  --record /logs/verifier/trusted-files.json \
  /tests/private \
  /tests/command-plan.json \
  /usr/local/lib/python3.12/site-packages/nl2repobench

env HOME=/root \
NL2REPO_CANDIDATE_TOTAL_TIMEOUT_SEC={candidate_total_timeout} \
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python -I -B -m nl2repobench.verification.run_pytest \
  --collection /tmp/trusted-results/collection.json \
  --junit /tmp/trusted-results/junit.xml \
  /tests/private \
  > /logs/verifier/pytest-stdout.txt \
  2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?
if ! python -I -m nl2repobench.verification.process_cleanup --uid 10001; then
  python -I -m nl2repobench.verification.cli \
    --expected {expected} \
    --metric-contract {metric} \
    --reason verifier-internal-error
  exit 0
fi

if ! python -I -m nl2repobench.verification.integrity verify \
  --record /logs/verifier/trusted-files.json \
  /tests/private \
  /tests/command-plan.json \
  /usr/local/lib/python3.12/site-packages/nl2repobench; then
  python -I -m nl2repobench.verification.cli \
    --expected {expected} \
    --metric-contract {metric} \
    --reason verifier-internal-error
  exit 0
fi

if [[ -f /tmp/trusted-results/collection.json ]]; then
  install -m 0444 /tmp/trusted-results/collection.json /logs/verifier/collection.json
fi
if [[ -f /tmp/trusted-results/junit.xml ]]; then
  install -m 0444 /tmp/trusted-results/junit.xml /logs/verifier/junit.xml
fi

python -I -m nl2repobench.verification.cli \
  --expected {expected} \
  --metric-contract {metric} \
  --collection /logs/verifier/collection.json \
  --junit /logs/verifier/junit.xml \
  --pytest-exit-code "$pytest_exit_code"
exit 0
"""

    def _copy_verifier_runtime(self, destination: Path) -> None:
        package_root = Path(__file__).parents[1]
        files = (
            "__init__.py",
            "domain/__init__.py",
            "domain/canonical.py",
            "domain/models.py",
            "verification/__init__.py",
            "verification/cli.py",
            "verification/candidate_client.py",
            "verification/candidate_install.py",
            "verification/candidate_runner.py",
            "verification/command_plan.py",
            "verification/grader.py",
            "verification/junit.py",
            "verification/models.py",
            "verification/network_check.py",
            "verification/integrity.py",
            "verification/process_cleanup.py",
            "verification/pytest_plugin.py",
            "verification/run_pytest.py",
            "verification/workspace_copy.py",
        )
        for relative in files:
            source = package_root / relative
            target = destination / "nl2repobench" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, source.read_bytes())

    def _extract_private_bundle(self, reference: ArtifactRef, destination: Path) -> None:
        if self.artifact_resolver is None:
            raise HarborCompileError("private artifact resolver is required")
        archive = self.artifact_resolver.resolve(reference)
        try:
            extract_bundle_archive(
                archive,
                destination,
                limits=BundleLimits(
                    max_members=self.MAX_BUNDLE_MEMBERS,
                    max_member_bytes=self.MAX_BUNDLE_MEMBER_BYTES,
                    max_total_bytes=self.MAX_BUNDLE_TOTAL_BYTES,
                ),
            )
        except BundleArchiveIOError as exc:
            raise HarborCompileError(f"cannot extract private bundle: {exc}") from exc
        except BundleArchiveError as exc:
            raise HarborCompileError(str(exc)) from exc

    def _copy_tree(self, source: Path, destination: Path) -> None:
        try:
            copy_bundle_tree(source, destination)
        except BundleTreeSourceError as exc:
            raise HarborCompileError(
                f"development fixture directory is missing: {source}"
            ) from exc
        except BundleTreeError as exc:
            raise HarborCompileError(str(exc)) from exc

    def _write_readme(
        self,
        manifest: TaskManifest,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        mode = "development fixture" if allow_incomplete else "production"
        text = f"""# `{manifest.task_id}` Harbor Bundle

Generated deterministically from the canonical NL2RepoBench catalog.

- Mode: {mode}
- Canonical manifest: `{manifest.content_digest()}`
- Toolchain lock: `{self.toolchain.content_digest()}`
- Metric: `{manifest.metric.contract_id}`
- Expected tests: `{manifest.tests.expected_total}`
- Verifier: separate environment, no network

Run with Harbor {self.toolchain.harbor.version}:

```bash
{self.toolchain.harbor.runner} run -p . -a oracle
```
"""
        atomic_write(task_root / "README.md", text.encode())

    def _write_bundle_manifest(
        self,
        manifest: TaskManifest,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        files = []
        for path in sorted(item for item in task_root.rglob("*") if item.is_file()):
            data = path.read_bytes()
            files.append(
                {
                    "path": path.relative_to(task_root).as_posix(),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "size_bytes": len(data),
                }
            )
        payload = {
            "schema_version": "1.0",
            "task_id": manifest.task_id,
            "task_version": manifest.version,
            "mode": "development" if allow_incomplete else "production",
            "canonical_manifest_digest": manifest.content_digest(),
            "toolchain_lock_digest": self.toolchain.content_digest(),
            "files": files,
        }
        atomic_write(
            task_root / "bundle.manifest.json",
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n",
        )

    def _refresh_bundle_manifest(self, task_root: Path, kind: str) -> None:
        path = task_root / "bundle.manifest.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HarborCompileError(f"invalid source bundle manifest: {path}: {exc}") from exc
        files = []
        for item in sorted(entry for entry in task_root.rglob("*") if entry.is_file()):
            if item == path:
                continue
            data = item.read_bytes()
            files.append(
                {
                    "path": item.relative_to(task_root).as_posix(),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "size_bytes": len(data),
                }
            )
        payload["mode"] = f"control-{kind}"
        payload["files"] = files
        atomic_write(
            path,
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n",
        )

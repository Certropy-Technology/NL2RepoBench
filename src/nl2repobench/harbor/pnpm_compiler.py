"""Node Harbor compiler composed with the pnpm package-manager adapter."""

# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from pathlib import Path

import tomli_w

from nl2repobench.domain.canonical_contract import PackageManager, TaskManifest
from nl2repobench.package_managers.base import PackageManagerError
from nl2repobench.package_managers.pnpm import PnpmPackageManager
from nl2repobench.storage.artifacts import LocalArtifactResolver
from nl2repobench.storage.files import atomic_write
from nl2repobench.storage.materialize import ArchiveKind

from .node_compiler import (
    NODE_EXECUTABLE,
    NODE_RUNTIME_ROOT,
    PNPM_LAUNCHER,
    NodeHarborCompileError,
    NodeHarborCompiler,
)


class PnpmHarborCompiler(NodeHarborCompiler):
    """Generate a Node task whose dependency lifecycle is owned by pnpm."""

    package_manager = PnpmPackageManager()
    runtime_package_manager = PackageManager.PNPM
    candidate_install_id = "pnpm-pack-offline-v1"

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        super().__init__(toolchain_path, artifact_resolver=artifact_resolver)
        if self.toolchain.status == "locked" and self.toolchain.runtime.pnpm_version is None:
            raise NodeHarborCompileError("locked pnpm toolchain requires an exact pnpm version")

    @property
    def pnpm_version(self) -> str:
        return self.toolchain.runtime.pnpm_version or "9.15.0"

    def _write_environment(
        self, manifest: TaskManifest, task_root: Path, allow_incomplete: bool
    ) -> None:
        if not allow_incomplete:
            raise NodeHarborCompileError(
                "Node pnpm closure manifest/artifact is unavailable for production"
            )
        self._write_pnpm_runtime(task_root / "environment/pnpm-runtime")
        super()._write_environment(manifest, task_root, allow_incomplete)

    def _runtime_stage_extra(self, allow_incomplete: bool) -> str:
        if not allow_incomplete:
            raise NodeHarborCompileError(
                "Node pnpm closure manifest/artifact is unavailable for production"
            )
        return (
            f"  && cp -a /usr/lib/node_modules/pnpm {NODE_RUNTIME_ROOT}/lib/pnpm \\\n"
            f"  && test -f {PNPM_LAUNCHER} \\\n"
        )

    def _write_verifier(
        self,
        source_dir: Path,
        manifest: TaskManifest,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        tests_root = task_root / "tests"
        tests_root.mkdir(parents=True)
        runtime_root = tests_root / "runtime"
        runtime_root.mkdir()
        self._write_node_runtime(runtime_root / "node")
        self._write_python_verifier_runtime(tests_root)
        self._write_node_python_adapter(tests_root / "python-adapter")
        self._write_python_runtime_manifest_check(tests_root)
        self._write_pnpm_adapter(runtime_root / "node/install_pnpm.py")
        command_plan = self._resolve_node_command_plan(manifest, allow_incomplete)
        atomic_write(
            tests_root / "command-plan.json",
            json.dumps(
                command_plan.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            + b"\n",
        )

        dependencies_root = tests_root / "dependencies"
        dependencies_root.mkdir()
        if allow_incomplete:
            self._write_empty_pnpm_bundle(dependencies_root)
        try:
            if not allow_incomplete:
                self._validate_canonical_dependencies(manifest)
                raise NodeHarborCompileError(
                    "private-staging-contract-missing: production pnpm closure "
                    "staging requires F0.5"
                )
            self.package_manager.validate_lock(dependencies_root, self.pnpm_version)
        except PackageManagerError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        self._copy_tree(dependencies_root, task_root / "environment/pnpm-bundle")

        private_root = tests_root / "private"
        if manifest.tests.test_bundle is not None and not allow_incomplete:
            self._extract_private_bundle(
                manifest.tests.test_bundle, private_root, ArchiveKind.TEST_BUNDLE
            )
        else:
            fixture = source_dir / "harbor/tests"
            if not fixture.is_dir():
                raise NodeHarborCompileError("development pnpm task is missing harbor/tests")
            self._copy_tree(fixture, private_root)

        image = self.toolchain.images.verifier_base
        python_image = self.toolchain.images.verifier_python_base
        self._write_pnpm_runtime(tests_root / "pnpm-runtime")
        runtime_manifest = self._runtime_manifest_payload(image, allow_incomplete=allow_incomplete)
        atomic_write(
            tests_root / "node-runtime.manifest.json",
            json.dumps(runtime_manifest, sort_keys=True, separators=(",", ":")).encode()
            + b"\n",
        )
        runtime_manifest_check = self._runtime_manifest_check(image)
        runtime_manifest_stage = self._runtime_manifest_stage(image, allow_incomplete)
        runtime_manifest_final = (
            "" if allow_incomplete else "COPY node-runtime.manifest.json "
            f"{NODE_RUNTIME_ROOT}/runtime.manifest.json\n"
        )
        dockerfile = f"""FROM --platform=linux/amd64 {image} AS node-runtime
RUN resolved_node="$(readlink -f /usr/local/bin/node)" \\
  && test -f "$resolved_node" \\
  && test "$(/usr/local/bin/node --version)" = "v{self.toolchain.runtime.runtime_version}" \\
  && mkdir -p {NODE_RUNTIME_ROOT}/bin {NODE_RUNTIME_ROOT}/lib \\
  && cp --dereference "$resolved_node" {NODE_EXECUTABLE} \\
  && cp -aL /usr/local/lib/node_modules/npm {NODE_RUNTIME_ROOT}/lib/npm \\
  && cp -aL /usr/lib/node_modules/pnpm {NODE_RUNTIME_ROOT}/lib/pnpm \\
  && test -f {PNPM_LAUNCHER} \\
  && chmod 0555 {NODE_EXECUTABLE} \\
  && find {NODE_RUNTIME_ROOT} -type f ! -path {NODE_EXECUTABLE} -exec chmod 0444 {{}} + \\
  && chmod -R a-w {NODE_RUNTIME_ROOT}
{runtime_manifest_stage}
FROM --platform=linux/amd64 {python_image}

COPY --from=node-runtime {NODE_RUNTIME_ROOT} {NODE_RUNTIME_ROOT}
{runtime_manifest_final}
RUN test -f {NODE_RUNTIME_ROOT}/runtime.manifest.json \\
  && test -f {NODE_EXECUTABLE} \\
  && test ! -L {NODE_EXECUTABLE} \\
  && test "$({NODE_EXECUTABLE} {PNPM_LAUNCHER} --version)" = "{self.pnpm_version}"
{runtime_manifest_check}
COPY python-runtime /opt/nl2repobench-runtime
COPY python-runtime-manifest.json /tests/python-runtime-manifest.json
COPY python-runtime-manifest-check.py /tests/python-runtime-manifest-check.py
COPY python-adapter /opt/nl2repobench-node-adapter
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN /usr/local/bin/python3 -I -B /tests/python-runtime-manifest-check.py \\
  --root /opt/nl2repobench-runtime/nl2repobench --manifest /tests/python-runtime-manifest.json
RUN python -m pip install --no-cache-dir --require-hashes \\
  -r /tmp/verifier-requirements.lock.txt
COPY dependencies /opt/pnpm-bundle
COPY runtime /tests/runtime
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0500 private /tests/private
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \\
  && chmod -R 0555 /opt/nl2repobench-runtime \\
  && chmod -R 0555 /opt/nl2repobench-node-adapter \\
  && chmod -R 0500 /tests/private \\
  && chmod -R 0555 /tests/runtime
WORKDIR /tests
"""
        atomic_write(tests_root / "Dockerfile", dockerfile.encode())
        atomic_write(
            tests_root / "docker-compose.yaml",
            b"services:\n  main:\n    network_mode: none\n",
        )
        atomic_write(tests_root / "test.sh", self._test_script(manifest).encode())
        os.chmod(tests_root / "test.sh", 0o755)

    def _agent_dependency_setup(self) -> str:
        return f"""COPY pnpm-runtime {NODE_RUNTIME_ROOT}/lib/pnpm
COPY pnpm-bundle /opt/pnpm-bundle
ENV PNPM_HOME=/usr/local/share/pnpm \\
    npm_config_offline=true \\
    npm_config_ignore_scripts=true
"""

    def _write_pnpm_runtime(self, destination: Path) -> None:
        """Stage the host's packaged pnpm closure for development builds."""

        source = Path("/usr/lib/node_modules/pnpm")
        if not source.is_dir():
            raise NodeHarborCompileError("packaged pnpm closure is unavailable")
        self._copy_tree(source, destination)

    def _write_empty_pnpm_bundle(self, root: Path) -> None:
        lock = b"""lockfileVersion: '9.0'
settings:
  autoInstallPeers: false
  excludeLinksFromLockfile: false
importers:
  .: {}
packages: {}
snapshots: {}
"""
        atomic_write(root / "pnpm-lock.yaml", lock)
        (root / "pnpm-store").mkdir()
        payload = {
            "schema_version": "1.0",
            "ecosystem": "npm",
            "lockfile_version": "9",
            "package_manager": "pnpm",
            "package_manager_version": self.pnpm_version,
            "install_mode": "offline",
            "lifecycle_scripts": "ignore-scripts",
            "lockfile_sha256": hashlib.sha256(lock).hexdigest(),
            "files": [
                {
                    "path": "pnpm-lock.yaml",
                    "sha256": hashlib.sha256(lock).hexdigest(),
                }
            ],
        }
        atomic_write(
            root / "bundle.manifest.json",
            json.dumps(payload, sort_keys=True, indent=2).encode() + b"\n",
        )

    def _write_task_toml(self, manifest: TaskManifest, task_root: Path) -> None:
        super()._write_task_toml(manifest, task_root)
        path = task_root / "task.toml"
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        data["metadata"]["package_manager"] = "pnpm"
        data["metadata"]["package_manager_version"] = self.pnpm_version
        data["metadata"]["metric_contract"] = "fixed-test-pass-rate-v1"
        atomic_write(path, tomli_w.dumps(data).encode())

    def _test_script(self, manifest: TaskManifest) -> str:
        expected = manifest.tests.expected_total
        return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json /logs/verifier/report.json
rm -rf /tmp/candidate-source /tmp/candidate-site /tmp/pnpm-store
NETWORK_CHECK='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime");'
NETWORK_CHECK+='from nl2repobench.verification.network_check import main; main()'
python3 -I -c "$NETWORK_CHECK" --output /logs/verifier/network.json
network_exit=$?
if [[ "$network_exit" -eq 1 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason verifier-network-available --output /logs/verifier
  exit 0
elif [[ "$network_exit" -ne 0 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason verifier-internal-error --output /logs/verifier
  exit 0
fi
install -d -o candidate -g candidate -m 0700 /tmp/pnpm-store
cp -a /opt/pnpm-bundle/pnpm-store/. /tmp/pnpm-store/
chown -R candidate:candidate /tmp/pnpm-store
if ! {NODE_EXECUTABLE} /tests/runtime/node/copy_workspace.mjs \\
  --source /workspace --destination /tmp/candidate-source; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason candidate-workspace-rejected --output /logs/verifier
  exit 0
fi
if ! {NODE_EXECUTABLE} /tests/runtime/node/validate-pnpm-command-plan.mjs \\
  --path /tests/command-plan.json; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason verifier-internal-error --output /logs/verifier
  exit 0
fi
mkdir -p /tmp/candidate-site /tmp/candidate-site/home /tmp/candidate-site/tmp
chown -R candidate:candidate /tmp/candidate-source /tmp/candidate-site
install_exit=0
/usr/local/bin/python3 -I -B /tests/runtime/node/install_pnpm.py \\
  --source /tmp/candidate-source --target /tmp/candidate-site --store /tmp/pnpm-store || install_exit=$?
if [[ "$install_exit" -eq 70 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason verifier-internal-error --output /logs/verifier
  exit 0
elif [[ "$install_exit" -ne 0 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason candidate-installation-failed --output /logs/verifier
  exit 0
fi
export NODE_CANDIDATE_SITE=/tmp/candidate-site
export NODE_TEST_CLIENT=/tests/private/test_client.mjs
runner_exit_code=0
{NODE_EXECUTABLE} /tests/runtime/node/run_tests.mjs \\
  --tests /tests/private --candidate /tmp/candidate-site \\
  --expected {expected} --output /logs/verifier/report.json || runner_exit_code=$?
if [[ "$runner_exit_code" -eq 70 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason candidate-call-failed --output /logs/verifier
  exit 0
fi
{NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs --expected {expected} \\
  --report /logs/verifier/report.json \\
  --runner-exit-code "$runner_exit_code" --output /logs/verifier
exit 0
"""

    def _write_readme(
        self, manifest: TaskManifest, task_root: Path, allow_incomplete: bool
    ) -> None:
        mode = "development-only fixture" if allow_incomplete else "production"
        text = f"""# `{manifest.task_id}` Harbor Bundle

Generated by the Node/pnpm runtime and package-manager adapters.

- Mode: {mode}
- pnpm: `{self.pnpm_version}`
- Metric: `fixed-test-pass-rate-v1`
- Verifier: separate environment, no network
"""
        atomic_write(task_root / "README.md", text.encode())

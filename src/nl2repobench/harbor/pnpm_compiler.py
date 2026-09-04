"""Node Harbor compiler composed with the pnpm package-manager adapter."""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from pathlib import Path

import tomli_w

from nl2repobench.domain.models_v2 import TaskManifestV2
from nl2repobench.package_managers.pnpm import PnpmPackageManager
from nl2repobench.storage.artifacts import LocalArtifactResolver
from nl2repobench.storage.files import atomic_write
from nl2repobench.verification.node_pnpm_command_plan import EXPECTED_PNPM_PLAN

from .node_compiler import NodeHarborCompileError, NodeHarborCompiler


class PnpmHarborCompiler(NodeHarborCompiler):
    """Generate a Node task whose dependency lifecycle is owned by pnpm."""

    package_manager = PnpmPackageManager()

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
            json.dumps(EXPECTED_PNPM_PLAN, sort_keys=True, separators=(",", ":")).encode()
            + b"\n",
        )

        dependencies_root = tests_root / "dependencies"
        dependencies_root.mkdir()
        if allow_incomplete:
            self._write_empty_pnpm_bundle(dependencies_root)
        else:
            self._materialize_dependencies(manifest, dependencies_root)
        try:
            self.package_manager.validate_offline_store(
                dependencies_root,
                lockfile=dependencies_root / "pnpm-lock.yaml",
                manifest=dependencies_root / "bundle.manifest.json",
                expected_version=self.pnpm_version,
            )
        except ValueError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        self._copy_tree(dependencies_root, task_root / "environment/pnpm-bundle")

        private_root = tests_root / "private"
        if manifest.tests.test_bundle is not None and not allow_incomplete:
            self._extract_private_bundle(manifest.tests.test_bundle, private_root)
        else:
            fixture = source_dir / "harbor/tests"
            if not fixture.is_dir():
                raise NodeHarborCompileError("development pnpm task is missing harbor/tests")
            self._copy_tree(fixture, private_root)

        image = self.toolchain.images.verifier_base
        python_image = self.toolchain.images.verifier_python_base
        dockerfile = f"""FROM --platform=linux/amd64 {image} AS node-runtime
FROM --platform=linux/amd64 {python_image}

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \\
  && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN npm install --global pnpm@{self.pnpm_version}
COPY python-runtime /opt/nl2repobench-runtime
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \\
  -r /tmp/verifier-requirements.lock.txt
COPY dependencies /opt/pnpm-bundle
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
            tests_root / "docker-compose.yaml",
            b"services:\n  main:\n    network_mode: none\n",
        )
        atomic_write(tests_root / "test.sh", self._test_script(manifest).encode())
        os.chmod(tests_root / "test.sh", 0o755)

    def _agent_dependency_setup(self) -> str:
        return f"""RUN npm install --global pnpm@{self.pnpm_version}
COPY pnpm-bundle /opt/pnpm-bundle
ENV PNPM_HOME=/usr/local/share/pnpm \\
    npm_config_offline=true \\
    npm_config_ignore_scripts=true
"""

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

    def _write_task_toml(self, manifest: TaskManifestV2, task_root: Path) -> None:
        super()._write_task_toml(manifest, task_root)
        path = task_root / "task.toml"
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        data["metadata"]["package_manager"] = "pnpm"
        data["metadata"]["package_manager_version"] = self.pnpm_version
        data["metadata"]["metric_contract"] = "fixed-test-pass-rate-v1"
        atomic_write(path, tomli_w.dumps(data).encode())

    def _test_script(self, manifest: TaskManifestV2) -> str:
        expected = manifest.tests.expected_total
        return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json /logs/verifier/report.json
rm -rf /tmp/candidate-source /tmp/candidate-site /tmp/pnpm-store
NETWORK_CHECK='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime");'
NETWORK_CHECK+='from nl2repobench.verification.network_check import main; main()'
if ! python3 -I -c "$NETWORK_CHECK" \\
  --output /logs/verifier/network.json; then
  node /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason verifier-network-available --output /logs/verifier
  exit 0
fi
install -d -o candidate -g candidate -m 0700 /tmp/pnpm-store
cp -a /opt/pnpm-bundle/pnpm-store/. /tmp/pnpm-store/
chown -R candidate:candidate /tmp/pnpm-store
if ! node /tests/runtime/node/copy_workspace.mjs \\
  --source /workspace --destination /tmp/candidate-source; then
  node /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason candidate-workspace-rejected --output /logs/verifier
  exit 0
fi
if ! node /tests/runtime/node/validate-pnpm-command-plan.mjs \\
  --path /tests/command-plan.json; then
  node /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason verifier-internal-error --output /logs/verifier
  exit 0
fi
mkdir -p /tmp/candidate-site /tmp/candidate-site/home /tmp/candidate-site/tmp
chown -R candidate:candidate /tmp/candidate-source /tmp/candidate-site
if ! runuser -u candidate -- env PATH=/usr/local/bin:/usr/bin:/bin \\
  /usr/local/bin/node /tests/runtime/node/install_candidate_pnpm.mjs \\
  --source /tmp/candidate-source --target /tmp/candidate-site --store /tmp/pnpm-store; then
  node /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason candidate-installation-failed --output /logs/verifier
  exit 0
fi
export NODE_CANDIDATE_SITE=/tmp/candidate-site
export NODE_TEST_CLIENT=/tests/private/test_client.mjs
runner_exit_code=0
node /tests/runtime/node/run_tests.mjs --tests /tests/private --candidate /tmp/candidate-site \\
  --expected {expected} --output /logs/verifier/report.json || runner_exit_code=$?
if [[ "$runner_exit_code" -eq 70 ]]; then
  node /tests/runtime/node/grade-report.mjs --expected {expected} \\
    --reason candidate-call-failed --output /logs/verifier
  exit 0
fi
node /tests/runtime/node/grade-report.mjs --expected {expected} \\
  --report /logs/verifier/report.json \\
  --runner-exit-code "$runner_exit_code" --output /logs/verifier
exit 0
"""

    def _write_readme(
        self, manifest: TaskManifestV2, task_root: Path, allow_incomplete: bool
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

"""Ruby/Bundler Harbor compiler for the first black-box Ruby lane."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler, DeclarativeTaskSource
from nl2repobench.domain.models import ArtifactRef, TaskManifest
from nl2repobench.package_managers.base import PackageManagerError
from nl2repobench.package_managers.bundler import BundlerPackageManager
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.files import atomic_write

from .bundle_io import BundleLimits
from .models import AgentRuntimeImageLock
from .task_writer import (
    TaskWriterError,
    copy_python_verifier_runtime,
    copy_tree,
    extract_private_bundle,
    write_file_manifest,
    write_instruction,
)


class RubyHarborCompileError(ValueError):
    """Raised when a Ruby task cannot satisfy the Bundler profile."""


class RubyHarborCompiler:
    """Generate a separate-verifier Ruby task with an offline Bundler cache."""

    MAX_BUNDLE_MEMBERS = 10_000
    MAX_BUNDLE_MEMBER_BYTES = 512 * 1024 * 1024
    MAX_BUNDLE_TOTAL_BYTES = 2 * 1024 * 1024 * 1024

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        self.toolchain_path = toolchain_path
        self.artifact_resolver = artifact_resolver
        try:
            data = tomllib.loads(toolchain_path.read_text(encoding="utf-8"))
            self.status = str(data.get("status") or "development-only")
            self.agent_runtime = AgentRuntimeImageLock.model_validate(data["agent_runtime"])
            ruby = data["ruby"]
            self.ruby_version = str(ruby["version"])
            self.bundler_version = str(ruby["bundler_version"])
            self.base_image = str(ruby["base_image"])
            harbor = data["harbor"]
            harbor_lock = toolchain_path.parent / str(harbor["lock_file"])
            self.harbor_lock_sha256 = str(harbor["lock_sha256"])
            self.harbor_version = str(harbor["version"])
            self.task_schema = str(harbor["task_schema"])
            verifier = data["verifier"]
            self.verifier_base_image = str(verifier["base_image"])
            requirements = str(
                data.get("verifier_requirements_lock") or "verifier/requirements.lock.txt"
            )
            self.requirements_path = toolchain_path.parent / requirements
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
            raise RubyHarborCompileError(f"invalid Ruby toolchain lock: {toolchain_path}") from exc
        if self.status not in {"development-only", "locked"}:
            raise RubyHarborCompileError(f"invalid Ruby toolchain status: {self.status}")
        if not re.fullmatch(r"[A-Za-z0-9._/-]+@sha256:[0-9a-f]{64}", self.base_image):
            raise RubyHarborCompileError("Ruby base image must be digest pinned")
        if not re.fullmatch(
            r"[A-Za-z0-9._/-]+@sha256:[0-9a-f]{64}", self.verifier_base_image
        ):
            raise RubyHarborCompileError("Ruby verifier base image must be digest pinned")
        try:
            actual_lock = f"sha256:{hashlib.sha256(harbor_lock.read_bytes()).hexdigest()}"
        except OSError as exc:
            raise RubyHarborCompileError(f"Harbor runner lock is missing: {harbor_lock}") from exc
        if actual_lock != self.harbor_lock_sha256:
            raise RubyHarborCompileError("Harbor runner lock digest does not match Ruby toolchain")
        if self.harbor_version != "0.21.0" or self.task_schema != "1.4":
            raise RubyHarborCompileError("Ruby Harbor contract must be 0.21.0/task 1.4")
        if not self.requirements_path.is_file():
            raise RubyHarborCompileError(
                f"verifier requirements lock is missing: {self.requirements_path}"
            )

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        if not isinstance(source, DeclarativeTaskSource) or source.metadata.language != "ruby":
            raise RubyHarborCompileError(
                "Ruby compiler accepts only an explicit language=ruby source"
            )
        if source.harbor is None:
            raise RubyHarborCompileError("Ruby task source is missing [harbor] settings")
        if self.status == "locked" and allow_incomplete:
            raise RubyHarborCompileError(
                "allow_incomplete is only valid for the development Ruby toolchain"
            )
        if not allow_incomplete and self.status != "locked":
            raise RubyHarborCompileError("Ruby production output requires a locked toolchain")
        if not allow_incomplete and (
            source.harbor.agent_network_mode != "no-network"
            or source.harbor.agent_allowed_hosts
        ):
            raise RubyHarborCompileError(
                "production Agent runtime must be no-network with no static allowed hosts"
            )
        with tempfile.TemporaryDirectory(prefix="nl2repo-ruby-canonical-") as canonical_temp:
            root = Path(canonical_temp)
            compiled = CatalogCompiler(FileArtifactStore(root / "artifacts")).compile_task(
                source_dir, root / "canonical"
            )
            manifest = compiled.manifest
        if not isinstance(manifest, TaskManifest):
            raise RubyHarborCompileError("Ruby source did not produce a canonical manifest")
        gaps = manifest.publication_gaps()
        if gaps and not allow_incomplete:
            raise RubyHarborCompileError("Ruby production source is incomplete: " + ", ".join(gaps))
        if manifest.tests.framework != "ruby-contract" or manifest.tests.expected_total <= 0:
            raise RubyHarborCompileError(
                "Ruby bridge profile requires framework=ruby-contract and a positive leaf count"
            )
        if source.dependencies.installer != "bundler":
            raise RubyHarborCompileError("Ruby task dependencies.installer must be bundler")
        if not allow_incomplete:
            expected_digest = self.base_image.rsplit("@", 1)[1]
            environment = manifest.environment_lock
            if environment.runtime_version != self.ruby_version:
                raise RubyHarborCompileError(
                    "Ruby source runtime_version does not match the locked toolchain"
                )
            if environment.base_image_digest != expected_digest:
                raise RubyHarborCompileError(
                    "Ruby source base_image_digest does not match the locked toolchain"
                )
        fixture = source_dir / "harbor"
        required = (
            (
                "dependencies/Gemfile",
                "dependencies/Gemfile.lock",
                "dependencies/gem.manifest.json",
                "tests/bridge.rb",
                "tests/contract.sh",
                "solution/solve.sh",
            )
            if allow_incomplete
            else ("tests/bridge.rb",)
        )
        for relative in required:
            if not (fixture / relative).is_file():
                raise RubyHarborCompileError(f"Ruby profile is missing harbor/{relative}")
        final_root = output_root / source.task_id
        if final_root.exists() or final_root.is_symlink():
            raise RubyHarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{source.task_id}-", dir=output_root))
        try:
            write_instruction(source_dir, source.instruction, temporary)
            self._write_environment(temporary)
            self._write_dependencies(source, fixture, temporary, allow_incomplete)
            self._write_verifier(source, fixture, temporary, allow_incomplete)
            self._write_solution(source, fixture, temporary, allow_incomplete)
            self._write_controls(fixture, temporary)
            self._write_task_toml(manifest, temporary)
            self._write_readme(source, temporary, allow_incomplete)
            write_file_manifest(
                temporary,
                payload={
                    "task_id": source.task_id,
                    "task_version": source.version,
                    "mode": "development" if allow_incomplete else "production",
                    "canonical_manifest_digest": manifest.content_digest(),
                    "toolchain_lock_digest": self._toolchain_digest(),
                },
                schema_version="1.0",
            )
            os.rename(temporary, final_root)
        except (OSError, TaskWriterError, PackageManagerError, RubyHarborCompileError):
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        return final_root

    def prepare_control_bundle(self, task_root: Path, kind: str, output_root: Path) -> Path:
        """Create a Ruby control bundle without mutating the compiled task."""

        supported = {
            "empty",
            "stub",
            "forgery",
            "install-failure",
            "hang",
            "oversized-output",
            "background-process",
        }
        if kind not in supported:
            raise RubyHarborCompileError(f"unsupported Ruby control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if not script.is_file() or script.is_symlink():
            raise RubyHarborCompileError(f"Ruby control script is missing: {script}")
        target = output_root / f"{task_root.name}-{kind}"
        if target.exists() or target.is_symlink():
            raise RubyHarborCompileError(f"Ruby control output already exists: {target}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = output_root / f".{target.name}-tmp"
        if temporary.exists():
            shutil.rmtree(temporary)
        try:
            copy_tree(task_root, temporary)
            atomic_write(temporary / "solution/solve.sh", script.read_bytes())
            os.chmod(temporary / "solution/solve.sh", 0o755)
            payload = self._read_bundle_payload(temporary / "bundle.manifest.json")
            payload["control_kind"] = kind
            write_file_manifest(temporary, payload=payload, schema_version="1.0")
            os.rename(temporary, target)
        except (OSError, TaskWriterError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            raise RubyHarborCompileError(str(exc)) from exc
        return target

    def _write_environment(self, task_root: Path) -> None:
        atomic_write(
            task_root / "environment/Dockerfile",
            f"""FROM --platform=linux/amd64 {self.base_image} AS ruby-runtime

FROM --platform=linux/amd64 {self.agent_runtime.image}

LABEL org.nl2repobench.agent-runtime-image=\"{self.agent_runtime.image}\" \\
  org.nl2repobench.agent-runtime-image-id=\"{self.agent_runtime.image_id}\" \\
  org.nl2repobench.agent-dependency-build=\"bundler-offline-cache-v1\"

COPY --from=ruby-runtime /usr/local/bin/ruby /usr/local/bin/ruby
COPY --from=ruby-runtime /usr/local/bin/bundle /usr/local/bin/bundle
COPY --from=ruby-runtime /usr/local/lib/ruby /usr/local/lib/ruby
COPY --from=ruby-runtime /usr/local/lib/libruby* /usr/local/lib/
COPY --from=ruby-runtime /lib/x86_64-linux-gnu/libyaml-0.so.2 /lib/x86_64-linux-gnu/
COPY --from=ruby-runtime /usr/local/bundle /usr/local/bundle
RUN case \"$(ruby --version)\" in \\
  \"ruby {self.ruby_version} \"*) ;; *) exit 1;; esac \\
  && test \"$(bundle --version)\" = \"Bundler version {self.bundler_version}\"
COPY gem-bundle /opt/gem-bundle
ENV BUNDLE_USER_CACHE=/opt/gem-bundle/vendor/cache \\
    BUNDLE_WITHOUT=development:test
WORKDIR /workspace
""".encode(),
        )

    def _write_dependencies(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        destination = task_root / "tests/dependencies"
        try:
            if allow_incomplete:
                copy_tree(fixture / "dependencies", destination)
            else:
                if source.dependencies.gem_bundle is None:
                    raise RubyHarborCompileError(
                        "Ruby production task requires dependencies.gem_bundle"
                    )
                self._extract_private_bundle(source.dependencies.gem_bundle, destination)
            BundlerPackageManager().validate_offline_store(
                destination,
                lockfile=destination / "Gemfile.lock",
                manifest=destination / "gem.manifest.json",
                expected_version=self.bundler_version,
            )
            copy_tree(destination, task_root / "environment/gem-bundle")
        except (TaskWriterError, PackageManagerError) as exc:
            raise RubyHarborCompileError(f"invalid Ruby gem closure: {exc}") from exc

    def _write_verifier(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        tests_root = task_root / "tests"
        private_root = tests_root / "private"
        private_root.mkdir(parents=True, exist_ok=True)
        if allow_incomplete:
            copy_tree(fixture / "tests", private_root)
        else:
            if source.verifier is None:
                raise RubyHarborCompileError("Ruby production task requires [verifier]")
            if source.verifier.entrypoint != "contract.sh":
                raise RubyHarborCompileError(
                    "Ruby verifier profile requires entrypoint=contract.sh"
                )
            self._extract_private_bundle(source.verifier.bundle, private_root)
        bridge = fixture / "tests/bridge.rb"
        if bridge.is_symlink() or not bridge.is_file():
            raise RubyHarborCompileError("Ruby task requires a reviewed public bridge.rb")
        atomic_write(private_root / "bridge.rb", bridge.read_bytes())
        contract = private_root / "contract.sh"
        if contract.is_symlink() or not contract.is_file():
            raise RubyHarborCompileError("Ruby verifier bundle must contain contract.sh")
        os.chmod(contract, 0o555)
        runtime = tests_root / "runtime"
        try:
            copy_python_verifier_runtime(runtime)
        except TaskWriterError as exc:
            raise RubyHarborCompileError(str(exc)) from exc
        atomic_write(
            tests_root / "verifier-requirements.lock.txt", self.requirements_path.read_bytes()
        )
        dockerfile = f"""FROM --platform=linux/amd64 {self.base_image} AS ruby-runtime

FROM --platform=linux/amd64 {self.verifier_base_image}

COPY --from=ruby-runtime /usr/local/bin/ruby /usr/local/bin/ruby
COPY --from=ruby-runtime /usr/local/bin/bundle /usr/local/bin/bundle
COPY --from=ruby-runtime /usr/local/lib/ruby /usr/local/lib/ruby
COPY --from=ruby-runtime /usr/local/lib/libruby* /usr/local/lib/
COPY --from=ruby-runtime /lib/x86_64-linux-gnu/libyaml-0.so.2 /lib/x86_64-linux-gnu/
COPY --from=ruby-runtime /usr/local/bundle /usr/local/bundle

RUN apt-get update \\
  && apt-get install -y --no-install-recommends python3 python3-pip \\
  && rm -rf /var/lib/apt/lists/*
COPY runtime /opt/nl2repobench-runtime
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN python3 -m pip install --break-system-packages --no-cache-dir --require-hashes \\
  -r /tmp/verifier-requirements.lock.txt
COPY dependencies /opt/gem-bundle
COPY --chmod=0500 private /tests/private
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \\
  && chmod -R 0555 /opt/nl2repobench-runtime
WORKDIR /tests
"""
        atomic_write(tests_root / "Dockerfile", dockerfile.encode())
        atomic_write(
            tests_root / "docker-compose.yaml", b"services:\n  main:\n    network_mode: none\n"
        )
        profile = source.harbor
        assert profile is not None
        atomic_write(
            tests_root / "test.sh",
            self._test_script(
                expected_total=source.tests.expected_total,
                install_timeout_sec=profile.candidate_install_timeout_sec,
                bridge_timeout_sec=profile.candidate_total_timeout_sec,
            ).encode(),
        )
        os.chmod(tests_root / "test.sh", 0o755)

    def _write_solution(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        destination = task_root / "solution"
        if allow_incomplete:
            copy_tree(fixture / "solution", destination)
        else:
            if source.oracle_bundle is None:
                raise RubyHarborCompileError("Ruby production task requires oracle_bundle")
            self._extract_private_bundle(source.oracle_bundle, destination)
        solve = destination / "solve.sh"
        if solve.is_symlink() or not solve.is_file():
            raise RubyHarborCompileError("Ruby Oracle bundle must contain solve.sh")
        os.chmod(solve, 0o755)

    @staticmethod
    def _write_controls(fixture: Path, task_root: Path) -> None:
        controls = fixture / "controls"
        if controls.is_dir():
            copy_tree(controls, task_root / "controls")

    def _write_task_toml(self, manifest: TaskManifest, task_root: Path) -> None:
        profile = manifest.harbor
        assert profile is not None
        data: dict[str, Any] = {
            "schema_version": self.task_schema,
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
                "language": "ruby",
                "runtime": "ruby",
                "runtime_version": self.ruby_version,
                "package_manager": "bundler",
                "package_manager_version": self.bundler_version,
                "test_framework": "ruby-contract",
                "metric_contract": "fixed-test-pass-rate-v1",
                "expected_test_count": manifest.tests.expected_total,
                "canonical_manifest_digest": manifest.content_digest(),
                "toolchain_lock_digest": self._toolchain_digest(),
            },
            "agent": {"timeout_sec": profile.agent_timeout_sec},
            "verifier": {
                "timeout_sec": profile.verifier_timeout_sec,
                "environment_mode": "separate",
                "network_mode": "no-network",
            },
            "environment": {
                "network_mode": profile.agent_network_mode,
                "cpus": profile.cpus,
                "memory_mb": profile.memory_mb,
                "storage_mb": profile.storage_mb,
            },
        }
        atomic_write(task_root / "task.toml", tomli_w.dumps(data).encode())

    def _test_script(
        self,
        *,
        expected_total: int,
        install_timeout_sec: float,
        bridge_timeout_sec: float,
    ) -> str:
        bridge_timeout = f"{bridge_timeout_sec:g}"
        return f"""#!/usr/bin/env bash
set -uo pipefail
PYTHON_ROOT='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime")'
grade() {{
  python3 -I -c "$PYTHON_ROOT; \\
from nl2repobench.verification.cli import main; main()" \\
    --runtime ruby --expected {expected_total} \\
    --metric-contract fixed-test-pass-rate-v1 \\
    --output /logs/verifier "$@"
}}
mkdir -p /logs/verifier
if ! python3 -I -c "$PYTHON_ROOT; \\
from nl2repobench.verification.network_check import main; main()" \\
  --output /logs/verifier/network.json; then
  grade --reason verifier-network-available
  exit 0
fi
COPY_WORKSPACE='from nl2repobench.verification.workspace_copy import main; main()'
if ! python3 -I -c "$PYTHON_ROOT; $COPY_WORKSPACE" \\
  --source /workspace --destination /tmp/ruby-candidate; then
  grade --reason candidate-workspace-rejected
  exit 0
fi
chown -R candidate:candidate /tmp/ruby-candidate
mkdir -p /tmp/ruby-candidate-bundle /tmp/ruby-candidate/vendor/cache
cp -a /opt/gem-bundle/vendor/cache/. /tmp/ruby-candidate/vendor/cache/ 2>/dev/null || true
chown -R candidate:candidate /tmp/ruby-candidate-bundle /tmp/ruby-candidate/vendor
VALIDATE='from pathlib import Path;'
VALIDATE+='from nl2repobench.package_managers.bundler import BundlerPackageManager;'
VALIDATE+='BundlerPackageManager().validate_lock('
VALIDATE+='Path("/tmp/ruby-candidate/Gemfile.lock"),'
VALIDATE+='expected_version="{self.bundler_version}")'
if ! runuser -u candidate -- python3 -I -c "$PYTHON_ROOT; $VALIDATE"; then
  grade --reason candidate-installation-failed
  exit 0
fi
INSTALL='from nl2repobench.verification.ruby_supervisor import run_ruby_bridge;'
INSTALL+='result=run_ruby_bridge(('
INSTALL+='"/usr/bin/env",'
INSTALL+='"BUNDLE_GEMFILE=/tmp/ruby-candidate/Gemfile",'
INSTALL+='"BUNDLE_USER_CACHE=/tmp/ruby-candidate/vendor/cache",'
INSTALL+='"BUNDLE_PATH=/tmp/ruby-candidate-bundle",'
INSTALL+='"BUNDLE_IGNORE_CONFIG=1",'
INSTALL+='"/usr/local/bin/bundle","install","--local","--jobs","1","--retry","0"),'
INSTALL+='b"",timeout_sec={install_timeout_sec},max_output_bytes=256*1024,'
INSTALL+='max_file_bytes=512*1024*1024);'
INSTALL+='raise SystemExit(result.returncode)'
if ! python3 -I -c "$PYTHON_ROOT; $INSTALL"; then
  grade --reason candidate-installation-failed
  exit 0
fi
install -o root -g root -m 0444 /tests/private/bridge.rb /tmp/ruby-candidate/bridge.rb
cat > /tmp/ruby-bridge-proxy <<'SH'
#!/bin/sh
exec python3 -I -- \\
  /opt/nl2repobench-runtime/nl2repobench/verification/ruby_bridge_proxy.py \\
  --timeout-sec {bridge_timeout} "$@"
SH
chmod 0555 /tmp/ruby-bridge-proxy
runner_exit_code=0
/bin/bash /tests/private/contract.sh /tmp/ruby-bridge-proxy \\
  /tmp/ruby-candidate/bridge.rb /tmp/ruby-candidate \\
  /tmp/ruby-candidate-bundle > /tmp/ruby-contract-output \\
  2> /tmp/ruby-contract-stderr || runner_exit_code=$?
if [[ "$runner_exit_code" -eq 124 || "$runner_exit_code" -eq 125 ]]; then
  grade --reason candidate-call-failed
  exit 0
fi
if [[ ! -s /tmp/ruby-contract-output ]]; then
  grade --reason candidate-call-failed
  exit 0
fi
if [[ "$runner_exit_code" -eq 0 ]]; then
  trusted_exit=0
else
  trusted_exit=1
fi
python3 -I -c "$PYTHON_ROOT; \\
from nl2repobench.verification.ruby_contract_report import main; \\
raise SystemExit(main())" \\
  --input /tmp/ruby-contract-output --output /tmp/ruby-report.json \\
  --expected {expected_total} --runner-exit-code "$trusted_exit" || \\
  grade --reason verifier-internal-error
if [[ ! -s /tmp/ruby-report.json ]]; then
  exit 0
fi
grade --report /tmp/ruby-report.json --runner-exit-code "$trusted_exit"
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
            raise RubyHarborCompileError(str(exc)) from exc

    def _toolchain_digest(self) -> str:
        return f"sha256:{hashlib.sha256(self.toolchain_path.read_bytes()).hexdigest()}"

    @staticmethod
    def _read_bundle_payload(path: Path) -> dict[str, object]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RubyHarborCompileError(f"invalid Ruby bundle manifest: {exc}") from exc
        if not isinstance(payload, dict):
            raise RubyHarborCompileError("invalid Ruby bundle manifest object")
        payload.pop("schema_version", None)
        payload.pop("files", None)
        return payload

    def _write_readme(
        self, source: DeclarativeTaskSource, task_root: Path, allow_incomplete: bool
    ) -> None:
        mode = "development-only fixture" if allow_incomplete else "production"
        atomic_write(
            task_root / "README.md",
            (
                f"# `{source.task_id}` Harbor Bundle\n\n"
                f"- Mode: {mode}\n- Ruby: `{self.ruby_version}`\n"
                f"- Bundler: `{self.bundler_version}`\n"
                "- Candidate execution: Ruby JSON subprocess bridge, no network\n"
            ).encode(),
        )


__all__ = ["RubyHarborCompileError", "RubyHarborCompiler"]

"""Go Harbor compiler entry point for the unified runtime registry."""

from __future__ import annotations

import hashlib
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
from nl2repobench.package_managers.go_modules import GoModulesPackageManager
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


class GoHarborCompileError(ValueError):
    """Raised when a Go task cannot satisfy the first production profile."""


GO_RUNTIME_LOCK_FILES = (
    "src/nl2repobench/verification/go_bridge.py",
    "src/nl2repobench/verification/go_bridge_proxy.py",
    "src/nl2repobench/verification/go_contract_runner.py",
    "src/nl2repobench/verification/go_grader.py",
    "src/nl2repobench/verification/go_supervisor.py",
    "src/nl2repobench/verification/normalize/go_json.py",
    "src/nl2repobench/package_managers/go_modules.py",
)


class GoHarborCompiler:
    """Registry-facing Go compiler shell.

    The compiler is intentionally strict until a Go catalog source supplies a
    locked toolchain, private contract bundle, and module closure. The typed
    bridge and closure validators are independently usable before that source
    package is published.
    """

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
            self.go_version = str(data["go"]["version"])
            self.base_image = str(data["go"]["base_image"])
            requirements_lock = str(
                data.get("verifier_requirements_lock") or "verifier/requirements.lock.txt"
            )
            self.requirements_path = toolchain_path.parent / requirements_lock
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
            raise GoHarborCompileError(f"invalid Go toolchain lock: {toolchain_path}") from exc
        if self.status not in {"development-only", "locked"}:
            raise GoHarborCompileError(f"invalid Go toolchain status: {self.status}")
        if not re.fullmatch(r"[A-Za-z0-9._/-]+@sha256:[0-9a-f]{64}", self.base_image):
            raise GoHarborCompileError("Go toolchain base image must be digest pinned")
        if self.status == "locked":
            self._validate_locked_toolchain(data)

    def _validate_locked_toolchain(self, data: dict[str, Any]) -> None:
        repository_root = self.toolchain_path.parent
        if data.get("schema_version") != "1.0":
            raise GoHarborCompileError("locked Go toolchain schema must be 1.0")
        if data.get("go_report_schema") != "go-test-json-v1":
            raise GoHarborCompileError("locked Go report schema must be go-test-json-v1")
        go = data.get("go")
        if not isinstance(go, dict) or go.get("platform") != "linux/amd64":
            raise GoHarborCompileError("locked Go toolchain platform must be linux/amd64")
        if go.get("executable") != "/usr/local/go/bin/go":
            raise GoHarborCompileError("locked Go executable must be /usr/local/go/bin/go")
        runtime_digest = hashlib.sha256()
        try:
            for relative in GO_RUNTIME_LOCK_FILES:
                path = repository_root / relative
                runtime_digest.update(relative.removeprefix("src/nl2repobench/").encode())
                runtime_digest.update(b"\0")
                runtime_digest.update(hashlib.sha256(path.read_bytes()).digest())
        except OSError as exc:
            raise GoHarborCompileError(f"cannot hash locked Go runtime: {exc}") from exc
        expected_runtime = f"sha256:{runtime_digest.hexdigest()}"
        if data.get("go_runtime_sha256") != expected_runtime:
            raise GoHarborCompileError("Go runtime digest does not match toolchain lock")
        harbor = data.get("harbor")
        if not isinstance(harbor, dict):
            raise GoHarborCompileError("locked Go toolchain requires [harbor]")
        if harbor.get("version") != "0.21.0" or harbor.get("task_schema") != "1.4":
            raise GoHarborCompileError("locked Go Harbor contract must be 0.21.0/task 1.4")
        self._validate_locked_file(
            str(data.get("verifier_requirements_lock") or ""),
            data.get("verifier_requirements_sha256"),
            "verifier requirements",
        )
        self._validate_locked_file(
            str(harbor.get("lock_file") or ""),
            harbor.get("lock_sha256"),
            "Harbor runner",
        )

    def _validate_locked_file(self, relative: str, expected: Any, description: str) -> None:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or relative in {"", "."}:
            raise GoHarborCompileError(f"locked {description} path is unsafe")
        try:
            payload = (self.toolchain_path.parent / path).read_bytes()
            actual = f"sha256:{hashlib.sha256(payload).hexdigest()}"
        except OSError as exc:
            raise GoHarborCompileError(f"cannot hash locked {description}: {exc}") from exc
        if expected != actual:
            raise GoHarborCompileError(f"locked {description} digest does not match")

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        if not isinstance(source, DeclarativeTaskSource) or source.metadata.language != "go":
            raise GoHarborCompileError("Go compiler accepts only an explicit language=go source")
        if source.harbor is None:
            raise GoHarborCompileError("Go task source is missing [harbor] settings")
        if not allow_incomplete and (
            source.harbor.agent_network_mode != "no-network"
            or source.harbor.agent_allowed_hosts
        ):
            raise GoHarborCompileError(
                "production Agent runtime must be no-network with no static allowed hosts"
            )
        if allow_incomplete and self.status != "development-only":
            raise GoHarborCompileError(
                "allow_incomplete is only valid for the development Go toolchain"
            )
        if not allow_incomplete and self.status != "locked":
            raise GoHarborCompileError("Go production output requires toolchain.go.lock.toml")
        with tempfile.TemporaryDirectory(prefix="nl2repo-go-canonical-") as canonical_temp:
            root = Path(canonical_temp)
            compiled = CatalogCompiler(FileArtifactStore(root / "artifacts")).compile_task(
                source_dir, root / "canonical"
            )
            manifest = compiled.manifest
        if not isinstance(manifest, TaskManifest):
            raise GoHarborCompileError("Go source did not produce a v1 manifest")
        gaps = manifest.publication_gaps()
        if gaps and not allow_incomplete:
            raise GoHarborCompileError(
                "Go production source is incomplete: " + ", ".join(gaps)
            )
        if source.tests.expected_total != 1:
            raise GoHarborCompileError(
                "the first Go bridge profile supports exactly one verifier-owned leaf"
            )
        fixture = source_dir / "harbor"
        required = (
            ("tests/bridge.go", "tests/contract.sh", "solution/solve.sh")
            if allow_incomplete
            else ("tests/bridge.go",)
        )
        for relative in required:
            if not (fixture / relative).is_file():
                raise GoHarborCompileError(f"Go profile is missing harbor/{relative}")
        final_root = output_root / source.task_id
        if final_root.exists() or final_root.is_symlink():
            raise GoHarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = output_root / f".{source.task_id}-tmp"
        if temporary.exists():
            shutil.rmtree(temporary)
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
                    "toolchain_version": self.go_version,
                    "canonical_manifest_digest": manifest.content_digest(),
                    "toolchain_lock_digest": self._toolchain_digest(),
                },
                schema_version="1.0",
            )
            os.rename(temporary, final_root)
        except (OSError, TaskWriterError, GoHarborCompileError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            if isinstance(exc, GoHarborCompileError):
                raise
            raise GoHarborCompileError(str(exc)) from exc
        return final_root

    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
    ) -> Path:
        """Create a Go control bundle without mutating the compiled task."""

        supported = {
            "stub",
            "forgery",
            "install-failure",
            "panic",
            "hang",
            "oversized-output",
            "background-process",
        }
        if kind not in supported:
            raise GoHarborCompileError(f"unsupported Go control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if not script.is_file() or script.is_symlink():
            raise GoHarborCompileError(f"Go control script is missing: {script}")
        target = output_root / f"{task_root.name}-{kind}"
        if target.exists() or target.is_symlink():
            raise GoHarborCompileError(f"Go control output already exists: {target}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = output_root / f".{target.name}-tmp"
        if temporary.exists():
            shutil.rmtree(temporary)
        try:
            copy_tree(task_root, temporary)
            atomic_write(temporary / "solution/solve.sh", script.read_bytes())
            os.chmod(temporary / "solution/solve.sh", 0o755)
            manifest = self._read_bundle_payload(temporary / "bundle.manifest.json")
            manifest["control_kind"] = kind
            write_file_manifest(temporary, payload=manifest, schema_version="1.0")
            os.rename(temporary, target)
        except (OSError, TaskWriterError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            raise GoHarborCompileError(str(exc)) from exc
        return target

    def _write_environment(self, task_root: Path) -> None:
        atomic_write(
            task_root / "environment/Dockerfile",
            f"""FROM --platform=linux/amd64 {self.base_image} AS go-runtime

FROM --platform=linux/amd64 {self.agent_runtime.image}

LABEL org.nl2repobench.agent-runtime-image="{self.agent_runtime.image}" \\
  org.nl2repobench.agent-runtime-image-id="{self.agent_runtime.image_id}" \\
  org.nl2repobench.agent-dependency-build="go-offline-module-bundle-v1"

COPY --from=go-runtime /usr/local/go /usr/local/go
ENV PATH=/usr/local/go/bin:$PATH \
    GOPROXY=off \
    GOSUMDB=off \
    GOWORK=off \
    GOTOOLCHAIN=local
RUN case "$(/usr/local/go/bin/go version)" in *"go{self.go_version}"*) true;; *) exit 1;; esac \
  && test -x /opt/openhands-sdk-venv/bin/python
COPY go-module-bundle /opt/go-module-bundle
WORKDIR /workspace
""".encode(),
        )
        tests_root = task_root / "tests"
        tests_root.mkdir(parents=True, exist_ok=True)
        try:
            copy_python_verifier_runtime(tests_root / "runtime")
        except TaskWriterError as exc:
            raise GoHarborCompileError(str(exc)) from exc
        if not self.requirements_path.is_file():
            raise GoHarborCompileError(
                f"verifier requirements lock is missing: {self.requirements_path}"
            )
        atomic_write(
            tests_root / "verifier-requirements.lock.txt",
            self.requirements_path.read_bytes(),
        )
        atomic_write(
            tests_root / "Dockerfile",
            f"""FROM --platform=linux/amd64 {self.base_image}

RUN apt-get update \\
  && apt-get install -y --no-install-recommends python3 python3-pip \\
  && rm -rf /var/lib/apt/lists/*
COPY runtime /opt/nl2repobench-runtime
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN python3 -m pip install --break-system-packages --no-cache-dir --require-hashes \\
  -r /tmp/verifier-requirements.lock.txt
COPY --chmod=0500 private /tests/private
COPY dependencies /opt/go-module-bundle
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \\
  && chmod -R 0555 /opt/nl2repobench-runtime
WORKDIR /tests
""".encode(),
        )
        atomic_write(tests_root / "test.sh", self._test_script().encode())
        atomic_write(
            tests_root / "docker-compose.yaml",
            b"services:\n  main:\n    network_mode: none\n",
        )
        os.chmod(tests_root / "test.sh", 0o755)

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
                dependencies = fixture / "dependencies"
                if not dependencies.is_dir():
                    raise GoHarborCompileError(
                        "Go task is missing a frozen dependencies closure"
                    )
                copy_tree(dependencies, destination)
            else:
                reference = source.dependencies.module_bundle
                if reference is None:
                    raise GoHarborCompileError(
                        "Go production task requires dependencies.module_bundle"
                    )
                self._extract_private_bundle(reference, destination)
            copy_tree(destination, task_root / "environment/go-module-bundle")
            GoModulesPackageManager().validate_offline_store(
                destination,
                lockfile=destination / "go.mod",
                manifest=destination / "module.manifest.json",
                expected_version=self.go_version,
            )
        except (TaskWriterError, PackageManagerError) as exc:
            raise GoHarborCompileError(f"invalid Go module closure: {exc}") from exc

    def _write_verifier(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        private_root = task_root / "tests/private"
        if allow_incomplete:
            copy_tree(fixture / "tests", private_root)
            entrypoint = "contract.sh"
        else:
            verifier = source.verifier
            if verifier is None:
                raise GoHarborCompileError("Go production task requires [verifier]")
            if verifier.entrypoint != "contract.sh":
                raise GoHarborCompileError(
                    "the first Go verifier profile requires entrypoint=contract.sh"
                )
            self._extract_private_bundle(verifier.bundle, private_root)
            entrypoint = verifier.entrypoint
            bridge = fixture / "tests/bridge.go"
            if bridge.is_symlink() or not bridge.is_file():
                raise GoHarborCompileError("Go task requires a reviewed public bridge.go")
            atomic_write(private_root / "bridge.go", bridge.read_bytes())
        contract = private_root / entrypoint
        bridge = private_root / "bridge.go"
        if contract.is_symlink() or not contract.is_file():
            raise GoHarborCompileError("Go verifier bundle must contain contract.sh")
        if bridge.is_symlink() or not bridge.is_file():
            raise GoHarborCompileError("Go verifier is missing bridge.go")

    def _write_solution(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        solution_root = task_root / "solution"
        if allow_incomplete:
            copy_tree(fixture / "solution", solution_root)
        else:
            if source.oracle_bundle is None:
                raise GoHarborCompileError("Go production task requires oracle_bundle")
            self._extract_private_bundle(source.oracle_bundle, solution_root)
        solve = solution_root / "solve.sh"
        if solve.is_symlink() or not solve.is_file():
            raise GoHarborCompileError("Go Oracle bundle must contain solve.sh")
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
            "schema_version": "1.4",
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
                "language": "go",
                "runtime": "go",
                "runtime_version": self.go_version,
                "package_manager": "go-modules",
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

    def _extract_private_bundle(self, reference: ArtifactRef, destination: Path) -> None:
        try:
            extract_private_bundle(
                reference,
                destination,
                artifact_resolver=self.artifact_resolver,
                limits=BundleLimits(
                    max_members=10_000,
                    max_member_bytes=512 * 1024 * 1024,
                    max_total_bytes=2 * 1024 * 1024 * 1024,
                ),
            )
        except TaskWriterError as exc:
            raise GoHarborCompileError(str(exc)) from exc

    def _toolchain_digest(self) -> str:
        return f"sha256:{hashlib.sha256(self.toolchain_path.read_bytes()).hexdigest()}"

    @staticmethod
    def _read_bundle_payload(path: Path) -> dict[str, object]:
        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise GoHarborCompileError(f"invalid Go bundle manifest: {exc}") from exc
        if not isinstance(payload, dict):
            raise GoHarborCompileError("invalid Go bundle manifest object")
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
                f"- Mode: {mode}\n- Go: `{self.go_version}`\n"
                "- Package manager: `go-modules`\n"
                "- Candidate execution: typed subprocess bridge, no network\n"
            ).encode(),
        )

    def _test_script(self) -> str:
        return """#!/usr/bin/env bash
set -uo pipefail
PYTHON_ROOT='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime")'
NETWORK_CHECK='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime");'
NETWORK_CHECK+='from nl2repobench.verification.network_check import main; main()'
grade() {
  python3 -I -c "$PYTHON_ROOT; from nl2repobench.verification.cli import main; main()" \
    --runtime go --expected 1 --metric-contract fixed-test-pass-rate-v1 --output /logs/verifier "$@"
}
mkdir -p /logs/verifier
if ! python3 -I -c "$NETWORK_CHECK" \
  --output /logs/verifier/network.json; then
  grade --reason verifier-network-available
  exit 0
fi
COPY_WORKSPACE='from nl2repobench.verification.workspace_copy import main; main()'
if ! python3 -I -c "$PYTHON_ROOT; $COPY_WORKSPACE" \
  --source /workspace --destination /tmp/go-candidate; then
  grade --reason candidate-workspace-rejected
  exit 0
fi
chown -R candidate:candidate /tmp/go-candidate
rm -rf /tmp/go-candidate/vendor
cp -a /opt/go-module-bundle/vendor /tmp/go-candidate/vendor
chown -R candidate:candidate /tmp/go-candidate/vendor
GO_VALIDATE=$(cat <<'PY'
from pathlib import Path
from nl2repobench.package_managers.go_modules import GoModulesPackageManager
GoModulesPackageManager().validate_lock(
    Path("/tmp/go-candidate/go.mod"), expected_version="__GO_VERSION__"
)
PY
)
if ! runuser -u candidate -- python3 -I -c "$PYTHON_ROOT; $GO_VALIDATE"; then
  grade --reason candidate-installation-failed
  exit 0
fi
install -m 0444 /tests/private/bridge.go /tmp/go-candidate/bridge.go
mkdir -p /tmp/go-candidate/cmd/bridge
mv /tmp/go-candidate/bridge.go /tmp/go-candidate/cmd/bridge/main.go
if ! runuser -u candidate -- sh -c 'cd /tmp/go-candidate && \\
  env PATH=/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin \\
  GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \\
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \\
  /usr/local/go/bin/go build -mod=vendor -o /tmp/go-candidate/bridge ./cmd/bridge'; then
  grade --reason candidate-installation-failed
  exit 0
fi
RUN_CONTRACT='from nl2repobench.verification.go_contract_runner import main;'
RUN_CONTRACT+='raise SystemExit(main())'
if ! /usr/bin/python3 -I -c "$PYTHON_ROOT; $RUN_CONTRACT" \\
  --script /tests/private/contract.sh --bridge /tmp/go-candidate/bridge \\
  --proxy /opt/nl2repobench-runtime/nl2repobench/verification/go_bridge_proxy.py \\
  > /logs/verifier/result.json; then
  cat > /tmp/go-report.json <<'JSON'
{"schema_version":"1.0","framework":"go","report_format":"go-test-json-v1","collected":1,"tests":[{"test_id":"contract::public-api","status":"failed","duration_ms":0,"details":"candidate-call-failed"}],"collection_errors":[],"runner_exit_code":1}
JSON
  grade --report /tmp/go-report.json --runner-exit-code 1
  exit 0
fi
cat > /tmp/go-report.json <<'JSON'
{"schema_version":"1.0","framework":"go","report_format":"go-test-json-v1","collected":1,"tests":[{"test_id":"contract::public-api","status":"passed","duration_ms":0}],"collection_errors":[],"runner_exit_code":0}
JSON
grade --report /tmp/go-report.json --runner-exit-code 0
exit 0
""".replace("__GO_VERSION__", self.go_version)


__all__ = ["GoHarborCompileError", "GoHarborCompiler"]

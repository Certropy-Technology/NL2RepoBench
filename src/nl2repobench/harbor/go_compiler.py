"""Go Harbor compiler entry point for the unified runtime registry."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler, DeclarativeTaskSource
from nl2repobench.package_managers.base import PackageManagerError
from nl2repobench.package_managers.go_modules import GoModulesPackageManager
from nl2repobench.storage.artifacts import LocalArtifactResolver
from nl2repobench.storage.files import atomic_write

from .task_writer import (
    TaskWriterError,
    copy_python_verifier_runtime,
    copy_tree,
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
        if allow_incomplete and self.status != "development-only":
            raise GoHarborCompileError(
                "allow_incomplete is only valid for the development Go toolchain"
            )
        if not allow_incomplete and self.status != "locked":
            raise GoHarborCompileError("Go production output requires toolchain.go.lock.toml")
        if not allow_incomplete and source.lifecycle.status.value not in {
            "oracle-passed",
            "controls-passed",
            "reviewed",
            "piloted",
            "published",
        }:
            raise GoHarborCompileError("Go production output requires a completed source lifecycle")
        if source.tests.expected_total != 1:
            raise GoHarborCompileError(
                "the first Go bridge profile supports exactly one verifier-owned leaf"
            )
        if not allow_incomplete:
            raise GoHarborCompileError(
                "Go production output requires private module, verifier, and Oracle "
                "artifact materialization; the development fixture cannot be published"
            )
        fixture = source_dir / "harbor"
        for relative in ("tests/bridge.go", "tests/contract.sh", "solution/solve.sh"):
            if not (fixture / relative).is_file():
                raise GoHarborCompileError(f"Go synthetic profile is missing harbor/{relative}")
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
            self._write_dependencies(fixture, temporary)
            copy_tree(fixture / "tests", temporary / "tests/private")
            copy_tree(fixture / "solution", temporary / "solution")
            self._write_task_toml(source, temporary)
            self._write_readme(source, temporary, allow_incomplete)
            write_file_manifest(
                temporary,
                payload={
                    "task_id": source.task_id,
                    "task_version": source.version,
                    "mode": "development" if allow_incomplete else "production",
                    "toolchain_version": self.go_version,
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
        """Fail closed until Go controls have catalog-owned solution scripts."""

        raise GoHarborCompileError(f"unsupported Go control kind: {kind}")

    def _write_environment(self, task_root: Path) -> None:
        atomic_write(
            task_root / "environment/Dockerfile",
            (
                f"FROM --platform=linux/amd64 {self.base_image}\n\n"
                "COPY go-module-bundle /opt/go-module-bundle\n"
                "WORKDIR /workspace\n"
            ).encode(),
        )
        tests_root = task_root / "tests"
        tests_root.mkdir(parents=True, exist_ok=True)
        try:
            copy_python_verifier_runtime(tests_root / "python-runtime")
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
COPY python-runtime /opt/nl2repobench-runtime
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

    def _write_dependencies(self, fixture: Path, task_root: Path) -> None:
        dependencies = fixture / "dependencies"
        if not dependencies.is_dir():
            raise GoHarborCompileError("Go task is missing a frozen dependencies closure")
        destination = task_root / "tests/dependencies"
        try:
            copy_tree(dependencies, destination)
            copy_tree(dependencies, task_root / "environment/go-module-bundle")
            GoModulesPackageManager().validate_offline_store(
                destination,
                lockfile=destination / "go.mod",
                manifest=destination / "module.manifest.json",
                expected_version=self.go_version,
            )
        except (TaskWriterError, PackageManagerError) as exc:
            raise GoHarborCompileError(f"invalid Go module closure: {exc}") from exc

    def _write_task_toml(self, source: DeclarativeTaskSource, task_root: Path) -> None:
        profile = source.harbor
        assert profile is not None
        data: dict[str, Any] = {
            "schema_version": "1.4",
            "artifacts": [profile.workspace_artifact],
            "task": {
                "name": f"nl2repobench/{source.task_id}",
                "version": source.version,
                "description": profile.description,
                "authors": [{"name": "NL2RepoBench"}],
                "keywords": list(profile.keywords),
            },
            "metadata": {
                "difficulty": source.metadata.difficulty,
                "category": source.metadata.category,
                "tags": list(source.metadata.tags),
                "language": "go",
                "runtime": "go",
                "runtime_version": self.go_version,
                "package_manager": "go-modules",
                "metric_contract": "fixed-test-pass-rate-v1",
                "expected_test_count": source.tests.expected_total,
            },
            "agent": {"timeout_sec": profile.agent_timeout_sec},
            "verifier": {
                "timeout_sec": profile.verifier_timeout_sec,
                "environment_mode": "separate",
                "network_mode": "no-network",
            },
            "environment": {
                "network_mode": "no-network",
                "cpus": profile.cpus,
                "memory_mb": profile.memory_mb,
                "storage_mb": profile.storage_mb,
            },
        }
        atomic_write(task_root / "task.toml", tomli_w.dumps(data).encode())

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
  grade --reason candidate-call-failed
  exit 0
fi
cat > /tmp/go-report.json <<'JSON'
{"schema_version":"1.0","framework":"go","report_format":"go-test-json-v1","collected":1,"tests":[{"test_id":"contract::public-api","status":"passed","duration_ms":0}],"collection_errors":[],"runner_exit_code":0}
JSON
grade --report /tmp/go-report.json --runner-exit-code 0
exit 0
""".replace("__GO_VERSION__", self.go_version)


__all__ = ["GoHarborCompileError", "GoHarborCompiler"]

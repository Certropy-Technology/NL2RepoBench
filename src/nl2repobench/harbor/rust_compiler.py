"""Rust/Cargo Harbor compiler with a separate trusted bridge verifier."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler, DeclarativeTaskSource
from nl2repobench.domain.models import TaskManifest
from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.package_managers.cargo import CargoPackageManager
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.files import atomic_write

from .bundle_io import BundleLimits
from .rust_toolchain import RustToolchainLock, load_rust_toolchain_lock
from .task_writer import (
    TaskWriterError,
    copy_python_verifier_runtime,
    copy_tree,
    extract_private_bundle,
    write_file_manifest,
    write_instruction,
)


class RustHarborCompileError(ValueError):
    """Raised when a Rust source cannot satisfy the R0 compiler contract."""


class RustHarborCompiler:
    """Project Cargo sources into separate-verifier Harbor bundles."""

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        self.toolchain_path = toolchain_path
        self.artifact_resolver = artifact_resolver
        try:
            self.toolchain = load_rust_toolchain_lock(toolchain_path)
        except ValueError as exc:
            raise RustHarborCompileError(str(exc)) from exc

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        if not isinstance(source, DeclarativeTaskSource):
            raise RustHarborCompileError("Rust R0 compiler requires schema_version=1.0")
        try:
            identity = RuntimeDiscriminator.from_catalog_source(
                source.model_dump(mode="python")
            )
        except ValueError as exc:
            raise RustHarborCompileError(str(exc)) from exc
        if identity != RuntimeDiscriminator(
            language=RuntimeLanguage.RUST,
            package_manager=PackageManager.CARGO,
        ):
            raise RustHarborCompileError(
                "Rust compiler requires language=rust and package_manager=cargo"
            )
        if source.harbor is None:
            raise RustHarborCompileError("Rust task source is missing [harbor] settings")
        if allow_incomplete and self.toolchain.status != "development-only":
            raise RustHarborCompileError(
                "Rust development compilation requires toolchain.rust.dev.lock.toml"
            )
        if not allow_incomplete and self.toolchain.status != "locked":
            raise RustHarborCompileError(
                "Rust production compilation requires toolchain.rust.lock.toml"
            )

        with tempfile.TemporaryDirectory(prefix="nl2repo-rust-canonical-") as canonical:
            compiled = CatalogCompiler(
                FileArtifactStore(Path(canonical) / "artifacts")
            ).compile_task(source_dir, Path(canonical) / "manifest")
            manifest = compiled.manifest
        if not isinstance(manifest, TaskManifest):
            raise RustHarborCompileError("Rust source did not produce a v1 manifest")

        if not allow_incomplete:
            gaps = manifest.publication_gaps()
            if gaps:
                raise RustHarborCompileError(
                    "Rust production source is incomplete: " + ", ".join(gaps)
                )
        fixture = source_dir / "harbor"
        if allow_incomplete:
            for relative in ("dependencies", "tests", "solution"):
                if not (fixture / relative).is_dir():
                    raise RustHarborCompileError(
                        f"Rust development fixture is missing harbor/{relative}"
                    )
        final_root = output_root / source.task_id
        if final_root.exists() or final_root.is_symlink():
            raise RustHarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{source.task_id}-", dir=output_root))
        try:
            write_instruction(source_dir, source.instruction, temporary)
            self._write_dependencies(source, fixture, temporary, allow_incomplete)
            self._write_environment(temporary, allow_incomplete)
            self._write_verifier(source, fixture, temporary, allow_incomplete)
            self._write_solution(source, fixture, temporary, allow_incomplete)
            self._write_controls(fixture, temporary)
            self._write_task_toml(manifest, temporary, allow_incomplete)
            self._write_readme(source, temporary, allow_incomplete)
            write_file_manifest(
                temporary,
                payload={
                    "task_id": source.task_id,
                    "task_version": source.version,
                    "mode": "development" if allow_incomplete else "production",
                    "language": "rust",
                    "package_manager": "cargo",
                    "toolchain_version": self.toolchain.rust_version,
                    "canonical_manifest_digest": manifest.content_digest(),
                    "toolchain_lock_digest": self._toolchain_digest(),
                },
                schema_version="1.0",
            )
            os.rename(temporary, final_root)
        except (OSError, TaskWriterError, RustHarborCompileError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            if isinstance(exc, RustHarborCompileError):
                raise
            raise RustHarborCompileError(str(exc)) from exc
        return final_root

    def prepare_control_bundle(self, task_root: Path, kind: str, output_root: Path) -> Path:
        if kind not in {
            "stub",
            "forgery",
            "build-script-network",
            "build-script-timeout",
            "build-script-child-process",
            "build-script-oversized-output",
        }:
            raise RustHarborCompileError(f"unsupported Rust control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if script.is_symlink() or not script.is_file():
            raise RustHarborCompileError(f"Rust control script is missing: {script}")
        target = output_root / f"{task_root.name}-{kind}"
        if target.exists() or target.is_symlink():
            raise RustHarborCompileError(f"Rust control output already exists: {target}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}-", dir=output_root))
        try:
            copy_tree(task_root, temporary)
            atomic_write(temporary / "solution/solve.sh", script.read_bytes())
            os.chmod(temporary / "solution/solve.sh", 0o755)
            payload = self._read_bundle_payload(temporary / "bundle.manifest.json")
            payload["control_kind"] = kind
            write_file_manifest(temporary, payload=payload, schema_version="1.0")
            os.rename(temporary, target)
        except (OSError, TaskWriterError, RustHarborCompileError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            if isinstance(exc, RustHarborCompileError):
                raise
            raise RustHarborCompileError(str(exc)) from exc
        return target

    def _write_dependencies(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        destination = task_root / "environment/cargo-bundle"
        try:
            if allow_incomplete:
                copy_tree(fixture / "dependencies", destination)
            else:
                reference = source.dependencies.cargo_bundle
                if reference is None:
                    raise RustHarborCompileError(
                        "Rust production source requires dependencies.cargo_bundle"
                    )
                extract_private_bundle(
                    reference,
                    destination,
                    artifact_resolver=self.artifact_resolver,
                    limits=BundleLimits(
                        max_members=100_000,
                        max_member_bytes=512 * 1024 * 1024,
                        max_total_bytes=2 * 1024 * 1024 * 1024,
                    ),
                )
            copy_tree(destination, task_root / "tests/cargo-bundle")
            lockfile = destination / "Cargo.lock"
            manifest = destination / "cargo.manifest.json"
            CargoPackageManager().validate_offline_store(
                destination,
                lockfile=lockfile,
                manifest=manifest,
                expected_version=self.toolchain.rust_version,
            )
        except (TaskWriterError, ValueError) as exc:
            raise RustHarborCompileError(f"invalid Cargo offline fixture: {exc}") from exc

    def _write_environment(self, task_root: Path, allow_incomplete: bool) -> None:
        dependency_label = (
            "cargo-offline-development-v1"
            if allow_incomplete
            else "cargo-offline-locked-v1"
        )
        atomic_write(
            task_root / "environment/Dockerfile",
            f"""FROM --platform=linux/amd64 {self.toolchain.base_image} AS rust-runtime

FROM --platform=linux/amd64 {self.toolchain.agent_runtime_image}

LABEL org.nl2repobench.agent-runtime-image=\"{self.toolchain.agent_runtime_image}\" \\
  org.nl2repobench.agent-runtime-image-id=\"{self.toolchain.agent_runtime_image_id}\" \\
  org.nl2repobench.agent-dependency-build=\"{dependency_label}\"

RUN apt-get update \\
  && apt-get install -y --no-install-recommends build-essential \\
  && rm -rf /var/lib/apt/lists/*

COPY --from=rust-runtime /usr/local/cargo /usr/local/cargo
COPY --from=rust-runtime /usr/local/rustup /usr/local/rustup
ENV PATH=/usr/local/cargo/bin:$PATH \\
    CARGO_HOME=/opt/nl2repo-cargo \\
    RUSTUP_HOME=/usr/local/rustup \\
    CARGO_NET_OFFLINE=true \\
    CARGO_INCREMENTAL=0 \\
    CARGO_TERM_COLOR=never \\
    RUST_BACKTRACE=0
COPY cargo-bundle /opt/nl2repo-cargo
RUN printf '%s\\n' '[source.crates-io]' 'replace-with = "vendored-sources"' \\
  '[source.vendored-sources]' 'directory = "/opt/nl2repo-cargo/vendor"' \\
  > /opt/nl2repo-cargo/config.toml
RUN test -x /usr/local/cargo/bin/cargo \\
  && case \"$(/usr/local/cargo/bin/rustc --version)\" in \\
    *\"{self.toolchain.rust_version}\"*) true;; *) exit 1;; esac \\
  && test -x /opt/openhands-sdk-venv/bin/python
WORKDIR /workspace
""".encode(),
        )

    def _write_verifier(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        tests_root = task_root / "tests"
        copy_python_verifier_runtime(tests_root / "runtime")
        if allow_incomplete:
            copy_tree(fixture / "tests", tests_root / "private")
        else:
            if source.verifier is None:
                raise RustHarborCompileError("Rust production source requires [verifier]")
            verifier_root = tests_root / "verifier"
            extract_private_bundle(
                source.verifier.bundle,
                verifier_root,
                artifact_resolver=self.artifact_resolver,
                limits=BundleLimits(
                    max_members=10_000,
                    max_member_bytes=512 * 1024 * 1024,
                    max_total_bytes=2 * 1024 * 1024 * 1024,
                ),
            )
            entrypoint = verifier_root / source.verifier.entrypoint
            if entrypoint.is_symlink() or not entrypoint.is_file():
                raise RustHarborCompileError("Rust verifier entrypoint is missing")
            verifier_cargo_files = tests_root / "verifier"
            for relative in ("Cargo.toml", "Cargo.lock", "src/main.rs"):
                if not (verifier_cargo_files / relative).is_file():
                    raise RustHarborCompileError(
                        "Rust verifier bundle is missing bridge file: " + relative
                    )
        requirements_relative = (
            self.toolchain.verifier_requirements_lock or "verifier/requirements.lock.txt"
        )
        requirements_path = self.toolchain_path.parent / requirements_relative
        if requirements_path.is_symlink() or not requirements_path.is_file():
            raise RustHarborCompileError(
                f"Rust verifier requirements lock is missing: {requirements_path}"
            )
        requirements = requirements_path.read_bytes()
        if self.toolchain.verifier_requirements_sha256 is not None:
            actual = "sha256:" + hashlib.sha256(requirements).hexdigest()
            if actual != self.toolchain.verifier_requirements_sha256:
                raise RustHarborCompileError(
                    "Rust verifier requirements lock digest does not match toolchain"
                )
        atomic_write(tests_root / "requirements.lock.txt", requirements)
        atomic_write(tests_root / "test.sh", self._test_script(source, allow_incomplete).encode())
        os.chmod(tests_root / "test.sh", 0o755)
        verifier_copy = (
            "COPY --chmod=0500 private /tests/private"
            if allow_incomplete
            else "COPY --chmod=0500 verifier /tests/verifier"
        )
        atomic_write(
            tests_root / "Dockerfile",
            f"""FROM --platform=linux/amd64 {self.toolchain.base_image} AS rust-runtime
FROM --platform=linux/amd64 {self.toolchain.verifier_base}

RUN apt-get update \\
  && apt-get install -y --no-install-recommends build-essential \\
  && rm -rf /var/lib/apt/lists/*

COPY --from=rust-runtime /usr/local/cargo /usr/local/cargo
COPY --from=rust-runtime /usr/local/rustup /usr/local/rustup
ENV PATH=/usr/local/cargo/bin:$PATH \\
    CARGO_HOME=/opt/nl2repo-cargo \\
    RUSTUP_HOME=/usr/local/rustup \\
    CARGO_NET_OFFLINE=true \\
    CARGO_TERM_COLOR=never
COPY runtime/nl2repobench /usr/local/lib/python3.12/site-packages/nl2repobench
COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \\
  -r /tmp/requirements.lock.txt
{verifier_copy}
COPY --chmod=0555 test.sh /tests/test.sh
COPY cargo-bundle /opt/nl2repo-cargo
RUN printf '%s\\n' '[source.crates-io]' 'replace-with = "vendored-sources"' \\
  '[source.vendored-sources]' 'directory = "/opt/nl2repo-cargo/vendor"' \\
  > /opt/nl2repo-cargo/config.toml
RUN useradd --uid 10001 --create-home candidate \\
  && test -x /usr/local/cargo/bin/cargo
WORKDIR /tests
""".encode(),
        )
        atomic_write(
            tests_root / "docker-compose.yaml",
            b"services:\n  main:\n    network_mode: none\n",
        )

    def _test_script(self, source: DeclarativeTaskSource, allow_incomplete: bool) -> str:
        expected = source.tests.expected_total
        if allow_incomplete:
            return self._development_test_script(expected)
        return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
if ! python3 -I -m nl2repobench.verification.network_check \\
  --output /logs/verifier/network.json; then
  python3 -I -m nl2repobench.verification.cli --expected {expected} \\
    --runtime rust --runner-exit-code 2 --reason verifier-network-available
  exit 0
fi
rm -rf /tmp/candidate /tmp/candidate-build
python3 -I -B -m nl2repobench.verification.workspace_copy \\
  --source /workspace --destination /tmp/candidate
copy_exit=$?
if [ "$copy_exit" -ne 0 ]; then
  python3 -I -m nl2repobench.verification.cli --expected {expected} \\
    --runtime rust --runner-exit-code "$copy_exit" --reason candidate-workspace-rejected
  exit 0
fi
chown -R candidate:candidate /tmp/candidate
export NL2REPO_RUST_CANDIDATE=/tmp/candidate
python3 -I -m nl2repobench.verification.rust_runner \\
  --entrypoint /tests/verifier/run.py --expected {expected} \\
  --report /logs/verifier/rust-report.json --timeout-sec 300 \\
  > /logs/verifier/runner-stdout.txt 2> /logs/verifier/runner-stderr.txt
runner_exit=$?
if [ "$runner_exit" -ne 0 ] && [ "$runner_exit" -ne 1 ]; then
  python3 -I -m nl2repobench.verification.cli --expected {expected} \\
    --runtime rust --runner-exit-code "$runner_exit" --reason verifier-internal-error
else
  python3 -I -m nl2repobench.verification.cli --expected {expected} \\
    --runtime rust --report /logs/verifier/rust-report.json \\
    --runner-exit-code "$runner_exit"
fi
exit 0
"""

    @staticmethod
    def _development_test_script(expected: int) -> str:
        return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
set +e
/usr/local/cargo/bin/cargo test --locked --offline --manifest-path /workspace/Cargo.toml \\
  > /logs/verifier/cargo-stdout.txt 2> /logs/verifier/cargo-stderr.txt
exit_code=$?
set -e
python3 -I -m nl2repobench.verification.cli --expected {expected} \\
  --runtime rust --runner-exit-code "$exit_code"
exit 0
"""

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
                raise RustHarborCompileError("Rust production source requires oracle_bundle")
            extract_private_bundle(
                source.oracle_bundle,
                solution_root,
                artifact_resolver=self.artifact_resolver,
                limits=BundleLimits(
                    max_members=10_000,
                    max_member_bytes=512 * 1024 * 1024,
                    max_total_bytes=2 * 1024 * 1024 * 1024,
                ),
            )
        solve = solution_root / "solve.sh"
        if solve.is_symlink() or not solve.is_file():
            raise RustHarborCompileError("Rust Oracle bundle must contain solve.sh")
        os.chmod(solve, 0o755)

    @staticmethod
    def _write_controls(fixture: Path, task_root: Path) -> None:
        controls = fixture / "controls"
        if controls.is_dir():
            copy_tree(controls, task_root / "controls")

    def _write_task_toml(
        self, manifest: TaskManifest, task_root: Path, allow_incomplete: bool
    ) -> None:
        assert manifest.harbor is not None
        data: dict[str, Any] = {
            "schema_version": "1.4",
            "artifacts": [manifest.harbor.workspace_artifact],
            "task": {
                "name": f"nl2repobench/{manifest.task_id}",
                "version": manifest.version,
                "description": manifest.harbor.description,
                "authors": [{"name": "NL2RepoBench"}],
                "keywords": list(manifest.harbor.keywords),
            },
            "metadata": {
                "difficulty": manifest.metadata.difficulty,
                "category": manifest.metadata.category,
                "tags": list(manifest.metadata.tags),
                "language": "rust",
                "runtime": "rust",
                "runtime_version": self.toolchain.rust_version,
                "package_manager": "cargo",
                "package_manager_version": self.toolchain.rust_version,
                "metric_contract": manifest.metric.contract_id,
                "expected_test_count": manifest.tests.expected_total,
                "canonical_manifest_digest": manifest.content_digest(),
                "toolchain_lock_digest": self._toolchain_digest(),
            },
            "agent": {"timeout_sec": manifest.harbor.agent_timeout_sec},
            "verifier": {
                "timeout_sec": manifest.harbor.verifier_timeout_sec,
                "environment_mode": "separate",
                "network_mode": "no-network",
            },
            "environment": {
                "network_mode": "no-network",
                "cpus": manifest.harbor.cpus,
                "memory_mb": manifest.harbor.memory_mb,
                "storage_mb": manifest.harbor.storage_mb,
            },
        }
        if allow_incomplete:
            data["metadata"]["r0_status"] = "development-only"
        atomic_write(task_root / "task.toml", tomli_w.dumps(data).encode())

    def _write_readme(
        self, source: DeclarativeTaskSource, task_root: Path, allow_incomplete: bool
    ) -> None:
        mode = "development-only" if allow_incomplete else "production"
        atomic_write(
            task_root / "README.md",
            (
                f"# `{source.task_id}` Rust/Cargo bundle\n\n"
                f"Mode: {mode}. Candidate calls run through a separate trusted Rust bridge.\n"
            ).encode(),
        )

    def _toolchain_digest(self) -> str:
        return f"sha256:{hashlib.sha256(self.toolchain_path.read_bytes()).hexdigest()}"

    @staticmethod
    def _read_bundle_payload(path: Path) -> dict[str, object]:
        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise RustHarborCompileError(f"invalid Rust bundle manifest: {exc}") from exc
        if not isinstance(payload, dict):
            raise RustHarborCompileError("Rust bundle manifest must be an object")
        payload.pop("schema_version", None)
        payload.pop("files", None)
        return payload


__all__ = ["RustHarborCompileError", "RustHarborCompiler", "RustToolchainLock"]

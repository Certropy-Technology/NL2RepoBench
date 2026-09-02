"""Development-only Rust/Cargo Harbor compiler for the R0 integration slice."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.harbor.task_writer import (
    TaskWriterError,
    copy_tree,
    write_file_manifest,
    write_instruction,
)
from nl2repobench.package_managers.cargo import CargoPackageManager
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.verification.rust_bridge import (
    canonical_api_plan_bytes,
    load_rust_api_plan,
)
from nl2repobench.verification.rust_profile import (
    canonical_rust_profile_bytes,
    load_rust_profile,
    rust_profile_projection_digest,
    validate_rust_profile_api_plan,
)

from .rust_toolchain import load_rust_toolchain_lock


class RustHarborCompileError(ValueError):
    """Raised when a Rust R0 development bundle cannot be generated."""


class RustHarborCompiler:
    """Render a bounded synthetic Rust bundle without claiming production readiness."""

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        del artifact_resolver
        try:
            self.toolchain = load_rust_toolchain_lock(toolchain_path)
        except ValueError as exc:
            raise RustHarborCompileError(str(exc)) from exc
        self.toolchain_path = toolchain_path
        self.toolchain_version = getattr(self.toolchain, "rustc_version", "1.100.0-nightly")

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        runtime = source.environment.runtime
        if runtime is None or runtime.language is not RuntimeLanguage.RUST:
            raise RustHarborCompileError("Rust compiler requires a canonical Rust runtime")
        if runtime.package_manager is not PackageManager.CARGO:
            raise RustHarborCompileError("Rust compiler requires package_manager=cargo")
        if source.harbor is None:
            raise RustHarborCompileError("Rust task source is missing [harbor] settings")
        if not allow_incomplete:
            raise RustHarborCompileError(
                "Rust R0 compiler is development-only until locked toolchain, private closure, "
                "Oracle, and controls evidence exist"
            )
        if self.toolchain.status not in {"provisional-unlocked", "locked"}:
            raise RustHarborCompileError(
                "Rust development compilation requires toolchain.rust.dev.lock.toml"
            )

        profile = None
        plan = None
        profile_path = source_dir / "rust-profile.toml"
        api_plan_path = source_dir / "rust-api-plan.json"
        if profile_path.is_file() or api_plan_path.is_file():
            if not profile_path.is_file() or not api_plan_path.is_file():
                raise RustHarborCompileError(
                    "Rust development source requires both rust-profile.toml and rust-api-plan.json"
                )
            try:
                profile = load_rust_profile(profile_path)
                plan, exact_plan_bytes = load_rust_api_plan(api_plan_path)
                validate_rust_profile_api_plan(profile, plan, exact_plan_bytes)
            except ValueError as exc:
                raise RustHarborCompileError(str(exc)) from exc

        try:
            with tempfile.TemporaryDirectory(
                prefix="nl2repo-rust-canonical-"
            ) as canonical_temp:
                with tempfile.TemporaryDirectory(
                    prefix="nl2repo-rust-artifacts-"
                ) as artifacts_temp:
                    compiled = CatalogCompiler(
                        FileArtifactStore(Path(artifacts_temp))
                    ).compile_task(
                        source_dir, Path(canonical_temp)
                    )
                    manifest = compiled.manifest
        except (OSError, ValueError) as exc:
            raise RustHarborCompileError(f"cannot compile canonical Rust source: {exc}") from exc

        final_root = output_root / source.task_id
        if final_root.exists() or final_root.is_symlink():
            raise RustHarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{source.task_id}-", dir=output_root))
        try:
            write_instruction(source_dir, source.instruction, temporary)
            self._write_environment(temporary)
            fixture = source_dir / "harbor"
            for relative, destination in (
                ("tests", "tests/private"),
                ("solution", "solution"),
                ("controls", "controls"),
            ):
                candidate = fixture / relative
                if candidate.is_dir():
                    copy_tree(candidate, temporary / destination)
            if profile is not None and plan is not None:
                (temporary / "rust-profile.json").write_bytes(canonical_rust_profile_bytes(profile))
                (temporary / "rust-api-plan.json").write_bytes(canonical_api_plan_bytes(plan))
                profile_digest = rust_profile_projection_digest(profile)
            else:
                profile_digest = None
            dependencies = fixture / "dependencies"
            if dependencies.is_dir():
                copy_tree(dependencies, temporary / "environment/cargo-bundle")
                lock_root = temporary / "environment/cargo-bundle"
                try:
                    CargoPackageManager().validate_lock(lock_root, self.toolchain_version)
                except Exception as exc:
                    raise RustHarborCompileError(f"invalid Rust Cargo fixture lock: {exc}") from exc
            task_data: dict[str, Any] = {
                "schema_version": "1.4",
                "artifacts": [source.harbor.workspace_artifact],
                "task": {
                    "name": f"nl2repobench/{source.task_id}",
                    "version": source.version,
                    "description": source.harbor.description,
                    "authors": [{"name": "NL2RepoBench"}],
                    "keywords": list(source.harbor.keywords),
                },
                "metadata": {
                    "difficulty": source.metadata.difficulty,
                    "category": source.metadata.category,
                    "tags": list(source.metadata.tags),
                    "language": "rust",
                    "runtime": "rust",
                    "runtime_version": self.toolchain_version,
                    "package_manager": "cargo",
                    "package_manager_version": self.toolchain_version,
                    "metric_contract": "fixed-test-pass-rate-v1",
                    "expected_test_count": source.tests.expected_total,
                    "r0_status": "development-only",
                    "toolchain_lock_digest": self._toolchain_digest(),
                },
                "agent": {"timeout_sec": source.harbor.agent_timeout_sec},
                "verifier": {
                    "timeout_sec": source.harbor.verifier_timeout_sec,
                    "environment_mode": "separate",
                    "network_mode": "no-network",
                },
                "environment": {
                    "network_mode": "no-network",
                    "cpus": source.harbor.cpus,
                    "memory_mb": source.harbor.memory_mb,
                    "storage_mb": source.harbor.storage_mb,
                },
            }
            if profile_digest is not None:
                task_data["metadata"]["rust_profile_digest"] = profile_digest
            (temporary / "task.toml").write_bytes(tomli_w.dumps(task_data).encode())
            (temporary / "README.md").write_text(
                f"# `{source.task_id}` Rust R0 development bundle\n\n"
                "This bundle is preparatory only; no production or Oracle claim is made.\n",
                encoding="utf-8",
            )
            write_file_manifest(
                temporary,
                payload={
                    "task_id": source.task_id,
                    "task_version": source.version,
                    "mode": "development",
                    "toolchain_version": self.toolchain_version,
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
        if kind not in {"stub", "forgery"}:
            raise RustHarborCompileError(f"unsupported Rust R0 control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if script.is_symlink() or not script.is_file():
            raise RustHarborCompileError(f"Rust control script is missing: {script}")
        target = output_root / f"{task_root.name}-{kind}"
        if target.exists() or target.is_symlink():
            raise RustHarborCompileError(f"control output already exists: {target}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}-", dir=output_root))
        try:
            copy_tree(task_root, temporary)
            solution = temporary / "solution/solve.sh"
            solution.parent.mkdir(parents=True, exist_ok=True)
            solution.write_bytes(script.read_bytes())
            solution.chmod(0o755)
            os.rename(temporary, target)
        except (OSError, TaskWriterError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            raise RustHarborCompileError(str(exc)) from exc
        return target

    def _write_environment(self, task_root: Path) -> None:
        environment = task_root / "environment"
        environment.mkdir(parents=True, exist_ok=True)
        image = self.toolchain.expected_debian_base
        (environment / "Dockerfile").write_text(
            f"FROM --platform=linux/amd64 {image}\n"
            "# R0 development projection: Rust binaries are supplied only by a future "
            "locked image.\n"
            "ENV CARGO_NET_OFFLINE=true CARGO_INCREMENTAL=0 CARGO_TERM_COLOR=never\n"
            "WORKDIR /workspace\n",
            encoding="utf-8",
        )

    def _toolchain_digest(self) -> str:
        return f"sha256:{hashlib.sha256(self.toolchain_path.read_bytes()).hexdigest()}"


__all__ = ["RustHarborCompileError", "RustHarborCompiler"]

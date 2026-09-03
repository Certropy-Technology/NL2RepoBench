"""Shared deterministic Harbor task-tree operations.

Runtime compilers own their Dockerfiles, command plans, and test scripts. This
module owns only bounded tree copying, instruction materialization, private
bundle extraction, and content-addressed file manifests.
"""

from __future__ import annotations

import hashlib
import json
import tarfile
from collections.abc import Mapping
from pathlib import Path

from nl2repobench.domain.models import ArtifactRef
from nl2repobench.storage.artifacts import LocalArtifactResolver
from nl2repobench.storage.files import atomic_write

from .bundle_io import (
    BundleArchiveError,
    BundleArchiveIOError,
    BundleArchiveMemberSizeError,
    BundleLimits,
    BundleTreeError,
    BundleTreeSourceError,
    copy_bundle_tree,
    extract_bundle_archive,
)


class TaskWriterError(ValueError):
    """A shared task-tree operation could not be completed safely."""


def write_instruction(source_dir: Path, relative: str, task_root: Path) -> None:
    """Copy a public instruction only when it is a regular in-tree file."""

    source = source_dir / relative
    if (
        source.is_symlink()
        or not source.is_file()
        or not source.resolve().is_relative_to(source_dir.resolve())
    ):
        raise TaskWriterError("instruction must be a regular in-tree file")
    atomic_write(task_root / "instruction.md", source.read_bytes())


def copy_tree(source: Path, destination: Path) -> None:
    """Copy a bounded regular tree while rejecting links and special files."""

    try:
        copy_bundle_tree(source, destination)
    except BundleTreeSourceError as exc:
        raise TaskWriterError(f"fixture directory is missing: {source}") from exc
    except BundleTreeError as exc:
        raise TaskWriterError(str(exc)) from exc


def extract_private_bundle(
    reference: ArtifactRef,
    destination: Path,
    *,
    artifact_resolver: LocalArtifactResolver | None,
    limits: BundleLimits,
) -> None:
    """Extract a private artifact through the shared bounded bundle policy."""

    if artifact_resolver is None:
        raise TaskWriterError("private artifact resolver is required")
    try:
        archive = artifact_resolver.resolve(reference)
        extract_bundle_archive(archive, destination, limits=limits)
    except BundleArchiveMemberSizeError as exc:
        raise TaskWriterError(f"archive member exceeds limit: {exc.member_name}") from exc
    except BundleArchiveIOError as exc:
        raise TaskWriterError(f"cannot extract private bundle: {exc}") from exc
    except BundleArchiveError as exc:
        raise TaskWriterError(str(exc)) from exc
    except (OSError, RuntimeError, tarfile.TarError) as exc:
        raise TaskWriterError(f"cannot extract private bundle: {exc}") from exc


def write_file_manifest(
    task_root: Path,
    *,
    payload: Mapping[str, object],
    schema_version: str,
) -> None:
    """Write a deterministic manifest for every regular generated file."""

    files: list[dict[str, object]] = []
    for path in sorted(item for item in task_root.rglob("*") if item.is_file()):
        if path == task_root / "bundle.manifest.json":
            continue
        data = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(task_root).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )
    manifest = {"schema_version": schema_version, **dict(payload), "files": files}
    atomic_write(
        task_root / "bundle.manifest.json",
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n",
    )


__all__ = [
    "TaskWriterError",
    "copy_tree",
    "extract_private_bundle",
    "write_file_manifest",
    "write_instruction",
]


_PYTHON_VERIFIER_FILES = (
    "__init__.py",
    "domain/__init__.py",
    "domain/canonical.py",
    "domain/models.py",
    "domain/models_v2.py",
    "domain/network_policy.py",
    "domain/runtime.py",
    "package_managers/__init__.py",
    "package_managers/base.py",
    "package_managers/go_modules.py",
    "package_managers/maven.py",
    "verification/__init__.py",
    "verification/cli.py",
    "verification/candidate_client.py",
    "verification/candidate_install.py",
    "verification/candidate_runner.py",
    "verification/command_plan.py",
    "verification/custom_verifier.py",
    "verification/evaluator.py",
    "verification/go_grader.py",
    "verification/go_bridge_proxy.py",
    "verification/go_contract_runner.py",
    "verification/java_candidate.py",
    "verification/java_bridge.py",
    "verification/java_grader.py",
    "verification/java_process.py",
    "verification/go_supervisor.py",
    "verification/grader.py",
    "verification/integrity.py",
    "verification/junit.py",
    "verification/leaf_report.py",
    "verification/metric_contract.py",
    "verification/models.py",
    "verification/network_check.py",
    "verification/node_grader.py",
    "verification/node_models.py",
    "verification/process_cleanup.py",
    "verification/pytest_plugin.py",
    "verification/registry.py",
    "verification/run_pytest.py",
    "verification/taxonomy.py",
    "verification/workspace_copy.py",
    "verification/normalize/__init__.py",
    "verification/normalize/go_json.py",
    "verification/normalize/junit_open_test_report.py",
    "verification/normalize/node_test_json.py",
    "verification/normalize/pytest_junit.py",
)


def copy_python_verifier_runtime(destination: Path) -> None:
    """Copy the complete trusted Python normalization/evaluation runtime."""

    package_root = Path(__file__).parents[1]
    for relative in _PYTHON_VERIFIER_FILES:
        source = package_root / relative
        if not source.is_file():
            raise TaskWriterError(f"canonical verifier runtime file is missing: {relative}")
        target = destination / "nl2repobench" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(target, source.read_bytes())


__all__.append("copy_python_verifier_runtime")

"""Shared deterministic Harbor task-tree operations.

Runtime compilers own their Dockerfiles, command plans, and test scripts. This
module owns only bounded tree copying, instruction materialization, private
bundle extraction, and content-addressed file manifests.
"""

from __future__ import annotations

import hashlib
import json
import stat
from collections.abc import Mapping
from pathlib import Path

from nl2repobench.domain.canonical_models import ArtifactRef
from nl2repobench.storage.artifacts import (
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.files import atomic_write
from nl2repobench.storage.materialize import (
    ArchiveKind,
    MaterializationLimits,
    materialize_archive,
)

from .bundle_io import BundleLimits, BundleTreeError, BundleTreeSourceError, copy_bundle_tree


class TaskWriterError(ValueError):
    """A shared task-tree operation could not be completed safely."""


RUNTIME_DIGEST_ALGORITHM = "sha256:path-nul-raw-file-sha256-v1"


def canonical_runtime_digest(root: Path, relative_paths: tuple[str, ...]) -> str:
    """Hash a closed regular-file tree using the runtime's canonical encoding."""

    digest = hashlib.sha256()
    for relative in sorted(relative_paths, key=lambda value: value.encode("utf-8")):
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or str(path) in {"", "."}:
            raise TaskWriterError(f"runtime path is unsafe: {relative}")
        source = root / path
        try:
            metadata = source.lstat()
        except OSError as exc:
            raise TaskWriterError(f"runtime file is missing: {relative}") from exc
        if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            raise TaskWriterError(f"runtime file must be a regular non-link: {relative}")
        if metadata.st_nlink != 1:
            raise TaskWriterError(f"runtime hardlink is forbidden: {relative}")
        data = source.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
    return f"sha256:{digest.hexdigest()}"


def python_runtime_manifest(
    root: Path,
    *,
    runtime_root: str = "/usr/local/lib/python/site-packages/nl2repobench",
) -> dict[str, object]:
    """Return the closed manifest for the exact shared Python verifier tree."""

    entries: list[dict[str, object]] = []
    for relative in sorted(_PYTHON_VERIFIER_FILES, key=lambda value: value.encode("utf-8")):
        path = root / relative
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise TaskWriterError(f"runtime file is missing: {relative}") from exc
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_ISLNK(metadata.st_mode)
            or metadata.st_nlink != 1
        ):
            raise TaskWriterError(f"runtime entry is not a regular unique file: {relative}")
        data = path.read_bytes()
        entries.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
                "mode": stat.S_IMODE(metadata.st_mode),
                "type": "file",
            }
        )
    return {
        "schema_version": "1.0",
        "runtime_root": runtime_root,
        "digest_algorithm": RUNTIME_DIGEST_ALGORITHM,
        "files": entries,
        "runtime_sha256": canonical_runtime_digest(root, _PYTHON_VERIFIER_FILES),
    }


def validate_python_runtime_manifest(root: Path, manifest: Mapping[str, object]) -> None:
    """Fail closed when a copied runtime has missing, extra, or altered files."""

    expected = python_runtime_manifest(root)
    if dict(manifest) != expected:
        raise TaskWriterError("Python verifier runtime manifest does not match the closed tree")
    actual: set[str] = set()
    for path in root.rglob("*"):
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise TaskWriterError(f"cannot inspect Python verifier runtime: {path}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise TaskWriterError(f"Python verifier runtime contains a symlink: {path}")
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise TaskWriterError(f"Python verifier runtime contains an unsafe file: {path}")
        actual.add(path.relative_to(root).as_posix())
    if actual != set(_PYTHON_VERIFIER_FILES):
        raise TaskWriterError("Python verifier runtime contains an extra or missing file")


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
    kind: ArchiveKind,
) -> None:
    """Materialize only a canonical private bundle through scoped authorization."""

    if artifact_resolver is None:
        raise TaskWriterError("private artifact resolver is required")
    authorization = artifact_resolver.authorization
    if not isinstance(authorization, PrivateArtifactAuthorization):
        raise TaskWriterError("canonical bundle materialization requires scoped authorization")
    try:
        materialize_archive(
            reference,
            kind,
            destination,
            MaterializationLimits(
                limits.max_members, limits.max_member_bytes, limits.max_total_bytes
            ),
            authorization,
            resolver=artifact_resolver,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise TaskWriterError(f"cannot materialize private bundle: {exc}") from exc


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
    "canonical_runtime_digest",
    "python_runtime_manifest",
    "validate_python_runtime_manifest",
]


_PYTHON_VERIFIER_FILES = (
    "__init__.py",
    "domain/__init__.py",
    "domain/canonical.py",
    "domain/canonical_contract.py",
    "domain/canonical_models.py",
    "domain/command_plan.py",
    "domain/network_policy.py",
    "domain/runtime.py",
    "package_managers/__init__.py",
    "package_managers/base.py",
    "package_managers/go_modules.py",
    "verification/__init__.py",
    "verification/cli.py",
    "verification/candidate_client.py",
    "verification/candidate_install.py",
    "verification/candidate_process_cli.py",
    "verification/candidate_runner.py",
    "verification/command_plan.py",
    "verification/custom_verifier.py",
    "verification/evaluator.py",
    "verification/go_grader.py",
    "verification/go_bridge_proxy.py",
    "verification/go_contract_runner.py",
    "verification/go_command_plan.py",
    "verification/go_supervisor.py",
    "verification/grader.py",
    "verification/integrity.py",
    "verification/junit.py",
    "verification/leaf_report.py",
    "verification/metric_contract.py",
    "verification/network_check.py",
    "verification/node_grader.py",
    "verification/process_cleanup.py",
    "verification/pytest_plugin.py",
    "verification/registry.py",
    "verification/run_pytest.py",
    "verification/subprocess_supervisor.py",
    "verification/taxonomy.py",
    "verification/workspace_copy.py",
    "verification/normalize/__init__.py",
    "verification/normalize/go_json.py",
    "verification/normalize/node_test_json.py",
    "verification/normalize/pytest_junit.py",
)


def copy_python_verifier_runtime(destination: Path) -> None:
    """Copy the complete trusted Python normalization/evaluation runtime."""

    package_root = Path(__file__).parents[1]
    destination.mkdir(parents=True, exist_ok=True)
    for path in destination.rglob("*"):
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise TaskWriterError(f"cannot inspect verifier runtime destination: {path}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise TaskWriterError(f"destination contains a verifier runtime symlink: {path}")
        if not stat.S_ISDIR(metadata.st_mode) and (
            not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
        ):
            raise TaskWriterError(f"destination contains an unsafe verifier runtime file: {path}")
        if stat.S_ISREG(metadata.st_mode):
            relative = path.relative_to(destination).as_posix()
            if relative.removeprefix("nl2repobench/") not in set(_PYTHON_VERIFIER_FILES):
                raise TaskWriterError("destination contains an unlisted verifier runtime file")
    for relative in _PYTHON_VERIFIER_FILES:
        source = package_root / relative
        try:
            metadata = source.lstat()
        except OSError as exc:
            raise TaskWriterError(
                f"canonical verifier runtime file is missing: {relative}"
            ) from exc
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_ISLNK(metadata.st_mode)
            or metadata.st_nlink != 1
        ):
            raise TaskWriterError(f"canonical verifier runtime file is missing: {relative}")
        target = destination / "nl2repobench" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(target, source.read_bytes())
        target.chmod(0o555)
    package_destination = destination / "nl2repobench"
    validate_python_runtime_manifest(
        package_destination, python_runtime_manifest(package_destination)
    )


__all__.append("copy_python_verifier_runtime")

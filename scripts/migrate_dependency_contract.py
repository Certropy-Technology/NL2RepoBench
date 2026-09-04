#!/usr/bin/env python3
"""Migrate catalog dependency blocks to lock/offline_store/inventory refs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.domain.models import ArtifactRef, DependencyBundle, Visibility
from nl2repobench.harbor.bundle_io import BundleLimits, extract_bundle_archive
from nl2repobench.package_managers.dependency_artifacts import (
    LOCK_MEDIA_TYPE,
    STORE_MEDIA_TYPE,
    put_dependency_archive,
    put_dependency_inventory,
)
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.canonical_ustar import (
    CanonicalEntry,
    encode_ustar,
    entries_from_tree,
)

LEGACY_LIMITS = BundleLimits(
    max_members=100_000,
    max_member_bytes=512 * 1024 * 1024,
    max_total_bytes=2 * 1024 * 1024 * 1024,
)
RUNTIME_RECOVERY_LIFECYCLES = frozenset({"controls-passed", "published"})


class MigrationError(ValueError):
    """A source cannot be migrated without inventing dependency evidence."""




@dataclass(frozen=True)
class RuntimeProfile:
    identity: str
    package_manager: str
    adapter_version: str
    toolchain: Path
    smoke_command_id: str


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_dict(reference: ArtifactRef) -> dict[str, Any]:
    return reference.model_dump(mode="json", exclude={"schema_version"})


def _profile(root: Path, source: dict[str, Any]) -> RuntimeProfile:
    language = str(source.get("metadata", {}).get("language"))
    dependencies = source.get("dependencies", {})
    runtime = source.get("environment", {}).get("runtime", {})
    if language == "python":
        package_manager = str(
            dependencies.get("package_manager") or dependencies.get("installer") or "unknown"
        )
        return RuntimeProfile(
            f"python+{package_manager}",
            package_manager,
            "python-preinstalled-image-v1",
            root / "toolchain.lock.toml",
            "python-preinstalled-image-v1",
        )
    if language == "node":
        package_manager = str(
            dependencies.get("package_manager") or runtime.get("package_manager") or "unknown"
        )
        return RuntimeProfile(
            f"node+{package_manager}",
            package_manager,
            f"{package_manager}-offline-v1",
            root / "toolchain.node.lock.toml",
            f"{package_manager}-offline-install-v1",
        )
    if language == "go":
        return RuntimeProfile(
            "go+go-modules",
            "go-modules",
            "go-modules-offline-v1",
            root / "toolchain.go.lock.toml",
            "go-test-offline-v1",
        )
    if language == "java":
        return RuntimeProfile(
            "java+maven",
            "maven",
            "maven-offline-v1",
            root / "toolchain.java.lock.toml",
            "maven-test-offline-v1",
        )
    raise MigrationError(f"unsupported dependency runtime language: {language!r}")


def _recover_package_manager(root: Path, task_id: str, source: dict[str, Any]) -> None:
    dependencies = source.get("dependencies")
    if not isinstance(dependencies, dict) or dependencies.get("package_manager") != "unknown":
        return
    try:
        raw = subprocess.check_output(
            ["git", "show", f"main:catalog/sources/{task_id}/task.toml"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        old = tomllib.loads(raw)
    except (OSError, subprocess.CalledProcessError, tomllib.TOMLDecodeError):
        return
    old_dependencies = old.get("dependencies", {})
    old_runtime = old.get("environment", {}).get("runtime", {})
    recovered = old_dependencies.get("installer") or old_runtime.get("package_manager")
    if recovered == "system" and source.get("metadata", {}).get("language") == "go":
        recovered = "go-modules"
    if isinstance(recovered, str) and recovered in {
        "uv",
        "pip",
        "npm",
        "pnpm",
        "go-modules",
        "maven",
        "cargo",
        "none",
    }:
        dependencies["package_manager"] = recovered


def _find_legacy_artifact(
    reference: dict[str, Any], artifact_roots: tuple[Path, ...]
) -> Path | None:
    digest = str(reference["digest"])
    value = digest.removeprefix("sha256:")
    visibility = str(reference.get("visibility", "private"))
    for root in artifact_roots:
        path = root / visibility / "sha256" / value[:2] / value
        if path.is_file() and path.stat().st_size == reference.get("size_bytes"):
            if _sha256(path) == digest:
                return path
    return None


def _copy_selected(
    source: Path,
    destination: Path,
    names: tuple[str, ...],
) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in names:
        candidate = source / name
        if not candidate.exists():
            continue
        target = destination / name
        if candidate.is_dir():
            shutil.copytree(candidate, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, target)


def _write_node_store(source: Path, destination: Path, package_manager: str) -> None:
    mapping: list[dict[str, Any]] = []
    roots: list[str] = []
    objects = destination / "objects"
    for root_name in ("npm-cache", "pnpm-store"):
        root = source / root_name
        if not root.is_dir():
            continue
        roots.append(root_name)
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = (Path(root_name) / path.relative_to(root)).as_posix()
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            target = objects / digest[:2] / digest
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
            mapping.append({"path": relative, "sha256": digest, "size": len(data)})
    if not roots:
        roots.append("pnpm-store" if package_manager == "pnpm" else "npm-cache")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "node-store-paths.json").write_text(
        json.dumps(
            {"schema_version": "1.0", "roots": roots, "files": mapping},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )


def _normalize_node_manifest(source: Path, destination: Path) -> None:
    """Bind the legacy npm manifest to the files actually retained in the store."""

    manifest_path = source / "bundle.manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    cache_root = source / "npm-cache"
    cache_entries = (
        sorted(
            path.relative_to(cache_root).as_posix()
            for path in cache_root.rglob("*")
            if path.is_file()
        )
        if cache_root.is_dir()
        else []
    )
    files = [
        {
            "path": "package-lock.json",
            "sha256": hashlib.sha256(
                (source / "package-lock.json").read_bytes()
            ).hexdigest(),
        }
    ]
    files.extend(
        {
            "path": (Path("npm-cache") / relative).as_posix(),
            "sha256": hashlib.sha256((cache_root / relative).read_bytes()).hexdigest(),
        }
        for relative in cache_entries
    )
    payload["cache_entries"] = cache_entries
    payload["files"] = files
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "bundle.manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )


def _legacy_tree(
    root: Path,
    task_id: str,
    language: str,
    dependency: dict[str, Any],
    artifact_roots: tuple[Path, ...],
    temporary: Path,
) -> Path:
    runtime = root / "catalog/tasks" / task_id
    candidates = {
        "node": runtime / "environment/npm-bundle",
        "go": runtime / "environment/go-module-bundle",
    }
    candidate = candidates.get(language)
    if candidate is not None and candidate.is_dir():
        return candidate
    if language == "node":
        legacy_node = runtime / "tests/dependencies"
        if legacy_node.is_dir():
            return legacy_node
    reference = dependency.get("artifact") or dependency.get("module_bundle")
    if not isinstance(reference, dict):
        raise MigrationError(f"{task_id}: legacy dependency bundle is missing")
    archive = _find_legacy_artifact(reference, artifact_roots)
    if archive is None:
        raise MigrationError(f"{task_id}: legacy dependency artifact is unavailable")
    destination = temporary / task_id
    extract_bundle_archive(archive, destination, limits=LEGACY_LIMITS)
    return destination


def _python_lock(
    root: Path,
    task_id: str,
    dependency: dict[str, Any],
    artifact_roots: tuple[Path, ...],
) -> bytes:
    runtime_lock = root / "catalog/tasks" / task_id / "environment/candidate-requirements.lock.txt"
    if runtime_lock.is_file():
        return runtime_lock.read_bytes()
    reference = dependency.get("lock_artifact")
    if not isinstance(reference, dict):
        raise MigrationError(f"{task_id}: Python dependency lock is missing")
    lock = _find_legacy_artifact(reference, artifact_roots)
    if lock is None:
        raise MigrationError(f"{task_id}: Python dependency lock artifact is unavailable")
    return lock.read_bytes()


def _trees(
    root: Path,
    source: dict[str, Any],
    task_id: str,
    artifact_roots: tuple[Path, ...],
    temporary: Path,
) -> tuple[tuple[CanonicalEntry, ...], tuple[CanonicalEntry, ...]]:
    language = str(source["metadata"]["language"])
    dependency = source["dependencies"]
    if language == "python":
        lock = _python_lock(root, task_id, dependency, artifact_roots)
        return (CanonicalEntry("requirements.lock.txt", "file", 0o444, lock),), ()

    legacy = _legacy_tree(
        root, task_id, language, dependency, artifact_roots, temporary
    )
    lock_root = temporary / f"{task_id}-lock"
    store_root = temporary / f"{task_id}-store"
    if language == "node":
        lockfile = str(dependency.get("lockfile_name", "package-lock.json"))
        _copy_selected(legacy, lock_root, (lockfile, "bundle.manifest.json"))
        if lockfile != "package-lock.json":
            raise MigrationError(f"{task_id}: Node lockfile must be package-lock.json")
        _normalize_node_manifest(legacy, lock_root)
        _write_node_store(
            legacy,
            store_root,
            str(dependency.get("package_manager", "npm")),
        )
    elif language == "go":
        _copy_selected(legacy, lock_root, ("go.mod", "go.sum"))
        _copy_selected(legacy, store_root, ("vendor", "module-cache"))
    elif language == "java":
        _copy_selected(legacy, lock_root, ("maven-lock-v1.json",))
        _copy_selected(legacy, store_root, ("maven-repository",))
    else:
        raise MigrationError(f"{task_id}: unsupported dependency language: {language}")
    if not any(lock_root.rglob("*")):
        raise MigrationError(f"{task_id}: dependency lock tree is empty")
    return entries_from_tree(lock_root), entries_from_tree(store_root)


def _replace_dependencies(text: str, block: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    inserted = False
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            skipping = stripped == "[dependencies]" or stripped.startswith("[dependencies.")
            if skipping:
                if not inserted:
                    output.append(block.rstrip() + "\n\n")
                    inserted = True
                continue
        if not skipping:
            output.append(line)
    if not inserted:
        raise MigrationError("source lacks [dependencies]")
    return "".join(output)


def _nested_reference(source: dict[str, Any], path: tuple[str, ...]) -> dict[str, Any] | None:
    value: object = source
    for name in path:
        if not isinstance(value, dict):
            return None
        value = value.get(name)
    return value if isinstance(value, dict) else None


def _set_nested_reference(
    source: dict[str, Any], path: tuple[str, ...], reference: ArtifactRef
) -> None:
    value: dict[str, Any] = source
    for name in path[:-1]:
        child = value.get(name)
        if not isinstance(child, dict):
            raise MigrationError(f"missing artifact section: {'.'.join(path)}")
        value = child
    value[path[-1]] = _artifact_dict(reference)


def _recover_runtime_private_artifacts(
    root: Path,
    task_id: str,
    source: dict[str, Any],
    store: FileArtifactStore,
    artifact_roots: tuple[Path, ...],
) -> list[str]:
    """Move unavailable legacy private refs from a generated runtime into CAS."""

    runtime = root / "catalog/tasks" / task_id
    candidates = (
        (("verifier", "bundle"), runtime / "tests/verifier", True),
        (("tests", "test_bundle"), runtime / "tests/private", True),
        (("tests", "commands_artifact"), runtime / "tests/command-plan.json", False),
        (("oracle_bundle",), runtime / "solution", True),
    )
    recovered: list[str] = []
    for path, payload_root, is_directory in candidates:
        raw = _nested_reference(source, path)
        if raw is None:
            continue
        try:
            old_reference = ArtifactRef.model_validate(raw)
        except ValueError as exc:
            raise MigrationError(f"{task_id}: invalid private ref {'.'.join(path)}: {exc}") from exc
        if old_reference.visibility is not Visibility.PRIVATE:
            continue
        if _find_legacy_artifact(raw, artifact_roots) is not None:
            continue
        if is_directory:
            if not payload_root.is_dir() or payload_root.is_symlink():
                raise MigrationError(
                    f"{task_id}: cannot recover {'.'.join(path)} from generated runtime"
                )
            entries = entries_from_tree(payload_root)
        else:
            if not payload_root.is_file() or payload_root.is_symlink():
                raise MigrationError(
                    f"{task_id}: cannot recover {'.'.join(path)} from generated runtime"
                )
            entries = (
                CanonicalEntry(
                    payload_root.name,
                    "file",
                    0o444,
                    payload_root.read_bytes(),
                ),
            )
        if not entries:
            raise MigrationError(
                f"{task_id}: generated runtime has no bytes for {'.'.join(path)}"
            )
        replacement = store.put_bytes(
            encode_ustar(entries),
            media_type=old_reference.media_type,
            visibility=Visibility.PRIVATE,
        )
        _set_nested_reference(source, path, replacement)
        recovered.append(".".join(path))
    return recovered


def _source_task_paths(sources_root: Path) -> list[Path]:
    """Return declarative source descriptors, excluding legacy Harbor inputs."""

    paths: list[Path] = []
    for path in sorted(sources_root.rglob("task.toml")):
        relative_parts = path.relative_to(sources_root).parts
        if "harbor" in relative_parts:
            continue
        paths.append(path)
    return paths


def migrate(
    root: Path,
    sources_root: Path,
    store: FileArtifactStore,
    artifact_roots: tuple[Path, ...],
    *,
    apply: bool,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    pending_writes: list[tuple[Path, str]] = []
    with tempfile.TemporaryDirectory(prefix="nl2repo-dependency-migration-") as temp:
        temporary = Path(temp)
        output_store = store if apply else FileArtifactStore(temporary / "dry-run-artifacts")
        for path in _source_task_paths(sources_root):
            source_root = path.parent
            source = tomllib.loads(path.read_text(encoding="utf-8"))
            task_id = str(source.get("task_id", source_root.relative_to(sources_root)))
            _recover_package_manager(root, task_id, source)
            recovered: list[str] = []
            if source.get("lifecycle", {}).get("status") in RUNTIME_RECOVERY_LIFECYCLES:
                try:
                    recovered = _recover_runtime_private_artifacts(
                        root,
                        task_id,
                        source,
                        output_store,
                        artifact_roots,
                    )
                except (OSError, ValueError) as exc:
                    rows.append(
                        {"task_id": task_id, "status": "error", "reason": str(exc)}
                    )
                    continue
            source_text = (
                tomli_w.dumps(source)
                if recovered
                else path.read_text(encoding="utf-8")
            )
            dependency = source.get("dependencies")
            if not isinstance(dependency, dict):
                rows.append(
                    {"task_id": task_id, "status": "error", "reason": "missing dependencies"}
                )
                continue
            canonical = all(
                isinstance(dependency.get(name), dict)
                for name in ("lock", "offline_store", "inventory")
            ) and isinstance(dependency.get("package_manager"), str)
            language = source.get("metadata", {}).get("language")
            runtime_exists = (root / "catalog/tasks" / task_id).is_dir()
            if canonical and not (language == "node" and runtime_exists):
                canonical_dependency = {
                    "status": dependency.get("status", "unknown"),
                    "package_manager": dependency["package_manager"],
                    "packages": dependency.get("packages", []),
                    "lock": dependency["lock"],
                    "offline_store": dependency["offline_store"],
                    "inventory": dependency["inventory"],
                }
                migrated = _replace_dependencies(
                    source_text,
                    tomli_w.dumps({"dependencies": canonical_dependency}),
                )
                pending_writes.append((path, migrated))
                rows.append(
                    {
                        "task_id": task_id,
                        "status": "recovered" if recovered else "already-canonical",
                        "recovered": recovered,
                    }
                )
                continue
            profile = _profile(root, source)
            new_dependency: dict[str, Any] = {
                "status": dependency.get("status", "unknown"),
                "package_manager": profile.package_manager,
                "packages": dependency.get("packages", []),
            }
            if dependency.get("status") == "known":
                try:
                    lock_entries, store_entries = _trees(
                        root, source, task_id, artifact_roots, temporary
                    )
                    lock_ref = put_dependency_archive(
                        output_store, lock_entries, media_type=LOCK_MEDIA_TYPE
                    )
                    store_ref = put_dependency_archive(
                        output_store, store_entries, media_type=STORE_MEDIA_TYPE
                    )
                    inventory_ref = put_dependency_inventory(
                        output_store,
                        identity=profile.identity,
                        adapter_version=profile.adapter_version,
                        toolchain_digest=_sha256(profile.toolchain),
                        lock_ref=lock_ref,
                        lock_entries=lock_entries,
                        store_ref=store_ref,
                        store_entries=store_entries,
                        smoke_command_id=profile.smoke_command_id,
                    )
                    new_dependency.update(
                        {
                            "lock": _artifact_dict(lock_ref),
                            "offline_store": _artifact_dict(store_ref),
                            "inventory": _artifact_dict(inventory_ref),
                        }
                    )
                except (OSError, ValueError) as exc:
                    lifecycle = source.get("lifecycle", {}).get("status")
                    if lifecycle not in {"blocked", "excluded"}:
                        rows.append(
                            {"task_id": task_id, "status": "error", "reason": str(exc)}
                        )
                        continue
                    new_dependency["status"] = "unknown"
            DependencyBundle.model_validate(new_dependency)
            block = tomli_w.dumps({"dependencies": new_dependency})
            migrated = _replace_dependencies(source_text, block)
            pending_writes.append((path, migrated))
            rows.append(
                {
                    "task_id": task_id,
                    "status": "migrated",
                    "recovered": recovered,
                }
            )
    errors = [row for row in rows if row["status"] == "error"]
    recoveries = [
        {"task_id": row["task_id"], "artifacts": row["recovered"]}
        for row in rows
        if row.get("recovered")
    ]
    if apply and not errors:
        for path, content in pending_writes:
            path.write_text(content, encoding="utf-8")
    return {
        "schema_version": "1.0",
        "sources": len(rows),
        "migrated": len(rows) - len(errors),
        "errors": errors,
        "recoveries": recoveries,
        "ok": not errors,
        "applied": apply and not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path("catalog/sources"))
    parser.add_argument("--artifact-root", type=Path, default=Path(".nl2repo/artifacts"))
    parser.add_argument("--legacy-artifact-root", type=Path, action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    report = migrate(
        root,
        args.sources.resolve(),
        FileArtifactStore(args.artifact_root.resolve()),
        tuple(
            [args.artifact_root.resolve()]
            + [path.resolve() for path in args.legacy_artifact_root]
        ),
        apply=args.apply,
    )
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

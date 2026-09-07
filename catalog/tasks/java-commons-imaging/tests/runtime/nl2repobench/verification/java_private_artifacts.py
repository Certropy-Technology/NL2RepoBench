"""Materialize Java verifier inputs from a task-scoped private CAS mount."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.models import DependencyInventory
from nl2repobench.package_managers.maven import MavenPackageManager

MAX_ARCHIVE_MEMBERS = 10_000
MAX_MEMBER_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
REF_KEYS = {"schema_version", "digest", "size_bytes", "media_type", "uri", "visibility"}
MEDIA_TYPES = {
    "lock": "application/vnd.nl2repobench.package-lock.tar",
    "offline_store": "application/vnd.nl2repobench.offline-store.tar",
    "inventory": "application/vnd.nl2repobench.inventory+json",
    "verifier": "application/vnd.nl2repobench.verifier+tar",
}


class JavaPrivateArtifactError(ValueError):
    """A private Java artifact failed the CAS or archive contract."""


def _ref_path(
    cas_root: Path,
    reference: object,
    *,
    reference_kind: str | None = None,
) -> Path:
    if not isinstance(reference, dict) or set(reference) != REF_KEYS:
        raise JavaPrivateArtifactError("private artifact reference is malformed")
    digest = reference["digest"]
    if (
        reference["schema_version"] != "1.0"
        or not isinstance(digest, str)
        or len(digest) != 71
        or not digest.startswith("sha256:")
        or any(char not in "0123456789abcdef" for char in digest[7:])
    ):
        raise JavaPrivateArtifactError("private artifact digest is invalid")
    if (
        reference["visibility"] != "private"
        or reference["uri"] != f"artifact://private/{digest}"
    ):
        raise JavaPrivateArtifactError("private artifact visibility or URI is invalid")
    if reference_kind is not None and reference.get("media_type") != MEDIA_TYPES[reference_kind]:
        raise JavaPrivateArtifactError(
            f"private artifact media type is invalid for {reference_kind}"
        )
    size = reference["size_bytes"]
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise JavaPrivateArtifactError("private artifact size is invalid")
    resolved_root = cas_root.resolve()
    target = cas_root / "private" / "sha256" / digest[7:9] / digest[7:]
    for parent in (cas_root / "private", cas_root / "private/sha256", target.parent):
        if parent.is_symlink() or not parent.resolve().is_relative_to(resolved_root):
            raise JavaPrivateArtifactError("private CAS namespace contains an unsafe symlink")
    if target.is_symlink() or not target.is_file():
        raise JavaPrivateArtifactError(f"private artifact is missing: {digest}")
    metadata = target.stat()
    if metadata.st_size != size:
        raise JavaPrivateArtifactError(f"private artifact size mismatch: {digest}")
    checksum = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    if f"sha256:{checksum.hexdigest()}" != digest:
        raise JavaPrivateArtifactError(f"private artifact digest mismatch: {digest}")
    return target


def _safe_target(root: Path, member_name: str) -> Path:
    relative = PurePosixPath(member_name)
    if relative.is_absolute() or not relative.parts or any(
        part in {"", ".", ".."} for part in relative.parts
    ):
        raise JavaPrivateArtifactError(f"private archive path is unsafe: {member_name}")
    target = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise JavaPrivateArtifactError(
                f"private archive path crosses a symlink: {member_name}"
            )
    return target


def _extract(
    reference: object,
    cas_root: Path,
    destination: Path,
    *,
    reference_kind: str,
) -> None:
    archive = _ref_path(cas_root, reference, reference_kind=reference_kind)
    if destination.exists() or destination.is_symlink():
        raise JavaPrivateArtifactError(
            f"private archive destination already exists: {destination}"
        )
    destination.mkdir(parents=True)
    seen: set[PurePosixPath] = set()
    total = 0
    try:
        with tarfile.open(archive, mode="r:*") as handle:
            for index, member in enumerate(handle, 1):
                if index > MAX_ARCHIVE_MEMBERS:
                    raise JavaPrivateArtifactError("private archive contains too many members")
                if member.name in {".", "./"} and member.isdir():
                    continue
                relative = PurePosixPath(member.name)
                if relative in seen:
                    raise JavaPrivateArtifactError(
                        f"private archive has duplicate path: {member.name}"
                    )
                seen.add(relative)
                if member.size < 0 or member.size > MAX_MEMBER_BYTES:
                    raise JavaPrivateArtifactError(
                        f"private archive member is too large: {member.name}"
                    )
                target = _safe_target(destination, member.name)
                if member.issym() or member.islnk() or member.isdev():
                    raise JavaPrivateArtifactError(
                        f"private archive links/devices are forbidden: {member.name}"
                    )
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    os.chmod(target, 0o555)
                    continue
                if not member.isfile():
                    raise JavaPrivateArtifactError(
                        f"private archive member type is unsupported: {member.name}"
                    )
                total += member.size
                if total > MAX_TOTAL_BYTES:
                    raise JavaPrivateArtifactError(
                        "private archive expanded size exceeds the limit"
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                extracted = handle.extractfile(member)
                if extracted is None:
                    raise JavaPrivateArtifactError(
                        f"private archive member cannot be read: {member.name}"
                    )
                with target.open("xb") as output:
                    shutil.copyfileobj(extracted, output, length=1024 * 1024)
                mode = stat.S_IMODE(member.mode) & 0o777
                if mode & 0o600 == 0:
                    mode = 0o444
                os.chmod(target, mode)
    except (OSError, tarfile.TarError) as exc:
        raise JavaPrivateArtifactError(f"cannot extract private archive: {exc}") from exc


def _load_refs(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JavaPrivateArtifactError(f"private artifact refs are invalid: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {
        "schema_version",
        "dependency_refs",
        "verifier_ref",
        "toolchain_digest",
        "maven_version",
    } or data["schema_version"] != "1.0":
        raise JavaPrivateArtifactError("private artifact refs schema is invalid")
    dependencies = data["dependency_refs"]
    if not isinstance(dependencies, dict) or set(dependencies) != {
        "lock", "offline_store", "inventory"
    }:
        raise JavaPrivateArtifactError("Java dependency refs are incomplete")
    return data


def _validate_tree(root: Path, expected: Any) -> None:
    executable = {
        entry.path for entry in expected.entries if entry.type == "file" and entry.mode == "0555"
    }
    actual: list[dict[str, object]] = []
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix().encode("utf-8"),
    ):
        relative = path.relative_to(root).as_posix()
        metadata = path.lstat()
        if path.is_symlink() or not (
            stat.S_ISDIR(metadata.st_mode) or stat.S_ISREG(metadata.st_mode)
        ):
            raise JavaPrivateArtifactError(
                f"materialized dependency tree is unsafe: {relative}"
            )
        if path.is_dir():
            actual.append(
                {
                    "path": relative + "/",
                    "type": "directory",
                    "mode": "0555",
                    "size": 0,
                    "sha256": None,
                }
            )
        else:
            data = path.read_bytes()
            actual.append(
                {
                    "path": relative,
                    "type": "file",
                    "mode": "0555" if relative in executable else "0444",
                    "size": len(data),
                    "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
                }
            )
    actual.sort(key=lambda entry: (str(entry["path"]).encode("utf-8"), str(entry["type"])))
    expected_entries = [entry.model_dump(mode="json") for entry in expected.entries]
    if actual != expected_entries:
        raise JavaPrivateArtifactError(
            "materialized dependency archive inventory does not match"
        )
    digest = hashlib.sha256(b"nl2repobench-tree-v1\0")
    for entry in actual:
        path_bytes = str(entry["path"]).encode("utf-8")
        digest.update(b"F" if entry["type"] == "file" else b"D")
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(int(str(entry["mode"]), 8).to_bytes(4, "big"))
        size = entry["size"]
        if not isinstance(size, int):
            raise JavaPrivateArtifactError("materialized dependency archive size is invalid")
        digest.update(size.to_bytes(8, "big"))
        digest.update(
            bytes.fromhex(str(entry["sha256"])[7:])
            if entry["sha256"] is not None
            else b"\0" * 32
        )
    if "sha256:" + digest.hexdigest() != expected.tree_digest:
        raise JavaPrivateArtifactError(
            "materialized dependency archive tree digest does not match"
        )


def materialize(refs_path: Path, cas_root: Path, dependencies: Path, verifier: Path) -> None:
    """Resolve and extract one Java task's private verifier inputs."""

    refs = _load_refs(refs_path)
    dependency_refs = refs["dependency_refs"]
    try:
        inventory_data = _ref_path(
            cas_root,
            dependency_refs["inventory"],
            reference_kind="inventory",
        ).read_bytes()
        inventory = DependencyInventory.model_validate_json(inventory_data)
        if inventory_data != canonical_json(inventory) + b"\n":
            raise JavaPrivateArtifactError("dependency inventory is not canonical JSON")
        if inventory.identity != "java+maven":
            raise JavaPrivateArtifactError("dependency inventory identity is invalid")
        if inventory.adapter_version != "maven-offline-v1":
            raise JavaPrivateArtifactError("dependency inventory adapter is invalid")
        if inventory.toolchain_digest != refs["toolchain_digest"]:
            raise JavaPrivateArtifactError("dependency inventory toolchain is invalid")
        if inventory.lock.archive_digest != dependency_refs["lock"]["digest"]:
            raise JavaPrivateArtifactError("dependency lock digest does not match inventory")
        if inventory.store.archive_digest != dependency_refs["offline_store"]["digest"]:
            raise JavaPrivateArtifactError("dependency store digest does not match inventory")
    except (OSError, ValueError) as exc:
        raise JavaPrivateArtifactError(
            f"dependency inventory does not match the declared refs: {exc}"
        ) from exc

    temporary = dependencies.with_name(f".{dependencies.name}-tmp")
    shutil.rmtree(temporary, ignore_errors=True)
    try:
        temporary.mkdir(parents=True)
        lock_root = temporary / "lock"
        store_root = temporary / "store"
        _extract(
            dependency_refs["lock"],
            cas_root,
            lock_root,
            reference_kind="lock",
        )
        _extract(
            dependency_refs["offline_store"],
            cas_root,
            store_root,
            reference_kind="offline_store",
        )
        _validate_tree(lock_root, inventory.lock)
        _validate_tree(store_root, inventory.store)
        lock_file = lock_root / "maven-lock-v1.json"
        repository = store_root / "maven-repository"
        if not lock_file.is_file() or lock_file.is_symlink():
            raise JavaPrivateArtifactError("private Java lock file is missing")
        try:
            MavenPackageManager().validate_lock(
                lock_file,
                expected_version=str(refs["maven_version"]),
            )
            MavenPackageManager().validate_store_payload(
                store_root / "maven-repository",
                lockfile=lock_file,
                expected_version=str(refs["maven_version"]),
            )
        except ValueError as exc:
            raise JavaPrivateArtifactError(f"private Maven closure is invalid: {exc}") from exc
        target_lock = temporary / "maven-lock-v1.json"
        shutil.copyfile(lock_file, target_lock)
        target_repository = temporary / "maven-repository"
        if repository.is_dir() and not repository.is_symlink():
            shutil.copytree(repository, target_repository)
        else:
            target_repository.mkdir()
        shutil.rmtree(lock_root)
        shutil.rmtree(store_root)
        temporary.rename(dependencies)

        verifier_tmp = verifier.with_name(f".{verifier.name}-tmp")
        shutil.rmtree(verifier_tmp, ignore_errors=True)
        _extract(
            refs["verifier_ref"],
            cas_root,
            verifier_tmp,
            reference_kind="verifier",
        )
        verifier_tmp.rename(verifier)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        shutil.rmtree(verifier.with_name(f".{verifier.name}-tmp"), ignore_errors=True)
        shutil.rmtree(dependencies, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refs", type=Path, required=True)
    parser.add_argument("--cas", type=Path, required=True)
    parser.add_argument("--dependencies", type=Path, required=True)
    parser.add_argument("--verifier", type=Path, required=True)
    args = parser.parse_args()
    try:
        materialize(args.refs, args.cas, args.dependencies, args.verifier)
    except JavaPrivateArtifactError as exc:
        print(str(exc))
        return 20
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["JavaPrivateArtifactError", "materialize"]

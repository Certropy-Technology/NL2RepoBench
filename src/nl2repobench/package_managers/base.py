"""Typed package-manager boundary for the canonical dependency bundle."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from nl2repobench.domain.canonical_contract import RuntimeProfile
from nl2repobench.domain.runtime import RuntimeDiscriminator


class PackageManagerErrorCode(StrEnum):
    LOCK_MISSING = "lock-missing"
    LOCK_MALFORMED = "lock-malformed"
    TOOLCHAIN_MISMATCH = "toolchain-mismatch"
    STORE_MALFORMED = "store-malformed"
    INVENTORY_MISMATCH = "inventory-mismatch"
    OFFLINE_SMOKE_FAILED = "offline-smoke-failed"
    UNSUPPORTED_PROFILE = "unsupported-profile"


class PackageManagerError(ValueError):
    """A package-manager input violates the canonical dependency contract."""

    def __init__(
        self,
        code: PackageManagerErrorCode | str,
        identity: RuntimeDiscriminator,
        stage: str,
        message: str,
        details: object | None = None,
    ) -> None:
        try:
            self.code = PackageManagerErrorCode(code)
        except ValueError as exc:
            raise ValueError(f"invalid package-manager error code: {code}") from exc
        if not stage.strip() or not message.strip():
            raise ValueError("package-manager error stage and message must be non-empty")
        self.identity = identity
        self.stage = stage
        self.details = details
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class ResolvedPackage:
    name: str
    version: str
    kind: str
    artifact_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.version or not self.kind:
            raise ValueError("resolved package fields must be non-empty")


@dataclass(frozen=True, slots=True)
class LockSummary:
    identity: RuntimeDiscriminator
    toolchain_version: str
    lockfile_names: tuple[str, ...]
    lock_digest: str
    resolved: tuple[ResolvedPackage, ...] = ()

    def __post_init__(self) -> None:
        if not self.toolchain_version:
            raise ValueError("lock summary requires a toolchain version")
        if not self.lockfile_names and self.identity.package_manager.value != "none":
            raise ValueError("lock summary requires lockfile names")
        _require_digest(self.lock_digest, "lock digest")


@dataclass(frozen=True, slots=True)
class StoreSummary:
    identity: RuntimeDiscriminator
    store_digest: str
    inventory_digest: str
    file_count: int
    total_bytes: int
    offline_smoke: bool

    def __post_init__(self) -> None:
        _require_digest(self.store_digest, "store digest")
        _require_digest(self.inventory_digest, "inventory digest")
        if self.file_count < 0 or self.total_bytes < 0:
            raise ValueError("store counts cannot be negative")


@dataclass(frozen=True, slots=True)
class CommandSpec:
    argv: tuple[str, ...]
    cwd: str
    environment: tuple[tuple[str, str], ...]
    timeout_sec: int

    def __post_init__(self) -> None:
        if not self.argv or any(not item for item in self.argv):
            raise ValueError("command argv must be non-empty")
        if not self.cwd or self.cwd.startswith("/") or ".." in Path(self.cwd).parts:
            raise ValueError("command cwd must be a safe relative path")
        if self.timeout_sec <= 0:
            raise ValueError("command timeout must be positive")


def _require_digest(value: str, description: str) -> None:
    if len(value) != 71 or not value.startswith("sha256:"):
        raise ValueError(f"{description} must be a SHA-256 digest")
    try:
        bytes.fromhex(value.removeprefix("sha256:"))
    except ValueError as exc:
        raise ValueError(f"{description} must be a SHA-256 digest") from exc


def inventory_store_summary(
    *,
    identity: RuntimeDiscriminator,
    store_root: Path,
    inventory: object,
) -> StoreSummary:
    """Validate the shared external inventory against one materialized store."""

    import hashlib
    import json
    import stat

    from nl2repobench.storage.canonical_ustar import tree_digest, tree_entries

    def fail(message: str) -> PackageManagerError:
        return PackageManagerError(
            PackageManagerErrorCode.INVENTORY_MISMATCH,
            identity,
            "store",
            message,
        )

    if not isinstance(inventory, dict):
        raise fail("dependency inventory must be an object")
    expected_keys = {
        "schema_version",
        "identity",
        "adapter_version",
        "toolchain_digest",
        "lock",
        "store",
        "offline_smoke",
    }
    if set(inventory) != expected_keys or inventory.get("schema_version") != "1.0":
        raise fail("dependency inventory shape is invalid")
    expected_identity = f"{identity.language.value}+{identity.package_manager.value}"
    if inventory.get("identity") != expected_identity:
        raise fail("dependency inventory identity does not match adapter")
    smoke = inventory.get("offline_smoke")
    if (
        not isinstance(smoke, dict)
        or set(smoke) != {"status", "command_id"}
        or smoke.get("status") != "passed"
        or not isinstance(smoke.get("command_id"), str)
        or not smoke.get("command_id")
    ):
        raise PackageManagerError(
            PackageManagerErrorCode.OFFLINE_SMOKE_FAILED,
            identity,
            "store",
            "dependency inventory has no successful offline smoke",
        )
    section = inventory.get("store")
    if not isinstance(section, dict):
        raise fail("dependency store inventory section is invalid")
    entries = tree_entries(store_root)
    actual_entries = [
        {
            "path": entry.path,
            "type": entry.type,
            "mode": entry.mode,
            "size": entry.size,
            "sha256": entry.sha256,
        }
        for entry in entries
    ]
    if section.get("entries") != actual_entries:
        raise fail("dependency store file inventory does not match")
    if section.get("tree_digest") != tree_digest(entries):
        raise fail("dependency store tree digest does not match")
    if section.get("file_count") != sum(entry.type == "file" for entry in entries):
        raise fail("dependency store file count does not match")
    if section.get("directory_count") != sum(entry.type == "directory" for entry in entries):
        raise fail("dependency store directory count does not match")
    if section.get("total_bytes") != sum(entry.size for entry in entries):
        raise fail("dependency store byte count does not match")
    for path in store_root.rglob("*"):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise PackageManagerError(
                PackageManagerErrorCode.STORE_MALFORMED,
                identity,
                "store",
                f"dependency store contains unsafe path: {path}",
            )
    inventory_bytes = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    archive_digest = section.get("archive_digest")
    _require_digest(str(archive_digest), "store archive digest")
    return StoreSummary(
        identity=identity,
        store_digest=str(archive_digest),
        inventory_digest=f"sha256:{hashlib.sha256(inventory_bytes).hexdigest()}",
        file_count=sum(entry.type == "file" for entry in entries),
        total_bytes=sum(entry.size for entry in entries),
        offline_smoke=True,
    )


class PackageManagerAdapter(Protocol):
    """Package-manager responsibilities below the runtime adapter."""

    identity: RuntimeDiscriminator
    lockfile_names: tuple[str, ...]

    def validate_lock(
        self,
        lock_root: Path,
        expected_toolchain: str,
        *,
        runtime_profile: RuntimeProfile | None = None,
    ) -> LockSummary: ...

    def validate_offline_store(
        self,
        store_root: Path,
        lock_summary: LockSummary,
        inventory: object,
        expected_toolchain: str,
        *,
        runtime_profile: RuntimeProfile | None = None,
    ) -> StoreSummary: ...

    def build_commands(self, profile: object) -> tuple[CommandSpec, ...]: ...

    def offline_environment(self, profile: object) -> dict[str, str]: ...


__all__ = [
    "CommandSpec",
    "LockSummary",
    "PackageManagerAdapter",
    "PackageManagerError",
    "PackageManagerErrorCode",
    "ResolvedPackage",
    "StoreSummary",
    "inventory_store_summary",
]

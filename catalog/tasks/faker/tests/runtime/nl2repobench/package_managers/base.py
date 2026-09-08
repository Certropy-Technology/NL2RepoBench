"""Typed package-manager adapter boundary."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


class PackageManagerError(ValueError):
    """A package-manager lock or offline closure is unsafe or malformed."""


class PackageManagerAdapter(Protocol):
    """Package-manager responsibilities below the runtime adapter."""

    identity: str
    lockfile_name: str

    def validate_lock(self, lockfile: Path, *, expected_version: str) -> object: ...

    def validate_offline_store(
        self,
        bundle_root: Path,
        *,
        lockfile: Path,
        manifest: Path,
        expected_version: str,
    ) -> None: ...

    def install_command(self, *, store_dir: str) -> Sequence[str]: ...

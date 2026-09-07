"""Rust toolchain locks used by the Cargo Harbor adapter."""

from __future__ import annotations

import hashlib
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

_DIGEST_IMAGE = re.compile(r"^[A-Za-z0-9._/-]+@sha256:[0-9a-f]{64}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class RustToolchainLock:
    status: str
    rust_version: str
    base_image: str
    base_image_digest: str
    verifier_base: str
    agent_runtime_image: str
    agent_runtime_image_id: str
    harbor_version: str | None = None
    task_schema: str | None = None
    harbor_lock_file: str | None = None
    harbor_lock_sha256: str | None = None
    verifier_requirements_lock: str | None = None
    verifier_requirements_sha256: str | None = None


def load_rust_toolchain_lock(path: Path) -> RustToolchainLock:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Rust toolchain lock must be a regular file: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"invalid Rust toolchain lock {path}: {exc}") from exc
    if data.get("schema_version") != "1.0":
        raise ValueError("Rust toolchain schema_version must be 1.0")
    status = data.get("status")
    if status not in {"development-only", "locked"}:
        raise ValueError("Rust toolchain status must be development-only or locked")
    runtime = data.get("agent_runtime")
    if not isinstance(runtime, dict):
        raise ValueError("Rust toolchain requires [agent_runtime]")
    required = {
        "rust_version": data.get("rust_version"),
        "base_image": data.get("base_image"),
        "base_image_digest": data.get("base_image_digest"),
        "verifier_base": data.get("verifier_base"),
        "agent_runtime_image": runtime.get("image"),
        "agent_runtime_image_id": runtime.get("image_id"),
    }
    if any(not isinstance(value, str) or not value for value in required.values()):
        raise ValueError("Rust toolchain lock is missing a required string field")
    rust_version = cast(str, required["rust_version"])
    base_image = cast(str, required["base_image"])
    base_image_digest = cast(str, required["base_image_digest"])
    verifier_base = cast(str, required["verifier_base"])
    agent_runtime_image = cast(str, required["agent_runtime_image"])
    agent_runtime_image_id = cast(str, required["agent_runtime_image_id"])
    if not _DIGEST_IMAGE.fullmatch(base_image):
        raise ValueError("Rust base image must be digest pinned")
    if base_image.rsplit("@", 1)[1] != base_image_digest:
        raise ValueError("Rust base image digest does not match base_image")
    if not _DIGEST_IMAGE.fullmatch(verifier_base):
        raise ValueError("Rust verifier base image must be digest pinned")
    if not _DIGEST.fullmatch(agent_runtime_image_id):
        raise ValueError("Rust Agent runtime image ID must be a SHA-256 digest")
    if "@sha256:" in agent_runtime_image:
        if not _DIGEST_IMAGE.fullmatch(agent_runtime_image):
            raise ValueError("Rust Agent runtime image reference is invalid")
        if agent_runtime_image.rsplit("@", 1)[1] != agent_runtime_image_id:
            raise ValueError("Rust Agent runtime image digest does not match image ID")
    harbor = data.get("harbor")
    harbor_values: dict[str, str | None] = {
        "harbor_version": None,
        "task_schema": None,
        "harbor_lock_file": None,
        "harbor_lock_sha256": None,
        "verifier_requirements_lock": None,
        "verifier_requirements_sha256": None,
    }
    if status == "locked":
        if not isinstance(harbor, dict):
            raise ValueError("locked Rust toolchain requires [harbor]")
        harbor_values = {
            "harbor_version": harbor.get("version"),
            "task_schema": harbor.get("task_schema"),
            "harbor_lock_file": harbor.get("lock_file"),
            "harbor_lock_sha256": harbor.get("lock_sha256"),
        }
        if (
            harbor_values["harbor_version"] != "0.21.0"
            or harbor_values["task_schema"] != "1.4"
        ):
            raise ValueError("locked Rust Harbor contract must be 0.21.0/task 1.4")
        lock_file = harbor_values["harbor_lock_file"]
        lock_sha256 = harbor_values["harbor_lock_sha256"]
        if (
            not isinstance(lock_file, str)
            or Path(lock_file).is_absolute()
            or ".." in Path(lock_file).parts
        ):
            raise ValueError("locked Rust Harbor lock path is unsafe")
        if not isinstance(lock_sha256, str) or not _DIGEST.fullmatch(lock_sha256):
            raise ValueError("locked Rust Harbor lock digest is invalid")
        lock_path = path.parent / lock_file
        if lock_path.is_symlink() or not lock_path.is_file():
            raise ValueError(f"locked Rust Harbor lock is missing: {lock_path}")
        actual_lock_sha256 = "sha256:" + hashlib.sha256(lock_path.read_bytes()).hexdigest()
        if actual_lock_sha256 != lock_sha256:
            raise ValueError("locked Rust Harbor lock digest does not match")
        requirements_lock = data.get("verifier_requirements_lock")
        requirements_sha256 = data.get("verifier_requirements_sha256")
        if (
            not isinstance(requirements_lock, str)
            or Path(requirements_lock).is_absolute()
            or ".." in Path(requirements_lock).parts
            or not isinstance(requirements_sha256, str)
            or not _DIGEST.fullmatch(requirements_sha256)
        ):
            raise ValueError("locked Rust verifier requirements lock is invalid")
        requirements_path = path.parent / requirements_lock
        if requirements_path.is_symlink() or not requirements_path.is_file():
            raise ValueError(f"locked Rust verifier requirements are missing: {requirements_path}")
        actual_requirements_sha256 = "sha256:" + hashlib.sha256(
            requirements_path.read_bytes()
        ).hexdigest()
        if actual_requirements_sha256 != requirements_sha256:
            raise ValueError("locked Rust verifier requirements digest does not match")
        harbor_values["verifier_requirements_lock"] = requirements_lock
        harbor_values["verifier_requirements_sha256"] = requirements_sha256
    return RustToolchainLock(
        status=cast(str, status),
        rust_version=rust_version,
        base_image=base_image,
        base_image_digest=base_image_digest,
        verifier_base=verifier_base,
        agent_runtime_image=agent_runtime_image,
        agent_runtime_image_id=agent_runtime_image_id,
        **harbor_values,
    )


__all__ = ["RustToolchainLock", "load_rust_toolchain_lock"]

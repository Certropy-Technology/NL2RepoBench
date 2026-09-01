"""Node Harbor toolchain lock records for the canonical runtime."""

from __future__ import annotations

import hashlib
import re
import stat
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from nl2repobench.domain.canonical_models import CanonicalRecord as RecordModel

from .models import PINNED_IMAGE, AgentRuntimeImageLock, HarborVersionLock

SEMVER_PATTERN = r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$"
NODE_RUNTIME_ROOT = "/opt/nl2repobench-node"


class NodeRuntimeFile(RecordModel):
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(ge=0)
    mode: int = Field(ge=0, le=0o777)
    type: Literal["file"] = "file"


class NodeRuntimeManifest(RecordModel):
    schema_version: Literal["1.0"] = "1.0"
    ecosystem: Literal["node"] = "node"
    platform: Literal["linux/amd64"] = "linux/amd64"
    root: Literal["/opt/nl2repobench-node"] = "/opt/nl2repobench-node"
    source_image: str
    runtime_version: str = Field(pattern=SEMVER_PATTERN)
    npm_version: str = Field(pattern=SEMVER_PATTERN)
    pnpm_version: str | None = Field(default=None, pattern=SEMVER_PATTERN)
    digest_algorithm: Literal["sha256"] = "sha256"
    files: tuple[NodeRuntimeFile, ...]
    executables: tuple[NodeRuntimeFile, ...] = ()
    launchers: tuple[NodeRuntimeFile, ...] = ()
    tree_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_closed_tree(self) -> NodeRuntimeManifest:
        paths = [entry.path for entry in self.files]
        if len(paths) != len(set(paths)) or paths != sorted(paths, key=lambda p: p.encode()):
            raise ValueError("Node runtime manifest paths must be unique and UTF-8 sorted")
        for entry in self.files:
            path = Path(entry.path)
            if path.is_absolute() or ".." in path.parts or not entry.path:
                raise ValueError("Node runtime manifest path is unsafe")
            if entry.mode & 0o6000:
                raise ValueError("Node runtime manifest forbids setuid/setgid files")
        if not any(entry.path == "bin/node" and entry.mode == 0o555 for entry in self.files):
            raise ValueError("Node runtime manifest requires bin/node mode 0555")
        file_paths = set(paths)
        for entry in (*self.executables, *self.launchers):
            if entry.path not in file_paths:
                raise ValueError("Node runtime executable is not in files")
        return self


def node_tree_digest(root: Path, files: tuple[NodeRuntimeFile, ...]) -> str:
    digest = hashlib.sha256()
    for entry in files:
        path = root / entry.path
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError(f"Node runtime entry is not a regular unique file: {entry.path}")
        data = path.read_bytes()
        if len(data) != entry.size_bytes or hashlib.sha256(data).hexdigest() != entry.sha256:
            raise ValueError(f"Node runtime entry digest mismatch: {entry.path}")
        digest.update(entry.path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
    return f"sha256:{digest.hexdigest()}"


def validate_node_runtime_manifest(root: Path, manifest: NodeRuntimeManifest) -> None:
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    declared = {entry.path for entry in manifest.files}
    if actual != declared:
        raise ValueError("Node runtime tree has an extra or missing file")
    if node_tree_digest(root, manifest.files) != manifest.tree_sha256:
        raise ValueError("Node runtime tree digest does not match manifest")


class NodeImageLock(RecordModel):
    agent_base: str
    verifier_base: str
    verifier_python_base: str = (
        "python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a"
    )
    platform: Literal["linux/amd64"] = "linux/amd64"
    status: Literal["locked", "development-only"] = "development-only"

    @model_validator(mode="after")
    def validate_image_provenance(self) -> NodeImageLock:
        for name, value in {
            "agent_base": self.agent_base,
            "verifier_base": self.verifier_base,
            "verifier_python_base": self.verifier_python_base,
        }.items():
            if self.status == "locked":
                if not re.fullmatch(PINNED_IMAGE, value):
                    raise ValueError(f"{name} must be pinned by sha256 digest")
            elif "@sha256:" in value and not re.fullmatch(PINNED_IMAGE, value):
                raise ValueError(f"{name} has an invalid image digest")
        return self


class NodeRuntimeLock(RecordModel):
    runtime_version: str = Field(pattern=r"^(?:22|24)\.[0-9]+\.[0-9]+$")
    npm_version: str = Field(pattern=SEMVER_PATTERN)
    pnpm_version: str | None = Field(default=None, pattern=SEMVER_PATTERN)
    libc: Literal["glibc", "musl"]
    executable: str = f"{NODE_RUNTIME_ROOT}/bin/node"
    npm_executable: str = f"{NODE_RUNTIME_ROOT}/lib/npm/bin/npm-cli.js"
    pnpm_executable: str | None = None
    runtime_root: str = NODE_RUNTIME_ROOT
    node_runtime_manifest: str | None = None
    node_runtime_manifest_sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    node_runtime_tree_sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")


class NodeHarborToolchainLock(RecordModel):
    status: Literal["locked", "development-only"] = "development-only"
    harbor: HarborVersionLock
    images: NodeImageLock
    agent_runtime: AgentRuntimeImageLock
    runtime: NodeRuntimeLock
    node_grader: Literal["absent", "locked"] = "absent"
    node_runtime_sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    verifier_requirements_lock: str = "verifier/requirements.lock.txt"
    verifier_requirements_sha256: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    node_report_schema: Literal["node-test-json-v1"] = "node-test-json-v1"

    @model_validator(mode="after")
    def validate_toolchain_scope(self) -> NodeHarborToolchainLock:
        if self.harbor.task_schema != "1.4":
            raise ValueError("Node Harbor compiler requires task schema 1.4")
        if self.status == "locked" and self.images.status != "locked":
            raise ValueError("locked Node toolchain requires locked images")
        if self.status == "locked" and self.node_grader != "locked":
            raise ValueError("production Node toolchain requires a locked Node grader")
        if self.status == "locked" and self.node_runtime_sha256 is None:
            raise ValueError("production Node toolchain requires a Node runtime hash")
        if self.status == "locked" and self.verifier_requirements_sha256 is None:
            raise ValueError("production Node toolchain requires verifier requirements hash")
        return self


def load_node_toolchain_lock(path: Path) -> NodeHarborToolchainLock:
    """Load and validate the standalone canonical Node toolchain lock."""

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return NodeHarborToolchainLock.model_validate(data)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise ValueError(f"invalid Node toolchain lock {path}: {exc}") from exc


__all__ = [
    "NODE_RUNTIME_ROOT",
    "NodeHarborToolchainLock",
    "NodeRuntimeFile",
    "NodeRuntimeManifest",
    "load_node_toolchain_lock",
    "node_tree_digest",
    "validate_node_runtime_manifest",
]

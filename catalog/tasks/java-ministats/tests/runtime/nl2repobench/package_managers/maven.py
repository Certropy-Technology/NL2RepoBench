"""Fail-closed Maven lock and candidate POM validation.

Maven does not provide a complete lockfile equivalent to ``package-lock`` or
``go.sum``.  The Java lane therefore consumes a verifier-owned
``maven-lock-v1.json`` plus a content-addressed local repository.  This module
only validates those inputs and renders a fixed offline command; it never
executes Maven or contacts Maven Central.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from defusedxml import ElementTree

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage

from .base import PackageManagerError

JAVA_MAVEN_IDENTITY = RuntimeDiscriminator(
    language=RuntimeLanguage.JAVA,
    package_manager=PackageManager.MAVEN,
)
MAX_LOCK_BYTES = 4 * 1024 * 1024
MAX_POM_BYTES = 256 * 1024
MAX_STORE_FILES = 100_000
MAVEN_VERSION = re.compile(r"^3\.9\.[0-9]+$")
JDK_VERSION = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*-21\.0\.[0-9]+\+[0-9]+(?:\.[0-9]+)?$")
COORDINATE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]*$")
ALLOWED_REPOSITORY = "https://repo.maven.apache.org/maven2"
MUTABLE_STORE_FILES = frozenset(
    {"_remote.repositories", "resolver-status.properties", "maven-metadata-local.xml"}
)
NATIVE_SUFFIXES = frozenset({".so", ".dll", ".dylib", ".a", ".o", ".exe", ".bat", ".cmd", ".sh"})


@dataclass(frozen=True)
class MavenLockSummary:
    maven_version: str
    jdk_version: str
    digest: str
    artifacts: tuple[dict[str, Any], ...]


def _fail(message: str) -> PackageManagerError:
    return PackageManagerError(message)


def _coordinate(group_id: str, artifact_id: str, version: str) -> None:
    if (
        not all(COORDINATE.fullmatch(part) for part in group_id.split("."))
        or not COORDINATE.fullmatch(artifact_id)
        or not VERSION.fullmatch(version)
        or "SNAPSHOT" in version.upper()
        or version.upper() in {"LATEST", "RELEASE"}
        or any(marker in version for marker in "[](),")
    ):
        raise _fail("Maven coordinate is malformed or uses a dynamic version")


def maven_repository_path(artifact: Mapping[str, Any]) -> PurePosixPath:
    """Return the canonical repository path for one lock artifact."""

    group_id = str(artifact.get("group_id", ""))
    artifact_id = str(artifact.get("artifact_id", ""))
    version = str(artifact.get("version", ""))
    kind = str(artifact.get("type", ""))
    classifier = artifact.get("classifier")
    _coordinate(group_id, artifact_id, version)
    if kind not in {"jar", "pom"}:
        raise _fail("Maven artifact type must be jar or pom")
    suffix = f"-{classifier}" if classifier else ""
    if classifier is not None and not COORDINATE.fullmatch(str(classifier)):
        raise _fail("Maven artifact classifier is malformed")
    return PurePosixPath(
        *group_id.split("."), artifact_id, version, f"{artifact_id}-{version}{suffix}.{kind}"
    )


def load_maven_lock(data: bytes) -> dict[str, Any]:
    """Load canonical Maven lock JSON and validate its frozen closure."""

    if len(data) > MAX_LOCK_BYTES:
        raise _fail("Maven lock exceeds the size limit")
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _fail(f"invalid Maven lock JSON: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != "1.0":
        raise _fail("Maven lock schema_version must be 1.0")
    if not isinstance(payload.get("maven_version"), str) or not MAVEN_VERSION.fullmatch(
        payload["maven_version"]
    ):
        raise _fail("Maven lock requires an exact Maven 3.9.x version")
    if not isinstance(payload.get("jdk_version"), str) or not JDK_VERSION.fullmatch(
        payload["jdk_version"]
    ):
        raise _fail("Maven lock requires an exact JDK 21 identity")
    project = payload.get("effective_project")
    if not isinstance(project, dict):
        raise _fail("Maven lock effective_project is missing")
    _coordinate(
        str(project.get("group_id", "")),
        str(project.get("artifact_id", "")),
        str(project.get("version", "")),
    )
    if project.get("packaging", "jar") != "jar" or project.get("release") not in {8, 11, 17, 21}:
        raise _fail("Maven effective project must be a jar with a supported release")
    artifacts = payload.get("artifacts")
    plugins = payload.get("plugins")
    repositories = payload.get("repositories")
    if (
        not isinstance(artifacts, list)
        or not isinstance(plugins, list)
        or not isinstance(repositories, list)
    ):
        raise _fail("Maven lock artifacts, plugins, and repositories must be arrays")
    if len(artifacts) > MAX_STORE_FILES or len(plugins) > 1_000:
        raise _fail("Maven lock closure exceeds the entry limit")
    keys: list[str] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise _fail("Maven artifact entry must be an object")
        _coordinate(
            str(artifact.get("group_id", "")),
            str(artifact.get("artifact_id", "")),
            str(artifact.get("version", "")),
        )
        maven_repository_path(artifact)
        digest = artifact.get("sha256")
        size = artifact.get("size")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise _fail("Maven artifact sha256 is invalid")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise _fail("Maven artifact size is invalid")
        keys.append(str(maven_repository_path(artifact)))
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise _fail("Maven artifacts must be sorted and unique")
    for plugin in plugins:
        if not isinstance(plugin, dict):
            raise _fail("Maven plugin entry must be an object")
        _coordinate(
            str(plugin.get("group_id", "")),
            str(plugin.get("artifact_id", "")),
            str(plugin.get("version", "")),
        )
    for repository in repositories:
        if not isinstance(repository, dict) or repository.get("url") != ALLOWED_REPOSITORY:
            raise _fail("Maven repository is not approved")
        if repository.get("snapshots_enabled", False) is not False:
            raise _fail("Maven snapshots must be disabled")
    smoke = payload.get("offline_smoke")
    if not isinstance(smoke, dict) or smoke.get("status") != "passed":
        raise _fail("Maven offline smoke is not recorded as passed")
    canonical = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        + b"\n"
    )
    if data != canonical:
        raise _fail("Maven lock JSON is not canonical")
    return payload


def _child_map(root: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for child in list(root):
        name = child.tag.rsplit("}", 1)[-1]
        if name in result:
            raise _fail(f"candidate POM contains duplicate {name}")
        result[name] = child
    return result


def validate_candidate_pom(data: bytes | None) -> dict[str, Any] | None:
    """Parse candidate POM metadata without treating it as build authority."""

    if data is None:
        return None
    if len(data) > MAX_POM_BYTES:
        raise _fail("candidate POM exceeds the size limit")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise _fail("candidate POM DTD and entities are forbidden")
    try:
        root = ElementTree.fromstring(data)
    except Exception as exc:
        raise _fail(f"cannot parse candidate POM: {exc}") from exc
    if root.tag.rsplit("}", 1)[-1] != "project" or root.attrib:
        raise _fail("candidate POM root must be an attribute-free project")
    children = _child_map(root)
    forbidden = {
        "parent",
        "dependencies",
        "dependencyManagement",
        "build",
        "profiles",
        "modules",
        "repositories",
        "pluginRepositories",
        "reporting",
    }
    if forbidden.intersection(children):
        raise _fail("candidate POM contains forbidden build or dependency configuration")
    values = {name: (node.text or "").strip() for name, node in children.items()}
    artifact_id = values.get("artifactId", "")
    if not artifact_id:
        raise _fail("candidate POM artifactId is required")
    _coordinate(values.get("groupId", "example"), artifact_id, values.get("version", "0"))
    packaging = values.get("packaging", "jar")
    if packaging != "jar":
        raise _fail("candidate POM packaging must be jar")
    release: int | None = None
    properties = children.get("properties")
    if properties is not None:
        property_children = list(properties)
        if (
            len(property_children) != 1
            or property_children[0].tag.rsplit("}", 1)[-1] != "maven.compiler.release"
        ):
            raise _fail("candidate POM properties are unsupported")
        try:
            release = int((property_children[0].text or "").strip())
        except ValueError as exc:
            raise _fail("candidate compiler release is invalid") from exc
        if release not in {8, 11, 17, 21}:
            raise _fail("candidate compiler release is unsupported")
    return {
        "group_id": values.get("groupId"),
        "artifact_id": artifact_id,
        "version": values.get("version"),
        "release": release,
    }


class MavenPackageManager:
    """Package-manager adapter for the Java/Maven runtime identity."""

    identity = "maven"
    lockfile_name = "maven-lock-v1.json"

    def validate_lock(self, lockfile: Path, *, expected_version: str) -> MavenLockSummary:
        root = lockfile if lockfile.is_dir() else lockfile.parent
        path = root / self.lockfile_name if lockfile.is_dir() else lockfile
        if path.is_symlink() or not path.is_file():
            raise _fail("Maven lock must be a regular maven-lock-v1.json file")
        payload = load_maven_lock(path.read_bytes())
        if payload["maven_version"] != expected_version:
            raise _fail("Maven lock toolchain does not match the expected Maven version")
        return MavenLockSummary(
            maven_version=payload["maven_version"],
            jdk_version=payload["jdk_version"],
            digest=f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}",
            artifacts=tuple(payload["artifacts"]),
        )

    def validate_offline_store(
        self,
        bundle_root: Path,
        *,
        lockfile: Path,
        manifest: Path,
        expected_version: str,
    ) -> None:
        summary = self.validate_lock(lockfile, expected_version=expected_version)
        if (
            manifest.is_symlink()
            or not manifest.is_file()
            or manifest.stat().st_size > MAX_LOCK_BYTES
        ):
            raise _fail("Maven store inventory must be a bounded regular file")
        try:
            inventory = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise _fail(f"invalid Maven store inventory: {exc}") from exc
        if not isinstance(inventory, dict) or inventory.get("lock_sha256") != summary.digest:
            raise _fail("Maven store inventory does not match the lock")
        files = [
            path
            for path in bundle_root.rglob("*")
            if path.is_file() and path != manifest and path != lockfile
        ]
        if len(files) > MAX_STORE_FILES:
            raise _fail("Maven store contains too many files")
        expected = {maven_repository_path(artifact): artifact for artifact in summary.artifacts}
        actual: set[PurePosixPath] = set()
        for path in files:
            mode = path.lstat().st_mode
            relative = PurePosixPath(path.relative_to(bundle_root).as_posix())
            if (
                stat.S_ISLNK(mode)
                or not stat.S_ISREG(mode)
                or path.name in MUTABLE_STORE_FILES
                or path.suffix.lower() in NATIVE_SUFFIXES
            ):
                raise _fail(f"Maven store contains unsafe payload: {relative}")
            actual.add(relative)
        if actual != set(expected):
            raise _fail("Maven store payload paths do not match the lock")
        for relative, artifact in expected.items():
            data = (bundle_root / relative).read_bytes()
            if (
                len(data) != artifact["size"]
                or hashlib.sha256(data).hexdigest() != artifact["sha256"]
            ):
                raise _fail(f"Maven store payload does not match the lock: {relative}")

    def install_command(self, *, store_dir: str) -> tuple[str, ...]:
        return (
            "/opt/maven/bin/mvn",
            "--offline",
            "--batch-mode",
            "--no-transfer-progress",
            "--strict-checksums",
            f"-Dmaven.repo.local={store_dir}",
            "test",
        )

    def offline_environment(self, profile: object) -> dict[str, str]:
        del profile
        return {
            "MAVEN_ARGS": "--offline --batch-mode --no-transfer-progress --strict-checksums",
            "MAVEN_OPTS": "-Djava.awt.headless=true",
        }


__all__ = [
    "JAVA_MAVEN_IDENTITY",
    "MavenLockSummary",
    "MavenPackageManager",
    "load_maven_lock",
    "maven_repository_path",
    "validate_candidate_pom",
]

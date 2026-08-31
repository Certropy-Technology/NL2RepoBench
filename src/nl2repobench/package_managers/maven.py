"""Pure validation for the first Java/Maven dependency profile."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal, Self, cast
from xml.etree.ElementTree import Element

from defusedxml import ElementTree
from pydantic import BaseModel, ConfigDict, Field, model_validator

from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.storage.canonical_ustar import encode_tree

from .base import (
    CommandSpec,
    LockSummary,
    PackageManagerError,
    PackageManagerErrorCode,
    ResolvedPackage,
    StoreSummary,
    inventory_store_summary,
)

MAX_MAVEN_LOCK_BYTES = 4 * 1024 * 1024
MAX_CANDIDATE_POM_BYTES = 256 * 1024
MAX_POM_NODES = 10_000
MAX_POM_DEPTH = 64
MAX_ARTIFACTS = 20_000
MAX_PLUGINS = 1_000
MAX_PLUGIN_DEPENDENCIES = 100
MAX_STRING = 512
MAVEN_VERSION = re.compile(r"^3\.9\.[0-9]+$")
JDK_VERSION = re.compile(
    r"^[A-Za-z][A-Za-z0-9._-]*-21\.0\.[0-9]+\+[0-9]+(?:\.[0-9]+)?$"
)
COORDINATE_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]*$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
APPROVED_REPOSITORIES = frozenset({"https://repo.maven.apache.org/maven2"})
MUTABLE_STORE_NAMES = frozenset(
    {"_remote.repositories", "resolver-status.properties", "maven-metadata-local.xml"}
)
NATIVE_SUFFIXES = frozenset(
    {".so", ".dll", ".dylib", ".jnilib", ".a", ".o", ".exe", ".bat", ".cmd", ".sh"}
)

JAVA_MAVEN_IDENTITY = RuntimeDiscriminator(
    language=RuntimeLanguage.JAVA,
    package_manager=PackageManager.MAVEN,
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class MavenProject(_StrictModel):
    group_id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    artifact_id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    version: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    packaging: Literal["jar"] = "jar"
    release: Literal[8, 11, 17, 21]
    pom_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class MavenArtifact(_StrictModel):
    group_id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    artifact_id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    version: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    type: Literal["jar", "pom"]
    classifier: Annotated[str | None, Field(min_length=1, max_length=MAX_STRING)] = None
    scope: Literal["compile", "runtime", "test", "provided", "plugin"]
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    size: Annotated[int, Field(ge=0)]


class MavenPlugin(_StrictModel):
    group_id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    artifact_id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    version: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    dependencies: tuple[Annotated[str, Field(min_length=1, max_length=MAX_STRING)], ...] = ()

    @model_validator(mode="after")
    def validate_dependency_bound(self) -> Self:
        if len(self.dependencies) > MAX_PLUGIN_DEPENDENCIES:
            raise ValueError("Maven plugin dependency list exceeds the limit")
        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError("Maven plugin dependency references must be unique")
        return self


class MavenRepository(_StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    url: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    releases_enabled: Literal[True] = True
    snapshots_enabled: Literal[False] = False


class MavenOfflineSmoke(_StrictModel):
    status: Literal["passed"]
    command_id: Literal["maven-offline-compile-discovery-v1"]


class MavenLock(_StrictModel):
    schema_version: Literal["1.0"]
    maven_version: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    jdk_version: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    effective_project: MavenProject
    artifacts: tuple[MavenArtifact, ...]
    plugins: tuple[MavenPlugin, ...]
    repositories: tuple[MavenRepository, ...]
    offline_smoke: MavenOfflineSmoke

    @model_validator(mode="after")
    def validate_closure(self) -> Self:
        if not MAVEN_VERSION.fullmatch(self.maven_version):
            raise ValueError("Maven lock requires an exact Maven 3.9.x version")
        if not JDK_VERSION.fullmatch(self.jdk_version):
            raise ValueError("Maven lock requires an exact JDK 21 distribution and build")
        if len(self.artifacts) > MAX_ARTIFACTS or len(self.plugins) > MAX_PLUGINS:
            raise ValueError("Maven lock closure exceeds the entry limit")
        _validate_coordinate(
            self.effective_project.group_id,
            self.effective_project.artifact_id,
            self.effective_project.version,
        )
        for artifact in self.artifacts:
            _validate_coordinate(artifact.group_id, artifact.artifact_id, artifact.version)
            if artifact.classifier is not None and not COORDINATE_PART.fullmatch(
                artifact.classifier
            ):
                raise ValueError("Maven artifact classifier is malformed")
        for plugin in self.plugins:
            _validate_coordinate(plugin.group_id, plugin.artifact_id, plugin.version)
        keys = tuple(_artifact_key(artifact) for artifact in self.artifacts)
        if tuple(sorted(keys)) != keys or len(set(keys)) != len(keys):
            raise ValueError("Maven artifacts must be sorted by unique coordinate")
        plugin_keys = tuple(
            f"{plugin.group_id}:{plugin.artifact_id}:{plugin.version}" for plugin in self.plugins
        )
        if tuple(sorted(plugin_keys)) != plugin_keys or len(set(plugin_keys)) != len(plugin_keys):
            raise ValueError("Maven plugins must be sorted by unique coordinate")
        artifact_keys = set(keys)
        for plugin in self.plugins:
            prefix = f"{plugin.group_id}:{plugin.artifact_id}:{plugin.version}:"
            if not any(key.startswith(prefix) for key in artifact_keys):
                raise ValueError("Maven plugin is absent from the artifact closure")
            missing = sorted(set(plugin.dependencies) - artifact_keys)
            if missing:
                raise ValueError("Maven plugin dependency is absent from the artifact closure")
            if tuple(sorted(plugin.dependencies)) != plugin.dependencies:
                raise ValueError("Maven plugin dependency references must be sorted")
        for repository in self.repositories:
            if repository.url not in APPROVED_REPOSITORIES:
                raise ValueError("Maven repository is not approved")
        return self


class MavenCandidateMetadata(_StrictModel):
    group_id: str | None = None
    artifact_id: Annotated[str, Field(min_length=1, max_length=MAX_STRING)]
    version: str | None = None
    packaging: Literal["jar"] = "jar"
    release: Literal[8, 11, 17, 21] | None = None


@dataclass(frozen=True, slots=True)
class MavenLockSummary(LockSummary):
    """Validated Maven closure details retained for subsequent store checks."""

    jdk_version: str = ""
    artifacts: tuple[MavenArtifact, ...] = ()


def _error(
    message: str,
    code: PackageManagerErrorCode = PackageManagerErrorCode.LOCK_MALFORMED,
    *,
    stage: str = "lock",
) -> PackageManagerError:
    return PackageManagerError(code, JAVA_MAVEN_IDENTITY, stage, message)


def _validate_coordinate(group_id: str, artifact_id: str, version: str) -> None:
    upper = version.upper()
    if (
        "SNAPSHOT" in upper
        or upper in {"LATEST", "RELEASE"}
        or any(marker in version for marker in "[](),")
    ):
        raise ValueError("Maven dynamic or snapshot versions are forbidden")
    if (
        not all(COORDINATE_PART.fullmatch(part) for part in group_id.split("."))
        or not COORDINATE_PART.fullmatch(artifact_id)
        or not VERSION.fullmatch(version)
    ):
        raise ValueError("Maven coordinate is malformed")


def _artifact_key(artifact: MavenArtifact) -> str:
    classifier = f":{artifact.classifier}" if artifact.classifier is not None else ""
    return (
        f"{artifact.group_id}:{artifact.artifact_id}:{artifact.version}:"
        f"{artifact.type}{classifier}"
    )


def maven_repository_path(artifact: MavenArtifact) -> PurePosixPath:
    """Derive the sole repository payload path for a locked artifact."""

    _validate_coordinate(artifact.group_id, artifact.artifact_id, artifact.version)
    classifier = f"-{artifact.classifier}" if artifact.classifier is not None else ""
    filename = f"{artifact.artifact_id}-{artifact.version}{classifier}.{artifact.type}"
    return PurePosixPath(
        *artifact.group_id.split("."), artifact.artifact_id, artifact.version, filename
    )


def load_maven_lock(data: bytes) -> MavenLock:
    """Load exact canonical Maven lock bytes without filesystem or network access."""

    if len(data) > MAX_MAVEN_LOCK_BYTES:
        raise _error("Maven lock exceeds the size limit")
    try:
        payload = json.loads(data)
        lock = MavenLock.model_validate(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise _error(f"invalid Maven lock: {exc}") from exc
    canonical = json.dumps(
        lock.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    ).encode() + b"\n"
    if data != canonical:
        raise _error("Maven lock JSON is not canonical")
    return lock


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate_candidate_pom(data: bytes | None) -> MavenCandidateMetadata | None:
    """Treat a bounded candidate POM as metadata, never as build authority."""

    if data is None:
        return None
    if len(data) > MAX_CANDIDATE_POM_BYTES:
        raise _error("candidate POM exceeds the size limit", stage="candidate-pom")
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise _error("candidate POM DTD and entities are forbidden", stage="candidate-pom")
    try:
        root = ElementTree.fromstring(data)
    except Exception as exc:
        raise _error(f"cannot parse candidate POM: {exc}", stage="candidate-pom") from exc
    if _local_name(root.tag) != "project" or root.attrib:
        raise _error("candidate POM root must be one attribute-free project", stage="candidate-pom")
    forbidden = {
        "parent",
        "dependencies",
        "dependencyManagement",
        "repositories",
        "pluginRepositories",
        "build",
        "profiles",
        "modules",
        "reporting",
        "distributionManagement",
        "extensions",
        "annotationProcessorPaths",
    }
    nodes = 0
    stack: list[tuple[Element, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        nodes += 1
        if nodes > MAX_POM_NODES or depth > MAX_POM_DEPTH:
            raise _error("candidate POM exceeds structural bounds", stage="candidate-pom")
        if _local_name(node.tag) in forbidden:
            raise _error(
                f"candidate POM element {_local_name(node.tag)} is forbidden",
                stage="candidate-pom",
            )
        if node.attrib:
            raise _error("candidate POM attributes are forbidden", stage="candidate-pom")
        if node.text is not None and len(node.text) > MAX_STRING:
            raise _error("candidate POM text exceeds the size limit", stage="candidate-pom")
        stack.extend((child, depth + 1) for child in list(node))
    allowed_top = {
        "modelVersion",
        "groupId",
        "artifactId",
        "version",
        "packaging",
        "name",
        "description",
        "properties",
    }
    children: dict[str, Element] = {}
    for child in list(root):
        name = _local_name(child.tag)
        if name not in allowed_top or name in children:
            raise _error(f"candidate POM element {name} is unsupported", stage="candidate-pom")
        children[name] = child
    model = children.get("modelVersion")
    if model is None or (model.text or "").strip() != "4.0.0":
        raise _error("candidate POM requires modelVersion 4.0.0", stage="candidate-pom")

    def text(name: str) -> str | None:
        node = children.get(name)
        value = (node.text or "").strip() if node is not None else ""
        if len(value) > MAX_STRING:
            raise _error("candidate POM value exceeds the size limit", stage="candidate-pom")
        return value or None

    artifact_id = text("artifactId")
    if artifact_id is None:
        raise _error("candidate POM requires artifactId", stage="candidate-pom")
    packaging = text("packaging") or "jar"
    if packaging != "jar":
        raise _error("candidate POM packaging must be jar", stage="candidate-pom")
    group_id = text("groupId")
    version = text("version")
    try:
        _validate_coordinate(group_id or "example", artifact_id, version or "0")
    except ValueError as exc:
        raise _error(f"candidate POM coordinate is invalid: {exc}", stage="candidate-pom") from exc
    release: Literal[8, 11, 17, 21] | None = None
    properties = children.get("properties")
    if properties is not None:
        property_nodes = list(properties)
        if len(property_nodes) > 1:
            raise _error("candidate POM properties are unsupported", stage="candidate-pom")
        if property_nodes:
            prop = property_nodes[0]
            if _local_name(prop.tag) != "maven.compiler.release":
                raise _error("candidate POM property is unsupported", stage="candidate-pom")
            try:
                release_value = int((prop.text or "").strip())
            except ValueError as exc:
                raise _error(
                    "candidate compiler release is invalid", stage="candidate-pom"
                ) from exc
            if release_value not in {8, 11, 17, 21}:
                raise _error("candidate compiler release is unsupported", stage="candidate-pom")
            release = cast(Literal[8, 11, 17, 21], release_value)
    try:
        return MavenCandidateMetadata(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
            packaging="jar",
            release=release,
        )
    except ValueError as exc:
        raise _error(f"candidate POM metadata is invalid: {exc}", stage="candidate-pom") from exc


class MavenPackageManager:
    identity = JAVA_MAVEN_IDENTITY
    lockfile_names = ("maven-lock-v1.json",)

    def validate_lock(
        self,
        lock_root: Path,
        expected_toolchain: str,
        *,
        expected_jdk_version: str | None = None,
    ) -> LockSummary:
        if lock_root.is_symlink() or not lock_root.is_dir():
            raise _error("Maven lock root is missing", PackageManagerErrorCode.LOCK_MISSING)
        entries = list(lock_root.iterdir())
        lock_path = lock_root / self.lockfile_names[0]
        if (
            len(entries) != 1
            or entries[0].name != self.lockfile_names[0]
            or lock_path.is_symlink()
            or not lock_path.is_file()
        ):
            raise _error("Maven lock root must contain only maven-lock-v1.json")
        try:
            lock = load_maven_lock(lock_path.read_bytes())
        except OSError as exc:
            raise _error(
                f"cannot read Maven lock: {exc}", PackageManagerErrorCode.LOCK_MISSING
            ) from exc
        if lock.maven_version != expected_toolchain:
            raise _error(
                "Maven lock toolchain does not match the expected Maven version",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
            )
        if expected_jdk_version is None:
            raise _error(
                "Java/Maven lock validation requires the selected exact JDK identity",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
            )
        if not JDK_VERSION.fullmatch(expected_jdk_version):
            raise _error(
                "selected JDK identity is not an exact JDK 21 distribution and build",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
            )
        if lock.jdk_version != expected_jdk_version:
            raise _error(
                "Maven lock JDK identity does not match the selected JDK",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
            )
        return MavenLockSummary(
            identity=self.identity,
            toolchain_version=lock.maven_version,
            lockfile_names=self.lockfile_names,
            lock_digest=f"sha256:{hashlib.sha256(encode_tree(lock_root)).hexdigest()}",
            jdk_version=lock.jdk_version,
            artifacts=lock.artifacts,
            resolved=tuple(
                ResolvedPackage(
                    name=_artifact_key(artifact),
                    version=artifact.version,
                    kind=f"maven-{artifact.scope}",
                    artifact_digest=f"sha256:{artifact.sha256}",
                )
                for artifact in lock.artifacts
            ),
        )

    def validate_offline_store(
        self,
        store_root: Path,
        lock_summary: LockSummary,
        inventory: object,
        expected_toolchain: str,
        *,
        expected_jdk_version: str | None = None,
    ) -> StoreSummary:
        if (
            lock_summary.identity != self.identity
            or lock_summary.toolchain_version != expected_toolchain
        ):
            raise _error(
                "Maven lock and store toolchains do not match",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                stage="store",
            )
        if not isinstance(lock_summary, MavenLockSummary):
            raise _error(
                "Maven store requires a Maven lock summary",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        if expected_jdk_version is None:
            raise _error(
                "Java/Maven store validation requires the selected exact JDK identity",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                stage="store",
            )
        if lock_summary.jdk_version != expected_jdk_version:
            raise _error(
                "Maven lock JDK identity does not match the selected JDK",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                stage="store",
            )
        summary = inventory_store_summary(
            identity=self.identity,
            store_root=store_root,
            inventory=inventory,
        )
        if not isinstance(inventory, dict) or inventory.get("adapter_version") != "maven-lock-v1":
            raise _error(
                "Maven inventory adapter version is invalid",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        lock_inventory = inventory.get("lock")
        if (
            not isinstance(lock_inventory, dict)
            or lock_inventory.get("archive_digest") != lock_summary.lock_digest
            or lock_inventory.get("jdk_version") != expected_jdk_version
        ):
            raise _error(
                "Maven inventory lock digest does not match the validated lock",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        smoke = inventory.get("offline_smoke")
        if not isinstance(smoke, dict) or smoke.get("command_id") != (
            "maven-offline-compile-discovery-v1"
        ):
            raise _error(
                "Maven offline smoke command is invalid",
                PackageManagerErrorCode.OFFLINE_SMOKE_FAILED,
                stage="store",
            )
        expected_paths = {
            maven_repository_path(artifact): artifact for artifact in lock_summary.artifacts
        }
        actual_paths: set[PurePosixPath] = set()
        for path in store_root.rglob("*"):
            relative = PurePosixPath(path.relative_to(store_root).as_posix())
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode) or mode & 0o111 or path.stat().st_nlink != 1:
                raise _error(
                    f"Maven store contains unsafe payload: {relative}",
                    PackageManagerErrorCode.STORE_MALFORMED,
                    stage="store",
                )
            if path.name in MUTABLE_STORE_NAMES or path.name.endswith(".lastUpdated"):
                raise _error(
                    f"Maven store contains mutable metadata: {relative}",
                    PackageManagerErrorCode.STORE_MALFORMED,
                    stage="store",
                )
            if path.suffix.casefold() in NATIVE_SUFFIXES:
                raise _error(
                    f"Maven store contains native or executable payload: {relative}",
                    PackageManagerErrorCode.STORE_MALFORMED,
                    stage="store",
                )
            actual_paths.add(relative)
        if actual_paths != set(expected_paths):
            raise _error(
                "Maven store payload paths do not match the locked closure",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        for relative, artifact in expected_paths.items():
            data = (store_root / relative).read_bytes()
            if len(data) != artifact.size or hashlib.sha256(data).hexdigest() != artifact.sha256:
                raise _error(
                    f"Maven store payload does not match lock: {relative}",
                    PackageManagerErrorCode.INVENTORY_MISMATCH,
                    stage="store",
                )
        return summary

    def build_commands(self, profile: object) -> tuple[CommandSpec, ...]:
        del profile
        raise _error(
            "Java/Maven build commands require the future candidate supervisor profile",
            PackageManagerErrorCode.UNSUPPORTED_PROFILE,
            stage="build",
        )

    def offline_environment(self, profile: object) -> dict[str, str]:
        del profile
        return {
            "MAVEN_ARGS": "--offline --batch-mode --no-transfer-progress --strict-checksums",
            "MAVEN_OPTS": "-Djava.awt.headless=true",
        }


__all__ = [
    "JAVA_MAVEN_IDENTITY",
    "MavenArtifact",
    "MavenCandidateMetadata",
    "MavenLock",
    "MavenLockSummary",
    "MavenPackageManager",
    "load_maven_lock",
    "maven_repository_path",
    "validate_candidate_pom",
]
